import feedparser

RSS_FEEDS= {
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "Guardian": "https://www.theguardian.com/world/rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"
}


def fetch_news(limit_per_source=5):
    """
    Fetch latest news articles from multiple RSS feeds.

    Returns:
        List of dictionaries containing
        {source, headline, url}
    """

    articles= []

    for source, url in RSS_FEEDS.items():
        feed= feedparser.parse(url)

        for entry in feed.entries[:limit_per_source]:
            articles.append({
                "source": source,
                "headline": entry.title,
                "url": entry.link
            })

    return articles


if __name__ == "__main__":

    news= fetch_news()

    for article in news:
        print(article)