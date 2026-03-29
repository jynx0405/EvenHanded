# connector.py
import requests
from backend.analyzer import analyze_article

def sentiment_label(score):
    """Convert number to word that Member 4 expects"""
    if score > 0.1:
        return "positive"
    elif score < -0.1:
        return "negative"
    else:
        return "neutral"

def flatten_entities(entities_dict):
    """Convert {"ORG": ["BBC"], "GPE": ["India"]} → ["BBC", "India"]"""
    flat = []
    for label, names in entities_dict.items():
        flat.extend(names)
    return flat

def format_for_pipeline(article):
    """
    Takes your raw article dict and returns
    exactly what Member 4's /analyze needs
    
    article = {
        "source": "BBC",
        "headline": "...",
        "text": "...",
        "summary": "..."   ← 2-3 sentence summary of the article
    }
    """
    # run your analyzer
    features = analyze_article(article["text"], article["headline"])

    # reformat to match Member 4's structure
    return {
        "source": article["source"],
        "headline": article["headline"],
        "summary": article.get("summary", article["text"][:300]),  # fallback to first 300 chars
        "features": {
            "sentiment": sentiment_label(features["sentiment"]),
            "emotions": [features["emotion"]["dominant"]],
            "speculative_language": features["speculative_words"],
            "loaded_terms": features["loaded_words"],
            "key_entities": flatten_entities(features["entities"])
        }
    }

def send_to_pipeline(event_description, articles):
    formatted = [format_for_pipeline(a) for a in articles]
    request_body = {
        "event_description": event_description,
        "articles": formatted
    }

    # show what we WOULD send, even if server is offline
    print("\n✅ Data formatted successfully. Would send this to /analyze:")
    import json
    print(json.dumps(request_body, indent=2))

    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json=request_body,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print("Error:", response.status_code, response.text)
            return None
    except Exception as e:
        print("\n⚠️  Member 4's server not running yet. But YOUR data is ready ☝️")
        return None