import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_article(url: str):
    from newspaper import Article, Config
    config = Config()
    config.browser_user_agent = HEADERS["User-Agent"]

    try:
        article = Article(url, config=config)
        article.download()
        article.parse()

        if article.text and len(article.text.strip()) > 100:
            return {
                "source": url,
                "headline": article.title,
                "summary": article.text[:300],
                "text": article.text,
                "url": url
            }
    except:
        pass

    # 🔥 Improved fallback
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        paragraphs = [p.get_text() for p in soup.find_all("p")]
        text = " ".join(paragraphs)

        if len(text) > 100:
            return {
                "source": url,
                "headline": soup.title.string if soup.title else "",
                "summary": text[:300],
                "text": text,
                "url": url
            }

    except:
        pass

    return None