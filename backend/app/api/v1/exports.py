from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import Export, Job, User
from app.schemas import ExportRequest, ExportResponse, PaginatedResponse
from app.workers.exports import generate_export_task
import structlog
import os

logger = structlog.get_logger()

router = APIRouter()


@router.post("", response_model=ExportResponse, status_code=201)
async def create_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    export = Export(
        user_id=current_user.id,
        format=request.format,
        filters=request.filters,
        status="pending",
    )
    db.add(export)
    await db.commit()
    await db.refresh(export)

    generate_export_task.delay(export.id)

    return ExportResponse(
        id=export.id,
        user_id=export.user_id,
        format=export.format,
        status=export.status,
        filters=export.filters,
        download_url=None,
        expires_at=export.expires_at,
        row_count=0,
        created_at=export.created_at,
        completed_at=None,
    )


@router.get("", response_model=PaginatedResponse)
async def list_exports(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Export).where(Export.user_id == current_user.id).order_by(Export.created_at.desc())

    from sqlalchemy import func
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    exports = result.scalars().all()

    return PaginatedResponse(
        items=[
            ExportResponse(
                id=e.id,
                user_id=e.user_id,
                format=e.format,
                status=e.status,
                filters=e.filters,
                download_url=e.download_url,
                expires_at=e.expires_at,
                row_count=e.row_count,
                created_at=e.created_at,
                completed_at=e.completed_at,
            )
            for e in exports
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{export_id}", response_model=ExportResponse)
async def get_export(
    export_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Export).where(Export.id == export_id, Export.user_id == current_user.id)
    result = await db.execute(stmt)
    export = result.scalar_one_or_none()

    if not export:
        raise HTTPException(status_code=404, detail="Export not found")

    return ExportResponse(
        id=export.id,
        user_id=export.user_id,
        format=export.format,
        status=export.status,
        filters=export.filters,
        download_url=export.download_url,
        expires_at=export.expires_at,
        row_count=export.row_count,
        created_at=export.created_at,
        completed_at=export.completed_at,
    )


@router.get("/{export_id}/download")
async def download_export(
    export_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Export).where(Export.id == export_id, Export.user_id == current_user.id)
    result = await db.execute(stmt)
    export = result.scalar_one_or_none()

    if not export:
        raise HTTPException(status_code=404, detail="Export not found")

    if export.status != "completed":
        raise HTTPException(status_code=400, detail="Export not ready")

    if export.expires_at and export.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Export download link expired")

    if not export.file_path or not os.path.exists(export.file_path):
        raise HTTPException(status_code=404, detail="Export file not found")

    from fastapi.responses import FileResponse
    return FileResponse(
        export.file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"JobShield_{datetime.utcnow().strftime('%Y-%m-%d')}.xlsx",
    )


@router.delete("/{export_id}")
async def delete_export(
    export_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Export).where(Export.id == export_id, Export.user_id == current_user.id)
    result = await db.execute(stmt)
    export = result.scalar_one_or_none()

    if not export:
        raise HTTPException(status_code=404, detail="Export not found")

    if export.file_path and os.path.exists(export.file_path):
        os.remove(export.file_path)

    await db.delete(export)
    await db.commit()

    return {"message": "Export deleted"}