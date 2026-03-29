from fastapi import APIRouter
from models.schemas import URLRequest
from services.scraper import scrape_article
from services.pipeline import run_url_comparison

router = APIRouter()

@router.post("/compare-urls")
def compare_urls(req: URLRequest):
    a1 = scrape_article(req.url1)
    a2 = scrape_article(req.url2)
    print("Article 1:", a1)
    print("Article 2:", a2)
    
    if not a1 or not a2:
        return {"error": "Failed to scrape URLs"}

    return run_url_comparison([a1, a2])