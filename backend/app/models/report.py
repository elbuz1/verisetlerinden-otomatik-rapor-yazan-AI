from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    report_type = Column(String(50), default="full")  # full, summary, executive
    format = Column(String(20), default="pdf")  # pdf, docx
    file_path = Column(String(1000))
    file_size = Column(Integer)
    executive_summary = Column(Text)
    ai_comments = Column(JSON)
    recommendations = Column(JSON)
    statistics = Column(JSON)
    status = Column(String(50), default="pending")  # pending, generating, completed, error
    error_message = Column(String(2000))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="reports")
    dataset = relationship("Dataset", back_populates="reports")
