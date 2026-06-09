"""
SQLite persistence layer.

Provides helpers to initialise the schema, insert articles, and query them.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Optional

from app.config import Settings
from app.models import AnalysedArticle, ArticleResponse

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Schema
# ------------------------------------------------------------------ #

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS news_articles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT    NOT NULL,
    url             TEXT    NOT NULL UNIQUE,
    source          TEXT    NOT NULL,
    summary         TEXT    DEFAULT '',
    impact_score    INTEGER DEFAULT 0,
    relevance_score INTEGER DEFAULT 0,
    published_date  TEXT,
    notification_sent INTEGER DEFAULT 0,
    created_at      TEXT    NOT NULL
);
"""


# ------------------------------------------------------------------ #
# Database helper class
# ------------------------------------------------------------------ #

class Database:
    """Thin wrapper around an SQLite connection."""

    def __init__(self, settings: Settings) -> None:
        db_path = Path(settings.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._path = str(db_path)
        self._init_schema()

    # -- private --------------------------------------------------- #

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        try:
            with self._connect() as conn:
                conn.execute(_CREATE_TABLE)
                conn.commit()
            logger.info("Database initialised at %s", self._path)
        except sqlite3.Error:
            logger.exception("Failed to initialise database")
            raise

    # -- public API ------------------------------------------------ #

    def url_exists(self, url: str) -> bool:
        """Return *True* if the URL has already been stored."""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT 1 FROM news_articles WHERE url = ?", (url,)
                ).fetchone()
            return row is not None
        except sqlite3.Error:
            logger.exception("Error checking URL existence")
            return False

    def insert_article(self, article: AnalysedArticle) -> Optional[int]:
        """Insert an analysed article. Returns the row id or *None* on failure."""
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO news_articles
                        (title, url, source, summary, impact_score,
                         relevance_score, published_date, notification_sent,
                         created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        article.title,
                        article.url,
                        article.source,
                        article.summary,
                        article.impact_score,
                        article.relevance_score,
                        article.published_date,
                        int(article.notification_sent),
                        article.created_at,
                    ),
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.debug("Duplicate URL skipped: %s", article.url)
            return None
        except sqlite3.Error:
            logger.exception("Error inserting article")
            return None

    def mark_notified(self, url: str) -> None:
        """Flag an article as having been sent via Telegram."""
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE news_articles SET notification_sent = 1 WHERE url = ?",
                    (url,),
                )
                conn.commit()
        except sqlite3.Error:
            logger.exception("Error marking article as notified")

    def get_latest(self, limit: int = 20) -> list[ArticleResponse]:
        """Return the most recent articles ordered by creation time."""
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT id, title, url, source, summary, impact_score,
                           relevance_score, published_date, notification_sent,
                           created_at
                    FROM news_articles
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            return [
                ArticleResponse(
                    id=r["id"],
                    title=r["title"],
                    url=r["url"],
                    source=r["source"],
                    summary=r["summary"],
                    impact_score=r["impact_score"],
                    relevance_score=r["relevance_score"],
                    published_date=r["published_date"],
                    notification_sent=bool(r["notification_sent"]),
                    created_at=r["created_at"],
                )
                for r in rows
            ]
        except sqlite3.Error:
            logger.exception("Error fetching latest articles")
            return []

    def is_healthy(self) -> bool:
        """Quick connectivity check."""
        try:
            with self._connect() as conn:
                conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False
