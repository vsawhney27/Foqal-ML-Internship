#!/usr/bin/env python3
"""
Simple but effective job scraper that focuses on getting REAL job postings
from multiple reliable sources without needing complex parsing.
"""

import json
import requests
import time
import logging
from typing import List, Dict
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleJobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def scrape_github_jobs_api(self, limit=100):
        """Use GitHub's public jobs API if available"""
        jobs = []
        try:
            # Try JSearch API through RapidAPI (requires API key)
            # For now, let's use a simple approach with known public APIs
            
            # Try Adzuna API (UK/US job aggregator)
            app_id = "test"  # You'd need real credentials
            app_key = "test"
            
            # For demo, let's create realistic job data from known companies
            jobs = self.get_real_company_jobs(limit)
            
        except Exception as e:
            logger.error(f"Error with job APIs: {e}")
        
        return jobs

    def get_real_company_jobs(self, limit=100):
        """Get real jobs from company career pages using public APIs"""
        jobs = []
        
        # Real companies with actual public job APIs
        real_jobs_data = [
            # Greenhouse companies (these APIs are real and public)
            {"company": "Stripe", "api": "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"},
            {"company": "Airbnb", "api": "https://boards-api.greenhouse.io/v1/boards/airbnb/jobs"},
            {"company": "Shopify", "api": "https://boards-api.greenhouse.io/v1/boards/shopify/jobs"},
            {"company": "Coinbase", "api": "https://boards-api.greenhouse.io/v1/boards/coinbase/jobs"},
            {"company": "Databricks", "api": "https://boards-api.greenhouse.io/v1/boards/databricks/jobs"},
            
            # Lever companies (these APIs are real and public)  
            {"company": "Netflix", "api": "https://api.lever.co/v0/postings/netflix"},
            {"company": "Uber", "api": "https://api.lever.co/v0/postings/uber"},
            {"company": "Robinhood", "api": "https://api.lever.co/v0/postings/robinhood"},
            {"company": "Discord", "api": "https://api.lever.co/v0/postings/discord"},
            {"company": "Twitch", "api": "https://api.lever.co/v0/postings/twitch"},
        ]
        
        for company_info in real_jobs_data:
            try:
                logger.info(f"Scraping {company_info['company']}...")
                response = self.session.get(company_info['api'], timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle Greenhouse format
                    if 'jobs' in data:
                        company_jobs = data['jobs'][:10]  # Limit per company
                        for job_data in company_jobs:
                            job = {
                                'title': job_data.get('title', 'Software Engineer'),
                                'company': company_info['company'],
                                'location': job_data.get('location', {}).get('name', 'Various') if isinstance(job_data.get('location'), dict) else 'Various',
                                'description': self.clean_text(job_data.get('content', f"Real job posting at {company_info['company']}")),
                                'department': job_data.get('departments', [{}])[0].get('name') if job_data.get('departments') else 'Engineering',
                                'job_url': job_data.get('absolute_url', f"https://{company_info['company'].lower()}.com/careers"),
                                'source': f"{company_info['company']} Careers",
                                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if len(job['description']) > 50:
                                jobs.append(job)
                                logger.info(f"Added real job: {job['title']} at {job['company']}")
                    
                    # Handle Lever format
                    elif isinstance(data, list):
                        for job_data in data[:10]:  # Limit per company
                            job = {
                                'title': job_data.get('text', 'Software Engineer'),
                                'company': company_info['company'],
                                'location': job_data.get('categories', {}).get('location', 'Various'),
                                'description': self.clean_text(job_data.get('description', f"Real job posting at {company_info['company']}")),
                                'department': job_data.get('categories', {}).get('team', 'Engineering'),
                                'job_url': job_data.get('applyUrl', f"https://{company_info['company'].lower()}.com/careers"),
                                'source': f"{company_info['company']} Careers",
                                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if len(job['description']) > 50:
                                jobs.append(job)
                                logger.info(f"Added real job: {job['title']} at {job['company']}")
                else:
                    logger.warning(f"Failed to fetch {company_info['company']}: HTTP {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error scraping {company_info['company']}: {e}")
                continue
        
        return jobs[:limit]

    def clean_text(self, text):
        """Clean HTML and format text"""
        if not text:
            return "Job details available on company website"
        
        # Remove HTML tags if present
        import re
        text = re.sub(r'<[^>]+>', '', str(text))
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text[:2000]  # Limit length

    def scrape_job_boards(self, limit=100):
        """Scrape from job boards that allow scraping"""
        jobs = []
        
        try:
            # Try to get more jobs from various sources
            jobs.extend(self.scrape_remoteok())
            jobs.extend(self.scrape_ycombinator_startups())
            
        except Exception as e:
            logger.error(f"Error scraping job boards: {e}")
        
        return jobs[:limit]

    def scrape_remoteok(self):
        """Scrape RemoteOK API"""
        jobs = []
        try:
            url = "https://remoteok.io/api"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 1:
                    # Skip first item (metadata)
                    for job_data in data[1:51]:  # Get up to 50 jobs
                        if self.is_tech_job(job_data):
                            job = {
                                'title': job_data.get('position', 'Remote Developer'),
                                'company': job_data.get('company', 'Remote Company'),
                                'location': 'Remote',
                                'description': self.clean_text(job_data.get('description', 'Remote job opportunity')),
                                'department': 'Engineering',
                                'job_url': f"https://remoteok.io/remote-jobs/{job_data.get('id', '')}",
                                'source': 'RemoteOK',
                                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            jobs.append(job)
                            logger.info(f"Added RemoteOK job: {job['title']} at {job['company']}")
        
        except Exception as e:
            logger.warning(f"RemoteOK error: {e}")
        
        return jobs

    def scrape_ycombinator_startups(self):
        """NO MORE FAKE DATA - Removed all generated job listings"""
        jobs = []
        # Completely removed fake job generation
        return jobs

    def is_tech_job(self, job_data):
        """Check if job is tech-related"""
        tech_keywords = ['engineer', 'developer', 'programmer', 'software', 'backend', 'frontend', 
                        'fullstack', 'python', 'javascript', 'react', 'node', 'data', 'ai', 'ml']
        
        title = str(job_data.get('position', '')).lower()
        tags = str(job_data.get('tags', [])).lower()
        
        return any(keyword in title or keyword in tags for keyword in tech_keywords)

def main():
    """Main scraping function"""
    scraper = SimpleJobScraper()
    all_jobs = []
    
    logger.info("Starting comprehensive job scraping...")
    
    # Scrape from company APIs
    api_jobs = scraper.scrape_github_jobs_api(200)
    all_jobs.extend(api_jobs)
    logger.info(f"Collected {len(api_jobs)} jobs from company APIs")
    
    # Scrape from job boards
    board_jobs = scraper.scrape_job_boards(100)
    all_jobs.extend(board_jobs)
    logger.info(f"Collected {len(board_jobs)} jobs from job boards")
    
    logger.info(f"Total jobs collected: {len(all_jobs)}")
    
    # Save to JSON
    with open('/Users/veersawhney/Downloads/Foqal Internship ML Project/scraped_jobs.json', 'w') as f:
        json.dump(all_jobs, f, indent=2)
    
    logger.info(f"Saved {len(all_jobs)} jobs to scraped_jobs.json")
    return all_jobs

if __name__ == "__main__":
    main()