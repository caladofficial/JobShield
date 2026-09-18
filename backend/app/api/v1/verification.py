from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import Job, JobVerification, VerificationSignal, RiskEvent, JobStatus, RiskLevel, User
from app.schemas import JobVerificationResponse, RiskEventResponse, VerificationProgress
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/job/{job_id}", response_model=JobVerificationResponse)
async def get_job_verification(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(JobVerification)
        .join(Job, Job.id == JobVerification.job_id)
        .where(JobVerification.job_id == job_id, Job.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    verification = result.scalar_one_or_none()

    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")

    return verification


@router.get("/job/{job_id}/signals")
async def get_job_verification_signals(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    stmt = select(VerificationSignal).where(VerificationSignal.job_id == job_id).order_by(VerificationSignal.stage, VerificationSignal.created_at)
    result = await db.execute(stmt)
    signals = result.scalars().all()

    grouped = {}
    for signal in signals:
        if signal.stage not in grouped:
            grouped[signal.stage] = []
        grouped[signal.stage].append({
            "name": signal.signal_name,
            "value": signal.signal_value,
            "weight": signal.weight,
            "details": signal.details,
            "created_at": signal.created_at,
        })

    return grouped


@router.get("/job/{job_id}/risk-events", response_model=List[RiskEventResponse])
async def get_job_risk_events(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    stmt = select(RiskEvent).where(RiskEvent.job_id == job_id).order_by(RiskEvent.created_at.desc())
    result = await db.execute(stmt)
    events = result.scalars().all()

    return events


@router.post("/job/{job_id}")
async def trigger_verification(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    from app.workers.verification import verify_job_task
    verify_job_task.delay(job_id)

    return {"message": "Verification started", "job_id": job_id}