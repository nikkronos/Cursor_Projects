from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    shortcode: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    media_type: Mapped[str] = mapped_column(String(64), nullable=False)
    author_username: Mapped[str] = mapped_column(String(128), nullable=False)
    caption: Mapped[str] = mapped_column(Text, default="")
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    hook_score: Mapped[int] = mapped_column(Integer, default=0)
    retention_score: Mapped[int] = mapped_column(Integer, default=0)
    transfer_score: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[str] = mapped_column(String(64), default="0.00")
    insights_json: Mapped[str] = mapped_column(Text, default="{}")
    exported_google: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    total_urls: Mapped[int] = mapped_column(Integer, default=0)
    processed_urls: Mapped[int] = mapped_column(Integer, default=0)
    success_urls: Mapped[int] = mapped_column(Integer, default=0)
    failed_urls: Mapped[int] = mapped_column(Integer, default=0)
    comments_limit: Mapped[int] = mapped_column(Integer, default=200)
    include_comment_replies: Mapped[bool] = mapped_column(Boolean, default=False)
    export_google: Mapped[bool] = mapped_column(Boolean, default=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=2)
    last_error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class BatchJobItem(Base):
    __tablename__ = "batch_job_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_job_id: Mapped[int] = mapped_column(ForeignKey("batch_jobs.id"), index=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    analysis_id: Mapped[int | None] = mapped_column(ForeignKey("analysis_records.id"), nullable=True)
    error_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
