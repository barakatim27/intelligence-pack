from collectors.collector import collect_news
from collectors.tech_sources import TECH_SOURCES
from collectors.finance_sources import FINANCE_SOURCES
from collectors.geo_sources import GEO_SOURCES

from parsers.article_parser import parse_article
from ranking.importance_score import rank_articles
from summarizer.ai_digest import build_digest
from delivery.email_sender import send_email_digest


def run_daily_job():
    articles = []

    for source in [TECH_SOURCES, FINANCE_SOURCES, GEO_SOURCES]:
        raw = collect_news(source)
        parsed = [parse_article(a) for a in raw]
        articles.extend(parsed)

    ranked = rank_articles(articles)
    digest = build_digest(ranked)

    send_email_digest(digest)
    
