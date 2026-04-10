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


def rank_articles_by_category(articles: list[dict]) -> dict[str, list[dict]]:
    ranked_by_category: dict[str, list[dict]] = {}

    for category in KEYWORDS:
        category_articles = [
            article for article in articles
            if article.get("category") == category
        ]
        ranked_by_category[category] = rank_articles(category_articles)

    return ranked_by_category
