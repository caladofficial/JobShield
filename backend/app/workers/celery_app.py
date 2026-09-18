from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "jobshield",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.ingestion",
        "app.workers.normalization",
        "app.workers.verification",
        "app.workers.risk",
        "app.workers.contacts",
        "app.workers.exports",
        "app.workers.email",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_routes={
        "app.workers.ingestion.*": {"queue": "ingestion"},
        "app.workers.normalization.*": {"queue": "normalization"},
        "app.workers.verification.*": {"queue": "verification"},
        "app.workers.risk.*": {"queue": "risk"},
        "app.workers.contacts.*": {"queue": "contacts"},
        "app.workers.exports.*": {"queue": "exports"},
        "app.workers.email.*": {"queue": "email"},
    },
    beat_schedule={
        "cleanup-expired-exports": {
            "task": "app.workers.exports.cleanup_expired_exports",
            "schedule": 3600.0,
        },
        "check-source-health": {
            "task": "app.workers.ingestion.check_all_sources_health",
            "schedule": 300.0,
        },
    },
)