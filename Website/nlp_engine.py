# nlp_engine.py
# NLP Intelligence Engine for Even Handed

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load models once at the top (not inside functions)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load('en_core_web_sm')
vader = SentimentIntensityAnalyzer()

# Word lists
SPECULATIVE_WORDS = [
    "may", "might", "could", "possibly", "perhaps", "expected",
    "likely", "allegedly", "reportedly", "suggest", "appears"
]

LOADED_WORDS = [
    "controversial", "shocking", "dramatic", "historic", "explosive",
    "catastrophic", "devastating", "radical", "alarming", "terrifying",
    "unprecedented", "massive", "brutal", "outrage", "chaos"
]


# ─────────────────────────────────────────────
# FUNCTION 1 — Find most relevant articles
# ─────────────────────────────────────────────
def get_relevant_articles(query: str, articles: list, top_n: int = 5) -> list:
    """
    query    : topic string e.g. "India economic policy"
    articles : list of dicts, each must have a 'text' key
    top_n    : how many articles to return (default 5)
    """
    query_embedding = embedding_model.encode([query])

    article_texts = [a['text'][:500] for a in articles]
    article_embeddings = embedding_model.encode(article_texts)

    scores = cosine_similarity(query_embedding, article_embeddings)[0]

    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    top_articles = [articles[i] for i in ranked_indices[:top_n]]

    return top_articles


# ─────────────────────────────────────────────
# FUNCTION 2 — Analyze a single article
# ─────────────────────────────────────────────
def analyze_article(text: str) -> dict:
    """
    text : raw article text
    returns dict with all NLP features
    """
    text_lower = text.lower()
    words = text_lower.split()

    # 1. Sentiment score (-1 to +1)
    scores = vader.polarity_scores(text)
    sentiment_score = round(scores['compound'], 3)

    # 2. Emotion based on sentiment score
    if sentiment_score <= -0.5:
        emotion = "fear"
    elif sentiment_score <= -0.1:
        emotion = "anger"
    elif sentiment_score >= 0.3:
        emotion = "optimism"
    else:
        emotion = "neutral"

    # 3. Speculative words
    found_speculative = [w for w in SPECULATIVE_WORDS if w in words]

    # 4. Loaded words
    found_loaded = [w for w in LOADED_WORDS if w in text_lower]

    # 5. Named entities (people, orgs, places)
    doc = nlp(text[:1000])
    entities = list(set([
        ent.text for ent in doc.ents
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC"]
    ]))

    return {
        "sentiment": sentiment_score,
        "emotion": emotion,
        "speculative_words": found_speculative,
        "loaded_words": found_loaded,
        "entities": entities
    }