"""
n8n Entegrasyon Endpoint'leri
=============================
Bu router, n8n workflow'unun dışarıdan çağıracağı endpoint'leri sağlar.
n8n her adımı sırayla bu endpoint'ler üzerinden tetikler.

Akış:
  n8n Webhook tetiklenir → n8n HTTP Request node'ları sırayla:
  1. /api/n8n/parse-data      → Veriyi parse eder
  2. /api/n8n/run-analysis    → İstatistiksel analiz yapar
  3. /api/n8n/generate-comments → AI yorumları üretir
  4. /api/n8n/generate-charts  → Grafikleri oluşturur
  5. /api/n8n/generate-report  → PDF/DOCX rapor üretir
  6. /api/n8n/complete         → Workflow'u tamamlandı olarak işaretler
"""

import os
import time
import uuid
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_context
from app.models.dataset import Dataset
from app.models.analytics import AnalyticsResult
from app.models.report import Report
from app.models.workflow_log import WorkflowLog
from app.services.data_parser import data_parser
from app.services.analysis_service import analysis_service
from app.services.nlp_service import nlp_service
from app.services.chart_service import chart_service
from app.services.report_service import report_service
from app.services.workflow_service import workflow_service

router = APIRouter(prefix="/api/n8n", tags=["n8n-webhook"])


# ============ Pydantic Modelleri ============

class N8NTriggerRequest(BaseModel):
    dataset_id: int
    user_id: int
    format: str = "pdf"


class N8NStepRequest(BaseModel):
    dataset_id: int
    workflow_id: Optional[int] = None


class N8NReportRequest(BaseModel):
    dataset_id: int
    user_id: int
    format: str = "pdf"
    workflow_id: Optional[int] = None


# ============ n8n Webhook Endpoint'leri ============

