"""
Wellfound (formerly AngelList) Job Collecter
Fetches job postings from Wellfound
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager 

import time
import random

def setup_driver():
    """
    Creates a Chrome browser with anti-bot detection measures.
    
    Returns:
        webdriver.Chrome: Configured ChromeDriver instance
    """
    chrome_options = Options()
    
    # Anti-detection measures
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Comment out headless for now to see if CAPTCHA appears
    # chrome_options.add_argument("--headless")

    driver_path = ChromeDriverManager().install()
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute script to hide webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def get_text_safe(parent, by, value):
    """
    Attempts to extract text from a sub-element. Returns 'N/A' if not found.
    """
    try:
        return parent.find_element(by, value).text
    except NoSuchElementException:
        return "N/A"

def scrape_job_description(driver, job_url):
    """
    Visits a job URL and extracts the full job description.
    
    Args:
        driver: Selenium WebDriver instance
        job_url: URL of the job posting
        
    Returns:
        str: Full job description or 'N/A' if not found
    """
    if job_url == "N/A":
        return "N/A"
    
    try:
        driver.get(job_url)
        wait = WebDriverWait(driver, 10)
        
        # Try multiple selectors for job description
        description_selectors = [
            "//div[contains(@class, 'job-description')]",
            "//div[contains(@class, 'description')]//div[contains(@class, 'content')]",
            "//div[contains(@class, 'prose')]",
            "//div[contains(@data-test, 'JobDescription')]",
            "//section[contains(@class, 'description')]",
            "//div[contains(text(), 'What you')]//parent::div",
            "//div[contains(text(), 'About the role')]//parent::div"
        ]
        
        for selector in description_selectors:
            try:
                desc_element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                description = desc_element.text.strip()
                if description and len(description) > 50:  # Ensure meaningful content
                    return description
            except (TimeoutException, NoSuchElementException):
                continue
        
        # Fallback: try to get any substantial text content
        try:
            main_content = driver.find_element(By.XPATH, "//main | //div[contains(@class, 'main')] | //div[contains(@class, 'content')]")
            paragraphs = main_content.find_elements(By.XPATH, ".//p | .//div[contains(@class, 'text')]")
            full_text = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
            if len(full_text) > 100:
                return full_text
        except NoSuchElementException:
            pass
            
        return "N/A"
        
    except Exception as e:
        print(f"[WARN] Failed to scrape description from {job_url}: {e}")
        return "N/A"

def parse_job_card(job_card):
    """
    Extracts job information from a single job card element.
    
    Args:
        job_card: Selenium WebElement representing a job card
        
    Returns:
        dict: Job information dictionary or None if parsing fails
    """
    try:
        title = get_text_safe(job_card, By.XPATH, ".//h3")
        company = get_text_safe(job_card, By.XPATH, ".//h2")
        location = get_text_safe(job_card, By.XPATH, ".//span[contains(text(), 'Remote') or contains(text(), ',')]")

        try: 
            link_elem = job_card.find_element(By.XPATH, ".//a[contains(@href, '/job/')]")
            job_url = link_elem.get_attribute("href")
        except NoSuchElementException:
            job_url = "N/A"

        # Skip if essential fields are missing
        if title == "N/A" or company == "N/A":
            return None

        return {
            "title": title,
            "company": company,
            "location": location,
            "url": job_url,
            "source": "Wellfound"
        }
    except Exception as e:
        print(f"[WARN] Failed to parse job card: {e}")
        return None

def collect_jobs(limit=50):
    """
    Scrapes remote software job postings from Wellfound.com.
    
    Args:
        limit (int): Maximum number of jobs to return

    Returns:
        List[dict]: List of job posting dictionaries with title, company, location, etc.
    """
    jobs = []
    driver = setup_driver()

    url = "https://wellfound.com/jobs?query=software-engineer&location=remote"
    
    try:
        print(f"[INFO] Navigating to: {url}")
        driver.get(url)
        time.sleep(random.uniform(5, 8))  # Longer wait
        
        print(f"[INFO] Page title: {driver.title}")
        print(f"[INFO] Current URL: {driver.current_url}")
        
        # Check for CAPTCHA
        if "captcha" in driver.page_source.lower() or "DataDome" in driver.page_source:
            print("[CAPTCHA] CAPTCHA detected! Please solve it manually in the browser window.")
            print("[CAPTCHA] Once solved, the scraper will continue automatically...")
            
            # Wait for CAPTCHA to be solved (check every 3 seconds)
            max_wait = 120  # 2 minutes max
            waited = 0
            
            while waited < max_wait:
                time.sleep(3)
                waited += 3
                
                # Check if we're past the CAPTCHA
                current_source = driver.page_source
                if "captcha" not in current_source.lower() and "DataDome" not in current_source:
                    print("[SUCCESS] CAPTCHA solved! Continuing with job scraping...")
                    break
                    
                if waited % 15 == 0:  # Print every 15 seconds
                    print(f"[WAITING] Still waiting for CAPTCHA to be solved... ({waited}s elapsed)")
            
            if waited >= max_wait:
                print("[TIMEOUT] CAPTCHA not solved within 2 minutes. Exiting...")
                return jobs

        # Try multiple selectors for job cards
        job_selectors = [
            "//div[contains(@class, 'styles_component')]",
            "//div[contains(@class, 'job')]",
            "//article",
            "//div[contains(@class, 'card')]",
            "//div[contains(@class, 'listing')]"
        ]
        
        job_cards = []
        for selector in job_selectors:
            try:
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                job_cards = driver.find_elements(By.XPATH, selector)
                if job_cards:
                    print(f"[INFO] Found {len(job_cards)} job cards using selector: {selector}")
                    break
            except TimeoutException:
                print(f"[WARN] Selector failed: {selector}")
                continue
        
        if not job_cards:
            print("[ERROR] No job cards found with any selector")
            return jobs

        for i, job_card in enumerate(job_cards):
            if len(jobs) >= limit:
                break

            print(f"[INFO] Processing job {i+1}/{min(len(job_cards), limit)}")
            
            # Parse basic job information
            job_data = parse_job_card(job_card)
            if not job_data:
                continue

            # Add rate limiting between job card processing
            time.sleep(random.uniform(1, 2))

            # Scrape full job description
            try:
                description = scrape_job_description(driver, job_data["url"])
                job_data["description"] = description
                job_data["posting_date"] = "N/A"  # Wellfound doesn't show posting dates
                
                jobs.append(job_data)
                print(f"[SUCCESS] Scraped job: {job_data['title']} at {job_data['company']}")
                
                # Rate limiting between full page visits
                time.sleep(random.uniform(2, 4))
                
            except Exception as desc_err:
                print(f"[WARN] Failed to get description for job {i+1}: {desc_err}")
                job_data["description"] = "N/A"
                job_data["posting_date"] = "N/A"
                jobs.append(job_data)

    except Exception as e:
        print(f"[ERROR] Failed to scrape Wellfound jobs: {e}")
    finally:
        driver.quit()
    
    print(f"[INFO] Successfully collected {len(jobs)} jobs")
    return jobs

# -------------------------------------------
# Local test: Run this file directly to preview results
# -------------------------------------------
if __name__ == "__main__":
    print("Testing Wellfound scraper with manual CAPTCHA solving...")
    print("A Chrome browser window will open. Solve any CAPTCHA that appears.")
    print("The scraper will collect 2 jobs for testing.\n")
    
    sample_jobs = collect_jobs(limit=2)
    
    print(f"\n{'='*60}")
    print("SCRAPED JOBS RESULTS")
    print('='*60)
    
    for i, job in enumerate(sample_jobs, 1):
        print(f"\n--- JOB {i} ---")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"URL: {job['url']}")
        print(f"Description: {job['description'][:200]}...")
        print(f"Source: {job['source']}")
    
    print(f"\nTotal jobs collected: {len(sample_jobs)}")