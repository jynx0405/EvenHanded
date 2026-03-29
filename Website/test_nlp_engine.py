# test_nlp_engine.py
from nlp_engine import get_relevant_articles, analyze_article

# ── Test 1: analyze_article ──
print("=" * 40)
print("TEST 1 — analyze_article")
print("=" * 40)

sample_text = """
The Supreme Court may issue a controversial ruling that could dramatically 
reshape India's economic policy. Officials allegedly ignored warnings, 
which may have led to the shocking collapse of talks.
"""

result = analyze_article(sample_text)
print(result)


# ── Test 2: get_relevant_articles ──
print("\n" + "=" * 40)
print("TEST 2 — get_relevant_articles")
print("=" * 40)

articles = [
    {"text": "India's GDP grew by 7% this quarter according to finance ministry.", "headline": "India GDP Growth", "url": "https://example.com/1"},
    {"text": "A new Bollywood film broke box office records this weekend.", "headline": "Bollywood Hits", "url": "https://example.com/2"},
    {"text": "RBI raised interest rates amid inflation concerns in the Indian economy.", "headline": "RBI Rate Hike", "url": "https://example.com/3"},
    {"text": "Cricket World Cup final was won by India in a dramatic match.", "headline": "Cricket Victory", "url": "https://example.com/4"},
    {"text": "Government announced new economic reforms to boost manufacturing.", "headline": "Economic Reforms", "url": "https://example.com/5"},
]

top = get_relevant_articles("India economic policy", articles, top_n=3)

print("Top relevant articles:")
for a in top:
    print(" -", a['headline'])