@router.post("/trigger")
async def n8n_trigger_workflow(payload: N8NTriggerRequest):
    """
    n8n bu endpoint'i ilk tetikleyici olarak çağırır.
    Workflow başlatır ve n8n'e dataset bilgilerini döner.
    n8n'deki Webhook Node → bu endpoint'e POST atar.
    """
    async with get_db_context() as db:
        result = await db.execute(
            select(Dataset).where(Dataset.id == payload.dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset bulunamadi")

        # Workflow kaydı başlat
        wf_log = await workflow_service.start_workflow(db, payload.dataset_id)
        await db.commit()

        return {
            "status": "triggered",
            "workflow_id": wf_log.id,
            "dataset_id": dataset.id,
            "file_path": dataset.file_path,
            "file_type": dataset.file_type,
            "original_filename": dataset.original_filename,
            "user_id": payload.user_id,
            "message": "Workflow baslatildi. n8n siradaki adimlari calistirabilir."
        }


@router.post("/parse-data")
async def n8n_parse_data(payload: N8NStepRequest):
    """
    n8n'in 1. HTTP Request Node'u bu endpoint'i çağırır.
    Veri dosyasını parse eder, satır/sütun bilgisini döner.
    """
    async with get_db_context() as db:
        result = await db.execute(
            select(Dataset).where(Dataset.id == payload.dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset bulunamadi")

        # Workflow adımını güncelle
        if payload.workflow_id:
            wf_result = await db.execute(
                select(WorkflowLog).where(WorkflowLog.id == payload.workflow_id)
            )
            wf_log = wf_result.scalar_one_or_none()
            if wf_log:
                await workflow_service.update_step(db, wf_log, "data_parsing", "running")

        try:
            df = data_parser.parse(dataset.file_path, dataset.file_type)

            # Dataset bilgilerini güncelle
            dataset.row_count = len(df)
            dataset.column_count = len(df.columns)
            dataset.status = "processing"

            if payload.workflow_id and wf_log:
                await workflow_service.update_step(db, wf_log, "data_parsing", "completed",
                                                   {"rows": len(df), "cols": len(df.columns)})
            await db.commit()

            return {
                "status": "success",
                "step": "data_parsing",
                "dataset_id": payload.dataset_id,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "message": "Veri basariyla parse edildi"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Parse hatasi: {str(e)}")


@router.post("/run-analysis")
async def n8n_run_analysis(payload: N8NStepRequest):
    """
    n8n'in 2. HTTP Request Node'u bu endpoint'i çağırır.
    İstatistiksel analiz, trend tespiti, anomali algılama yapar.
    """
    async with get_db_context() as db:
        result = await db.execute(
            select(Dataset).where(Dataset.id == payload.dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset bulunamadi")

        if payload.workflow_id:
            wf_result = await db.execute(
                select(WorkflowLog).where(WorkflowLog.id == payload.workflow_id)
            )
            wf_log = wf_result.scalar_one_or_none()
            if wf_log:
                await workflow_service.update_step(db, wf_log, "statistical_analysis", "running")

        try:
            df = data_parser.parse(dataset.file_path, dataset.file_type)
            analysis = analysis_service.run_full_analysis(df)

            # Veritabanına kaydet
            analytics_result = AnalyticsResult(
                dataset_id=payload.dataset_id,
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
                status="completed",
            )
            db.add(analytics_result)

            if payload.workflow_id and wf_log:
                await workflow_service.update_step(db, wf_log, "statistical_analysis", "completed")
                await workflow_service.update_step(db, wf_log, "trend_detection", "completed")
                await workflow_service.update_step(db, wf_log, "anomaly_detection", "completed")

            await db.commit()

            return {
                "status": "success",
                "step": "statistical_analysis",
                "dataset_id": payload.dataset_id,
                "analytics_id": analytics_result.id,
                "quality_score": analysis.get("data_quality_score", {}).get("overall"),
                "num_trends": len(analysis.get("trend_analysis", {}).get("trends", [])),
                "num_anomalies": len(analysis.get("anomalies", {}).get("anomalies", [])),
                "message": "Istatistiksel analiz tamamlandi"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analiz hatasi: {str(e)}")


@router.post("/generate-comments")
async def n8n_generate_comments(payload: N8NStepRequest):
    """
    n8n'in 3. HTTP Request Node'u bu endpoint'i çağırır.
    Rule-based NLP ile Türkçe AI yorumları üretir.
    """
    async with get_db_context() as db:
        result = await db.execute(
            select(Dataset).where(Dataset.id == payload.dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset bulunamadi")

        # En son analiz sonucunu al
        result = await db.execute(
            select(AnalyticsResult)
            .where(AnalyticsResult.dataset_id == payload.dataset_id)
            .order_by(AnalyticsResult.created_at.desc())
            .limit(1)
        )
        analytics = result.scalar_one_or_none()
        if not analytics:
            raise HTTPException(status_code=404, detail="Once analiz calistirilmali")

        if payload.workflow_id:
            wf_result = await db.execute(
                select(WorkflowLog).where(WorkflowLog.id == payload.workflow_id)
            )
            wf_log = wf_result.scalar_one_or_none()
            if wf_log:
                await workflow_service.update_step(db, wf_log, "ai_commentary", "running")

        try:
            analysis_data = {
                "basic_stats": analytics.basic_stats,
                "correlation_matrix": analytics.correlation_matrix,
                "missing_data": analytics.missing_data,
                "distribution_info": analytics.distribution_info,
                "trend_analysis": analytics.trend_analysis,
                "anomalies": analytics.anomalies,
                "category_analysis": analytics.category_analysis,
            }

            ai_comments = nlp_service.generate_all_comments(analysis_data, dataset.original_filename)

            # Analiz kaydını güncelle
            analytics.ai_insights = ai_comments
            analytics.executive_summary = ai_comments.get("executive_summary", "")

            if payload.workflow_id and wf_log:
                await workflow_service.update_step(db, wf_log, "ai_commentary", "completed")

            await db.commit()

            return {
                "status": "success",
                "step": "ai_commentary",
                "dataset_id": payload.dataset_id,
                "executive_summary": ai_comments.get("executive_summary", "")[:200] + "...",
                "num_recommendations": len(ai_comments.get("recommendations", [])),
                "comment_sections": list(ai_comments.keys()),
                "message": "AI yorumlari basariyla uretildi"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Yorum uretme hatasi: {str(e)}")


@router.post("/generate-charts")
async def n8n_generate_charts(payload: N8NStepRequest):
    """
    n8n'in 4. HTTP Request Node'u bu endpoint'i çağırır.
    Matplotlib/seaborn ile grafikleri oluşturur.
    """
    async with get_db_context() as db:
        result = await db.execute(
            select(Dataset).where(Dataset.id == payload.dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset bulunamadi")

        result = await db.execute(
            select(AnalyticsResult)
            .where(AnalyticsResult.dataset_id == payload.dataset_id)
            .order_by(AnalyticsResult.created_at.desc())
            .limit(1)
        )
        analytics = result.scalar_one_or_none()
        if not analytics:
            raise HTTPException(status_code=404, detail="Once analiz calistirilmali")

        if payload.workflow_id:
            wf_result = await db.execute(
                select(WorkflowLog).where(WorkflowLog.id == payload.workflow_id)
            )
            wf_log = wf_result.scalar_one_or_none()
            if wf_log:
                await workflow_service.update_step(db, wf_log, "chart_generation", "running")

        try:
            df = data_parser.parse(dataset.file_path, dataset.file_type)
            analysis_data = {
                "basic_stats": analytics.basic_stats,
                "correlation_matrix": analytics.correlation_matrix,
                "missing_data": analytics.missing_data,
                "distribution_info": analytics.distribution_info,
                "trend_analysis": analytics.trend_analysis,
                "anomalies": analytics.anomalies,
                "category_analysis": analytics.category_analysis,
            }

            session_id = str(uuid.uuid4())[:8]
            charts = chart_service.generate_all_charts(df, analysis_data, session_id)

            if payload.workflow_id and wf_log:
                await workflow_service.update_step(db, wf_log, "chart_generation", "completed")

            await db.commit()

            return {
                "status": "success",
                "step": "chart_generation",
                "dataset_id": payload.dataset_id,
                "charts_generated": list(charts.keys()),
                "num_charts": len(charts),
                "message": "Grafikler basariyla olusturuldu"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Grafik hatasi: {str(e)}")


@router.post("/generate-report")
async def n8n_generate_report(payload: N8NReportRequest):
    """
    n8n'in 5. HTTP Request Node'u bu endpoint'i çağırır.
    PDF veya DOCX formatında rapor üretir.
    """
    async with get_db_context() as db:
        result = await db.execute(
            select(Dataset).where(Dataset.id == payload.dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset bulunamadi")

        result = await db.execute(
            select(AnalyticsResult)
            .where(AnalyticsResult.dataset_id == payload.dataset_id)
            .order_by(AnalyticsResult.created_at.desc())
            .limit(1)
        )
        analytics = result.scalar_one_or_none()
        if not analytics:
            raise HTTPException(status_code=404, detail="Once analiz calistirilmali")

        if payload.workflow_id:
            wf_result = await db.execute(
                select(WorkflowLog).where(WorkflowLog.id == payload.workflow_id)
            )
            wf_log = wf_result.scalar_one_or_none()
            if wf_log:
                await workflow_service.update_step(db, wf_log, "report_generation", "running")

        try:
            df = data_parser.parse(dataset.file_path, dataset.file_type)
            analysis_data = {
                "basic_stats": analytics.basic_stats,
                "correlation_matrix": analytics.correlation_matrix,
                "missing_data": analytics.missing_data,
                "distribution_info": analytics.distribution_info,
                "trend_analysis": analytics.trend_analysis,
                "anomalies": analytics.anomalies,
                "category_analysis": analytics.category_analysis,
                "data_quality_score": {"overall": analytics.overall_score},
            }
            ai_comments = analytics.ai_insights or {}
            session_id = str(uuid.uuid4())[:8]
            charts = chart_service.generate_all_charts(df, analysis_data, session_id)

            basic_info = {
                "file_type": dataset.file_type,
                "file_size_readable": f"{dataset.file_size / 1024:.1f} KB",
                "original_filename": dataset.original_filename,
            }

            if payload.format == "pdf":
                filepath = report_service.generate_pdf(
                    analysis_data, ai_comments, charts, dataset.original_filename, basic_info
                )
            else:
                filepath = report_service.generate_docx(
                    analysis_data, ai_comments, charts, dataset.original_filename, basic_info
                )

            file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0

            report = Report(
                user_id=payload.user_id,
                dataset_id=payload.dataset_id,
                title=f"Analiz Raporu - {dataset.original_filename}",
                report_type="full",
                format=payload.format,
                file_path=filepath,
                file_size=file_size,
                executive_summary=ai_comments.get("executive_summary", ""),
                ai_comments=ai_comments,
                recommendations=ai_comments.get("recommendations"),
                statistics=analytics.basic_stats,
                status="completed",
            )
            db.add(report)

            dataset.status = "analyzed"

            if payload.workflow_id and wf_log:
                await workflow_service.update_step(db, wf_log, "report_generation", "completed")

            await db.commit()

            return {
                "status": "success",
                "step": "report_generation",
                "dataset_id": payload.dataset_id,
                "report_id": report.id,
                "format": payload.format,
                "file_size": file_size,
                "download_url": f"/api/reports/download/{report.id}",
                "message": f"{payload.format.upper()} rapor basariyla olusturuldu"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Rapor hatasi: {str(e)}")


@router.post("/complete")
async def n8n_complete_workflow(payload: N8NStepRequest):
    """
    n8n'in son node'u bu endpoint'i çağırır.
    Workflow'u 'tamamlandı' olarak işaretler.
    """
    async with get_db_context() as db:
        if payload.workflow_id:
            wf_result = await db.execute(
                select(WorkflowLog).where(WorkflowLog.id == payload.workflow_id)
            )
            wf_log = wf_result.scalar_one_or_none()
            if wf_log:
                await workflow_service.update_step(db, wf_log, "database_save", "completed")
                await workflow_service.complete_workflow(db, wf_log)
                await db.commit()

        return {
            "status": "success",
            "step": "workflow_complete",
            "dataset_id": payload.dataset_id,
            "workflow_id": payload.workflow_id,
            "message": "Tum workflow basariyla tamamlandi!"
        }


@router.get("/health")
async def n8n_health_check():
    """
    n8n'in backend'e erişebildiğini doğrulamak için sağlık kontrolü.
    n8n'de IF node ile kontrol edilebilir.
    """
    return {
        "status": "healthy",
        "service": "AI Rapor Sistemi Backend",
        "n8n_integration": "active",
        "available_endpoints": [
            "POST /api/n8n/trigger",
            "POST /api/n8n/parse-data",
            "POST /api/n8n/run-analysis",
            "POST /api/n8n/generate-comments",
            "POST /api/n8n/generate-charts",
            "POST /api/n8n/generate-report",
            "POST /api/n8n/complete",
        ]
    }
