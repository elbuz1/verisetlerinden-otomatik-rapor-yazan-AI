from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)  # csv, xlsx, json
    file_size = Column(BigInteger, nullable=False)
    file_path = Column(String(1000), nullable=False)
    row_count = Column(Integer)
    column_count = Column(Integer)
    columns_info = Column(JSON)  # {name, dtype, null_count, unique_count}
    status = Column(String(50), default="uploaded")  # uploaded, processing, analyzed, error
    error_message = Column(String(2000))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="datasets")
    analytics = relationship("AnalyticsResult", back_populates="dataset", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="dataset", cascade="all, delete-orphan")
