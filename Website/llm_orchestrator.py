# llm_orchestrator.py
# LLM Orchestrator Layer for Even Handed

import json

SYSTEM_PROMPT = """
You are the Framing Analysis Engine for the "Even Handed" news comparison platform.
Your task is to analyze multiple news articles about the same event and explain how each article frames the event differently.

⚠️ Core Principles:
- This system is NOT for fake news detection, bias labeling, political judgment.
- This system IS for explaining how language differs and how framing influences perception.

🚫 STRICT RULES:
✔ Stay neutral and analytical.
✔ Focus only on language, tone, and emphasis.
✔ Use small phrases from headlines/summaries as evidence.
❌ NEVER say any article is "biased" or "unbiased".
❌ NEVER say one article is correct or incorrect.
❌ NEVER infer political ideology (e.g., "left-wing", "conservative").
❌ NEVER criticize or praise sources.

📥 INPUT FORMAT:
You will receive:
- MODE: URL_COMPARISON or TOPIC_COMPARISON
- TOPIC (if applicable)
- A list of articles with their Source, Headline, Summary, and NLP Features (Sentiment, Emotion, Speculative Words, Loaded Terms, Entities).

📤 OUTPUT FORMAT (STRICT):
If MODE is TOPIC_COMPARISON, start with:
EVENT SUMMARY
<1-2 sentences neutrally summarizing the core event across all articles>

HEADLINE FRAMING
<Comparison of how each headline presents the event>

TONE DIFFERENCES
<Analysis of emotional variation across articles>

EMPHASIS DIFFERENCES
<Analysis of what each source highlights or downplays>

LANGUAGE SIGNALS
- Emotional wording: <Examples and analysis>
- Speculative wording: <Examples and analysis>

ENTITY FOCUS
<Analysis of which actors/entities are emphasized>

INTERPRETATION IMPACT
<2-3 sentences explaining how these framing differences might influence reader perception>

✍️ Style Guidelines:
- Clear and concise.
- Neutral, non-judgmental.
- Easy to read.
- Max length: 150-200 words.
"""

def format_articles_for_prompt(mode: str, topic: str, articles: list) -> str:
    """
    Formats the articles and their NLP features into the prompt text for the LLM.
    """
    prompt = f"MODE: {mode}\n"
    if mode == "TOPIC_COMPARISON" and topic:
        prompt += f"TOPIC: {topic}\n\n"
    else:
        prompt += "\n"

    for i, article in enumerate(articles, 1):
        prompt += f"ARTICLE {i}\n"
        prompt += f"Source: {article.get('source', 'Unknown')}\n"
        prompt += f"Headline: {article.get('headline', '')}\n"
        prompt += f"Summary: {article.get('summary', '')}\n"
        
        features = article.get('features', {})
        prompt += "Features:\n"
        prompt += f"- Sentiment: {features.get('sentiment', 'N/A')}\n"
        prompt += f"- Emotion: {features.get('emotion', 'N/A')}\n"
        prompt += f"- Speculative Words: {', '.join(features.get('speculative_words', []))}\n"
        prompt += f"- Loaded Terms: {', '.join(features.get('loaded_words', []))}\n"
        prompt += f"- Entities: {', '.join(features.get('entities', []))}\n\n"

    return prompt.strip()


def generate_prompt(mode: str, topic: str, articles: list) -> list:
    """
    Returns the messages list required for an LLM call.
    """
    user_prompt = "Analyze the provided articles and explain how the same event is framed differently, focusing only on tone, emphasis, and language patterns. Remember: Your goal is to make framing visible, not to judge the content.\n\n"
    user_prompt += format_articles_for_prompt(mode, topic, articles)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.strip()},
        {"role": "user", "content": user_prompt}
    ]
    return messages

# LLM calling function using Google Gemini
def call_llm(messages: list, api_key: str = None) -> str:
    """
    Calls the Google Gemini LLM to generate the framing analysis.
    Requires package: pip install google-generativeai
    """
    try:
        import google.generativeai as genai
        import os
        
        # Configure API key (use arg or env var)
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            return "ERROR: Gemini API key missing. Pass api_key or set GEMINI_API_KEY environment variable."
            
        genai.configure(api_key=key)
            
        # Extract system prompt and user prompt from the messages format
        system_prompt = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_prompt = next((m["content"] for m in messages if m["role"] == "user"), "")
        
        # Use gemini-1.5-flash for fast and high-quality processing (or change to gemini-1.5-pro if needed)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt
        )
        
        response = model.generate_content(user_prompt)
        return response.text
        
    except ImportError:
        return "ERROR: google.generativeai package not installed. Run: pip install google-generativeai"
    except Exception as e:
        return f"ERROR: {str(e)}"
