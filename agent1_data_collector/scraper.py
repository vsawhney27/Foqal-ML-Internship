import requests
from config import SCRAPINGDOG_API_KEY, SCRAPINGDOG_BASE_URL

def scrape_page(url: str) -> str:
    """Uses ScrapingDog API to scrape the given URL and return raw HTML."""
    params = {
        "api_key": SCRAPINGDOG_API_KEY,
        "url": url,
        "dynamic": "true",
        "premium": "true"  # needed for JS-heavy sites like LinkedIn
    }
    try:
        response = requests.get(SCRAPINGDOG_BASE_URL, params=params)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Scraping failed: {e}")
        return None
