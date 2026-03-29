from fastapi import APIRouter
from models.schemas import TopicRequest
from services.pipeline import run_topic_comparison
from services.news_fetcher import fetch_news
from services.scraper import scrape_article

router = APIRouter()

@router.post("/compare-topic")
def compare_topic(req: TopicRequest):
    # Step 1: Fetch news
    articles = fetch_news(req.topic)
    print("Fetched articles:", len(articles))

    if not articles:
        return {"error": "No articles found"}

    # Step 2: Scrape
    scraped_articles = []

    for a in articles:
        print("\nTrying URL:", a["url"])
        scraped = scrape_article(a["url"])

        # ✅ FILTER BAD / IRRELEVANT ARTICLES
        if scraped and len(scraped.get("text", "")) > 500:
            print("[SUCCESS]:", len(scraped["text"]))
            scraped_articles.append(scraped)
        else:
            print("[FAILED] or TOO SHORT")

    print("\nTotal scraped (valid):", len(scraped_articles))

    if len(scraped_articles) < 2:
        return {"error": "Not enough valid articles"}

    # ✅ LIMIT TO TOP 5–6 ARTICLES (PERFORMANCE)
    scraped_articles = scraped_articles[:6]

    return run_topic_comparison(req.topic, scraped_articles)