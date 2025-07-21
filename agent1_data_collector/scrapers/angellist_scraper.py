#!/usr/bin/env python3
"""
AngelList (Wellfound) Job Scraper
AngelList/Wellfound is more accessible for scraping than LinkedIn/Glassdoor
"""

import requests
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
from urllib.parse import urlencode, urljoin
import json

logger = logging.getLogger(__name__)

class AngelListScraper:
    def __init__(self, proxy_list=None, delay_range=(1, 4)):
        self.base_url = "https://wellfound.com"  # AngelList rebranded to Wellfound
        self.proxy_list = proxy_list or []
        self.delay_range = delay_range
        self.session = requests.Session()
        
        # Set headers to mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_proxy(self):
        """Get random proxy from proxy list"""
        if self.proxy_list:
            return random.choice(self.proxy_list)
        return None
    
    def rate_limit(self):
        """Implement rate limiting"""
        delay = random.uniform(*self.delay_range)
        logger.info(f"AngelList rate limiting: waiting {delay:.2f} seconds")
        time.sleep(delay)
    
    def search_jobs(self, role="machine-learning-engineer", location="", limit=20):
        """Search for jobs on AngelList/Wellfound"""
        jobs = []
        
        # AngelList job search URL structure
        if location:
            search_url = f"{self.base_url}/jobs/{role}/l/{location.lower().replace(' ', '-')}"
        else:
            search_url = f"{self.base_url}/jobs/{role}"
        
        try:
            # Use proxy if available
            proxy = self.get_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            logger.info(f"Searching AngelList/Wellfound: {search_url}")
            response = self.session.get(search_url, proxies=proxies, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards (AngelList structure)
            job_cards = (soup.find_all('div', {'data-test': 'JobSearchCard'}) or
                        soup.find_all('div', class_='styles_jobCard') or
                        soup.find_all('div', class_='job-card') or
                        soup.find_all('a', class_='startup-link'))
            
            logger.info(f"Found {len(job_cards)} job cards on AngelList")
            
            for card in job_cards[:limit]:
                try:
                    job_data = self.extract_job_data(card)
                    if job_data:
                        jobs.append(job_data)
                    
                    # Rate limit between extractions
                    if len(jobs) < limit:
                        time.sleep(random.uniform(0.3, 1))
                        
                except Exception as e:
                    logger.warning(f"Error extracting AngelList job data: {e}")
                    continue
            
            self.rate_limit()
            
        except Exception as e:
            logger.error(f"Error searching AngelList: {e}")
        
        return jobs
    
    def extract_job_data(self, card):
        """Extract job data from AngelList job card"""
        try:
            # Title
            title_elem = (card.find('h2', {'data-test': 'JobTitle'}) or
                         card.find('a', class_='job-title') or
                         card.find('h3') or
                         card.find('a'))
            
            title = title_elem.get_text(strip=True) if title_elem else None
            
            # Company
            company_elem = (card.find('h3', {'data-test': 'StartupName'}) or
                           card.find('div', class_='company-name') or
                           card.find('h4'))
            
            company = company_elem.get_text(strip=True) if company_elem else None
            
            # Location
            location_elem = (card.find('span', {'data-test': 'JobLocation'}) or
                            card.find('div', class_='location') or
                            card.find('span', class_='location'))
            
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Salary/Equity
            salary_elem = (card.find('div', {'data-test': 'JobSalary'}) or
                          card.find('span', class_='salary') or
                          card.find('div', class_='compensation'))
            
            salary = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Job URL
            job_url = None
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    job_url = urljoin(self.base_url, href)
                else:
                    job_url = href
            
            # Description/Summary
            desc_elem = (card.find('div', {'data-test': 'JobDescription'}) or
                        card.find('div', class_='description') or
                        card.find('p'))
            
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Company stage/size
            stage_elem = (card.find('div', class_='company-stage') or
                         card.find('span', class_='stage'))
            
            company_stage = stage_elem.get_text(strip=True) if stage_elem else None
            
            # Skills/Tags
            skills_elems = card.find_all('span', class_='tag') or card.find_all('div', class_='skill')
            skills = [skill.get_text(strip=True) for skill in skills_elems]
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'description': description,
                'job_url': job_url,
                'company_stage': company_stage,
                'skills': skills,
                'source': 'AngelList/Wellfound',
                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Filter out jobs with missing critical data
            if not title or not company:
                return None
                
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting AngelList job data: {e}")
            return None

def scrape_angellist_jobs(role="machine-learning-engineer", location="", limit=20, proxy_list=None):
    """Convenience function to scrape AngelList/Wellfound jobs"""
    scraper = AngelListScraper(proxy_list=proxy_list)
    return scraper.search_jobs(role=role, location=location, limit=limit)