from celery import shared_task
from app.core.database import async_session_maker
from app.services.source_adapters import get_adapter
from app.models import SourceConnection, SourceStatus, Job, SystemEvent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from datetime import datetime

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def ingest_from_source(self, connection_id: int, query: str = None, location: str = None, limit: int = 50):
    import asyncio
    return asyncio.run(_ingest_from_source_async(connection_id, query, location, limit))


async def _ingest_from_source_async(connection_id: int, query: str = None, location: str = None, limit: int = 50):
    async with async_session_maker() as db:
        stmt = select(SourceConnection).where(SourceConnection.id == connection_id)
        result = await db.execute(stmt)
        connection = result.scalar_one_or_none()

        if not connection:
            logger.error("source_connection_not_found", connection_id=connection_id)
            return {"status": "error", "message": "Connection not found"}

        if connection.status != SourceStatus.CONNECTED:
            logger.warning("source_not_connected", connection_id=connection_id, status=connection.status)
            return {"status": "error", "message": f"Source not connected: {connection.status}"}

        adapter = get_adapter(connection.source.name.lower(), connection.config, connection.get_credentials())
        if not await adapter.authenticate():
            connection.status = SourceStatus.ERROR
            connection.last_error = "Authentication failed"
            await db.commit()
            return {"status": "error", "message": "Authentication failed"}

        try:
            jobs = await adapter.search_jobs(query=query, location=location, limit=limit)
            collected = 0

            for norm_job in jobs:
                from app.workers.normalization import normalize_job_task
                normalize_job_task.delay(connection.user_id, connection.source_id, norm_job.__dict__)
                collected += 1

            connection.jobs_collected += collected
            connection.last_sync_at = datetime.utcnow()
            connection.last_error = None
            await db.commit()

            await _log_system_event(db, "ingestion_completed", "source_adapter", "info",
                                    f"Collected {collected} jobs from {connection.source.name}",
                                    {"connection_id": connection_id, "jobs_collected": collected})

            return {"status": "success", "jobs_collected": collected}

        except Exception as e:
            connection.last_error = str(e)
            await db.commit()
            logger.error("ingestion_failed", connection_id=connection_id, error=str(e))
            await _log_system_event(db, "ingestion_failed", "source_adapter", "error",
                                    f"Ingestion failed: {str(e)}", {"connection_id": connection_id})
            raise


@shared_task
def check_all_sources_health():
    import asyncio
    return asyncio.run(_check_all_sources_health_async())


async def _check_all_sources_health_async():
    async with async_session_maker() as db:
        stmt = select(SourceConnection).where(SourceConnection.status == SourceStatus.CONNECTED)
        result = await db.execute(stmt)
        connections = result.scalars().all()

        for conn in connections:
            adapter = get_adapter(conn.source.name.lower(), conn.config, conn.get_credentials())
            health = await adapter.health_check()

            if health.status == "connected":
                conn.status = SourceStatus.CONNECTED
                conn.last_error = None
            elif health.status == "rate_limited":
                conn.status = SourceStatus.RATE_LIMITED
            else:
                conn.status = SourceStatus.ERROR
                conn.last_error = health.error

            await db.commit()

        return {"checked": len(connections)}


async def _log_system_event(db: AsyncSession, event_type: str, source: str, level: str, message: str, details: dict):
    event = SystemEvent(
        event_type=event_type,
        source=source,
        level=level,
        message=message,
        details=details,
    )
    db.add(event)
    await db.commit()