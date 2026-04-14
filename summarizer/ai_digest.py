from collections import defaultdict
from math import ceil
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


def _strip_html(text: str) -> str:
    if not text:
        return ""
    without_tags = re.sub(r"<[^>]+>", " ", text)
    normalized_space = re.sub(r"\s+", " ", without_tags)
    return normalized_space.strip()


def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip() + "..."


def _word_count(text: str) -> int:
    return len(text.split())


def _article_blurb(article: dict, max_words: int) -> str:
    summary = _strip_html(article.get("summary", ""))
    if summary:
        return _truncate_words(summary, max_words)

    fallback = f"{article.get('title', '').strip()} ({article.get('source', 'Unknown')})"
    return _truncate_words(fallback, max_words)


def _estimate_digest_words(articles: list[dict], blurb_words: int) -> int:
    total = 0
    for article in articles:
        title_words = _word_count(article.get("title", ""))
        metadata_words = 8  # category + source + link labels
        blurb = _article_blurb(article, blurb_words)
        total += title_words + metadata_words + _word_count(blurb)
    return total


def build_digest(
    articles: list[dict],
    per_category: int = 3,
    max_per_source: int = 1,
    min_read_minutes: int = 4,
    words_per_minute: int = 200,
) -> str:
    target_words = max(min_read_minutes * words_per_minute, 1)
    ranked_by_category = rank_articles_by_category(articles)
    source_counts: dict[str, int] = defaultdict(int)
    selected_articles: list[dict] = []
    seen_titles: list[str] = []

    def add_article(
        article: dict,
        enforce_source_cap: bool,
        enforce_dedupe: bool,
        source_cap: int,
    ) -> bool:
        link = article.get("link", "")
        if link and any(existing.get("link", "") == link for existing in selected_articles):
            return False

        source = article.get("source", "Unknown")
        if enforce_source_cap and source_counts[source] >= source_cap:
            return False

        title = article.get("title", "")
        if enforce_dedupe and _is_similar_story(title, seen_titles):
            return False

        selected_articles.append(article)
        seen_titles.append(title)
        source_counts[source] += 1
        return True

    for category in ("tech", "finance", "geo"):
        picked = 0

        for article in ranked_by_category.get(category, []):
            if add_article(
                article,
                enforce_source_cap=True,
                enforce_dedupe=True,
                source_cap=max_per_source,
            ):
                picked += 1

            if picked >= per_category:
                break

    all_ranked = sorted(articles, key=score_article, reverse=True)

    # Relax constraints in stages until we hit the minimum reading target.
    expansion_stages = [
        {"enforce_source_cap": True, "enforce_dedupe": True, "source_cap": max_per_source},
        {"enforce_source_cap": False, "enforce_dedupe": True, "source_cap": max_per_source},
        {"enforce_source_cap": False, "enforce_dedupe": False, "source_cap": max_per_source},
    ]

    for stage in expansion_stages:
        if _estimate_digest_words(selected_articles, blurb_words=45) >= target_words:
            break
        for article in all_ranked:
            add_article(
                article,
                enforce_source_cap=stage["enforce_source_cap"],
                enforce_dedupe=stage["enforce_dedupe"],
                source_cap=stage["source_cap"],
            )
            if _estimate_digest_words(selected_articles, blurb_words=45) >= target_words:
                break

    selected_articles = sorted(
        selected_articles,
        key=score_article,
        reverse=True
    )

    blurb_words = 45
    while blurb_words < 120 and _estimate_digest_words(selected_articles, blurb_words) < target_words:
        blurb_words += 10

    digest = []
    estimated_words = _estimate_digest_words(selected_articles, blurb_words)
    estimated_minutes = max(1, ceil(estimated_words / max(words_per_minute, 1)))
    digest.append(
        f"Estimated read time: ~{estimated_minutes} min ({estimated_words} words)\n"
    )

    for article in selected_articles:
        blurb = _article_blurb(article, max_words=blurb_words)
        digest.append(
            f"- [{article['category'].upper()}] {article['title']}\n"
            f"  Source: {article['source']}\n"
            f"  Summary: {blurb}\n"
            f"  Link: {article['link']}\n"
        )

    return "\n".join(digest)
