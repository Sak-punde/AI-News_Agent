"""
Background scheduler — orchestrates the fetch → analyse → notify pipeline.
"""

from __future__ import annotations

import logging

from app.ai_ranker import analyse_article
from app.config import Settings
from app.database import Database
from app.news_fetcher import fetch_articles
from app.notifier import send_notification

logger = logging.getLogger(__name__)


def process_news(settings: Settings, db: Database) -> dict[str, int]:
    """
    Run one full cycle of the news pipeline:

    1. Fetch articles from RSS feeds.
    2. Deduplicate against the database.
    3. Analyse new articles with OpenAI.
    4. Store results in SQLite.
    5. Send Telegram notifications for high-impact articles.

    Returns a summary dict with counts.
    """
    stats = {"fetched": 0, "new": 0, "analysed": 0, "notified": 0}

    # 1. Fetch
    raw_articles = fetch_articles(settings)
    stats["fetched"] = len(raw_articles)

    for raw in raw_articles:
        # 2. Skip duplicates
        if db.url_exists(raw.url):
            continue
        stats["new"] += 1

        # 3. AI analysis
        analysed = analyse_article(raw, settings)
        if analysed is None:
            continue
        stats["analysed"] += 1

        # 4. Persist
        db.insert_article(analysed)

        # 5. Notify if high-impact
        
    print("\n" + "=" * 60)
print("TITLE:", analysed.title)
print("IMPACT SCORE:", analysed.impact_score)
print("THRESHOLD:", settings.impact_threshold)
print("=" * 60)

# TEST MODE - SEND EVERY ARTICLE
success = send_notification(analysed, settings)

if success:
    print("✅ NOTIFICATION SENT")

    db.mark_notified(analysed.url)
    analysed.notification_sent = True
    stats["notified"] += 1

else:
    print("❌ NOTIFICATION FAILED")