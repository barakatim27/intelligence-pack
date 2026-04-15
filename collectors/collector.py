import feedparser
import logging

logger = logging.getLogger(__name__)


def collect_news(source_config: dict) -> list[dict]:
    category = str(source_config.get("category", "")).strip().lower()
    feeds = source_config.get("feeds", {})
    articles: list[dict] = []

    if not category:
        raise ValueError("source_config.category is required")
    if not isinstance(feeds, dict):
        raise ValueError("source_config.feeds must be a dictionary")

    for source_name, feed_url in feeds.items():
        try:
            feed = feedparser.parse(feed_url)
            entries = getattr(feed, "entries", [])
            for entry in entries:
                title = str(entry.get("title", "")).strip()
                link = str(entry.get("link", "")).strip()
                if not title or not link:
                    continue

                articles.append({
                    "title": title,
                    "link": link,
                    "source": str(source_name).strip() or "Unknown",
                    "category": category,
                    "summary": str(entry.get("summary", "")).strip(),
                    "published": str(entry.get("published", "")).strip(),
                })
        except Exception:
            logger.exception("Failed to collect feed", extra={"source": source_name, "url": feed_url})

    return articles
