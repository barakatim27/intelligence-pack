from collections import defaultdict
import re

from ranking.importance_score import rank_articles_by_category, score_article


STOP_WORDS = {
    "a", "an", "and", "are", "at", "be", "for", "from", "in", "into", "of",
    "on", "or", "over", "that", "the", "their", "this", "to", "with"
}


def _normalize_title(title: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", title.lower())
    tokens = [token for token in cleaned.split() if token not in STOP_WORDS]
    return " ".join(tokens)


def _is_similar_story(title: str, seen_titles: list[str]) -> bool:
    normalized = set(_normalize_title(title).split())
    if not normalized:
        return False

    for seen_title in seen_titles:
        seen_tokens = set(_normalize_title(seen_title).split())
        if not seen_tokens:
            continue

        overlap = len(normalized & seen_tokens)
        similarity = overlap / max(min(len(normalized), len(seen_tokens)), 1)
        if similarity >= 0.75:
            return True

    return False


def build_digest(
    articles: list[dict],
    per_category: int = 3,
    max_per_source: int = 1
) -> str:
    ranked_by_category = rank_articles_by_category(articles)
    source_counts: dict[str, int] = defaultdict(int)
    selected_articles: list[dict] = []
    seen_titles: list[str] = []

    for category in ("tech", "finance", "geo"):
        picked = 0

        for article in ranked_by_category.get(category, []):
            source = article.get("source", "Unknown")
            if source_counts[source] >= max_per_source:
                continue

            if _is_similar_story(article.get("title", ""), seen_titles):
                continue

            selected_articles.append(article)
            seen_titles.append(article.get("title", ""))
            source_counts[source] += 1
            picked += 1

            if picked >= per_category:
                break

    selected_articles = sorted(
        selected_articles,
        key=score_article,
        reverse=True
    )

    digest = []
    for article in selected_articles:
        digest.append(
            f"- [{article['category'].upper()}] {article['title']}\n"
            f"  Source: {article['source']}\n"
            f"  Link: {article['link']}\n"
        )

    return "\n".join(digest)
