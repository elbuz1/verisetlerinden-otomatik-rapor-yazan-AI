import time
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.workflow_log import WorkflowLog
from app.models.dataset import Dataset


class WorkflowService:
    """
    n8n-benzeri dahili workflow motoru.
    Her analiz adimini izler, loglar ve workflow durumunu yonetir.
    """

    WORKFLOW_STEPS = {
        "data_analysis": [
            {"name": "file_validation", "label": "Dosya Dogrulama"},
            {"name": "data_parsing", "label": "Veri Ayristirma"},
            {"name": "data_profiling", "label": "Veri Profilleme"},
            {"name": "statistical_analysis", "label": "Istatistiksel Analiz"},
            {"name": "trend_detection", "label": "Trend Tespiti"},
            {"name": "anomaly_detection", "label": "Anomali Algilama"},
            {"name": "ai_commentary", "label": "AI Yorum Uretimi"},
            {"name": "chart_generation", "label": "Grafik Olusturma"},
            {"name": "report_generation", "label": "Rapor Olusturma"},
            {"name": "database_save", "label": "Veritabani Kayit"},
        ],
    }

    async def start_workflow(self, db: AsyncSession, dataset_id: int,
                             workflow_name: str = "data_analysis") -> WorkflowLog:
        log = WorkflowLog(
            dataset_id=dataset_id,
            workflow_name=workflow_name,
            workflow_type="analysis",
            status="started",
            step_current="file_validation",
            step_details={"steps": self.WORKFLOW_STEPS.get(workflow_name, []),
                          "completed": [], "current_index": 0},
            extra_metadata={"started_at": datetime.now().isoformat()},
        )
        db.add(log)
        await db.flush()
        return log

    async def update_step(self, db: AsyncSession, log: WorkflowLog,
                          step_name: str, status: str = "running",
                          details: dict = None) -> WorkflowLog:
        log.step_current = step_name
        log.status = status

        step_details = log.step_details or {}
        completed = step_details.get("completed", [])
        if status == "completed" and step_name not in completed:
            completed.append(step_name)
        step_details["completed"] = completed
        step_details["current_step"] = step_name
        step_details["current_status"] = status
        if details:
            step_details[step_name] = details
        log.step_details = step_details

        await db.flush()
        return log

    async def complete_workflow(self, db: AsyncSession, log: WorkflowLog,
                                duration_ms: int = None) -> WorkflowLog:
        log.status = "completed"
        log.completed_at = datetime.now()
        if duration_ms:
            log.duration_ms = duration_ms
        await db.flush()
        return log

    async def fail_workflow(self, db: AsyncSession, log: WorkflowLog,
                            error: str) -> WorkflowLog:
        log.status = "failed"
        log.error_message = error
        log.completed_at = datetime.now()
        await db.flush()
        return log

    async def get_workflow_status(self, db: AsyncSession, dataset_id: int) -> Optional[dict]:
        result = await db.execute(
            select(WorkflowLog)
            .where(WorkflowLog.dataset_id == dataset_id)
            .order_by(WorkflowLog.started_at.desc())
            .limit(1)
        )
        log = result.scalar_one_or_none()
        if not log:
            return None

        steps = self.WORKFLOW_STEPS.get(log.workflow_name, [])
        completed = (log.step_details or {}).get("completed", [])

        return {
            "workflow_id": log.id,
            "workflow_name": log.workflow_name,
            "status": log.status,
            "current_step": log.step_current,
            "progress": len(completed) / len(steps) * 100 if steps else 0,
            "steps": [
                {
                    "name": s["name"],
                    "label": s["label"],
                    "status": (
                        "completed" if s["name"] in completed
                        else "running" if s["name"] == log.step_current and log.status == "running"
                        else "pending"
                    ),
                }
                for s in steps
            ],
            "started_at": log.started_at.isoformat() if log.started_at else None,
            "completed_at": log.completed_at.isoformat() if log.completed_at else None,
            "duration_ms": log.duration_ms,
            "error": log.error_message,
        }

    async def get_recent_workflows(self, db: AsyncSession, limit: int = 20) -> list[dict]:
        result = await db.execute(
            select(WorkflowLog)
            .order_by(WorkflowLog.started_at.desc())
            .limit(limit)
        )
        logs = result.scalars().all()
        return [
            {
                "id": log.id,
                "dataset_id": log.dataset_id,
                "workflow_name": log.workflow_name,
                "status": log.status,
                "current_step": log.step_current,
                "started_at": log.started_at.isoformat() if log.started_at else None,
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "duration_ms": log.duration_ms,
            }
            for log in logs
        ]


workflow_service = WorkflowService()
