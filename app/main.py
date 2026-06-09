"""
FastAPI application entry-point.

Starts the background scheduler and exposes REST endpoints for health
checks and article retrieval.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.config import Settings, get_settings
from app.database import Database
from app.models import ArticleResponse, HealthResponse, StatusResponse
from app.scheduler import process_news

# ------------------------------------------------------------------ #
# Logging
# ------------------------------------------------------------------ #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Application state (populated during lifespan)
# ------------------------------------------------------------------ #

_settings: Settings | None = None
_db: Database | None = None
_scheduler: BackgroundScheduler | None = None
_start_time: float = 0.0

# ------------------------------------------------------------------ #
# Lifespan
# ------------------------------------------------------------------ #


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Start the scheduler on startup and shut it down on exit."""
    global _settings, _db, _scheduler, _start_time  # noqa: PLW0603

    _start_time = time.time()
    _settings = get_settings()
    _db = Database(_settings)
    _scheduler = BackgroundScheduler()

    _scheduler.add_job(
        process_news,
        "interval",
        minutes=_settings.fetch_interval_minutes,
        args=[_settings, _db],
        id="news_pipeline",
        replace_existing=True,
        max_instances=1,
    )
    _scheduler.start()
    logger.info(
        "Scheduler started — running every %d minutes",
        _settings.fetch_interval_minutes,
    )

    # Run the pipeline once immediately at startup
    try:
        process_news(_settings, _db)
    except Exception:
        logger.exception("Initial pipeline run failed")

    yield

    _scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down")


# ------------------------------------------------------------------ #
# FastAPI app
# ------------------------------------------------------------------ #

app = FastAPI(
    title="AI Tech News Agent",
    description=(
        "An intelligent agent that monitors technology news and "
        "sends Telegram notifications for high-impact events."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ------------------------------------------------------------------ #
# Endpoints
# ------------------------------------------------------------------ #


@app.get("/", response_model=StatusResponse)
async def root() -> StatusResponse:
    """API status page."""
    return StatusResponse(
        status="online",
        version="1.0.0",
        message="AI Tech News Agent is running",
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check — reports DB and scheduler status."""
    db_ok = _db.is_healthy() if _db else False
    sched_ok = _scheduler is not None and _scheduler.running
    return HealthResponse(
        status="healthy" if (db_ok and sched_ok) else "degraded",
        database="connected" if db_ok else "disconnected",
        scheduler="running" if sched_ok else "stopped",
        uptime_seconds=round(time.time() - _start_time, 2),
    )


@app.get("/latest", response_model=list[ArticleResponse])
async def latest() -> list[ArticleResponse]:
    """Return the 10 most recently processed articles."""
    if _db is None:
        return []
    return _db.get_latest(limit=10)


@app.get("/news", response_model=list[ArticleResponse])
async def news() -> list[ArticleResponse]:
    """Return the 50 most recently stored articles."""
    if _db is None:
        return []
    return _db.get_latest(limit=50)
