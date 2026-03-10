# explainer.py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def explain_framing(articles):
    """
    articles = list of dicts, each with:
        - source: "BBC"
        - headline: "..."
        - text: "..."
    """

    # Step 1: run your analyzer on each article
    analyzed = []
    for article in articles:
        features = analyze_article(article["text"], article["headline"])
        analyzed.append({
            "source": article["source"],
            "headline": article["headline"],
            "sentiment": features["sentiment"],
            "emotion": features["emotion"]["dominant"],
            "loaded_words": features["loaded_words"],
            "speculative_words": features["speculative_words"],
            "entities": features["entities"]
        })

    # Step 2: build a prompt for the LLM
    prompt = """
You are a media literacy assistant. 
You will be given analysis data from multiple news articles covering the SAME event.
Each article has been analyzed for sentiment, emotion, loaded language, and speculative language.

Your job is to explain in simple, clear English:
1. How each outlet is framing the story differently
2. Which outlet is most neutral vs most emotional
3. What specific words are shaping the narrative
4. What a reader should watch out for

Keep it conversational, like explaining to a friend. No bullet points, just natural paragraphs.

Here is the analysis data:
"""

    for a in analyzed:
        prompt += f"""
---
Source: {a['source']}
Headline: {a['headline']}
Sentiment Score: {a['sentiment']} (scale: -1 very negative to +1 very positive)
Dominant Emotion: {a['emotion']}
Loaded/Emotional Words Used: {', '.join(a['loaded_words']) if a['loaded_words'] else 'None'}
Speculative Words Used: {', '.join(a['speculative_words']) if a['speculative_words'] else 'None'}
Key Entities Mentioned: {a['entities']}
"""

    prompt += "\nNow explain the framing differences to the user:"

    # Step 3: call Groq
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content