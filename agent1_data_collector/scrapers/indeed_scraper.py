#!/usr/bin/env python3
"""
Indeed Job Scraper
Scrapes job postings from Indeed with rate limiting and proxy rotation
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

class IndeedScraper:
    def __init__(self, proxy_list=None, delay_range=(2, 5)):
        self.base_url = "https://www.indeed.com"
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
        logger.info(f"Rate limiting: waiting {delay:.2f} seconds")
        time.sleep(delay)
    
    def search_jobs(self, query="AI machine learning", location="remote", limit=20):
        """Search for jobs on Indeed"""
        jobs = []
        
        params = {
            'q': query,
            'l': location,
            'sort': 'date',
            'limit': min(limit, 50)  # Indeed limits per page
        }
        
        search_url = f"{self.base_url}/jobs?" + urlencode(params)
        
        try:
            # Use proxy if available
            proxy = self.get_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            logger.info(f"Searching Indeed: {search_url}")
            response = self.session.get(search_url, proxies=proxies, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards (Indeed's structure)
            job_cards = soup.find_all('div', {'data-jk': True}) or soup.find_all('a', {'data-jk': True})
            
            logger.info(f"Found {len(job_cards)} job cards on Indeed")
            
            for card in job_cards[:limit]:
                try:
                    job_data = self.extract_job_data(card, soup)
                    if job_data:
                        jobs.append(job_data)
                    
                    # Rate limit between job extractions
                    if len(jobs) < limit:
                        time.sleep(random.uniform(0.5, 1.5))
                        
                except Exception as e:
                    logger.warning(f"Error extracting job data: {e}")
                    continue
            
            self.rate_limit()  # Rate limit after each search
            
        except Exception as e:
            logger.error(f"Error searching Indeed: {e}")
        
        return jobs
    
    def extract_job_data(self, card, soup):
        """Extract job data from Indeed job card"""
        try:
            # Get job ID
            job_id = card.get('data-jk') or card.get('id', '')
            
            # Title
            title_elem = card.find('h2', class_='jobTitle') or card.find('a', {'data-jk': job_id})
            title = title_elem.get_text(strip=True) if title_elem else None
            
            # Company
            company_elem = card.find('span', class_='companyName') or card.find('div', class_='companyName')
            company = company_elem.get_text(strip=True) if company_elem else None
            
            # Location
            location_elem = card.find('div', class_='companyLocation')
            location = location_elem.get_text(strip=True) if location_elem else "Remote"
            
            # Salary (if available)
            salary_elem = card.find('span', class_='salary-snippet') or card.find('div', class_='salary-snippet')
            salary = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Job URL
            link_elem = card.find('a', {'data-jk': job_id}) or title_elem
            job_url = None
            if link_elem and link_elem.get('href'):
                job_url = urljoin(self.base_url, link_elem['href'])
            
            # Summary/snippet
            summary_elem = card.find('div', class_='job-snippet') or card.find('span', class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Get full description if URL available
            full_description = summary
            if job_url:
                try:
                    full_description = self.get_job_description(job_url)
                except Exception as e:
                    logger.warning(f"Could not get full description: {e}")
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'description': full_description,
                'summary': summary,
                'job_url': job_url,
                'job_id': job_id,
                'source': 'Indeed',
                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Filter out jobs with missing critical data
            if not title or not company:
                return None
                
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
    def get_job_description(self, job_url):
        """Get full job description from job detail page"""
        try:
            proxy = self.get_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            response = self.session.get(job_url, proxies=proxies, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job description
            desc_elem = (soup.find('div', class_='jobsearch-jobDescriptionText') or 
                        soup.find('div', id='jobDescriptionText') or
                        soup.find('div', class_='job-description'))
            
            if desc_elem:
                return desc_elem.get_text(separator='\n', strip=True)
            
            return "Description not available"
            
        except Exception as e:
            logger.warning(f"Error getting job description: {e}")
            return "Description not available"

def scrape_indeed_jobs(query="AI machine learning", location="remote", limit=20, proxy_list=None):
    """Convenience function to scrape Indeed jobs"""
    scraper = IndeedScraper(proxy_list=proxy_list)
    return scraper.search_jobs(query=query, location=location, limit=limit)