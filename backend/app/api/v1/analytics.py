from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import Job, JobContact, ContactType, JobVerification, SourceConnection, SourceStatus, SystemEvent, User, JobStatus, RiskLevel
from app.schemas import (
    StatsResponse, ChartDataPoint, VerificationActivityChart,
    JobsBySourceChart, RiskDistributionChart, DashboardResponse
)
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/overview", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Job).where(Job.user_id == current_user.id)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    total_jobs = len(jobs)
    verified_jobs = sum(1 for j in jobs if j.status == JobStatus.VERIFIED)
    needs_review = sum(1 for j in jobs if j.status == JobStatus.NEEDS_REVIEW)
    high_risk = sum(1 for j in jobs if j.risk_level == RiskLevel.HIGH)

    total_contacts = 0
    corporate_emails = 0
    free_mail_emails = 0
    valid_phones = 0

    for job in jobs:
        for c in job.contacts:
            if c.is_valid:
                total_contacts += 1
                if c.type == ContactType.EMAIL:
                    if c.is_corporate:
                        corporate_emails += 1
                    else:
                        free_mail_emails += 1
                elif c.type == ContactType.PHONE:
                    valid_phones += 1

    stmt = select(func.count(func.distinct(SourceConnection.source_id))).where(
        SourceConnection.user_id == current_user.id,
        SourceConnection.status == SourceStatus.CONNECTED
    )
    sources_result = await db.execute(stmt)
    sources_active = sources_result.scalar() or 0

    today = datetime.utcnow().date()
    jobs_today = sum(1 for j in jobs if j.created_at.date() == today)
    verified_today = sum(1 for j in jobs if j.verified_at and j.verified_at.date() == today)

    stats = StatsResponse(
        total_jobs=total_jobs,
        verified_jobs=verified_jobs,
        needs_review=needs_review,
        high_risk=high_risk,
        total_contacts=total_contacts,
        corporate_emails=corporate_emails,
        free_mail_emails=free_mail_emails,
        valid_phones=valid_phones,
        sources_active=sources_active,
        jobs_today=jobs_today,
        verified_today=verified_today,
    )

    verification_activity = await _get_verification_activity(db, current_user.id)
    jobs_by_source = await _get_jobs_by_source(db, current_user.id)
    risk_distribution = await _get_risk_distribution(db, current_user.id)
    recent_jobs = await _get_recent_jobs(db, current_user.id, 5)
    recent_events = await _get_recent_events(db, current_user.id, 10)
    source_health = await _get_source_health(db, current_user.id)

    return DashboardResponse(
        stats=stats,
        verification_activity=verification_activity,
        jobs_by_source=jobs_by_source,
        risk_distribution=risk_distribution,
        recent_jobs=recent_jobs,
        recent_events=recent_events,
        source_health=source_health,
    )


async def _get_verification_activity(db: AsyncSession, user_id: int) -> VerificationActivityChart:
    week_ago = datetime.utcnow() - timedelta(days=7)

    stmt = (
        select(func.date(Job.verified_at).label("date"), func.count().label("count"))
        .where(Job.user_id == user_id, Job.verified_at >= week_ago)
        .group_by(func.date(Job.verified_at))
        .order_by(func.date(Job.verified_at))
    )
    result = await db.execute(stmt)
    data = result.all()

    chart_data = []
    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=6-i)).date()
        count = next((row.count for row in data if row.date == date), 0)
        chart_data.append(ChartDataPoint(label=date.strftime("%a"), value=count))

    return VerificationActivityChart(data=chart_data)


async def _get_jobs_by_source(db: AsyncSession, user_id: int) -> JobsBySourceChart:
    stmt = (
        select(SourceConnection.source_id, SourceConnection.source.has(Source.name), func.count())
        .join(SourceConnection, Job.source_id == SourceConnection.source_id)
        .where(Job.user_id == user_id)
        .group_by(SourceConnection.source_id)
    )
    result = await db.execute(stmt)
    data = result.all()

    chart_data = []
    for row in data:
        chart_data.append(ChartDataPoint(label=row[1] or "Unknown", value=row[2]))

    return JobsBySourceChart(data=chart_data)


async def _get_risk_distribution(db: AsyncSession, user_id: int) -> RiskDistributionChart:
    stmt = (
        select(Job.risk_level, func.count())
        .where(Job.user_id == user_id)
        .group_by(Job.risk_level)
    )
    result = await db.execute(stmt)
    data = result.all()

    chart_data = []
    for level, count in data:
        chart_data.append(ChartDataPoint(label=level.value if level else "Unknown", value=count))

    return RiskDistributionChart(data=chart_data)


async def _get_recent_jobs(db: AsyncSession, user_id: int, limit: int) -> List:
    stmt = (
        select(Job)
        .where(Job.user_id == user_id)
        .options(selectinload(Job.company), selectinload(Job.source))
        .order_by(Job.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company.name if j.company else None,
            "source": j.source.name if j.source else None,
            "risk_level": j.risk_level.value if j.risk_level else None,
            "status": j.status.value if j.status else None,
            "has_email": any(c.type == ContactType.EMAIL and c.is_valid for c in j.contacts),
            "has_phone": any(c.type == ContactType.PHONE and c.is_valid for c in j.contacts),
            "created_at": j.created_at.isoformat(),
        }
        for j in jobs
    ]


async def _get_recent_events(db: AsyncSession, user_id: int, limit: int) -> List:
    stmt = (
        select(SystemEvent)
        .where(SystemEvent.details.op("->>")("user_id") == str(user_id))
        .order_by(SystemEvent.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()

    return [
        {
            "type": e.event_type,
            "message": e.message,
            "level": e.level,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]


async def _get_source_health(db: AsyncSession, user_id: int) -> List:
    stmt = (
        select(SourceConnection)
        .where(SourceConnection.user_id == user_id)
        .options(selectinload(SourceConnection.source))
    )
    result = await db.execute(stmt)
    connections = result.scalars().all()

    return [
        {
            "source": c.source.name if c.source else "Unknown",
            "status": c.status.value,
            "last_sync": c.last_sync_at.isoformat() if c.last_sync_at else None,
            "jobs_collected": c.jobs_collected,
            "last_error": c.last_error,
        }
        for c in connections
    ]


@router.get("/sources")
async def get_sources_analytics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Job.source_id, func.count().label("total"), func.sum(func.case((Job.status == JobStatus.VERIFIED, 1), else_=0)).label("verified"))
        .where(Job.user_id == current_user.id)
        .group_by(Job.source_id)
    )
    result = await db.execute(stmt)
    data = result.all()

    return [
        {
            "source_id": row[0],
            "total_jobs": row[1],
            "verified_jobs": row[2] or 0,
            "verification_rate": round((row[2] or 0) / row[1] * 100, 1) if row[1] > 0 else 0,
        }
        for row in data
    ]


@router.get("/risk")
async def get_risk_analytics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(RiskEvent.signal, func.count().label("count"))
        .join(Job, Job.id == RiskEvent.job_id)
        .where(Job.user_id == current_user.id)
        .group_by(RiskEvent.signal)
        .order_by(func.count().desc())
        .limit(20)
    )
    result = await db.execute(stmt)
    data = result.all()

    return [
        {"signal": row[0], "count": row[1]}
        for row in data
    ]