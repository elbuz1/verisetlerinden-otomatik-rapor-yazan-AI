from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.models.report import Report
from app.models.analytics import AnalyticsResult
from app.models.workflow_log import WorkflowLog
from app.utils.auth import get_current_user
from app.services.workflow_service import workflow_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds_count = await db.execute(
        select(func.count(Dataset.id)).where(Dataset.user_id == current_user.id)
    )
    total_datasets = ds_count.scalar() or 0

    rp_count = await db.execute(
        select(func.count(Report.id)).where(Report.user_id == current_user.id)
    )
    total_reports = rp_count.scalar() or 0

    total_rows_result = await db.execute(
        select(func.sum(Dataset.row_count)).where(Dataset.user_id == current_user.id)
    )
    total_rows = total_rows_result.scalar() or 0

    total_size_result = await db.execute(
        select(func.sum(Dataset.file_size)).where(Dataset.user_id == current_user.id)
    )
    total_size = total_size_result.scalar() or 0

    analyzed_count = await db.execute(
        select(func.count(Dataset.id)).where(
            Dataset.user_id == current_user.id, Dataset.status == "analyzed"
        )
    )
    total_analyzed = analyzed_count.scalar() or 0

    avg_quality_result = await db.execute(
        select(func.avg(AnalyticsResult.overall_score))
        .join(Dataset, AnalyticsResult.dataset_id == Dataset.id)
        .where(Dataset.user_id == current_user.id)
    )
    avg_quality = avg_quality_result.scalar() or 0

    return {
        "total_datasets": total_datasets,
        "total_reports": total_reports,
        "total_rows_analyzed": total_rows,
        "total_data_size_mb": round(total_size / 1024 / 1024, 2),
        "total_analyzed": total_analyzed,
        "average_quality_score": round(float(avg_quality), 1),
    }


@router.get("/recent-datasets")
async def get_recent_datasets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dataset)
        .where(Dataset.user_id == current_user.id)
        .order_by(Dataset.created_at.desc())
        .limit(10)
    )
    datasets = result.scalars().all()
    return [
        {
            "id": ds.id,
            "filename": ds.original_filename,
            "file_type": ds.file_type,
            "row_count": ds.row_count,
            "column_count": ds.column_count,
            "status": ds.status,
            "created_at": ds.created_at.isoformat() if ds.created_at else None,
        }
        for ds in datasets
    ]


@router.get("/recent-reports")
async def get_recent_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report)
        .where(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
        .limit(10)
    )
    reports = result.scalars().all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "format": r.format,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "download_url": f"/api/reports/download/{r.id}",
        }
        for r in reports
    ]


@router.get("/workflows")
async def get_workflows(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await workflow_service.get_recent_workflows(db)


@router.get("/workflow-status/{dataset_id}")
async def get_workflow_status(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status = await workflow_service.get_workflow_status(db, dataset_id)
    if not status:
        return {"status": "not_found", "message": "Bu veri seti icin workflow bulunamadi"}
    return status
