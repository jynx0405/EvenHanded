# NLP Intelligence Engine

## Setup

```bash
pip install -r requirement.txt
python -m spacy download en_core_web_sm
```

## Core Functions

### `get_relevant_articles(query, articles, top_n=5)`
Returns the top N most relevant articles for a specifically given topic by calculating embedding similarity.

### `analyze_article(text)`
Returns NLP features of an article including sentiment, emotion, speculative language, and entity mentions.

## Usage Example

```python
from nlp_engine import get_relevant_articles, analyze_article

# Step 1 - filter relevant articles
top_articles = get_relevant_articles("India economy", scraped_articles)

# Step 2 - analyze each one
for article in top_articles:
    article['analysis'] = analyze_article(article['text'])
```

## Input Format

```python
articles = [
    {
        "text": "full article text here",
        "headline": "Article Title",
        "url": "https://source.com/article"
    }
]
```

## Output Format

```json
{
    "sentiment": -0.42,
    "emotion": "anger",
    "speculative_words": ["may", "could"],
    "loaded_words": ["controversial", "shocking"],
    "entities": ["Supreme Court", "India"]
}
```