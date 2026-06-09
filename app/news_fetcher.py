"""
RSS feed fetcher — pulls articles from multiple technology news sources.
"""

from __future__ import annotations

import logging
from typing import Optional

import feedparser

from app.config import Settings
from app.models import RawArticle

logger = logging.getLogger(__name__)

# Friendly display names keyed by a substring of the feed URL.
_SOURCE_NAMES: dict[str, str] = {
    "news.google.com": "Google News",
    "techcrunch.com": "TechCrunch",
    "reuters.com": "Reuters",
    "theverge.com": "The Verge",
    "arstechnica.com": "Ars Technica",
}


def _detect_source(feed_url: str) -> str:
    """Derive a human-readable source name from the feed URL."""
    for fragment, name in _SOURCE_NAMES.items():
        if fragment in feed_url:
            return name
    return "Unknown"


def _parse_published(entry: dict) -> Optional[str]:
    """Extract a publication date string from a feed entry."""
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if value:
            return str(value)
    return None


def fetch_articles(settings: Settings) -> list[RawArticle]:
    """
    Fetch articles from every configured RSS feed.

    Network or parsing errors for individual feeds are logged and skipped so
    that one broken feed does not block the rest.
    """
    articles: list[RawArticle] = []

    for feed_url in settings.rss_feeds:
        source = _detect_source(feed_url)
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo and not feed.entries:
                logger.warning(
                    "Feed %s returned bozo error: %s", source, feed.bozo_exception
                )
                continue

            for entry in feed.entries:
                title: str = entry.get("title", "").strip()
                link: str = entry.get("link", "").strip()
                if not title or not link:
                    continue

                articles.append(
                    RawArticle(
                        title=title,
                        url=link,
                        source=source,
                        published_date=_parse_published(entry),
                    )
                )

            logger.info("Fetched %d entries from %s", len(feed.entries), source)

        except Exception:
            logger.exception("Error fetching feed %s", source)

    logger.info("Total raw articles fetched: %d", len(articles))
    return articles
