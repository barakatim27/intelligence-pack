from datetime import datetime

KEYWORDS = {
    "tech": ["ai", "openai", "microsoft", "google", "startup"],
    "finance": ["fed", "inflation", "stocks", "earnings", "market"],
    "geo": ["war", "election", "trade", "sanctions", "oil"]
}


def score_article(article: dict) -> int:
    score = 0
    title = article["title"].lower()
    category = article["category"]

    for keyword in KEYWORDS.get(category, []):
        if keyword in title:
            score += 10

    if article.get("published"):
        score += 5

    return score


def rank_articles(articles: list[dict]) -> list[dict]:
    return sorted(
        articles,
        key=score_article,
        reverse=True
    )