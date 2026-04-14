from collections import defaultdict
from html import unescape
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
    return unescape(normalized_space).strip()


def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip() + "..."


def _word_count(text: str) -> int:
    return len(text.split())


def _sentence_split(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def _unique_in_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return ordered


def _category_angle(category: str) -> str:
    if category == "tech":
        return (
            "In the technology landscape, this development points to changing product "
            "strategy, platform competition, and how quickly teams are moving from "
            "experiments to commercial deployment."
        )
    if category == "finance":
        return (
            "For markets and business decisions, this can influence investor sentiment, "
            "risk assumptions, and near-term planning across companies and households."
        )
    if category == "geo":
        return (
            "From a geopolitical perspective, the update may affect diplomatic positioning, "
            "policy choices, and the broader regional or global response."
        )
    return (
        "This update is relevant because it can shape both short-term decisions and "
        "long-term strategic direction for stakeholders."
    )


def _build_four_minute_summary(article: dict, max_words: int = 650) -> str:
    cleaned_summary = _strip_html(article.get("summary", ""))
    title = article.get("title", "Untitled Story").strip()
    source = article.get("source", "Unknown")
    category = article.get("category", "").lower()

    raw_sentences = _sentence_split(cleaned_summary)
    sentences = _unique_in_order(raw_sentences)

    lead = sentences[0] if sentences else f"{title} is the key development highlighted in this bulletin."
    details = sentences[1:6] if len(sentences) > 1 else []

    if not details:
        details = [
            "Based on the available source excerpt, this story appears significant and worth monitoring.",
            "The headline suggests an active shift that may influence decisions in the near term.",
            "Additional reporting from the source link can provide deeper factual and historical context.",
        ]

    key_points = _unique_in_order([_truncate_words(item, 24) for item in details[:3]])
    while len(key_points) < 3:
        key_points.append("The situation is still developing and further details may follow.")

    context_para = " ".join(details)
    if _word_count(context_para) < 80:
        context_para = (
            f"{context_para} The source excerpt is short, so this brief focuses on the clearest verified signals "
            "from the headline and summary while avoiding unsupported assumptions."
        ).strip()

    significance_para = (
        f"{_category_angle(category)} In practical terms, readers should focus on who is directly affected, "
        "what changed compared to the previous state, and what the source confirms versus what remains uncertain."
    )

    watch_items = _unique_in_order(
        [
            "Official statements, filings, or policy actions that confirm next steps.",
            f"Follow-up reporting from {source} and other primary outlets for additional evidence.",
            "Operational impacts over the next few days or weeks, especially any measurable outcomes.",
        ]
    )

    body = (
        "Here\'s a **4-minute read summary** of the article:\n\n"
        "---\n\n"
        f"# {title}\n\n"
        f"{lead}\n\n"
        "## Key Developments\n\n"
        f"* {key_points[0]}\n"
        f"* {key_points[1]}\n"
        f"* {key_points[2]}\n\n"
        "## What Happened\n\n"
        f"{context_para}\n\n"
        "## Why This Matters\n\n"
        f"{significance_para}\n\n"
        "## What To Watch Next\n\n"
        f"* {watch_items[0]}\n"
        f"* {watch_items[1]}\n"
        f"* {watch_items[2]}\n\n"
        "In short, this bulletin is most useful as a fast strategic snapshot; use the source link for full article depth."
    )

    return _truncate_words(body, max_words)


def build_digest(
    articles: list[dict],
    per_category: int = 3,
    max_per_source: int = 1,
) -> str:
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

    selected_articles = sorted(
        selected_articles,
        key=score_article,
        reverse=True
    )

    digest = []
    for article in selected_articles:
        long_summary = _build_four_minute_summary(article)
        digest.append(
            f"- [{article['category'].upper()}] {article['title']}\n"
            f"  Source: {article['source']}\n"
            f"  Link: {article['link']}\n"
            f"  Summary: {long_summary}\n"
        )

    return "\n".join(digest)

