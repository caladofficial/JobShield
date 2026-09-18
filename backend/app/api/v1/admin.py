from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User, SourceConnection, SourceStatus, Job, JobVerification, SystemEvent, Export, EmailCampaign, UserRole
import structlog

logger = structlog.get_logger()

router = APIRouter()


async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/health")
async def system_health(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    db_status = "healthy"
    try:
        await db.execute(select(1))
    except Exception:
        db_status = "unhealthy"

    redis_status = "healthy"
    try:
        from app.workers.celery_app import celery_app
        celery_app.control.ping(timeout=2)
    except Exception:
        redis_status = "unhealthy"

    return {
        "database": db_status,
        "redis": redis_status,
        "api": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/sources")
async def source_health(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(SourceConnection)
        .options(selectinload(SourceConnection.source), selectinload(SourceConnection.user))
    )
    result = await db.execute(stmt)
    connections = result.scalars().all()

    return [
        {
            "connection_id": c.id,
            "source": c.source.name if c.source else "Unknown",
            "user": c.user.email if c.user else "Unknown",
            "status": c.status.value,
            "last_sync": c.last_sync_at.isoformat() if c.last_sync_at else None,
            "jobs_collected": c.jobs_collected,
            "last_error": c.last_error,
            "rate_limit_remaining": c.rate_limit_remaining,
            "rate_limit_reset_at": c.rate_limit_reset_at.isoformat() if c.rate_limit_reset_at else None,
        }
        for c in connections
    ]


@router.get("/verification")
async def verification_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        func.count(Job.id).label("total"),
        func.sum(func.case((Job.status == "verified", 1), else_=0)).label("verified"),
        func.sum(func.case((Job.status == "needs_review", 1), else_=0)).label("needs_review"),
        func.sum(func.case((Job.risk_level == "high", 1), else_=0)).label("high_risk"),
    )
    result = await db.execute(stmt)
    row = result.first()

    return {
        "jobs_scanned": row[0] or 0,
        "jobs_verified": row[1] or 0,
        "jobs_needs_review": row[2] or 0,
        "jobs_high_risk": row[3] or 0,
    }


@router.get("/api-usage")
async def api_usage(
    days: int = 7,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)

    stmt = (
        select(SystemEvent.event_type, func.count().label("count"))
        .where(SystemEvent.created_at >= since)
        .group_by(SystemEvent.event_type)
        .order_by(func.count().desc())
    )
    result = await db.execute(stmt)
    data = result.all()

    return {
        "period_days": days,
        "events": [{"type": row[0], "count": row[1]} for row in data],
    }


@router.get("/errors")
async def error_logs(
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(SystemEvent)
        .where(SystemEvent.level.in_(["error", "critical"]))
        .order_by(SystemEvent.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()

    return [
        {
            "id": e.id,
            "type": e.event_type,
            "source": e.source,
            "level": e.level,
            "message": e.message,
            "details": e.details,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]


@router.get("/audit")
async def audit_logs(
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.models import AuditLog
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "resource_type": l.resource_type,
            "resource_id": l.resource_id,
            "details": l.details,
            "ip_address": l.ip_address,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]


@router.get("/queue")
async def queue_status(
    current_user: User = Depends(require_admin),
):
    from app.workers.celery_app import celery_app

    try:
        inspect = celery_app.control.inspect()
        active = inspect.active()
        scheduled = inspect.scheduled()
        reserved = inspect.reserved()
        stats = inspect.stats()

        return {
            "active_tasks": active,
            "scheduled_tasks": scheduled,
            "reserved_tasks": reserved,
            "worker_stats": stats,
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/queue/purge")
async def purge_queue(
    queue_name: str,
    current_user: User = Depends(require_admin),
):
    from app.workers.celery_app import celery_app

    try:
        celery_app.control.purge()
        return {"message": f"Queue {queue_name} purged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))