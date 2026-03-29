from newsapi import NewsApiClient
from dotenv import load_dotenv
import os
from pathlib import Path

# Force load the backend .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not NEWS_API_KEY:
    raise RuntimeError("NEWS_API_KEY not found in .env file")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)


def fetch_related_articles(query, max_articles=3):

    response = newsapi.get_everything(
        q=query,
        language="en",
        sort_by="relevancy",
        page_size=max_articles
    )

    articles = []

    for article in response["articles"]:
        articles.append({
            "source": article["source"]["name"],
            "headline": article["title"],
            "text": article["description"] or "",
            "summary": article["description"] or "",
            "url": article["url"]
        })

    return articles