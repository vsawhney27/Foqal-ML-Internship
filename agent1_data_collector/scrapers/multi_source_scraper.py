#!/usr/bin/env python3
"""
Multi-Source Job Scraper
Implements comprehensive data collection from multiple job platforms
with rate limiting, proxy rotation, and robust error handling
"""

import json
import requests
import time
import logging
import random
from typing import List, Dict
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import itertools
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiSourceJobScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Rotate user agents for better scraping
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Rate limiting settings (requests per minute)
        self.rate_limits = {
            'remoteok': 30,  # 30 requests per minute
            'indeed': 20,   # 20 requests per minute
            'glassdoor': 15, # 15 requests per minute
            'angellist': 25, # 25 requests per minute
            'company_careers': 40 # 40 requests per minute
        }
        
        self.last_request_times = {}
        
    def _rate_limit(self, source: str):
        """Implement rate limiting per source"""
        if source not in self.rate_limits:
            return
            
        current_time = time.time()
        if source in self.last_request_times:
            time_since_last = current_time - self.last_request_times[source]
            min_interval = 60.0 / self.rate_limits[source]  # seconds between requests
            
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                logger.info(f"Rate limiting {source}: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        self.last_request_times[source] = time.time()
    
    def _rotate_user_agent(self):
        """Rotate user agent for each request"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents)
        })
    
    def scrape_remoteok(self, limit=50):
        """Scrape RemoteOK API"""
        jobs = []
        try:
            self._rate_limit('remoteok')
            self._rotate_user_agent()
            
            url = "https://remoteok.io/api"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 1:
                    for job_data in data[1:limit+1]:
                        if self._is_valid_job(job_data):
                            job = self._normalize_remoteok_job(job_data)
                            jobs.append(job)
                            
            logger.info(f"RemoteOK: Collected {len(jobs)} jobs")
            
        except Exception as e:
            logger.error(f"RemoteOK scraping failed: {e}")
            
        return jobs
    
    def scrape_indeed_search(self, query="software engineer", location="remote", limit=30):
        """Scrape Indeed job search results"""
        jobs = []
        try:
            self._rate_limit('indeed')
            self._rotate_user_agent()
            
            # Indeed search URL
            base_url = "https://www.indeed.com/jobs"
            params = {
                'q': query,
                'l': location,
                'remotejob': '032b3046-06a3-4876-8dfd-474eb5e7ed11',  # Remote job filter
                'start': 0
            }
            
            response = self.session.get(base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', {'data-jk': True})
                
                for card in job_cards[:limit]:
                    try:
                        job = self._parse_indeed_job(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Failed to parse Indeed job: {e}")
                        continue
                        
            logger.info(f"Indeed: Collected {len(jobs)} jobs")
            
        except Exception as e:
            logger.error(f"Indeed scraping failed: {e}")
            
        return jobs
    
    def scrape_angellist_startups(self, limit=25):
        """Scrape AngelList/Wellfound startup jobs"""
        jobs = []
        try:
            self._rate_limit('angellist')
            self._rotate_user_agent()
            
            # AngelList jobs endpoint (public API when available)
            base_url = "https://wellfound.com/jobs"
            params = {
                'remote': 'true',
                'job_type': 'full-time'
            }
            
            response = self.session.get(base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Parse AngelList job structure
                job_items = soup.find_all('div', class_=re.compile('job.*item'))
                
                for item in job_items[:limit]:
                    try:
                        job = self._parse_angellist_job(item)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Failed to parse AngelList job: {e}")
                        continue
                        
            logger.info(f"AngelList: Collected {len(jobs)} jobs")
            
        except Exception as e:
            logger.error(f"AngelList scraping failed: {e}")
            
        return jobs
    
    def scrape_company_careers(self, companies=None, limit=20):
        """Scrape company career pages"""
        if not companies:
            companies = [
                'https://careers.google.com/api/v3/search/',
                'https://www.apple.com/careers/api/search',
                'https://careers.microsoft.com/api/search',
                'https://jobs.netflix.com/api/search',
                'https://www.shopify.com/careers/api/jobs'
            ]
        
        jobs = []
        for company_url in companies[:5]:  # Limit company searches
            try:
                self._rate_limit('company_careers')
                self._rotate_user_agent()
                
                company_jobs = self._scrape_single_company(company_url, limit//5)
                jobs.extend(company_jobs)
                
            except Exception as e:
                logger.error(f"Company career scraping failed for {company_url}: {e}")
                continue
                
        logger.info(f"Company Careers: Collected {len(jobs)} jobs")
        return jobs
    
    def _scrape_single_company(self, company_url, limit):
        """Scrape a single company's career page"""
        jobs = []
        
        # This is a simplified implementation - each company would need custom parsing
        response = self.session.get(company_url, timeout=15)
        
        if response.status_code == 200:
            try:
                # Try JSON API first
                data = response.json()
                if 'jobs' in data:
                    for job_data in data['jobs'][:limit]:
                        job = self._normalize_company_job(job_data, company_url)
                        jobs.append(job)
            except:
                # Fall back to HTML parsing
                soup = BeautifulSoup(response.content, 'html.parser')
                job_links = soup.find_all('a', href=re.compile(r'/job|/career|/position'))
                
                for link in job_links[:limit]:
                    try:
                        job = self._parse_company_job_link(link, company_url)
                        if job:
                            jobs.append(job)
                    except:
                        continue
        
        return jobs
    
    def _is_valid_job(self, job_data):
        """Validate job data quality"""
        if not isinstance(job_data, dict):
            return False
            
        required_fields = ['position', 'company']
        return all(field in job_data and job_data[field] for field in required_fields)
    
    def _normalize_remoteok_job(self, job_data):
        """Normalize RemoteOK job data"""
        return {
            'title': job_data.get('position', 'Unknown Position'),
            'company': job_data.get('company', 'Unknown Company'),
            'location': 'Remote',
            'description': self._clean_description(job_data.get('description', '')),
            'department': self._extract_department_from_tags(job_data.get('tags', [])),
            'job_url': f"https://remoteok.io/remote-jobs/{job_data.get('id', '')}",
            'source': 'RemoteOK',
            'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'salary_min': job_data.get('salary_min'),
            'salary_max': job_data.get('salary_max'),
            'job_type': job_data.get('job_type', 'full-time')
        }
    
    def _parse_indeed_job(self, job_card):
        """Parse Indeed job card"""
        try:
            title_elem = job_card.find('h2', class_='jobTitle')
            company_elem = job_card.find('span', {'data-testid': 'company-name'})
            location_elem = job_card.find('div', {'data-testid': 'job-location'})
            
            if not (title_elem and company_elem):
                return None
                
            job_id = job_card.get('data-jk', '')
            
            return {
                'title': title_elem.get_text(strip=True),
                'company': company_elem.get_text(strip=True),
                'location': location_elem.get_text(strip=True) if location_elem else 'Not specified',
                'description': 'Description requires individual job page fetch',
                'department': 'Engineering',  # Default assumption
                'job_url': f"https://www.indeed.com/viewjob?jk={job_id}",
                'source': 'Indeed',
                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'job_type': 'full-time'
            }
        except Exception as e:
            logger.warning(f"Error parsing Indeed job: {e}")
            return None
    
    def _parse_angellist_job(self, job_item):
        """Parse AngelList job item"""
        try:
            # This would need to be customized based on current AngelList structure
            title_elem = job_item.find('a', class_=re.compile('job.*title'))
            company_elem = job_item.find('a', class_=re.compile('company.*name'))
            
            if not (title_elem and company_elem):
                return None
                
            return {
                'title': title_elem.get_text(strip=True),
                'company': company_elem.get_text(strip=True),
                'location': 'Remote',
                'description': 'AngelList startup opportunity',
                'department': 'Engineering',
                'job_url': urljoin('https://wellfound.com', title_elem.get('href', '')),
                'source': 'AngelList',
                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'job_type': 'full-time'
            }
        except Exception as e:
            logger.warning(f"Error parsing AngelList job: {e}")
            return None
    
    def _normalize_company_job(self, job_data, company_url):
        """Normalize company career page job data"""
        domain = urlparse(company_url).netloc
        company_name = domain.split('.')[1] if '.' in domain else domain
        
        return {
            'title': job_data.get('title', 'Unknown Position'),
            'company': company_name.title(),
            'location': job_data.get('location', 'Not specified'),
            'description': job_data.get('description', ''),
            'department': job_data.get('department', 'Not specified'),
            'job_url': job_data.get('url', company_url),
            'source': f'{company_name.title()} Careers',
            'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'job_type': job_data.get('employment_type', 'full-time')
        }
    
    def _parse_company_job_link(self, link, company_url):
        """Parse company job link"""
        try:
            domain = urlparse(company_url).netloc
            company_name = domain.split('.')[1] if '.' in domain else domain
            
            return {
                'title': link.get_text(strip=True),
                'company': company_name.title(),
                'location': 'Not specified',
                'description': 'See job link for details',
                'department': 'Not specified',
                'job_url': urljoin(company_url, link.get('href', '')),
                'source': f'{company_name.title()} Careers',
                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'job_type': 'full-time'
            }
        except:
            return None
    
    def _clean_description(self, description):
        """Clean job description text"""
        if not description:
            return ""
        
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', ' ', str(description))
        # Clean up whitespace
        description = re.sub(r'\s+', ' ', description).strip()
        return description
    
    def _extract_department_from_tags(self, tags):
        """Extract department from job tags"""
        if not tags:
            return "Engineering"
        
        department_mapping = {
            'dev': 'Engineering',
            'engineering': 'Engineering',
            'frontend': 'Engineering',
            'backend': 'Engineering',
            'fullstack': 'Engineering',
            'marketing': 'Marketing',
            'sales': 'Sales',
            'design': 'Design',
            'product': 'Product',
            'data': 'Data Science',
            'finance': 'Finance',
            'hr': 'Human Resources'
        }
        
        for tag in tags:
            tag_lower = str(tag).lower()
            for key, dept in department_mapping.items():
                if key in tag_lower:
                    return dept
        
        return "Engineering"  # Default


def scrape_all_sources(limit_per_source=25):
    """Scrape jobs from all available sources"""
    scraper = MultiSourceJobScraper()
    all_jobs = []
    
    logger.info("Starting multi-source job collection...")
    
    # Scrape from each source
    sources = [
        ('RemoteOK', scraper.scrape_remoteok),
        ('Indeed', lambda: scraper.scrape_indeed_search(limit=limit_per_source)),
        ('AngelList', scraper.scrape_angellist_startups),
        ('Company Careers', scraper.scrape_company_careers)
    ]
    
    for source_name, scrape_func in sources:
        try:
            logger.info(f"Scraping {source_name}...")
            jobs = scrape_func(limit_per_source) if source_name == 'RemoteOK' else scrape_func()
            all_jobs.extend(jobs)
            logger.info(f"{source_name}: Added {len(jobs)} jobs")
            
            # Add delay between sources
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Failed to scrape {source_name}: {e}")
            continue
    
    logger.info(f"Total jobs collected: {len(all_jobs)}")
    return all_jobs