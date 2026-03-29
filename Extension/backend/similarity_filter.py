from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load model once (very important)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Simple in-memory cache
embedding_cache = {}


def get_embedding(text):
    """
    Return cached embedding if available,
    otherwise compute and store it.
    """

    if text in embedding_cache:
        return embedding_cache[text]

    emb = model.encode([text])[0]
    embedding_cache[text] = emb
    return emb


def filter_similar_articles(base_text, articles, threshold=0.45):

    if not articles:
        return []

    base_embedding = get_embedding(base_text)

    embeddings = []
    texts = []

    for a in articles:
        text = a.get("text") or a.get("headline")
        texts.append(text)
        embeddings.append(get_embedding(text))

    base_embedding = np.array(base_embedding).reshape(1, -1)
    embeddings = np.array(embeddings)

    similarities = cosine_similarity(base_embedding, embeddings)[0]

    filtered = []

    for article, score in zip(articles, similarities):
        if score >= threshold:
            filtered.append(article)

    return filtered