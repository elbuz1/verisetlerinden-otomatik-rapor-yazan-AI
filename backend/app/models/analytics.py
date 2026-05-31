from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AnalyticsResult(Base):
    __tablename__ = "analytics_results"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    analysis_type = Column(String(100), nullable=False)
    basic_stats = Column(JSON)
    correlation_matrix = Column(JSON)
    missing_data = Column(JSON)
    distribution_info = Column(JSON)
    trend_analysis = Column(JSON)
    anomalies = Column(JSON)
    category_analysis = Column(JSON)
    column_analysis = Column(JSON)
    overall_score = Column(Float)
    ai_insights = Column(JSON)
    executive_summary = Column(Text)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, server_default=func.now())

    dataset = relationship("Dataset", back_populates="analytics")
