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
MODEL          = "gemini-2.5-flash"        # free tier, fast and capable

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
client = genai.Client(api_key=GEMINI_API_KEY)

builder = InputBuilder()
parser  = OutputParser()


# -----------------------------------------------------------
# Request / Response Schemas
# -----------------------------------------------------------

class ArticleFeaturesSchema(BaseModel):
    sentiment:            str
    emotions:             List[str] = Field(default_factory=list)
    speculative_language: List[str] = Field(default_factory=list)
    loaded_terms:         List[str] = Field(default_factory=list)
    key_entities:         List[str] = Field(default_factory=list)


class ArticleSchema(BaseModel):
    source:   str
    headline: str
    summary:  str
    features: ArticleFeaturesSchema
    url:      Optional[str] = None


class FramingRequest(BaseModel):
    event_description: str
    articles:          List[ArticleSchema] = Field(..., min_length=1, max_length=5)


class FramingResponse(BaseModel):
    event:              str
    article_count:      int
    framing_comparison: dict


# -----------------------------------------------------------
# Helper: Call Gemini API
# -----------------------------------------------------------

async def call_llm(user_prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY environment variable is not set."
        )

    try:
        from google.genai import types
        config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)

        # generate_content is synchronous — run in a thread
        # so it does not block the FastAPI async event loop
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
# Helper: Convert Pydantic → Dataclasses
# -----------------------------------------------------------

def to_event_input(req: FramingRequest) -> EventInput:
    articles = [
        Article(
            source=a.source,
            headline=a.headline,
            summary=a.summary,
            url=a.url,
            features=ArticleFeatures(
                sentiment=a.features.sentiment,
                emotions=a.features.emotions,
                speculative_language=a.features.speculative_language,
                loaded_terms=a.features.loaded_terms,
                key_entities=a.features.key_entities,
            )
        )
        for a in req.articles
    ]
    return EventInput(event_description=req.event_description, articles=articles)


# -----------------------------------------------------------
# Routes
# -----------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "even-handed-api"}


@app.post("/analyze", response_model=FramingResponse)
async def analyze_framing(request: FramingRequest):
    try:
        event_input  = to_event_input(request)
        user_prompt  = builder.build(event_input)
        raw_response = await call_llm(user_prompt)

        # Parse raw LLM text → structured dict
        result     = parser.parse(raw_response)
        structured = parser.to_dict(result)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return FramingResponse(
        event=request.event_description,
        article_count=len(request.articles),
        framing_comparison=structured,
    )