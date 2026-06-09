"""
Telegram notification sender.
"""

from __future__ import annotations

import logging
import requests

from app.config import Settings
from app.models import AnalysedArticle

logger = logging.getLogger(__name__)

_TELEGRAM_SEND_URL = "https://api.telegram.org/bot{token}/sendMessage"

def _format_message(article: AnalysedArticle) -> str:
    bullets = "\n".join(f"• {bp}" for bp in article.bullet_points)

    return (
    "🚀 <b>Breaking Tech Update</b>\n\n"
    f"<b>Headline:</b>\n{article.title}\n\n"
    f"<b>Summary:</b>\n{bullets}\n\n"
    f"<b>Why It Matters:</b>\n{article.why_it_matters}\n\n"
    f"<b>Impact Score:</b> {article.impact_score}/10\n\n"
    f"<b>Source:</b>\n{article.url}"
)

def send_notification(
    article: AnalysedArticle,
    settings: Settings,
) -> bool:

    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.error("Telegram credentials not configured — skipping notification")
        return False

    url = _TELEGRAM_SEND_URL.format(token=settings.telegram_bot_token)

    print("\n" + "=" * 60)
    print("TELEGRAM DEBUG")
    print("BOT TOKEN:", settings.telegram_bot_token)
    print("CHAT ID:", settings.telegram_chat_id)
    print("URL:", url)
    print("=" * 60 + "\n")

    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": _format_message(article),
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(
            url,
            json=payload,
            timeout=15,
        )

        print("TELEGRAM STATUS:", resp.status_code)
        print("TELEGRAM RESPONSE:", resp.text)

        if resp.ok:
            logger.info(
                "Telegram notification sent for: %s",
                article.title,
            )
            return True

        logger.error(
            "Telegram API error %s: %s",
            resp.status_code,
            resp.text,
        )

    except requests.ConnectionError:
        logger.exception(
            "Connection error sending Telegram notification"
        )

    except requests.Timeout:
        logger.error(
            "Telegram request timed out for: %s",
            article.title,
        )

    except Exception:
        logger.exception(
            "Unexpected error sending Telegram notification"
        )

    return True

