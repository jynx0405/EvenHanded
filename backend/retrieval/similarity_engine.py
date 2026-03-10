from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load embedding model once
model= SentenceTransformer("all-MiniLM-L6-v2")


def find_similar_articles(user_text, articles, top_k=5):
    """
    Find the most similar news articles to the user article.

    Args:
        user_text (str): text of the user article
        articles (list): list of articles from RSS
        top_k (int): number of similar articles to return

    Returns:
        list of top_k similar articles
    """

    corpus= [user_text] + [article["headline"] for article in articles]
    embeddings= model.encode(corpus)
    user_embedding= embeddings[0]
    article_embeddings= embeddings[1:]
    similarities= cosine_similarity(
        [user_embedding],
        article_embeddings
    )[0]

    ranked= sorted(
        zip(articles, similarities),
        key=lambda x: x[1],
        reverse=True
    )

    return [article for article, score in ranked[:top_k]]


if __name__ == "__main__":

    sample_article= "Government announces major economic reform policy."

    sample_news = [
        {"headline": "Cabinet introduces new economic reform"},
        {"headline": "Football championship results announced"},
        {"headline": "New financial policy unveiled by government"},
        {"headline": "Stock market reaches new high"},
    ]

    results= find_similar_articles(sample_article, sample_news)

    for r in results:
        print(r)