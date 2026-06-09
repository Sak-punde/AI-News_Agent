"""
Pydantic models shared across the application.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------- Raw article coming from RSS ---------- #

class RawArticle(BaseModel):
    """Minimal representation of a news article fetched from an RSS feed."""

    title: str
    url: str
    source: str
    published_date: Optional[str] = None


# ---------- AI-analysed article ---------- #

class AnalysedArticle(BaseModel):
    """Article enriched with AI-generated analysis."""

    title: str
    url: str
    source: str
    summary: str = ""
    bullet_points: list[str] = Field(default_factory=list)
    why_it_matters: str = ""
    impact_score: int = 0
    relevance_score: int = 0
    published_date: Optional[str] = None
    notification_sent: bool = False
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


# ---------- API response schemas ---------- #

class StatusResponse(BaseModel):
    """GET / response."""

    status: str
    version: str
    message: str


class HealthResponse(BaseModel):
    """GET /health response."""

    status: str
    database: str
    scheduler: str
    uptime_seconds: float


class ArticleResponse(BaseModel):
    """Single article in API responses."""

    id: int
    title: str
    url: str
    source: str
    summary: str
    impact_score: int
    relevance_score: int
    published_date: Optional[str]
    notification_sent: bool
    created_at: str
