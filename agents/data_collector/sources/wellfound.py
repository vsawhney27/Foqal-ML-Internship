"""
Wellfound (formerly AngelList) Job Collecter
Fetches job postings from Wellfound
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager  # ✅ This is what was missing

import time
import random

"""
    Creates a headless Chrome browser using Selenium and WebDriver Manager.
    
    Returns:
        webdriver.Chrome: Configured ChromeDriver instance
"""
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--window-size=1920x1080")

    # Force correct driver version for Apple Silicon (mac64)
    driver_path = ChromeDriverManager().install()
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# -------------------------------------------
# Safely extract text from a child element
# -------------------------------------------
def get_text_safe(parent, by, value):
    """
    Attempts to extract text from a sub-element. Returns 'N/A' if not found.
    """
    try:
        return parent.find_element(by, value).text
    except NoSuchElementException:
        return "N/A"

"""
    Scrapes remote software job postings from Wellfound.com.
    
    Args:
        limit (int): Maximum number of jobs to return

    Returns:
        List[dict]: List of job posting dictionaries with title, company, location, etc.
"""
def collect_jobs(limit=50):
    jobs = []
    driver = setup_driver()

    url =  "https://wellfound.com/jobs?query=software-engineer&location=remote"
    driver.get(url)
    time.sleep(5)

    try:
        # Each job listing container
        job_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'styles_component')]")
        for job in job_cards:
            if len(jobs) >= limit:
                break;
            try:
                title = get_text_safe(job, By.XPATH, ".//h3")
                company = get_text_safe(job, By.XPATH, ".//h2")
                location = get_text_safe(job, By.XPATH, ".//span[contains(text(), 'Remote') or contains(text(), ',')]")

                try: 
                    link_elem = job.find_element(By.XPATH, ".//a[contains(@href, '/job/')]")
                    job_url = link_elem.get_attribute("href")
                except NoSuchElementException:
                    job_url = "N/A"

                job_data = {
                     "title": title,
                    "company": company,
                    "location": location,
                    "description": "N/A",  # Full scraping not yet implemented
                    "url": job_url,
                    "posting_date": "N/A",  # Wellfound doesn't show it
                    "source": "Wellfound"
                }
                jobs.append(job_data)
            except Exception as inner_err:
                print(f"[WARN] Skipped job card due to error: {inner_err}")
                continue
    except Exception as e:
        print(f"[ERROR] Failed to scrape Wellfound jobs: {e}")
    finally:
        driver.quit()
    return jobs

# -------------------------------------------
# Local test: Run this file directly to preview results
# -------------------------------------------
if __name__ == "__main__":
    sample_jobs = collect_jobs(limit=5)
    for job in sample_jobs:
        print(job)