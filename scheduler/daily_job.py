from collectors.collector import collect_news
from collectors.tech_sources import TECH_SOURCES
from collectors.finance_sources import FINANCE_SOURCES
from collectors.geo_sources import GEO_SOURCES
import logging

from parsers.article_parser import parse_article
from ranking.importance_score import rank_articles
from summarizer.ai_digest import build_digest
from delivery.email_sender import send_email_digest

logger = logging.getLogger(__name__)


def _safe_parse_articles(raw_articles: list[dict]) -> list[dict]:
    parsed_articles: list[dict] = []
    for article in raw_articles:
        try:
            parsed_articles.append(parse_article(article))
        except Exception:
            logger.exception("Failed to parse article", extra={"article": article})
    return parsed_articles


def run_daily_job() -> bool:
    articles: list[dict] = []

    for source in [TECH_SOURCES, FINANCE_SOURCES, GEO_SOURCES]:
        try:
            raw = collect_news(source)
        except Exception:
            logger.exception("Failed to collect category", extra={"source": source})
            continue

        parsed = _safe_parse_articles(raw)
        articles.extend(parsed)

    if not articles:
        logger.warning("No articles collected. Digest email skipped.")
        return False

    ranked = rank_articles(articles)
    digest = build_digest(ranked)

    if not digest.strip():
        logger.warning("Digest was empty after ranking/summarization. Email skipped.")
        return False

    send_email_digest(digest)
    logger.info("Daily digest sent successfully", extra={"article_count": len(articles)})
    return True
