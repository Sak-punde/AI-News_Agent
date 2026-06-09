"""
Application configuration — loads settings from environment variables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Settings:
    """Immutable application settings populated from env vars."""

    # --- OpenAI ---
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )

    # --- Telegram ---
    telegram_bot_token: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", "")
    )
    telegram_chat_id: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", "")
    )

    # --- Database ---
    db_path: str = field(
        default_factory=lambda: os.getenv(
            "DB_PATH",
            str(Path(__file__).resolve().parent / "data" / "news.db"),
        )
    )

    # --- Scheduler ---
    fetch_interval_minutes: int = field(
        default_factory=lambda: int(os.getenv("FETCH_INTERVAL_MINUTES", "30"))
    )

    # --- Scoring thresholds ---
    impact_threshold: int = field(
        default_factory=lambda: int(os.getenv("IMPACT_THRESHOLD", "8"))
    )

    # --- RSS feeds ---
    rss_feeds: list[str] = field(default_factory=lambda: [
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
        "https://techcrunch.com/feed/",
        "https://feeds.reuters.com/reuters/technologyNews",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
    ])


def get_settings() -> Settings:
    """Return a fresh ``Settings`` instance (reads env vars at call time)."""
    return Settings()
