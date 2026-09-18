from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.demo_data import generate_demo_jobs, create_demo_sources
from app.models import Source, SourceStatus, User
from app.services.normalization import NormalizationEngine
import structlog

logger = structlog.get_logger()


async def seed_demo_data(db: AsyncSession, user: User) -> None:
    """Seed demo sources and jobs for a user."""
    
    # Create demo sources
    sources = create_demo_sources()
    for source in sources:
        stmt = select(Source).where(Source.name == source.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if not existing:
            db.add(source)
    
    await db.flush()
    
    # Get source IDs
    stmt = select(Source).where(Source.name.in_(["demo", "manual"]))
    result = await db.execute(stmt)
    demo_sources = result.scalars().all()
    source_map = {s.name: s.id for s in demo_sources}
    
    # Generate and store demo jobs
    demo_jobs = generate_demo_jobs(50)
    
    for norm_job in demo_jobs:
        source_id = source_map.get(norm_job.source, source_map.get("demo"))
        
        engine = NormalizationEngine(db)
        await engine.normalize_and_store(norm_job, user.id, source_id)
    
    await db.commit()
    logger.info("demo_data_seeded", user_id=user.id, jobs_count=len(demo_jobs))


async def ensure_demo_sources(db: AsyncSession) -> None:
    """Ensure demo sources exist in the database."""
    sources = create_demo_sources()
    
    for source in sources:
        stmt = select(Source).where(Source.name == source.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if not existing:
            db.add(source)
    
    await db.commit()