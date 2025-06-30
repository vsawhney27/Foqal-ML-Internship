import os
from dotenv import load_dotenv

load_dotenv()

SCRAPINGDOG_API_KEY = os.getenv("SCRAPINGDOG_API_KEY")
SCRAPINGDOG_BASE_URL = "https://api.scrapingdog.com/scrape"
HEADERS = {
    "Content-Type": "application/json"
}
