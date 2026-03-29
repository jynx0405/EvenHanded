from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from dotenv import load_dotenv
load_dotenv()

import asyncio
import os

from prompt.system_prompt import SYSTEM_PROMPT
from prompt.input_builder import InputBuilder, EventInput, Article, ArticleFeatures
from prompt.output_parser import OutputParser

from backend.connector import format_for_pipeline
from backend.news_fetcher import fetch_related_articles
from backend.similarity_filter import filter_similar_articles


# -----------------------------------------------------------
# App Setup
# -----------------------------------------------------------

app = FastAPI(
    title="Even Handed API",
    description="LLM framing analysis layer for the Even Handed Chrome extension.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)

builder = InputBuilder()
parser = OutputParser()


# -----------------------------------------------------------
# Request / Response Schemas
# -----------------------------------------------------------

class ArticleSchema(BaseModel):
    source: str
    headline: str
    text: str
    summary: Optional[str] = ""
    url: Optional[str] = None


class FramingRequest(BaseModel):
    event_description: str
    articles: List[ArticleSchema] = Field(..., min_length=1, max_length=5)


class FramingResponse(BaseModel):
    event: str
    article_count: int
    framing_comparison: dict


# -----------------------------------------------------------
# Helper: Call Gemini API
# -----------------------------------------------------------

async def call_llm(user_prompt: str) -> str:
    try:
        from google.genai import types
        config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)

        response = await asyncio.to_thread(
            lambda: client.models.generate_content(
                model=MODEL,
                contents=user_prompt,
                config=config
            )
        )

        if not response.text:
            raise ValueError("Empty response received from Gemini.")

        return response.text

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini API error: {str(e)}"
        )


# -----------------------------------------------------------
# Convert Pydantic → Dataclasses
# -----------------------------------------------------------

def to_event_input(req: FramingRequest) -> EventInput:

    articles = []

    for a in req.articles:

        processed_data = format_for_pipeline(a.dict())
        feat = processed_data["features"]

        articles.append(
            Article(
                source=processed_data["source"],
                headline=processed_data["headline"],
                summary=processed_data["summary"],
                url=a.url,
                features=ArticleFeatures(
                    sentiment=feat["sentiment"],
                    emotions=feat["emotions"],
                    speculative_language=feat["speculative_language"],
                    loaded_terms=feat["loaded_terms"],
                    key_entities=feat["key_entities"],
                )
            )
        )

    return EventInput(
        event_description=req.event_description,
        articles=articles
    )


# -----------------------------------------------------------
# Routes
# -----------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "even-handed-api"}


@app.post("/analyze", response_model=FramingResponse)
async def analyze_framing(request: FramingRequest):

    try:

        # --------------------------------------------------
        # Auto-fetch related articles
        # --------------------------------------------------

        if len(request.articles) == 1:

            base_article = request.articles[0]

            query = base_article.headline

            extra_articles = fetch_related_articles(query)

            # NEW: semantic similarity filtering
            extra_articles = filter_similar_articles(
                base_article.text,
                extra_articles
            )

            for art in extra_articles:

                if len(request.articles) < 5:

                    request.articles.append(
                        ArticleSchema(**art)
                    )

        # --------------------------------------------------
        # Continue analysis pipeline
        # --------------------------------------------------

        event_input = to_event_input(request)

        user_prompt = builder.build(event_input)

        raw_response = await call_llm(user_prompt)

        result = parser.parse(raw_response)

        structured = parser.to_dict(result)

    except ValueError as e:

        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    return FramingResponse(
        event=request.event_description,
        article_count=len(request.articles),
        framing_comparison=structured,
    )