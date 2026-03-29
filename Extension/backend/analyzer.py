# analyzer.py

import nltk
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline

# ── one-time downloads ──────────────────────────────────────
nltk.download('vader_lexicon', quiet=True)
nlp = spacy.load("en_core_web_sm")

# emotion model loads once (downloads ~250MB first time, be patient)
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)

# ── word lists ──────────────────────────────────────────────
LOADED_WORDS = [
    "shocking", "controversial", "radical", "disastrous", "historic",
    "dramatic", "bold", "alarming", "explosive", "unprecedented",
    "crisis", "catastrophic", "slam", "blast", "vow", "claim",
    "warn", "admit", "insist", "refuse", "demand", "condemn",
    "threaten", "expose", "reveal", "secret", "dangerous", "extreme"
]

SPECULATIVE_WORDS = [
    "may", "might", "could", "possibly", "perhaps", "expected to",
    "likely to", "appears to", "seems to", "reportedly", "allegedly",
    "sources say", "according to", "believed to", "rumored"
]

# ── individual functions ────────────────────────────────────

def get_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(text)
    return round(score['compound'], 3)
    # returns a number: -1.0 (very negative) to +1.0 (very positive)

def get_emotion(text):
    try:
        result = emotion_classifier(text[:512])
        top = max(result[0], key=lambda x: x['score'])
        return {
            "dominant": top['label'],
            "scores": {r['label']: round(r['score'], 3) for r in result[0]}
        }
    except:
        return {"dominant": "unknown", "scores": {}}

def get_loaded_words(text):
    text_lower = text.lower()
    found = [w for w in LOADED_WORDS if w in text_lower]
    return list(set(found))

def get_speculative_words(text):
    text_lower = text.lower()
    found = [w for w in SPECULATIVE_WORDS if w in text_lower]
    return list(set(found))

def get_entities(text):
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT", "LAW"]:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            if ent.text not in entities[ent.label_]:
                entities[ent.label_].append(ent.text)
    return entities

# ── MASTER FUNCTION (this is what backend calls) ────────────

def analyze_article(text, headline=""):
    full_text = headline + " " + text
    result = {}

    try: result["sentiment"] = get_sentiment(full_text)
    except: result["sentiment"] = 0

    try: result["emotion"] = get_emotion(full_text)
    except: result["emotion"] = {"dominant": "unknown"}

    try: result["loaded_words"] = get_loaded_words(full_text)
    except: result["loaded_words"] = []

    try: result["speculative_words"] = get_speculative_words(full_text)
    except: result["speculative_words"] = []

    try: result["entities"] = get_entities(full_text)
    except: result["entities"] = {}

    return result