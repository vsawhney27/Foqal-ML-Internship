import requests
import time
from config import SCRAPINGDOG_API_KEY, SCRAPINGDOG_BASE_URL

def scrape_page(url: str) -> str:
    """
    Scrapes a page with multiple fallback methods:
    1. ScrapingDog API (if key available)
    2. Direct requests with user agent
    3. Requests with session and headers
    """
    
    # Method 1: Try ScrapingDog API if key is available
    if SCRAPINGDOG_API_KEY and SCRAPINGDOG_API_KEY.strip():
        try:
            params = {
                "api_key": SCRAPINGDOG_API_KEY,
                "url": url,
                "dynamic": "true",
                "premium": "true"
            }
            response = requests.get(SCRAPINGDOG_BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            print(f"✅ ScrapingDog API successful for {url}")
            return response.text
        except requests.RequestException as e:
            print(f"⚠️ ScrapingDog API failed: {e}")
    else:
        print("⚠️ No ScrapingDog API key found, using direct methods")
    
    # Method 2: Direct requests with proper headers
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Direct scraping successful for {url}")
        return response.text
        
    except requests.RequestException as e:
        print(f"⚠️ Direct scraping failed: {e}")
    
    # Method 3: Simple fallback
    try:
        time.sleep(2)  # Brief delay before final attempt
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            print(f"✅ Simple fallback successful for {url}")
            return response.text
        else:
            print(f"⚠️ Simple fallback returned status {response.status_code}")
    except Exception as e:
        print(f"❌ All scraping methods failed: {e}")
    
    return None
