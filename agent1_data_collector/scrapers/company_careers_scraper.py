#!/usr/bin/env python3
"""
Company Career Pages Scraper
Scrapes job postings directly from company career pages
"""

import requests
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

class CompanyCareerscraper:
    def __init__(self, proxy_list=None, delay_range=(1, 3)):
        self.proxy_list = proxy_list or []
        self.delay_range = delay_range
        self.session = requests.Session()
        
        # Set headers to mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        # Common career page patterns
        self.career_patterns = [
            '/careers',
            '/jobs',
            '/career',
            '/work-with-us',
            '/join-us',
            '/opportunities',
            '/open-positions'
        ]
        
        # Tech companies to scrape (focusing on AI/ML companies)
        self.target_companies = {
            'openai.com': '/careers',
            'anthropic.com': '/careers',
            'scale.ai': '/careers',
            'huggingface.co': '/careers',
            'databricks.com': '/company/careers',
            'snowflake.com': '/careers',
            'palantir.com': '/careers',
            'nvidia.com': '/careers',
            'microsoft.com': '/careers',
            'google.com': '/careers',
            'meta.com': '/careers',
            'apple.com': '/careers',
            'amazon.com': '/careers',
            'netflix.com': '/jobs',
            'uber.com': '/careers',
            'airbnb.com': '/careers',
            'stripe.com': '/careers',
            'shopify.com': '/careers'
        }
    
    def get_proxy(self):
        """Get random proxy from proxy list"""
        if self.proxy_list:
            return random.choice(self.proxy_list)
        return None
    
    def rate_limit(self):
        """Implement rate limiting"""
        delay = random.uniform(*self.delay_range)
        logger.info(f"Career page rate limiting: waiting {delay:.2f} seconds")
        time.sleep(delay)
    
    def scrape_all_companies(self, limit_per_company=5):
        """Scrape jobs from all target companies"""
        all_jobs = []
        
        for company_domain, career_path in self.target_companies.items():
            try:
                logger.info(f"Scraping {company_domain}")
                jobs = self.scrape_company_careers(company_domain, career_path, limit_per_company)
                all_jobs.extend(jobs)
                
                # Rate limit between companies
                self.rate_limit()
                
            except Exception as e:
                logger.warning(f"Error scraping {company_domain}: {e}")
                continue
        
        return all_jobs
    
    def scrape_company_careers(self, company_domain, career_path, limit=5):
        """Scrape jobs from a specific company's career page"""
        jobs = []
        career_url = f"https://{company_domain}{career_path}"
        
        try:
            # Use proxy if available
            proxy = self.get_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            logger.info(f"Accessing {career_url}")
            response = self.session.get(career_url, proxies=proxies, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract company name from domain
            company_name = company_domain.split('.')[0].title()
            
            # Find job listings using multiple strategies
            job_elements = self.find_job_elements(soup)
            
            logger.info(f"Found {len(job_elements)} potential job elements at {company_name}")
            
            for element in job_elements[:limit]:
                try:
                    job_data = self.extract_job_from_element(element, company_name, career_url)
                    if job_data and self.is_ai_ml_related(job_data):
                        jobs.append(job_data)
                        
                except Exception as e:
                    logger.warning(f"Error extracting job from element: {e}")
                    continue
            
            # If no jobs found with standard approach, try alternative methods
            if not jobs:
                jobs = self.try_alternative_extraction(soup, company_name, career_url, limit)
            
        except Exception as e:
            logger.error(f"Error scraping {career_url}: {e}")
        
        return jobs
    
    def find_job_elements(self, soup):
        """Find job listing elements using common patterns"""
        job_elements = []
        
        # Common job listing selectors
        selectors = [
            '[data-job-id]',
            '.job-item',
            '.job-listing',
            '.position',
            '.role',
            '.opportunity',
            '.career-item',
            'li[class*="job"]',
            'div[class*="job"]',
            'a[href*="job"]',
            'a[href*="position"]',
            'a[href*="career"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                job_elements.extend(elements)
                break  # Use first successful selector
        
        # If no specific job elements found, look for links with job-related keywords
        if not job_elements:
            job_keywords = ['engineer', 'scientist', 'developer', 'analyst', 'ai', 'ml', 'machine learning', 'data']
            links = soup.find_all('a', href=True)
            
            for link in links:
                text = link.get_text().lower()
                if any(keyword in text for keyword in job_keywords):
                    job_elements.append(link)
        
        return job_elements
    
    def extract_job_from_element(self, element, company_name, base_url):
        """Extract job data from a job element"""
        try:
            # Title
            title = self.extract_title(element)
            
            # Description (if available on listing page)
            description = self.extract_description(element)
            
            # Job URL
            job_url = self.extract_job_url(element, base_url)
            
            # Location
            location = self.extract_location(element)
            
            # Department/Category
            department = self.extract_department(element)
            
            job_data = {
                'title': title,
                'company': company_name,
                'location': location or 'Not specified',
                'description': description,
                'department': department,
                'job_url': job_url,
                'source': f'{company_name} Careers',
                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return job_data if title else None
            
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
    def extract_title(self, element):
        """Extract job title from element"""
        # Try various title selectors
        title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.job-title', '.position-title']
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                return title_elem.get_text(strip=True)
        
        # Fallback to element text if it's a link
        if element.name == 'a':
            return element.get_text(strip=True)
        
        return None
    
    def extract_description(self, element):
        """Extract job description from element"""
        desc_selectors = ['.description', '.summary', '.excerpt', 'p']
        
        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                return desc_elem.get_text(strip=True)
        
        return ""
    
    def extract_job_url(self, element, base_url):
        """Extract job URL from element"""
        if element.name == 'a' and element.get('href'):
            href = element['href']
            return urljoin(base_url, href)
        
        link = element.find('a', href=True)
        if link:
            return urljoin(base_url, link['href'])
        
        return base_url
    
    def extract_location(self, element):
        """Extract location from element"""
        location_selectors = ['.location', '.city', '.office', '[class*="location"]']
        
        for selector in location_selectors:
            loc_elem = element.select_one(selector)
            if loc_elem:
                return loc_elem.get_text(strip=True)
        
        return None
    
    def extract_department(self, element):
        """Extract department/category from element"""
        dept_selectors = ['.department', '.category', '.team', '[class*="dept"]']
        
        for selector in dept_selectors:
            dept_elem = element.select_one(selector)
            if dept_elem:
                return dept_elem.get_text(strip=True)
        
        return None
    
    def is_ai_ml_related(self, job_data):
        """Check if job is AI/ML related"""
        ai_ml_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'data scientist',
            'data engineer', 'nlp', 'computer vision', 'deep learning', 'neural',
            'tensorflow', 'pytorch', 'python', 'data analyst', 'research scientist',
            'software engineer', 'backend', 'frontend', 'full stack', 'devops'
        ]
        
        text_to_check = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
        
        return any(keyword in text_to_check for keyword in ai_ml_keywords)
    
    def try_alternative_extraction(self, soup, company_name, base_url, limit):
        """Try alternative extraction methods if standard approach fails"""
        jobs = []
        
        try:
            # Look for any links that might be job-related
            links = soup.find_all('a', href=True)
            job_links = []
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Filter for job-related links
                if (any(word in href.lower() for word in ['job', 'position', 'career', 'role']) or
                    any(word in text.lower() for word in ['engineer', 'scientist', 'developer', 'analyst'])):
                    job_links.append(link)
            
            for link in job_links[:limit]:
                title = link.get_text(strip=True)
                job_url = urljoin(base_url, link['href'])
                
                if title and len(title) > 5:  # Reasonable title length
                    job_data = {
                        'title': title,
                        'company': company_name,
                        'location': 'Not specified',
                        'description': 'See job page for details',
                        'job_url': job_url,
                        'source': f'{company_name} Careers',
                        'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    if self.is_ai_ml_related(job_data):
                        jobs.append(job_data)
        
        except Exception as e:
            logger.warning(f"Alternative extraction failed: {e}")
        
        return jobs

def scrape_company_careers(company_list=None, limit_per_company=5, proxy_list=None):
    """Convenience function to scrape company career pages"""
    scraper = CompanyCareerscraper(proxy_list=proxy_list)
    
    if company_list:
        # Custom company list
        jobs = []
        for company_info in company_list:
            if isinstance(company_info, dict):
                domain = company_info['domain']
                path = company_info.get('path', '/careers')
            else:
                domain = company_info
                path = '/careers'
            
            company_jobs = scraper.scrape_company_careers(domain, path, limit_per_company)
            jobs.extend(company_jobs)
    else:
        # Use default company list
        jobs = scraper.scrape_all_companies(limit_per_company)
    
    return jobs