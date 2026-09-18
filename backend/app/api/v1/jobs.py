from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import Job, JobContact, ContactType, JobVerification, Source, Company, Recruiter, User, JobStatus, RiskLevel
from app.schemas import (
    JobCreate, JobUpdate, JobResponse, JobListItem, JobScanRequest, JobScanResponse,
    PaginatedResponse, VerificationProgress
)
from app.workers.ingestion import ingest_from_source
from app.workers.normalization import normalize_job_task
from app.workers.verification import verify_job_task
from app.services.source_adapters import get_adapter, NormalizedJob
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[JobStatus] = None,
    risk_level: Optional[RiskLevel] = None,
    source_id: Optional[int] = None,
    company_id: Optional[int] = None,
    location: Optional[str] = None,
    employment_type: Optional[str] = None,
    has_email: Optional[bool] = None,
    has_phone: Optional[bool] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|posted_at|title|verification_score|risk_level)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Job)
        .where(Job.user_id == current_user.id)
        .options(
            selectinload(Job.source),
            selectinload(Job.company),
            selectinload(Job.recruiter),
            selectinload(Job.contacts),
            selectinload(Job.verification),
        )
    )

    if search:
        stmt = stmt.where(or_(
            Job.title.ilike(f"%{search}%"),
            Job.description.ilike(f"%{search}%"),
            Company.name.ilike(f"%{search}%"),
        )).join(Company, isouter=True)

    if status:
        stmt = stmt.where(Job.status == status)
    if risk_level:
        stmt = stmt.where(Job.risk_level == risk_level)
    if source_id:
        stmt = stmt.where(Job.source_id == source_id)
    if company_id:
        stmt = stmt.where(Job.company_id == company_id)
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
    if employment_type:
        stmt = stmt.where(Job.employment_type == employment_type)
    if has_email:
        stmt = stmt.where(Job.contacts.any(JobContact.type == ContactType.EMAIL, JobContact.is_valid == True))
    if has_phone:
        stmt = stmt.where(Job.contacts.any(JobContact.type == ContactType.PHONE, JobContact.is_valid == True))
    if date_from:
        stmt = stmt.where(Job.posted_at >= date_from)
    if date_to:
        stmt = stmt.where(Job.posted_at <= date_to)

    sort_column = getattr(Job, sort_by, Job.created_at)
    if sort_order == "desc":
        stmt = stmt.order_by(sort_column.desc())
    else:
        stmt = stmt.order_by(sort_column.asc())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    items = []
    for job in jobs:
        has_email_val = any(c.type == ContactType.EMAIL and c.is_valid for c in job.contacts)
        has_phone_val = any(c.type == ContactType.PHONE and c.is_valid for c in job.contacts)
        items.append(JobListItem(
            id=job.id,
            source_id=job.source_id,
            source_job_id=job.source_job_id,
            source_url=job.source_url,
            title=job.title,
            company_name=job.company.name if job.company else None,
            company_id=job.company_id,
            location=job.location,
            employment_type=job.employment_type,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            currency=job.currency,
            posted_at=job.posted_at,
            status=job.status,
            risk_level=job.risk_level,
            verification_score=job.verification_score,
            created_at=job.created_at,
            has_email=has_email_val,
            has_phone=has_phone_val,
            source_name=job.source.name if job.source else "",
        ))

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("/scan", response_model=JobScanResponse)
async def scan_job(
    request: JobScanRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if request.source_id:
        stmt = select(Source).where(Source.id == request.source_id, Source.is_active == True)
        result = await db.execute(stmt)
        source = result.scalar_one_or_none()
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        source_name = source.name.lower()
    else:
        source_name = "manual"

    adapter = get_adapter(source_name, {})
    norm_job = await adapter.get_job(str(request.source_url))

    if not norm_job:
        raise HTTPException(status_code=400, detail="Could not extract job from URL")

    job = Job(
        user_id=current_user.id,
        source_id=source.id if request.source_id else 1,
        source_job_id=norm_job.source_job_id,
        source_url=str(request.source_url),
        title=norm_job.title,
        description=norm_job.description,
        location=norm_job.location,
        employment_type=norm_job.employment_type,
        salary_min=norm_job.salary.get("min") if norm_job.salary else None,
        salary_max=norm_job.salary.get("max") if norm_job.salary else None,
        currency=norm_job.salary.get("currency", "INR") if norm_job.salary else "INR",
        posted_at=norm_job.posted_at,
        expires_at=norm_job.expires_at,
        apply_url=norm_job.apply_url,
        status=JobStatus.NEW,
        raw_source_metadata=norm_job.raw_source_metadata,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    normalize_job_task.delay(current_user.id, job.source_id, norm_job.__dict__)

    return JobScanResponse(
        job_id=job.id,
        status=JobStatus.PROCESSING,
        message="Job submitted for processing"
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Job)
        .where(Job.id == job_id, Job.user_id == current_user.id)
        .options(
            selectinload(Job.source),
            selectinload(Job.company),
            selectinload(Job.recruiter),
            selectinload(Job.contacts),
            selectinload(Job.verification),
        )
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    contacts = []
    for c in job.contacts:
        contacts.append({
            "type": c.type,
            "value": c.value,
            "normalized_value": c.normalized_value,
            "is_valid": c.is_valid,
            "is_corporate": c.is_corporate,
            "domain": c.domain,
            "confidence": c.confidence,
            "verification_method": c.verification_method,
            "verification_status": c.verification_status,
        })

    verification = None
    if job.verification:
        verification = {
            "source_score": job.verification.source_score,
            "employer_score": job.verification.employer_score,
            "uploader_score": job.verification.uploader_score,
            "content_score": job.verification.content_score,
            "contact_score": job.verification.contact_score,
            "risk_score": job.verification.risk_score,
            "final_confidence": job.verification.final_confidence,
            "status": job.verification.status,
            "source_signals": job.verification.source_signals,
            "employer_signals": job.verification.employer_signals,
            "uploader_signals": job.verification.uploader_signals,
            "content_signals": job.verification.content_signals,
            "contact_signals": job.verification.contact_signals,
            "risk_signals": job.verification.risk_signals,
            "ai_analysis": job.verification.ai_analysis,
            "verified_at": job.verification.verified_at,
        }

    return JobResponse(
        id=job.id,
        user_id=job.user_id,
        source_id=job.source_id,
        source_job_id=job.source_job_id,
        source_url=job.source_url,
        title=job.title,
        company_name=job.company.name if job.company else None,
        description=job.description,
        location=job.location,
        employment_type=job.employment_type,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        currency=job.currency,
        posted_at=job.posted_at,
        expires_at=job.expires_at,
        apply_url=job.apply_url,
        status=job.status,
        risk_level=job.risk_level,
        verification_score=job.verification_score,
        created_at=job.created_at,
        updated_at=job.updated_at,
        verified_at=job.verified_at,
        company=job.company,
        recruiter=job.recruiter,
        contacts=contacts,
        verification=verification,
    )


@router.post("/{job_id}/reverify")
async def reverify_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    verify_job_task.delay(job_id)

    return {"message": "Verification started", "job_id": job_id}


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    await db.delete(job)
    await db.commit()

    return {"message": "Job deleted"}


@router.get("/stats/summary")
async def get_job_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Job).where(Job.user_id == current_user.id)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    total = len(jobs)
    verified = sum(1 for j in jobs if j.status == JobStatus.VERIFIED)
    needs_review = sum(1 for j in jobs if j.status == JobStatus.NEEDS_REVIEW)
    high_risk = sum(1 for j in jobs if j.risk_level == RiskLevel.HIGH)

    contacts = 0
    emails = 0
    phones = 0
    for job in jobs:
        for c in job.contacts:
            if c.is_valid:
                contacts += 1
                if c.type == ContactType.EMAIL:
                    emails += 1
                elif c.type == ContactType.PHONE:
                    phones += 1

    sources_stmt = select(func.count(func.distinct(Job.source_id))).where(Job.user_id == current_user.id)
    sources_result = await db.execute(sources_stmt)
    sources_active = sources_result.scalar() or 0

    return {
        "total_jobs": total,
        "verified_jobs": verified,
        "needs_review": needs_review,
        "high_risk": high_risk,
        "total_contacts": contacts,
        "emails_found": emails,
        "phones_found": phones,
        "sources_active": sources_active,
    }