import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.models.analytics import AnalyticsResult
from app.utils.auth import get_current_user
from app.services.data_parser import data_parser
from app.services.analysis_service import analysis_service
from app.services.nlp_service import nlp_service
from app.services.chart_service import chart_service
from app.services.workflow_service import workflow_service
from app.services.n8n_trigger_service import n8n_trigger_service

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/{dataset_id}")
async def run_analysis(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Veri seti bulunamadi")

    start_time = time.time()
    wf_log = await workflow_service.start_workflow(db, dataset_id)

    try:
        await workflow_service.update_step(db, wf_log, "file_validation", "running")
        import os
        if not os.path.exists(dataset.file_path):
            raise HTTPException(status_code=404, detail="Dosya bulunamadi")
        await workflow_service.update_step(db, wf_log, "file_validation", "completed")

        await workflow_service.update_step(db, wf_log, "data_parsing", "running")
        df = data_parser.parse(dataset.file_path, dataset.file_type)
        await workflow_service.update_step(db, wf_log, "data_parsing", "completed",
                                           {"rows": len(df), "cols": len(df.columns)})

        await workflow_service.update_step(db, wf_log, "statistical_analysis", "running")
        analysis = analysis_service.run_full_analysis(df)
        await workflow_service.update_step(db, wf_log, "statistical_analysis", "completed")

        await workflow_service.update_step(db, wf_log, "trend_detection", "completed")
        await workflow_service.update_step(db, wf_log, "anomaly_detection", "completed")

        await workflow_service.update_step(db, wf_log, "ai_commentary", "running")
        ai_comments = nlp_service.generate_all_comments(analysis, dataset.original_filename)
        await workflow_service.update_step(db, wf_log, "ai_commentary", "completed")

        await workflow_service.update_step(db, wf_log, "chart_generation", "running")
        session_id = str(uuid.uuid4())[:8]
        charts = chart_service.generate_all_charts(df, analysis, session_id)
        await workflow_service.update_step(db, wf_log, "chart_generation", "completed")

        await workflow_service.update_step(db, wf_log, "database_save", "running")
        analytics_result = AnalyticsResult(
            dataset_id=dataset_id,
            analysis_type="full",
            basic_stats=analysis.get("basic_stats"),
            correlation_matrix=analysis.get("correlation_matrix"),
            missing_data=analysis.get("missing_data"),
            distribution_info=analysis.get("distribution_info"),
            trend_analysis=analysis.get("trend_analysis"),
            anomalies=analysis.get("anomalies"),
            category_analysis=analysis.get("category_analysis"),
            column_analysis=analysis.get("column_analysis"),
            overall_score=analysis.get("data_quality_score", {}).get("overall"),
            ai_insights=ai_comments,
            executive_summary=ai_comments.get("executive_summary", ""),
            status="completed",
        )
        db.add(analytics_result)

        dataset.status = "analyzed"
        await db.flush()
        await workflow_service.update_step(db, wf_log, "database_save", "completed")

        duration_ms = int((time.time() - start_time) * 1000)
        await workflow_service.complete_workflow(db, wf_log, duration_ms)

        charts_serializable = {}
        for k, v in charts.items():
            if isinstance(v, list):
                charts_serializable[k] = v
            elif isinstance(v, str):
                charts_serializable[k] = v
            else:
                charts_serializable[k] = str(v)

        return {
            "dataset_id": dataset_id,
            "analytics_id": analytics_result.id,
            "analysis": analysis,
            "ai_comments": ai_comments,
            "charts": charts_serializable,
            "duration_ms": duration_ms,
            "status": "completed",
        }

    except HTTPException:
        raise
    except Exception as e:
        await workflow_service.fail_workflow(db, wf_log, str(e))
        dataset.status = "error"
        dataset.error_message = str(e)
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Analiz hatasi: {str(e)}")


@router.post("/n8n/{dataset_id}")
async def run_analysis_via_n8n(
    dataset_id: int,
    format: str = "pdf",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    n8n üzerinden analiz başlatır.
    n8n çalışıyorsa → n8n webhook tetiklenir, n8n pipeline'ı yönetir.
    n8n çalışmıyorsa → dahili workflow'a fallback yapar.
    """
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Veri seti bulunamadi")

    # n8n'e trigger gönder
    n8n_result = await n8n_trigger_service.trigger_analysis_workflow(
        dataset_id=dataset_id,
        user_id=current_user.id,
        format=format
    )

    if n8n_result.get("fallback"):
        # n8n çalışmıyor, normal endpoint'e yönlendir
        return {
            "mode": "internal_workflow",
            "message": "n8n baglantisi yok, dahili workflow kullaniliyor",
            "info": "POST /api/analysis/{dataset_id} endpoint'ini kullanin"
        }

    return {
        "mode": "n8n_orchestrated",
        "status": "triggered",
        "dataset_id": dataset_id,
        "n8n_response": n8n_result,
        "message": "n8n workflow tetiklendi. Analiz n8n tarafindan yonetiliyor."
    }


@router.get("/n8n/status")
async def get_n8n_status(current_user: User = Depends(get_current_user)):
    """n8n bağlantı durumunu kontrol et."""
    status = await n8n_trigger_service.get_n8n_status()
    return status


@router.get("/{dataset_id}")
async def get_analysis(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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
        raise HTTPException(status_code=404, detail="Analiz sonucu bulunamadi. Once analiz calistirin.")

    return {
        "dataset_id": dataset_id,
        "analytics_id": analytics.id,
        "analysis": {
            "basic_stats": analytics.basic_stats,
            "correlation_matrix": analytics.correlation_matrix,
            "missing_data": analytics.missing_data,
            "distribution_info": analytics.distribution_info,
            "trend_analysis": analytics.trend_analysis,
            "anomalies": analytics.anomalies,
            "category_analysis": analytics.category_analysis,
            "column_analysis": analytics.column_analysis,
            "data_quality_score": {"overall": analytics.overall_score},
        },
        "ai_comments": analytics.ai_insights,
        "executive_summary": analytics.executive_summary,
        "status": analytics.status,
        "created_at": analytics.created_at.isoformat() if analytics.created_at else None,
    }
