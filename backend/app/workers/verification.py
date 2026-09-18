from celery import shared_task
from app.core.database import async_session_maker
from app.services.verification import VerificationPipeline
from app.models import Job, JobStatus
import structlog

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def verify_job_task(self, job_id: int):
    import asyncio
    return asyncio.run(_verify_job_async(job_id))


async def _verify_job_async(job_id: int):
    async with async_session_maker() as db:
        pipeline = VerificationPipeline(db)

        try:
            verification = await pipeline.run_full_verification(job_id)
            await db.commit()

            logger.info("job_verified", job_id=job_id, status=verification.status.value, confidence=verification.final_confidence)

            if verification.status in [JobStatus.NEEDS_REVIEW, JobStatus.HIGH_RISK]:
                from app.workers.email import send_verification_alert_task
                send_verification_alert_task.delay(job_id, verification.status.value)

            return {"status": "success", "job_id": job_id, "verification_status": verification.status.value, "confidence": verification.final_confidence}

        except Exception as e:
            await db.rollback()
            logger.error("verification_failed", job_id=job_id, error=str(e))
            raise