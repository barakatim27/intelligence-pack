def parse_article(article: dict) -> dict:
    return {
        "title": article["title"],
        "link": article["link"],
        "source": article["source"],
        "category": article["category"],
        "summary": article.get("summary", "").replace("\n", " ").strip(),
        "published": article.get("published", "")
    }