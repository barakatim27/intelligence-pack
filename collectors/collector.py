import feedparser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_news(source_config: dict) -> list[dict]:
    category = source_config["category"]
    feeds = source_config["feeds"]
    articles = []

    for source_name, feed_url in feeds.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                articles.append({
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", "").strip(),
                    "source": source_name,
                    "category": category,
                    "summary": entry.get("summary", "").strip(),
                    "published": entry.get("published", "")
                })
        except Exception as e:
            logger.error(f"{source_name}: {e}")

    return articles