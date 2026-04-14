from html import unescape
import re


def _clean_text(value: str, *, strip_html: bool = False) -> str:
    text = unescape((value or "").strip())
    if strip_html:
        text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_article(article: dict) -> dict:
    return {
        "title": _clean_text(article.get("title", "")),
        "link": (article.get("link", "") or "").strip(),
        "source": _clean_text(article.get("source", "")),
        "category": (article.get("category", "") or "").strip().lower(),
        "summary": _clean_text(article.get("summary", ""), strip_html=True),
        "published": (article.get("published", "") or "").strip(),
    }
