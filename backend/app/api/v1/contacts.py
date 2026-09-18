from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import Job, JobContact, ContactType, JobVerification, User
from app.schemas import ContactInfo, PaginatedResponse
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/job/{job_id}", response_model=List[ContactInfo])
async def get_job_contacts(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    stmt = select(JobContact).where(JobContact.job_id == job_id)
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    return [
        ContactInfo(
            type=c.type,
            value=c.value,
            normalized_value=c.normalized_value,
            is_valid=c.is_valid,
            is_corporate=c.is_corporate,
            domain=c.domain,
            confidence=c.confidence,
            verification_method=c.verification_method,
            verification_status=c.verification_status,
        )
        for c in contacts
    ]


@router.get("", response_model=PaginatedResponse)
async def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    contact_type: Optional[ContactType] = None,
    is_valid: Optional[bool] = None,
    is_corporate: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(JobContact)
        .join(Job, Job.id == JobContact.job_id)
        .where(Job.user_id == current_user.id)
        .options(selectinload(JobContact.job).selectinload(Job.company))
    )

    if contact_type:
        stmt = stmt.where(JobContact.type == contact_type)
    if is_valid is not None:
        stmt = stmt.where(JobContact.is_valid == is_valid)
    if is_corporate is not None:
        stmt = stmt.where(JobContact.is_corporate == is_corporate)
    if search:
        stmt = stmt.where(JobContact.normalized_value.ilike(f"%{search}%"))

    stmt = stmt.order_by(JobContact.created_at.desc())

    from sqlalchemy import func
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    items = []
    for c in contacts:
        items.append({
            "job": {
                "id": c.job.id,
                "title": c.job.title,
                "company": c.job.company.name if c.job.company else None,
            },
            "contact": ContactInfo(
                type=c.type,
                value=c.value,
                normalized_value=c.normalized_value,
                is_valid=c.is_valid,
                is_corporate=c.is_corporate,
                domain=c.domain,
                confidence=c.confidence,
                verification_method=c.verification_method,
                verification_status=c.verification_status,
            ),
            "source": c.job.source.name if c.job.source else "",
            "created_at": c.created_at,
        })

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/stats/summary")
async def get_contacts_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(JobContact)
        .join(Job, Job.id == JobContact.job_id)
        .where(Job.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    total = len(contacts)
    corporate_emails = sum(1 for c in contacts if c.type == ContactType.EMAIL and c.is_corporate and c.is_valid)
    free_mail = sum(1 for c in contacts if c.type == ContactType.EMAIL and not c.is_corporate and c.is_valid)
    valid_phones = sum(1 for c in contacts if c.type == ContactType.PHONE and c.is_valid)
    invalid = sum(1 for c in contacts if not c.is_valid)
    unverified = sum(1 for c in contacts if c.verification_status == "pending")

    return {
        "total_contacts": total,
        "corporate_emails": corporate_emails,
        "free_mail_addresses": free_mail,
        "valid_phones": valid_phones,
        "invalid_contacts": invalid,
        "unverified_contacts": unverified,
    }