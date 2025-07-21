#!/usr/bin/env python3
"""
LinkedIn Job Scraper
Note: LinkedIn has strict anti-bot measures. This scraper uses their public job search
without requiring authentication, but may have limited success due to bot detection.
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

class LinkedInScraper:
    def __init__(self, proxy_list=None, delay_range=(3, 8)):
        self.base_url = "https://www.linkedin.com"
        self.proxy_list = proxy_list or []
        self.delay_range = delay_range
        self.session = requests.Session()
        
        # Set headers to mimic real browser - very important for LinkedIn
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
    
    def get_proxy(self):
        """Get random proxy from proxy list"""
        if self.proxy_list:
            return random.choice(self.proxy_list)
        return None
    
    def rate_limit(self):
        """Implement aggressive rate limiting for LinkedIn"""
        delay = random.uniform(*self.delay_range)
        logger.info(f"LinkedIn rate limiting: waiting {delay:.2f} seconds")
        time.sleep(delay)
    
    def search_jobs(self, keywords="artificial intelligence machine learning", location="", limit=20):
        """
        Search for jobs on LinkedIn using their public job search
        Note: This may be blocked by LinkedIn's bot detection
        """
        jobs = []
        
        # LinkedIn job search parameters
        params = {
            'keywords': keywords,
            'location': location,
            'f_JT': 'F,P',  # Full-time and Part-time
            'f_E': '2,3,4',  # Experience levels
            'sortBy': 'DD',  # Date posted
            'start': 0
        }
        
        search_url = f"{self.base_url}/jobs/search?" + urlencode(params)
        
        try:
            # Use proxy if available
            proxy = self.get_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            logger.info(f"Searching LinkedIn: {search_url}")
            logger.warning("LinkedIn has strict anti-bot measures - this may not work without authentication")
            
            response = self.session.get(search_url, proxies=proxies, timeout=30)
            
            # Check if we're blocked
            if response.status_code == 429:
                logger.error("Rate limited by LinkedIn")
                return jobs
            elif response.status_code == 403:
                logger.error("Access forbidden by LinkedIn - bot detected")
                return jobs
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if we got redirected to login page
            if 'login' in response.url or 'challenge' in response.url:
                logger.error("LinkedIn redirected to login/challenge page - authentication required")
                return jobs
            
            # Find job cards (LinkedIn's structure changes frequently)
            job_cards = (soup.find_all('div', class_='job-search-card') or 
                        soup.find_all('div', class_='result-card') or
                        soup.find_all('li', class_='result-card'))
            
            logger.info(f"Found {len(job_cards)} job cards on LinkedIn")
            
            for card in job_cards[:limit]:
                try:
                    job_data = self.extract_job_data(card)
                    if job_data:
                        jobs.append(job_data)
                    
                    # Aggressive rate limiting between extractions
                    if len(jobs) < limit:
                        time.sleep(random.uniform(1, 3))
                        
                except Exception as e:
                    logger.warning(f"Error extracting LinkedIn job data: {e}")
                    continue
            
            self.rate_limit()  # Rate limit after search
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {e}")
            logger.info("Consider using LinkedIn API or authenticated access for reliable scraping")
        
        return jobs
    
    def extract_job_data(self, card):
        """Extract job data from LinkedIn job card"""
        try:
            # Title
            title_elem = (card.find('h3', class_='job-search-card__title') or 
                         card.find('h3', class_='result-card__title') or
                         card.find('a', class_='result-card__full-card-link'))
            
            title = title_elem.get_text(strip=True) if title_elem else None
            
            # Company
            company_elem = (card.find('h4', class_='job-search-card__subtitle') or
                           card.find('h3', class_='result-card__subtitle') or
                           card.find('a', class_='result-card__subtitle-link'))
            
            company = company_elem.get_text(strip=True) if company_elem else None
            
            # Location
            location_elem = (card.find('span', class_='job-search-card__location') or
                            card.find('span', class_='result-card__location'))
            
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Job URL
            link_elem = (card.find('a', class_='result-card__full-card-link') or
                        card.find('a', href=True))
            
            job_url = None
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                if href.startswith('/'):
                    job_url = urljoin(self.base_url, href)
                else:
                    job_url = href
            
            # Summary
            summary_elem = (card.find('div', class_='job-search-card__snippet') or
                           card.find('p', class_='result-card__snippet'))
            
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Posted date
            date_elem = (card.find('time', class_='job-search-card__listdate') or
                        card.find('time'))
            
            posted_date = date_elem.get('datetime') if date_elem else None
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'description': summary,  # LinkedIn doesn't provide full description without auth
                'summary': summary,
                'job_url': job_url,
                'posted_date': posted_date,
                'source': 'LinkedIn',
                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'note': 'Limited data - LinkedIn requires authentication for full access'
            }
            
            # Filter out jobs with missing critical data
            if not title or not company:
                return None
                
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn job data: {e}")
            return None

def scrape_linkedin_jobs(keywords="artificial intelligence machine learning", location="", limit=20, proxy_list=None):
    """
    Convenience function to scrape LinkedIn jobs
    Note: May have limited success due to LinkedIn's anti-bot measures
    """
    scraper = LinkedInScraper(proxy_list=proxy_list)
    jobs = scraper.search_jobs(keywords=keywords, location=location, limit=limit)
    
    if not jobs:
        logger.warning("No jobs found from LinkedIn - this is expected due to anti-bot measures")
        logger.info("For production use, consider LinkedIn API access or authenticated scraping")
    
    return jobs