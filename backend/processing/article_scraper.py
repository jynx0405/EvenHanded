import requests
from bs4 import BeautifulSoup


def scrape_article(url):
    """
    Extract article text from a news webpage.
    """

    try:
        response= requests.get(url, timeout=10)
        soup= BeautifulSoup(response.text, "html.parser")
        paragraphs= soup.find_all("p")
        text= " ".join(p.get_text() for p in paragraphs)

        return text

    except Exception as e:
        print("Error scraping:", url)
        return ""
    

if __name__ == "__main__":

    test_url= "https://www.bbc.com/news/world-60525350"
    article= scrape_article(test_url)

    print(article[:500])