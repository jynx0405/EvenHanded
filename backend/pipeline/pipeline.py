from backend.retrieval.rss_fetcher import fetch_news
from backend.retrieval.similarity_engine import find_similar_articles
from backend.processing.article_scraper import scrape_article


def run_pipeline(user_text):
    """
    Full backend pipeline.
    """

    news_articles= fetch_news()
    similar_articles= find_similar_articles(user_text, news_articles)

    results = []

    for article in similar_articles:
        text= scrape_article(article["url"])

        results.append({
            "source": article["source"],
            "headline": article["headline"],
            "text": text[:2000] 
        })

    return results


if __name__ == "__main__":

    user_article= user_article= """
        The government announced a major economic reform policy
        aimed at stabilizing inflation and boosting investment.
    """
    output= run_pipeline(user_article)

    for o in output:
        print(o["headline"])