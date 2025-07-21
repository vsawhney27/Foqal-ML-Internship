#!/usr/bin/env python3
"""
Glassdoor Job Scraper
Glassdoor has anti-bot measures but is more accessible than LinkedIn
"""

import requests
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
from urllib.parse import urlencode, urljoin
import re

logger = logging.getLogger(__name__)

class GlassdoorScraper:
    def __init__(self, proxy_list=None, delay_range=(2, 6)):
        self.base_url = "https://www.glassdoor.com"
        self.proxy_list = proxy_list or []
        self.delay_range = delay_range
        self.session = requests.Session()
        
        # Set headers to mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.glassdoor.com/'
        })
    
    def get_proxy(self):
        """Get random proxy from proxy list"""
        if self.proxy_list:
            return random.choice(self.proxy_list)
        return None
    
    def rate_limit(self):
        """Implement rate limiting"""
        delay = random.uniform(*self.delay_range)
        logger.info(f"Glassdoor rate limiting: waiting {delay:.2f} seconds")
        time.sleep(delay)
    
    def search_jobs(self, keyword="AI machine learning", location="", limit=20):
        """Search for jobs on Glassdoor"""
        jobs = []
        
        # Glassdoor job search parameters
        params = {
            'sc.keyword': keyword,
            'locT': 'C' if location else '',
            'locId': '',
            'jobType': '',
            'radius': '25',
            'fromAge': 1  # Jobs posted within 1 day
        }
        
        if location:
            params['sc.locationSeoString'] = location.lower().replace(' ', '-')
        
        search_url = f"{self.base_url}/Job/jobs.htm?" + urlencode(params)
        
        try:
            # Use proxy if available
            proxy = self.get_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            logger.info(f"Searching Glassdoor: {search_url}")
            response = self.session.get(search_url, proxies=proxies, timeout=30)
            
            # Check for common blocks
            if response.status_code == 429:
                logger.error("Rate limited by Glassdoor")
                return jobs
            elif 'blocked' in response.text.lower():
                logger.error("Request blocked by Glassdoor")
                return jobs
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards (Glassdoor structure)
            job_cards = (soup.find_all('li', {'data-jobid': True}) or 
                        soup.find_all('div', class_='react-job-listing') or
                        soup.find_all('article', class_='job-listing'))
            
            logger.info(f"Found {len(job_cards)} job cards on Glassdoor")
            
            for card in job_cards[:limit]:
                try:
                    job_data = self.extract_job_data(card)
                    if job_data:
                        jobs.append(job_data)
                    
                    # Rate limit between extractions
                    if len(jobs) < limit:
                        time.sleep(random.uniform(0.5, 2))
                        
                except Exception as e:
                    logger.warning(f"Error extracting Glassdoor job data: {e}")
                    continue
            
            self.rate_limit()
            
        except Exception as e:
            logger.error(f"Error searching Glassdoor: {e}")
        
        return jobs
    
    def extract_job_data(self, card):
        """Extract job data from Glassdoor job card"""
        try:
            # Job ID
            job_id = card.get('data-jobid') or card.get('id', '')
            
            # Title
            title_elem = (card.find('a', class_='jobLink') or 
                         card.find('h2', class_='jobTitle') or
                         card.find('a', {'data-test': 'job-title'}))
            
            title = title_elem.get_text(strip=True) if title_elem else None
            
            # Company
            company_elem = (card.find('div', class_='jobHeader') or
                           card.find('span', class_='employerName') or
                           card.find('a', {'data-test': 'employer-name'}))
            
            if company_elem:
                company = company_elem.get_text(strip=True)
            else:
                company = None
            
            # Location
            location_elem = (card.find('span', class_='loc') or
                            card.find('div', class_='location') or
                            card.find('span', {'data-test': 'job-location'}))
            
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Salary
            salary_elem = (card.find('span', class_='salaryText') or
                          card.find('div', class_='salary-estimate'))
            
            salary = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Job URL
            job_url = None
            if title_elem and title_elem.get('href'):
                href = title_elem['href']
                if href.startswith('/'):
                    job_url = urljoin(self.base_url, href)
                else:
                    job_url = href
            
            # Summary/Description
            summary_elem = (card.find('div', class_='jobDescription') or
                           card.find('div', class_='desc') or
                           card.find('div', {'data-test': 'job-desc'}))
            
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Posted date
            date_elem = (card.find('div', class_='jobAge') or
                        card.find('span', class_='date'))
            
            posted_date = date_elem.get_text(strip=True) if date_elem else None
            
            # Company rating
            rating_elem = card.find('span', class_='rating')
            rating = rating_elem.get_text(strip=True) if rating_elem else None
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'description': summary,
                'summary': summary,
                'job_url': job_url,
                'job_id': job_id,
                'posted_date': posted_date,
                'company_rating': rating,
                'source': 'Glassdoor',
                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Filter out jobs with missing critical data
            if not title or not company:
                return None
                
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting Glassdoor job data: {e}")
            return None

def scrape_glassdoor_jobs(keyword="AI machine learning", location="", limit=20, proxy_list=None):
    """Convenience function to scrape Glassdoor jobs"""
    scraper = GlassdoorScraper(proxy_list=proxy_list)
    return scraper.search_jobs(keyword=keyword, location=location, limit=limit)