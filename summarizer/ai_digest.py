def build_digest(articles: list[dict], top_n: int = 5) -> str:
    digest = []

    for article in articles[:top_n]:
        digest.append(
            f"- [{article['category'].upper()}] {article['title']}\n"
            f"  Source: {article['source']}\n"
            f"  Link: {article['link']}\n"
        )

    return "\n".join(digest)