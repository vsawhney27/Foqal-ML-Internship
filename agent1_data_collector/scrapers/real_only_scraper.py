#!/usr/bin/env python3
"""
Real Jobs Only Scraper - NO FAKE DATA
Only scrapes from verified real job sources that provide actual job postings
"""

import json
import requests
import time
import logging
from typing import List, Dict
import re
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealJobsOnlyScaper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def scrape_remoteok_verified(self, limit=100):
        """Scrape RemoteOK - verified real jobs API"""
        jobs = []
        try:
            url = "https://remoteok.io/api"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 1:
                    # Skip first item (metadata)
                    for job_data in data[1:limit+1]:
                        if self.is_real_tech_job(job_data):
                            job = {
                                'title': job_data.get('position', 'Remote Developer'),
                                'company': job_data.get('company', 'Remote Company'),
                                'location': 'Remote',
                                'description': self.clean_description(job_data.get('description', 'Remote job opportunity')),
                                'department': self.extract_department_from_tags(job_data.get('tags', [])),
                                'job_url': f"https://remoteok.io/remote-jobs/{job_data.get('id', '')}",
                                'source': 'RemoteOK',
                                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if len(job['description']) > 50:  # Only jobs with real descriptions
                                jobs.append(job)
                                logger.info(f"Added verified RemoteOK job: {job['title']} at {job['company']}")
        
        except Exception as e:
            logger.error(f"RemoteOK error: {e}")
        
        return jobs[:limit]

    def scrape_greenhouse_verified(self, limit=50):
        """Scrape only companies we know have working Greenhouse APIs"""
        jobs = []
        
        # Only companies we've verified have working public APIs
        verified_companies = ['stripe', 'airbnb', 'shopify']
        
        for company in verified_companies:
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    company_jobs = data.get('jobs', [])
                    
                    for job_data in company_jobs[:limit//len(verified_companies)]:
                        job = {
                            'title': job_data.get('title', 'Software Engineer'),
                            'company': company.title(),
                            'location': self.extract_location(job_data.get('location')),
                            'description': self.clean_description(job_data.get('content', '')),
                            'department': self.extract_department_greenhouse(job_data.get('departments')),
                            'job_url': job_data.get('absolute_url', ''),
                            'source': f'{company.title()} Careers (Greenhouse)',
                            'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        if len(job['description']) > 100:  # Only substantial job descriptions
                            jobs.append(job)
                            logger.info(f"Added verified Greenhouse job: {job['title']} at {job['company']}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error scraping {company} from Greenhouse: {e}")
                continue
        
        return jobs[:limit]

    def scrape_lever_verified(self, limit=25):
        """Scrape only verified Lever companies"""
        jobs = []
        
        # Only companies with confirmed working APIs
        verified_companies = ['netflix', 'uber']
        
        for company in verified_companies:
            try:
                url = f"https://api.lever.co/v0/postings/{company}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200 and response.text.strip():
                    company_jobs = response.json()
                    
                    if isinstance(company_jobs, list):
                        for job_data in company_jobs[:limit//len(verified_companies)]:
                            job = {
                                'title': job_data.get('text', 'Software Engineer'),
                                'company': company.title(),
                                'location': self.extract_lever_location(job_data.get('categories')),
                                'description': self.clean_description(job_data.get('description', '')),
                                'department': self.extract_lever_department(job_data.get('categories')),
                                'job_url': job_data.get('applyUrl', ''),
                                'source': f'{company.title()} Careers (Lever)',
                                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if len(job['description']) > 100:
                                jobs.append(job)
                                logger.info(f"Added verified Lever job: {job['title']} at {job['company']}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error scraping {company} from Lever: {e}")
                continue
        
        return jobs[:limit]

    def is_real_tech_job(self, job_data):
        """Verify this is actually a tech job"""
        tech_keywords = [
            'engineer', 'developer', 'programmer', 'software', 'backend', 'frontend',
            'fullstack', 'python', 'javascript', 'react', 'node', 'data', 'ai', 'ml',
            'devops', 'security', 'mobile', 'ios', 'android', 'cloud', 'architect'
        ]
        
        title = str(job_data.get('position', '')).lower()
        tags = str(job_data.get('tags', [])).lower()
        
        return any(keyword in title or keyword in tags for keyword in tech_keywords)

    def clean_description(self, description):
        """Clean and validate job description"""
        if not description:
            return "Job details available on company website"
        
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', str(description))
        description = re.sub(r'\n\s*\n', '\n\n', description)
        description = description.strip()
        
        # Ensure minimum quality
        if len(description) < 50:
            return "Job details available on company website"
        
        return description[:2000]  # Limit length

    def extract_location(self, location_data):
        """Extract location from various formats"""
        if isinstance(location_data, dict):
            return location_data.get('name', 'Not specified')
        elif isinstance(location_data, str):
            return location_data
        return 'Not specified'

    def extract_department_greenhouse(self, departments):
        """Extract department from Greenhouse format"""
        if departments and isinstance(departments, list) and len(departments) > 0:
            return departments[0].get('name', 'Engineering')
        return 'Engineering'

    def extract_lever_location(self, categories):
        """Extract location from Lever categories"""
        if categories and isinstance(categories, dict):
            return categories.get('location', 'Not specified')
        return 'Not specified'

    def extract_lever_department(self, categories):
        """Extract department from Lever categories"""
        if categories and isinstance(categories, dict):
            return categories.get('team', 'Engineering')
        return 'Engineering'

    def extract_department_from_tags(self, tags):
        """Extract department from job tags"""
        if not tags:
            return 'Engineering'
        
        dept_mapping = {
            'engineering': 'Engineering',
            'data': 'Data Science',
            'design': 'Design',
            'product': 'Product',
            'marketing': 'Marketing',
            'sales': 'Sales'
        }
        
        tags_str = str(tags).lower()
        for key, dept in dept_mapping.items():
            if key in tags_str:
                return dept
        
        return 'Engineering'

def scrape_all_real_jobs(limit_per_source=50):
    """Main function to scrape only verified real job sources"""
    scraper = RealJobsOnlyScaper()
    all_jobs = []
    
    logger.info("Starting REAL JOBS ONLY scraping...")
    
    # Source 1: RemoteOK (verified working)
    logger.info("Scraping RemoteOK...")
    remote_jobs = scraper.scrape_remoteok_verified(limit_per_source)
    all_jobs.extend(remote_jobs)
    logger.info(f"Collected {len(remote_jobs)} verified RemoteOK jobs")
    
    # Source 2: Greenhouse (verified companies only)
    logger.info("Scraping verified Greenhouse companies...")
    greenhouse_jobs = scraper.scrape_greenhouse_verified(limit_per_source)
    all_jobs.extend(greenhouse_jobs)
    logger.info(f"Collected {len(greenhouse_jobs)} verified Greenhouse jobs")
    
    # Source 3: Lever (verified companies only)  
    logger.info("Scraping verified Lever companies...")
    lever_jobs = scraper.scrape_lever_verified(limit_per_source)
    all_jobs.extend(lever_jobs)
    logger.info(f"Collected {len(lever_jobs)} verified Lever jobs")
    
    logger.info(f"Total REAL jobs collected: {len(all_jobs)}")
    return all_jobs

if __name__ == "__main__":
    jobs = scrape_all_real_jobs(100)
    
    # Save to file  
    with open('/Users/veersawhney/Downloads/Foqal Internship ML Project/scraped_jobs.json', 'w') as f:
        json.dump(jobs, f, indent=2)
    
    logger.info(f"Saved {len(jobs)} REAL jobs to scraped_jobs.json")