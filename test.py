# test.py
from analyzer import analyze_article
from similarity import find_similar_articles

# ── Test 1: analyze_article ─────────────────────────────────
print("=" * 50)
print("TEST 1: ANALYZING AN ARTICLE")
print("=" * 50)

sample_text = """
The government may introduce a controversial new policy that could 
dramatically reshape the agricultural sector. Critics warn this bold move 
might devastate small farmers across the country. Sources say the decision 
was allegedly rushed without proper consultation. The Supreme Court and 
the Election Commission are reportedly monitoring the situation closely.
"""

sample_headline = "Government eyes radical farm reforms"

result = analyze_article(sample_text, sample_headline)

print("\nHeadline:", sample_headline)
print("\nSentiment Score:", result["sentiment"])
print("  → Meaning: -1 is very negative, 0 is neutral, +1 is very positive")

print("\nDominant Emotion:", result["emotion"]["dominant"])
print("Emotion Scores:", result["emotion"]["scores"])

print("\nLoaded Words Found:", result["loaded_words"])
print("Speculative Words Found:", result["speculative_words"])
print("Named Entities:", result["entities"])


# ── Test 2: find_similar_articles ──────────────────────────
print("\n" + "=" * 50)
print("TEST 2: FINDING SIMILAR ARTICLES")
print("=" * 50)

main_article = "India's government announces new farm subsidy policy"

candidates = [
    {"text": "New agricultural subsidies announced by Indian government", "headline": "Farm subsidy news", "source": "BBC"},
    {"text": "India launches space mission to the moon", "headline": "Space news", "source": "CNN"},
    {"text": "Government gives financial aid to farmers in India", "headline": "Farmer aid", "source": "NDTV"},
]

similar = find_similar_articles(main_article, candidates)
print("\nTop similar articles found:")
for a in similar:
    print(" -", a["source"], ":", a["headline"])

   # TEST 6: FULL INTEGRATION WITH MEMBER 4
print("\n" + "="*50)
print("TEST 6: SENDING TO MEMBER 4's PIPELINE")
print("="*50)

from connector import send_to_pipeline

articles = [
    {
        "source": "BBC News",
        "headline": "Fed lifts rates in cautious move to curb inflation",
        "text": "The Federal Reserve raised interest rates by a quarter point on Wednesday in a measured response to persistent inflation. Officials signalled that further hikes may follow depending on economic data.",
        "summary": "The Federal Reserve raised rates by 0.25% to combat inflation. Officials suggest more hikes could follow."
    },
    {
        "source": "OpinionPost",
        "headline": "Fed's shocking rate hike could devastate economy",
        "text": "The Federal Reserve may have made a catastrophic mistake by dramatically hiking interest rates. Critics warn the controversial decision could trigger a recession and devastate millions of Americans.",
        "summary": "Critics claim the Fed's rate hike was reckless and could cause a recession."
    }
]

result = send_to_pipeline(
    event_description="The Federal Reserve raises interest rates by 0.25%",
    articles=articles
)

if result:
    print("\nEvent:", result["event"])
    print("Articles analyzed:", result["article_count"])
    print("\nOverall Observation:")
    print(result["framing_comparison"]["overall_observation"])
    print("\nTone Differences:")
    for t in result["framing_comparison"]["tone_differences"]:
        print(f"  {t['source']}: {t['observation']}")