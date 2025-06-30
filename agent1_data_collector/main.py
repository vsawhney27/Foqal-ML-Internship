from scraper import scrape_page
from bs4 import BeautifulSoup
import json
import datetime
import re
import os
import time
import argparse
from pymongo import MongoClient
import time

def save_to_mongo(jobs, db_url, db_name="JobPosting", collection_name="ScrapedJobs"):
    client = MongoClient(db_url)
    db = client[db_name]
    collection = db[collection_name]

    if jobs:
        collection.insert_many(jobs)
        print(f"✅ Inserted {len(jobs)} jobs into MongoDB.")
    else:
        print("⚠️ No jobs to insert.")

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text)

def extract_jobs(html: str, delay_between_requests=2, max_jobs=30):
    soup = BeautifulSoup(html, "html.parser")
    job_cards = soup.find_all("tr", class_="job")
    jobs = []

    for idx, job in enumerate(job_cards[:max_jobs]):
        try:
            title_elem = job.find("h2", itemprop="title")
            company_elem = job.find("h3", itemprop="name")
            location_elem = job.find("div", class_="location")
            link_elem = job.get("data-href")

            date = datetime.datetime.now().strftime("%Y-%m-%d")
            detail_url = f"https://remoteok.com{link_elem}" if link_elem else None

            full_description = "No Description Found"
            if detail_url:
                print(f"🔎 [{idx+1}] Scraping detail page: {detail_url}")
                detail_html = scrape_page(detail_url)
                detail_soup = BeautifulSoup(detail_html, "html.parser")
                desc_div = detail_soup.find("div", {"class": "description"}) or \
                           detail_soup.find("div", {"id": "job-description"})
                if desc_div:
                    full_description = desc_div.get_text(separator="\n", strip=True)
                time.sleep(delay_between_requests)

            job_info = {
                "title": title_elem.get_text(strip=True) if title_elem else None,
                "company": company_elem.get_text(strip=True) if company_elem else None,
                "location": remove_emojis(location_elem.get_text(strip=True)).strip() if location_elem else "Remote",
                "description": full_description,
                "detail_url": detail_url,
                "scraped_date": date
            }
            jobs.append(job_info)

        except Exception as e:
            print(f"❌ Error parsing job card or detail page: {e}")

    print(f"📊 Total jobs scraped: {len(jobs)} (Est. API requests: {1 + len(jobs)})")
    return jobs


def fetch_or_load(url, cache_path="output.html", cache_hours=6):
    if os.path.exists(cache_path):
        modified_time = os.path.getmtime(cache_path)
        if (time.time() - modified_time) < cache_hours * 3600:
            print("⚡ Using cached HTML")
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
    print("🌐 Fetching fresh HTML using ScrapingDog")
    html = scrape_page(url)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Force fresh scrape")
    args = parser.parse_args()

    url = "https://remoteok.com/remote-ai-jobs"
    html = fetch_or_load(url, cache_path="output.html", cache_hours=6 if not args.force else 0)

    if html:
        jobs = extract_jobs(html)
        print(json.dumps(jobs, indent=2))

        mongo_url = "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/"
        save_to_mongo(jobs, mongo_url)
