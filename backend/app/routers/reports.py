import os
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.models.analytics import AnalyticsResult
from app.models.report import Report
from app.utils.auth import get_current_user
from app.services.data_parser import data_parser
from app.services.analysis_service import analysis_service
from app.services.nlp_service import nlp_service
from app.services.chart_service import chart_service
from app.services.report_service import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _human_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


@router.post("/generate/{dataset_id}")
async def generate_report(
    dataset_id: int,
    format: str = "pdf",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if format not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Gecersiz format. pdf veya docx kullanin.")

    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Veri seti bulunamadi")

    result = await db.execute(
        select(AnalyticsResult)
        .where(AnalyticsResult.dataset_id == dataset_id)
        .order_by(AnalyticsResult.created_at.desc())
        .limit(1)
    )
    analytics = result.scalar_one_or_none()

    if not analytics:
        df = data_parser.parse(dataset.file_path, dataset.file_type)
        analysis_data = analysis_service.run_full_analysis(df)
        ai_comments = nlp_service.generate_all_comments(analysis_data, dataset.original_filename)
        session_id = str(uuid.uuid4())[:8]
        charts = chart_service.generate_all_charts(df, analysis_data, session_id)
    else:
        analysis_data = {
            "basic_stats": analytics.basic_stats,
            "correlation_matrix": analytics.correlation_matrix,
            "missing_data": analytics.missing_data,
            "distribution_info": analytics.distribution_info,
            "trend_analysis": analytics.trend_analysis,
            "anomalies": analytics.anomalies,
            "category_analysis": analytics.category_analysis,
            "column_analysis": analytics.column_analysis,
            "data_quality_score": {"overall": analytics.overall_score},
        }
        ai_comments = analytics.ai_insights or nlp_service.generate_all_comments(
            analysis_data, dataset.original_filename
        )
        df = data_parser.parse(dataset.file_path, dataset.file_type)
        session_id = str(uuid.uuid4())[:8]
        charts = chart_service.generate_all_charts(df, analysis_data, session_id)

    basic_info = {
        "file_type": dataset.file_type,
        "file_size_readable": _human_size(dataset.file_size),
        "original_filename": dataset.original_filename,
    }

    try:
        if format == "pdf":
            filepath = report_service.generate_pdf(
                analysis_data, ai_comments, charts, dataset.original_filename, basic_info
            )
        else:
            filepath = report_service.generate_docx(
                analysis_data, ai_comments, charts, dataset.original_filename, basic_info
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rapor olusturma hatasi: {str(e)}")

    file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0

    report = Report(
        user_id=current_user.id,
        dataset_id=dataset_id,
        title=f"Analiz Raporu - {dataset.original_filename}",
        report_type="full",
        format=format,
        file_path=filepath,
        file_size=file_size,
        executive_summary=ai_comments.get("executive_summary", ""),
        ai_comments=ai_comments,
        recommendations=ai_comments.get("recommendations"),
        statistics=analysis_data.get("basic_stats"),
        status="completed",
    )
    db.add(report)
    await db.flush()

    return {
        "report_id": report.id,
        "title": report.title,
        "format": format,
        "file_size": file_size,
        "file_size_readable": _human_size(file_size),
        "status": "completed",
        "download_url": f"/api/reports/download/{report.id}",
    }


@router.get("/download/{report_id}")
async def download_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Rapor bulunamadi")

    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Rapor dosyasi bulunamadi")

    media_type = "application/pdf" if report.format == "pdf" else \
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        filename=f"{report.title}.{report.format}",
    )


@router.get("/")
async def list_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report)
        .where(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
    )
    reports = result.scalars().all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "dataset_id": r.dataset_id,
            "format": r.format,
            "file_size": r.file_size,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "download_url": f"/api/reports/download/{r.id}",
        }
        for r in reports
    ]
