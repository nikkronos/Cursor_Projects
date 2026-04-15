from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class AnalyzeRequest(BaseModel):
    url: HttpUrl
    comments_limit: int = Field(default=200, ge=10, le=1000)
    include_comment_replies: bool = False
    export_google: bool = False


class BatchAnalyzeRequest(BaseModel):
    urls: list[HttpUrl] = Field(min_length=1, max_length=30)
    comments_limit: int = Field(default=200, ge=10, le=1000)
    include_comment_replies: bool = False
    export_google: bool = False
    max_retries: int = Field(default=2, ge=1, le=5)


class ScoreBlock(BaseModel):
    score: int
    rationale: str


class AnalysisInsights(BaseModel):
    hook: ScoreBlock
    retention: ScoreBlock
    transfer: ScoreBlock
    confidence_score: int
    cta_detected: bool
    cta_type: str
    engagement: dict[str, Any] = Field(default_factory=dict)
    audience_reaction: dict[str, Any]
    actionable_recommendations: list[str]
    exports: dict[str, Any] = Field(default_factory=dict)


class AnalysisResponse(BaseModel):
    id: int
    url: str
    shortcode: str
    media_type: str
    author_username: str
    likes_count: int
    comments_count: int
    view_count: int
    comments_analyzed: int
    engagement_rate: str
    exported_google: bool
    insights: AnalysisInsights
    created_at: datetime


class AnalysisListItem(BaseModel):
    id: int
    url: str
    shortcode: str
    media_type: str
    author_username: str
    hook_score: int
    created_at: datetime


class BatchItemResponse(BaseModel):
    id: int
    url: str
    status: str
    attempts: int
    analysis_id: int | None
    error_text: str


class BatchJobResponse(BaseModel):
    id: int
    status: str
    total_urls: int
    processed_urls: int
    success_urls: int
    failed_urls: int
    comments_limit: int
    include_comment_replies: bool
    export_google: bool
    max_retries: int
    last_error: str
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    items: list[BatchItemResponse] = []


class BatchJobListItem(BaseModel):
    id: int
    status: str
    total_urls: int
    processed_urls: int
    success_urls: int
    failed_urls: int
    created_at: datetime
    finished_at: datetime | None
