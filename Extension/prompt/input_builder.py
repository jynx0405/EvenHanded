from dataclasses import dataclass, field
from typing import List, Optional


# -----------------------------------------------------------
# Data Models
# -----------------------------------------------------------

@dataclass
class ArticleFeatures:
    """NLP features extracted by the backend for a single article."""
    sentiment: str                          # e.g. "positive", "negative", "neutral", or a score like "0.72"
    emotions: List[str]                     # e.g. ["anger", "fear"]
    speculative_language: List[str]         # e.g. ["could trigger", "may lead to"]
    loaded_terms: List[str]                 # e.g. ["radical", "surged", "crisis"]
    key_entities: List[str]                 # e.g. ["Federal Reserve", "Jerome Powell"]


@dataclass
class Article:
    """A single news article with metadata and NLP features."""
    source: str                             # e.g. "BBC News"
    headline: str
    summary: str
    features: ArticleFeatures
    url: Optional[str] = None


@dataclass
class EventInput:
    """Full input payload for one framing comparison request."""
    event_description: str                  # Brief description of the real-world event
    articles: List[Article] = field(default_factory=list)


# -----------------------------------------------------------
# Input Builder
# -----------------------------------------------------------

class InputBuilder:
    """
    Converts an EventInput object into a formatted prompt string
    ready to be sent to the LLM as the user message.
    """

    def build(self, event_input: EventInput) -> str:
        """
        Main method. Takes an EventInput and returns a formatted prompt string.
        """
        self._validate(event_input)

        lines = []
        lines.append(f"EVENT: {event_input.event_description.strip()}")
        lines.append("")

        for i, article in enumerate(event_input.articles, start=1):
            lines.append(self._format_article(i, article))

        lines.append("")
        lines.append(
            "Analyze the articles above and explain how the same event is framed differently, "
            "focusing on tone, emphasis, and language. Follow the output format exactly."
        )

        return "\n".join(lines)

    def _format_article(self, index: int, article: Article) -> str:
        """Formats a single article block."""
        f = article.features

        emotions_str       = ", ".join(f.emotions) if f.emotions else "none detected"
        speculative_str    = ", ".join(f.speculative_language) if f.speculative_language else "none detected"
        loaded_str         = ", ".join(f.loaded_terms) if f.loaded_terms else "none detected"
        entities_str       = ", ".join(f.key_entities) if f.key_entities else "none detected"

        lines = [
            f"ARTICLE {index}",
            f"Source: {article.source}",
            f"Headline: {article.headline}",
            f"Summary: {article.summary.strip()}",
            "Features:",
            f"  Sentiment: {f.sentiment}",
            f"  Emotion: {emotions_str}",
            f"  Speculative language: {speculative_str}",
            f"  Loaded terms: {loaded_str}",
            f"  Key entities: {entities_str}",
            "",
        ]
        return "\n".join(lines)

    def _validate(self, event_input: EventInput):
        """Basic validation before building the prompt."""
        if not event_input.event_description:
            raise ValueError("event_description cannot be empty.")
        if not event_input.articles:
            raise ValueError("At least one article is required.")
        if len(event_input.articles) > 5:
            raise ValueError("Maximum of 5 articles allowed per request.")
        for i, article in enumerate(event_input.articles, start=1):
            if not article.source:
                raise ValueError(f"Article {i} is missing a source name.")
            if not article.headline:
                raise ValueError(f"Article {i} is missing a headline.")
            if not article.summary:
                raise ValueError(f"Article {i} is missing a summary.")


# -----------------------------------------------------------
# Quick test
# -----------------------------------------------------------

if __name__ == "__main__":
    sample = EventInput(
        event_description="The Federal Reserve raises interest rates by 0.25%",
        articles=[
            Article(
                source="BBC News",
                headline="Fed lifts rates in cautious move to curb inflation",
                summary="The Federal Reserve raised interest rates by a quarter point, signalling a measured approach to tackling persistent inflation.",
                features=ArticleFeatures(
                    sentiment="neutral",
                    emotions=["concern"],
                    speculative_language=["could slow growth", "may stabilise prices"],
                    loaded_terms=["cautious", "persistent"],
                    key_entities=["Federal Reserve", "Jerome Powell"]
                )
            ),
            Article(
                source="Fox Business",
                headline="Fed hikes rates again — economy braces for impact",
                summary="The Fed announced another rate hike, raising fears among investors that the aggressive tightening cycle will tip the economy into recession.",
                features=ArticleFeatures(
                    sentiment="negative",
                    emotions=["fear", "anxiety"],
                    speculative_language=["will tip", "raising fears"],
                    loaded_terms=["aggressive", "braces", "recession"],
                    key_entities=["Federal Reserve", "investors", "recession"]
                )
            ),
        ]
    )

    builder = InputBuilder()
    prompt = builder.build(sample)
    print(prompt)