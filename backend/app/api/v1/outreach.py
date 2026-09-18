from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import EmailCampaign, EmailRecipient, Job, JobContact, ContactType, User
from app.schemas import (
    EmailCampaignCreate, EmailCampaignUpdate, EmailCampaignResponse,
    EmailRecipientResponse, PaginatedResponse
)
from app.workers.email import send_campaign_task, send_test_email_task
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/campaigns", response_model=PaginatedResponse)
async def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(EmailCampaign).where(EmailCampaign.user_id == current_user.id)

    if status:
        stmt = stmt.where(EmailCampaign.status == status)

    stmt = stmt.order_by(EmailCampaign.created_at.desc())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    campaigns = result.scalars().all()

    return PaginatedResponse(
        items=[
            EmailCampaignResponse(
                id=c.id,
                user_id=c.user_id,
                name=c.name,
                subject_template=c.subject_template,
                body_html_template=c.body_html_template,
                body_text_template=c.body_text_template,
                from_email=c.from_email,
                from_name=c.from_name,
                provider=c.provider,
                status=c.status,
                total_recipients=c.total_recipients,
                sent_count=c.sent_count,
                failed_count=c.failed_count,
                created_at=c.created_at,
                updated_at=c.updated_at,
                sent_at=c.sent_at,
            )
            for c in campaigns
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("/campaigns", response_model=EmailCampaignResponse, status_code=201)
async def create_campaign(
    campaign_in: EmailCampaignCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    contacts = []
    if campaign_in.recipient_contact_ids:
        stmt = (
            select(JobContact)
            .join(Job, Job.id == JobContact.job_id)
            .where(JobContact.id.in_(campaign_in.recipient_contact_ids), Job.user_id == current_user.id)
        )
        result = await db.execute(stmt)
        contacts = result.scalars().all()

        if len(contacts) != len(campaign_in.recipient_contact_ids):
            raise HTTPException(status_code=400, detail="Some contacts not found or not accessible")

    campaign = EmailCampaign(
        user_id=current_user.id,
        name=campaign_in.name,
        subject_template=campaign_in.subject_template,
        body_html_template=campaign_in.body_html_template,
        body_text_template=campaign_in.body_text_template,
        from_email=campaign_in.from_email,
        from_name=campaign_in.from_name,
        provider=campaign_in.provider,
        status="draft",
        total_recipients=len(contacts),
    )
    db.add(campaign)
    await db.flush()

    for contact in contacts:
        job = contact.job
        recruiter_name = job.recruiter.name if job.recruiter else None

        recipient = EmailRecipient(
            campaign_id=campaign.id,
            job_id=job.id,
            contact_id=contact.id,
            email=contact.normalized_value,
            name=recruiter_name,
            status="pending",
        )
        db.add(recipient)

    await db.commit()
    await db.refresh(campaign)

    return EmailCampaignResponse(
        id=campaign.id,
        user_id=campaign.user_id,
        name=campaign.name,
        subject_template=campaign.subject_template,
        body_html_template=campaign.body_html_template,
        body_text_template=campaign.body_text_template,
        from_email=campaign.from_email,
        from_name=campaign.from_name,
        provider=campaign.provider,
        status=campaign.status,
        total_recipients=campaign.total_recipients,
        sent_count=campaign.sent_count,
        failed_count=campaign.failed_count,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        sent_at=campaign.sent_at,
    )


@router.get("/campaigns/{campaign_id}", response_model=EmailCampaignResponse)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(EmailCampaign).where(EmailCampaign.id == campaign_id, EmailCampaign.user_id == current_user.id)
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return EmailCampaignResponse(
        id=campaign.id,
        user_id=campaign.user_id,
        name=campaign.name,
        subject_template=campaign.subject_template,
        body_html_template=campaign.body_html_template,
        body_text_template=campaign.body_text_template,
        from_email=campaign.from_email,
        from_name=campaign.from_name,
        provider=campaign.provider,
        status=campaign.status,
        total_recipients=campaign.total_recipients,
        sent_count=campaign.sent_count,
        failed_count=campaign.failed_count,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        sent_at=campaign.sent_at,
    )


@router.patch("/campaigns/{campaign_id}", response_model=EmailCampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_update: EmailCampaignUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(EmailCampaign).where(EmailCampaign.id == campaign_id, EmailCampaign.user_id == current_user.id)
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign_update.name is not None:
        campaign.name = campaign_update.name
    if campaign_update.subject_template is not None:
        campaign.subject_template = campaign_update.subject_template
    if campaign_update.body_html_template is not None:
        campaign.body_html_template = campaign_update.body_html_template
    if campaign_update.body_text_template is not None:
        campaign.body_text_template = campaign_update.body_text_template
    if campaign_update.from_email is not None:
        campaign.from_email = campaign_update.from_email
    if campaign_update.from_name is not None:
        campaign.from_name = campaign_update.from_name
    if campaign_update.status is not None:
        campaign.status = campaign_update.status

    campaign.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(campaign)

    return EmailCampaignResponse(
        id=campaign.id,
        user_id=campaign.user_id,
        name=campaign.name,
        subject_template=campaign.subject_template,
        body_html_template=campaign.body_html_template,
        body_text_template=campaign.body_text_template,
        from_email=campaign.from_email,
        from_name=campaign.from_name,
        provider=campaign.provider,
        status=campaign.status,
        total_recipients=campaign.total_recipients,
        sent_count=campaign.sent_count,
        failed_count=campaign.failed_count,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        sent_at=campaign.sent_at,
    )


@router.get("/campaigns/{campaign_id}/recipients", response_model=PaginatedResponse)
async def list_campaign_recipients(
    campaign_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(EmailCampaign).where(EmailCampaign.id == campaign_id, EmailCampaign.user_id == current_user.id)
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    stmt = select(EmailRecipient).where(EmailRecipient.campaign_id == campaign_id)

    if status:
        stmt = stmt.where(EmailRecipient.status == status)

    stmt = stmt.order_by(EmailRecipient.created_at.desc())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    recipients = result.scalars().all()

    return PaginatedResponse(
        items=[
            EmailRecipientResponse(
                id=r.id,
                campaign_id=r.campaign_id,
                job_id=r.job_id,
                contact_id=r.contact_id,
                email=r.email,
                name=r.name,
                status=r.status,
                sent_at=r.sent_at,
                delivered_at=r.delivered_at,
                opened_at=r.opened_at,
                clicked_at=r.clicked_at,
                bounced_at=r.bounced_at,
                error_message=r.error_message,
                created_at=r.created_at,
            )
            for r in recipients
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("/campaigns/{campaign_id}/preview")
async def preview_campaign(
    campaign_id: int,
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(EmailCampaign)
        .where(EmailCampaign.id == campaign_id, EmailCampaign.user_id == current_user.id)
        .options(selectinload(EmailCampaign.recipients).selectinload(EmailRecipient.job))
    )
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    recipient = next((r for r in campaign.recipients if r.contact_id == contact_id), None)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found in campaign")

    job = recipient.job
    job_title = job.title if job else "the position"
    company_name = job.company.name if job and job.company else "the company"
    recruiter_name = recipient.name or (job.recruiter.name if job and job.recruiter else "Hiring Manager")

    subject = campaign.subject_template.format(
        candidate_name="Preview User",
        company_name=company_name,
        job_title=job_title,
        recruiter_name=recruiter_name,
        job_location=job.location if job else "",
    )

    body_html = campaign.body_html_template.format(
        candidate_name="Preview User",
        company_name=company_name,
        job_title=job_title,
        recruiter_name=recruiter_name,
        job_location=job.location if job else "",
    )

    body_text = campaign.body_text_template.format(
        candidate_name="Preview User",
        company_name=company_name,
        job_title=job_title,
        recruiter_name=recruiter_name,
        job_location=job.location if job else "",
    )

    return {
        "to": recipient.email,
        "subject": subject,
        "body_html": body_html,
        "body_text": body_text,
    }


@router.post("/campaigns/{campaign_id}/send-test")
async def send_test_email(
    campaign_id: int,
    test_email: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(EmailCampaign).where(EmailCampaign.id == campaign_id, EmailCampaign.user_id == current_user.id)
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    send_test_email_task.delay(campaign_id, test_email)

    return {"message": "Test email queued"}


@router.post("/campaigns/{campaign_id}/send")
async def send_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(EmailCampaign).where(EmailCampaign.id == campaign_id, EmailCampaign.user_id == current_user.id)
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status not in ["draft", "scheduled", "paused"]:
        raise HTTPException(status_code=400, detail=f"Campaign cannot be sent from status: {campaign.status}")

    send_campaign_task.delay(campaign_id)

    return {"message": "Campaign queued for sending"}


@router.post("/campaigns/{campaign_id}/cancel")
async def cancel_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(EmailCampaign).where(EmailCampaign.id == campaign_id, EmailCampaign.user_id == current_user.id)
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status not in ["sending", "pending"]:
        raise HTTPException(status_code=400, detail=f"Campaign cannot be cancelled from status: {campaign.status}")

    campaign.status = "cancelled"
    await db.commit()

    return {"message": "Campaign cancelled"}


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(EmailCampaign).where(EmailCampaign.id == campaign_id, EmailCampaign.user_id == current_user.id)
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    await db.delete(campaign)
    await db.commit()

    return {"message": "Campaign deleted"}