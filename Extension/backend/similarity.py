# similarity.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return model.encode(text)

def find_similar_articles(query_text, candidate_articles):
    """
    query_text: string (the main article)
    candidate_articles: list of dicts like:
        [{"text": "...", "headline": "...", "source": "BBC"}, ...]
    returns: top 5 most similar articles
    """
    query_emb = get_embedding(query_text)
    results = []

    for article in candidate_articles:
        emb = get_embedding(article['text'])
        score = cosine_similarity([query_emb], [emb])[0][0]
        results.append((float(score), article))

    results.sort(reverse=True)
    return [article for _, article in results[:5]]