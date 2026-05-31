from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from app.database import Base


class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    workflow_name = Column(String(200), nullable=False)
    workflow_type = Column(String(100))  # upload, analysis, report, notification
    status = Column(String(50), default="started")  # started, running, completed, failed
    step_current = Column(String(200))
    step_details = Column(JSON)
    error_message = Column(Text)
    duration_ms = Column(Integer)
    extra_metadata = Column(JSON)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
