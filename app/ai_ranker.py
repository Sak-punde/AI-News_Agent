"""
AI analysis module — uses the OpenAI API to summarise and score articles.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import openai

from app.config import Settings
from app.models import AnalysedArticle, RawArticle

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Prompt template
# ------------------------------------------------------------------ #

_SYSTEM_PROMPT = """\
You are an expert technology news analyst. Given the headline and source of a \
news article, produce a JSON object with EXACTLY these keys:

{
  "summary": "<concise 2-3 sentence summary>",
  "bullet_points": ["<point 1>", "<point 2>", "<point 3>"],
  "why_it_matters": "<1-2 sentence explanation of broader significance>",
  "impact_score": <integer 1-10>,
  "relevance_score": <integer 1-10>
}

Scoring guidelines
------------------
Impact Score (1-10):
  10 — Industry-redefining event (major acquisition, breakthrough AI model release)
   8 — Significant industry event (large funding round, major product launch)
   5 — Moderate news (incremental update, minor partnership)
   1 — Trivial or unrelated

High-priority categories (bias toward higher scores):
  • AI breakthroughs, OpenAI / Google AI / Microsoft AI / Anthropic announcements
  • AWS / Azure / Google Cloud announcements
  • Major cybersecurity incidents
  • Startup funding > $50 M, acquisitions
  • Major product launches
  • Government tech regulations
  • Semiconductor industry news

Relevance Score (1-10):
  10 — Core technology / AI news
   5 — Tangentially related
   1 — Not technology-related

Return ONLY valid JSON — no markdown fences, no extra text.
"""


def _build_user_prompt(article: RawArticle) -> str:
    return f"Headline: {article.title}\nSource: {article.source}"


# ------------------------------------------------------------------ #
# Public API
# ------------------------------------------------------------------ #


def analyse_article(
    article: RawArticle,
    settings: Settings,
) -> Optional[AnalysedArticle]:

    if not settings.openai_api_key:
        logger.error("API key is not set — skipping analysis")
        return None

    print("API KEY FOUND:", bool(settings.openai_api_key))
    print("MODEL:", settings.openai_model)

    # Groq client
    client = openai.OpenAI(
        api_key=settings.openai_api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(article)},
            ],
            temperature=0.3,
            max_tokens=512,
        )

        content = response.choices[0].message.content

        if not content:
            logger.warning("Empty response for: %s", article.title)
            return None

        data = json.loads(content)

        return AnalysedArticle(
            title=article.title,
            url=article.url,
            source=article.source,
            summary=data.get("summary", ""),
            bullet_points=data.get("bullet_points", []),
            why_it_matters=data.get("why_it_matters", ""),
            impact_score=int(data.get("impact_score", 0)),
            relevance_score=int(data.get("relevance_score", 0)),
            published_date=article.published_date,
        )

    except json.JSONDecodeError:
        logger.exception("Failed to parse AI response for: %s", article.title)

    except openai.APITimeoutError:
        logger.error("AI request timed out for: %s", article.title)

    except openai.APIError:
        logger.exception("AI API error for: %s", article.title)

    except Exception:
        logger.exception("Unexpected error analysing: %s", article.title)

    return None