from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import Source, SourceConnection, SourceStatus, User
from app.schemas import (
    SourceResponse, SourceConnectionCreate, SourceConnectionUpdate, SourceConnectionResponse
)
from app.services.source_adapters import get_adapter
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("", response_model=List[SourceResponse])
async def list_sources(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Source).where(Source.is_active == True).order_by(Source.display_name)
    result = await db.execute(stmt)
    sources = result.scalars().all()
    return sources


@router.get("/connections", response_model=List[SourceConnectionResponse])
async def list_source_connections(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(SourceConnection)
        .where(SourceConnection.user_id == current_user.id)
        .options(selectinload(SourceConnection.source))
        .order_by(SourceConnection.created_at.desc())
    )
    result = await db.execute(stmt)
    connections = result.scalars().all()
    return connections


@router.post("/connections", response_model=SourceConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_source_connection(
    connection_in: SourceConnectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Source).where(Source.id == connection_in.source_id, Source.is_active == True)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    stmt = select(SourceConnection).where(
        SourceConnection.user_id == current_user.id,
        SourceConnection.source_id == source.id
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Connection already exists")

    adapter = get_adapter(source.name.lower(), connection_in.config, connection_in.credentials)
    authenticated = await adapter.authenticate()

    connection = SourceConnection(
        user_id=current_user.id,
        source_id=source.id,
        config=connection_in.config,
        status=SourceStatus.CONNECTED if authenticated else SourceStatus.ERROR,
    )

    if connection_in.credentials:
        connection.set_credentials(connection_in.credentials)

    db.add(connection)
    await db.commit()
    await db.refresh(connection)

    if authenticated:
        from app.workers.ingestion import ingest_from_source
        ingest_from_source.delay(connection.id)

    logger.info("source_connected", user_id=current_user.id, source_id=source.id, connection_id=connection.id)
    return connection


@router.get("/connections/{connection_id}", response_model=SourceConnectionResponse)
async def get_source_connection(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(SourceConnection)
        .where(SourceConnection.id == connection_id, SourceConnection.user_id == current_user.id)
        .options(selectinload(SourceConnection.source))
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    return connection


@router.patch("/connections/{connection_id}", response_model=SourceConnectionResponse)
async def update_source_connection(
    connection_id: int,
    connection_update: SourceConnectionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SourceConnection).where(
        SourceConnection.id == connection_id, SourceConnection.user_id == current_user.id
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if connection_update.config is not None:
        connection.config = connection_update.config
    if connection_update.credentials is not None:
        connection.set_credentials(connection_update.credentials)

    adapter = get_adapter(connection.source.name.lower(), connection.config, connection.get_credentials())
    authenticated = await adapter.authenticate()
    connection.status = SourceStatus.CONNECTED if authenticated else SourceStatus.ERROR

    await db.commit()
    await db.refresh(connection)

    return connection


@router.delete("/connections/{connection_id}")
async def delete_source_connection(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SourceConnection).where(
        SourceConnection.id == connection_id, SourceConnection.user_id == current_user.id
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    await db.delete(connection)
    await db.commit()

    return {"message": "Connection deleted"}


@router.post("/connections/{connection_id}/sync")
async def sync_source(
    connection_id: int,
    query: str = None,
    location: str = None,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SourceConnection).where(
        SourceConnection.id == connection_id, SourceConnection.user_id == current_user.id
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    from app.workers.ingestion import ingest_from_source
    ingest_from_source.delay(connection_id, query, location, limit)

    return {"message": "Sync started", "connection_id": connection_id}


@router.post("/connections/{connection_id}/health")
async def check_source_health(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(SourceConnection)
        .where(SourceConnection.id == connection_id, SourceConnection.user_id == current_user.id)
        .options(selectinload(SourceConnection.source))
    )
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    adapter = get_adapter(connection.source.name.lower(), connection.config, connection.get_credentials())
    health = await adapter.health_check()

    if health.status == "connected":
        connection.status = SourceStatus.CONNECTED
        connection.last_error = None
    elif health.status == "rate_limited":
        connection.status = SourceStatus.RATE_LIMITED
    else:
        connection.status = SourceStatus.ERROR
        connection.last_error = health.error

    await db.commit()

    return {
        "status": health.status,
        "last_check": health.last_check.isoformat() if health.last_check else None,
        "error": health.error,
        "rate_limit_remaining": health.rate_limit_remaining,
        "rate_limit_reset_at": health.rate_limit_reset_at.isoformat() if health.rate_limit_reset_at else None,
    }