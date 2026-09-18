from celery import shared_task
from app.core.database import async_session_maker
from app.services.normalization import NormalizationEngine
from app.services.source_adapters import NormalizedJob
from app.models import Job, JobStatus
from sqlalchemy import select
import structlog

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def normalize_job_task(self, user_id: int, source_id: int, job_data: dict):
    import asyncio
    return asyncio.run(_normalize_job_async(user_id, source_id, job_data))


async def _normalize_job_async(user_id: int, source_id: int, job_data: dict):
    async with async_session_maker() as db:
        norm_job = NormalizedJob(**job_data)
        engine = NormalizationEngine(db)

        try:
            job = await engine.normalize_and_store(norm_job, user_id, source_id)
            await db.commit()

            from app.workers.verification import verify_job_task
            verify_job_task.delay(job.id)

            logger.info("job_normalized", job_id=job.id, title=job.title)
            return {"status": "success", "job_id": job.id}

        except Exception as e:
            await db.rollback()
            logger.error("normalization_failed", error=str(e), job_data=job_data)
            raise