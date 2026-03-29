import requests

# API_KEY = "REMOVED_FOR_SECURITY"
import os
API_KEY = os.getenv("NEWS_API_KEY") # Recommended: load from env var



def fetch_news(topic: str, max_articles=10):
    url = "https://newsapi.org/v2/everything"

    params = {
        "q": topic,
        "language": "en",
        "pageSize": max_articles,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        articles = []

        for item in data.get("articles", []):
            if not item.get("url"):
                continue

            articles.append({
                "source": item["source"]["name"],
                "headline": item["title"],
                "summary": item.get("description", ""),
                "text": "",
                "url": item["url"]
            })

        print(f"Fetched {len(articles)} CLEAN NewsAPI articles")

        return articles

    except Exception as e:
        print("NewsAPI Error:", e)
        return []