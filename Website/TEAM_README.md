# Even Handed - Integration Guide

## Overview
This document explains how the current codebase works and how the different layers of the **Even Handed** project connect, specifically focusing on the NLP Intelligence Engine and the LLM Orchestration Layer.

## Folder Structure
- **`nlp_engine.py`**: The NLP intelligence module. Uses `sentence-transformers`, `VADER`, and `spaCy` to calculate sentiment, emotion, speculative words, loaded terms, and entities.
- **`llm_orchestrator.py`**: The LLM generation module. Formats the NLP outputs into a strict prompt for Google Gemini to generate the neutral, analytical framing comparison.
- **`requirement.txt`**: Python dependencies required for the project.
- **`test_nlp_engine.py`** & **`test_llm_orchestrator.py`**: Local testing scripts to verify that both layers work independently.

## Data Flow (How it all connects)

1. **Scraping / Ingestion**:
   - Fetches 5-6 articles based on a search topic or compares two specific URLs.
   - Extracts the `text`, `headline`, `summary`, and `source` for each article.

2. **NLP Processing (nlp_engine)**:
   - The backend passes the list of articles to `nlp_engine.get_relevant_articles()` to filter the top most relevant articles for a topic.
   - Then, the backend loops through the selected articles and passes the raw text to `nlp_engine.analyze_article(text)`.
   - `analyze_article` returns a dictionary of structural features: `sentiment`, `emotion`, `speculative_words`, `loaded_words`, and `entities`.

3. **LLM Generation (llm_orchestrator)**:
   - The backend attaches the features dictionary to each article object.
   - The backend calls `llm_orchestrator.generate_prompt()` (or `llm_orchestrator.call_llm()`) passing in the mode, topic, and the structured list of articles.
   - Gemini processes the strict system prompt alongside the structured NLP features to output a neutral comparison of how the articles frame the event, strictly adhering to the output format without judging the sources.

## How to Integrate (Backend System)

```python
from nlp_engine import get_relevant_articles, analyze_article
from llm_orchestrator import call_llm, generate_prompt

# 1. You scraped these articles from the internet:
scraped_articles = [
    {
        "source": "NewsA", 
        "headline": "Economic Policy Announced", 
        "summary": "Government signs new bill.", 
        "text": "Full article text...", 
        "url": "https://..."
    },
    # ... more articles
]

# 2. Filter relevant articles (Topic Mode)
top_articles = get_relevant_articles("India economic policy", scraped_articles, top_n=5)

# 3. Analyze each article with NLP (nlp_engine)
for article in top_articles:
    features = analyze_article(article['text'])
    article['features'] = features  # Attach the NLP output array to the article!

# 4. Generate the final framing comparison using LLM (llm_orchestrator)
# Make sure GEMINI_API_KEY is set in your environment
messages = generate_prompt(mode="TOPIC_COMPARISON", topic="India economic policy", articles=top_articles)
final_analysis_markdown = call_llm(messages)

# Send this markdown back to the UI/Client!
print(final_analysis_markdown)
```

## Setup & Running the Project Locally
Ensure you have all dependencies installed before running the integration:

1. **Install requirements:**
   ```bash
   pip install -r requirement.txt
   pip install google-generativeai
   python -m spacy download en_core_web_sm
   ```

2. **Set API Key:**
   ```bash
   export GEMINI_API_KEY="your_google_gemini_key_here"
   ```

3. **Run the individual tests:**
   ```bash
   python3 test_nlp_engine.py
   python3 test_llm_orchestrator.py
   ```

## Backend & System Integration
### Overview
The core backend system is responsible for orchestrating the entire Even Handed pipeline, connecting data ingestion, NLP processing, and LLM-based analysis into a unified workflow.

### Key Responsibilities & Contributions
1. **API Development (FastAPI)**
Developed REST APIs:
- `POST /compare-urls` → Compare two news articles
- `POST /compare-topic` → Analyze multiple articles for a given topic
- Integrated Swagger UI for testing and debugging

2. **Pipeline Orchestration**
Designed and implemented the complete data flow:
`User Input → Scraper → NLP (nlp_engine) → LLM (llm_orchestrator) → Structured Output`
- Managed sequential processing across modules
- Ensured consistent data format across components

3. **Article Scraping System**
Implemented robust article extraction using:
- `newspaper3k`
- `BeautifulSoup` (fallback)
- Handled invalid URLs, empty content, and blocked pages.

4. **Topic-Based News Retrieval**
- Integrated NewsAPI for reliable article fetching
- Filtered and processed articles down to top 5–6 relevant ones.

5. **NLP + LLM Integration**
Connected:
- `analyze_article()` → feature extraction
- `get_relevant_articles()` → ranking
- `generate_prompt()` + `call_llm()` → final reasoning
- Ensured structured input format for LLM processing

6. **Data Structuring**
Maintained consistent JSON format:
```json
{
  "articles": [...],
  "comparison": "...",
  "summary": "..."
}
```

7. **Performance Optimization**
- Limited processing to top 5–6 articles
- Filtered low-quality articles
- Ensured response time within acceptable limits (~5–10 seconds)

8. **Error Handling**
Handled edge cases such as:
- Invalid or inaccessible URLs
- No articles found
- Scraping failures
- Insufficient valid data