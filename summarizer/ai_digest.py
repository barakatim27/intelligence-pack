from collections import defaultdict
from html import unescape
import re

from ranking.importance_score import KEYWORDS, rank_articles_by_category, score_article


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


def _extract_named_terms(text: str, limit: int = 5) -> list[str]:
    matches = re.findall(r"\b[A-Z][a-zA-Z0-9&.-]*(?:\s+[A-Z][a-zA-Z0-9&.-]*)*", text)
    filtered = []
    for term in matches:
        if len(term) < 3:
            continue
        if term.lower() in {"the", "and", "for", "with"}:
            continue
        filtered.append(term.strip())
    return _unique_in_order(filtered)[:limit]


def _signal_sentences(sentences: list[str], category: str, limit: int = 3) -> list[str]:
    category_keywords = KEYWORDS.get(category, [])
    scored: list[tuple[int, str]] = []

    for sentence in sentences:
        lower = sentence.lower()
        keyword_hits = sum(1 for kw in category_keywords if kw in lower)
        number_hits = 1 if re.search(r"\d", sentence) else 0
        action_hits = sum(
            1 for token in ["acquire", "launch", "charge", "ban", "raise", "cut", "approve", "kill"]
            if token in lower
        )
        score = keyword_hits * 3 + number_hits * 2 + action_hits
        scored.append((score, sentence))

    ranked = [item for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True) if item]
    unique_ranked = _unique_in_order(ranked)
    return unique_ranked[:limit] if unique_ranked else []


def _assess_confidence(cleaned_summary: str) -> tuple[str, str]:
    words = _word_count(cleaned_summary)
    if words >= 90:
        return "High", "The source excerpt includes enough detail to support a confident brief."
    if words >= 45:
        return "Medium", "The source excerpt is moderately detailed; conclusions are directional."
    return "Low", "The source excerpt is short, so several details still require confirmation."


def _category_angle(category: str) -> str:
    if category == "tech":
        return (
            "In technology, this can shift product strategy, competitive positioning, "
            "and near-term execution priorities for teams and investors."
        )
    if category == "finance":
        return (
            "In finance, this may affect market sentiment, capital allocation decisions, "
            "and forward risk assumptions for households and institutions."
        )
    if category == "geo":
        return (
            "In geopolitics, this can influence diplomatic posture, policy responses, "
            "and cross-border economic or security decisions."
        )
    return (
        "This update can shape both short-term decisions and long-term strategic planning."
    )


def _build_curated_summary(article: dict, max_words: int = 520) -> str:
    cleaned_summary = _strip_html(article.get("summary", ""))
    title = article.get("title", "Untitled Story").strip()
    source = article.get("source", "Unknown")
    category = article.get("category", "").lower()
    link = article.get("link", "").strip()

    raw_sentences = _sentence_split(cleaned_summary)
    sentences = _unique_in_order(raw_sentences)

    lead = sentences[0] if sentences else f"{title} is the central development in this bulletin."
    details = sentences[1:7] if len(sentences) > 1 else []

    if not details:
        details = [
            "The source excerpt is limited, but the headline indicates a meaningful shift worth tracking.",
            "Immediate impact is likely to depend on follow-up actions and official confirmations.",
            "Use the source link for deeper context, timelines, and direct quotations.",
        ]

    key_points = _signal_sentences([lead] + details, category, limit=3)
    if not key_points:
        key_points = _unique_in_order([_truncate_words(item, 26) for item in details[:3]])
    while len(key_points) < 3:
        key_points.append("The situation is still developing and details may change with new reporting.")

    context_para = " ".join(details)
    if _word_count(context_para) < 80:
        context_para = (
            f"{context_para} This brief intentionally avoids unsupported assumptions and focuses on "
            "information that can be inferred directly from the available excerpt."
        ).strip()

    confidence, confidence_note = _assess_confidence(cleaned_summary)
    named_terms = _extract_named_terms(f"{title}. {cleaned_summary}")
    if not named_terms:
        named_terms = ["Not enough named entities in source excerpt"]

    body = (
        "Here is a **curated 4-minute brief** of the article:\n\n"
        "---\n\n"
        f"# {title}\n\n"
        "## Executive Take\n\n"
        f"{lead}\n\n"
        "## Key Facts (From Source)\n\n"
        f"- {key_points[0]}\n"
        f"- {key_points[1]}\n"
        f"- {key_points[2]}\n\n"
        "## Context\n\n"
        f"{context_para}\n\n"
        "## Editorial View\n\n"
        f"{_category_angle(category)}\n\n"
        "## Strategic Implications\n\n"
        "1. Watch for official confirmations, filings, or policy actions that validate next steps.\n"
        f"2. Compare follow-up reporting from **{source}** with other primary outlets for signal consistency.\n"
        "3. Track measurable operational outcomes over the next few days or weeks.\n\n"
        "## Confidence and Gaps\n\n"
        f"- Confidence: **{confidence}**\n"
        f"- Evidence quality: {confidence_note}\n"
        f"- Named entities surfaced: {', '.join(named_terms)}\n\n"
        "## Full Article\n\n"
        f"- Source: **{source}**\n"
        f"- Link: {link}\n"
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

    selected_articles = sorted(selected_articles, key=score_article, reverse=True)

    digest = []
    for article in selected_articles:
        curated_summary = _build_curated_summary(article)
        digest.append(
            f"- [{article['category'].upper()}] {article['title']}\n"
            f"  Source: {article['source']}\n"
            f"  Link: {article['link']}\n"
            f"  Summary: {curated_summary}\n"
        )

    return "\n".join(digest)
