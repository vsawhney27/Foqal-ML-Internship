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
        
        # Enhanced job listing selectors
        selectors = [
            # Data attributes
            '[data-job-id]', '[data-position-id]', '[data-role-id]',
            
            # Common class patterns
            '.job-item', '.job-listing', '.job-card', '.job-post',
            '.position', '.position-item', '.position-card',
            '.role', '.role-item', '.role-card',
            '.opportunity', '.career-item', '.career-post',
            
            # Generic patterns
            'li[class*="job"]', 'div[class*="job"]', 'article[class*="job"]',
            'li[class*="position"]', 'div[class*="position"]',
            'li[class*="role"]', 'div[class*="role"]',
            'li[class*="career"]', 'div[class*="career"]',
            
            # Link patterns
            'a[href*="job"]', 'a[href*="jobs"]',
            'a[href*="position"]', 'a[href*="positions"]',
            'a[href*="career"]', 'a[href*="careers"]',
            'a[href*="role"]', 'a[href*="roles"]',
            'a[href*="opening"]', 'a[href*="opportunity"]'
        ]
        
        # Try each selector and collect all matches
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    job_elements.extend(elements)
            except Exception:
                continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_elements = []
        for elem in job_elements:
            elem_id = id(elem)
            if elem_id not in seen:
                seen.add(elem_id)
                unique_elements.append(elem)
        
        job_elements = unique_elements
        
        # If still no specific job elements found, look for links with job-related keywords
        if not job_elements:
            job_keywords = [
                'engineer', 'scientist', 'developer', 'analyst', 
                'ai', 'ml', 'machine learning', 'data',
                'software', 'python', 'backend', 'frontend',
                'senior', 'junior', 'lead', 'principal',
                'manager', 'director', 'architect'
            ]
            links = soup.find_all('a', href=True)
            
            for link in links:
                text = link.get_text().lower()
                href = link.get('href', '').lower()
                
                # Check both text and href for job-related terms
                if (any(keyword in text for keyword in job_keywords) or
                    any(term in href for term in ['job', 'position', 'career', 'role'])):
                    job_elements.append(link)
        
        logger.info(f"Found {len(job_elements)} potential job elements")
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
            
            # If no description found on listing page, try to fetch from job page
            if not description or description == "" or len(description) < 50:
                if job_url and job_url != base_url:
                    description = self.extract_job_page_content(job_url)
            
            # Location
            location = self.extract_location(element)
            
            # Department/Category
            department = self.extract_department(element)
            
            job_data = {
                'title': title,
                'company': company_name,
                'location': location or 'Not specified',
                'description': description or 'Job details available on company website',
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
    
    def extract_job_page_content(self, job_url):
        """Extract detailed content from individual job page"""
        try:
            # Add rate limiting for individual job page requests
            time.sleep(random.uniform(0.5, 1.5))
            
            proxy = self.get_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            logger.info(f"Fetching job details from: {job_url}")
            response = self.session.get(job_url, proxies=proxies, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple content extraction strategies
            content_strategies = [
                # Strategy 1: Look for job description containers
                lambda s: s.find('div', {'class': re.compile(r'.*description.*', re.I)}),
                lambda s: s.find('div', {'id': re.compile(r'.*description.*', re.I)}),
                lambda s: s.find('section', {'class': re.compile(r'.*description.*', re.I)}),
                
                # Strategy 2: Look for job content containers
                lambda s: s.find('div', {'class': re.compile(r'.*job-content.*', re.I)}),
                lambda s: s.find('div', {'class': re.compile(r'.*job-details.*', re.I)}),
                lambda s: s.find('div', {'class': re.compile(r'.*position-details.*', re.I)}),
                
                # Strategy 3: Look for main content areas
                lambda s: s.find('main'),
                lambda s: s.find('article'),
                lambda s: s.find('div', {'class': re.compile(r'.*content.*', re.I)}),
                
                # Strategy 4: Look for specific job posting elements
                lambda s: s.find('div', {'data-testid': re.compile(r'.*description.*', re.I)}),
                lambda s: s.find('div', {'role': 'main'}),
            ]
            
            description_text = ""
            
            for strategy in content_strategies:
                try:
                    container = strategy(soup)
                    if container:
                        # Extract text, preserving some structure
                        text = container.get_text(separator='\n', strip=True)
                        if text and len(text) > 100:  # Reasonable content length
                            description_text = text
                            break
                except:
                    continue
            
            # Fallback: get all paragraph text if nothing specific found
            if not description_text:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    text_parts = []
                    for p in paragraphs:
                        p_text = p.get_text(strip=True)
                        if len(p_text) > 20:  # Filter out short/empty paragraphs
                            text_parts.append(p_text)
                    
                    description_text = '\n'.join(text_parts)
            
            # Clean up the text
            if description_text:
                # Remove excessive whitespace
                description_text = re.sub(r'\n\s*\n', '\n\n', description_text)
                description_text = re.sub(r' +', ' ', description_text)
                description_text = description_text.strip()
                
                # Truncate if too long (keep first 2000 chars)
                if len(description_text) > 2000:
                    description_text = description_text[:2000] + "..."
                
                return description_text
            
            return "Job details available on company website"
            
        except Exception as e:
            logger.warning(f"Failed to extract content from {job_url}: {e}")
            return "See job page for details"
    
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
                
                # More specific filtering for actual job postings
                job_indicators_in_href = ['job/', '/job-', 'position/', '/position-', 'role/', '/role-', 'opening/', '/opening-']
                job_indicators_in_text = ['engineer', 'scientist', 'developer', 'analyst', 'manager', 'director', 'lead', 'senior', 'junior']
                
                # Must have specific job indicators and avoid generic career links
                if ((any(indicator in href.lower() for indicator in job_indicators_in_href) or
                     any(indicator in text.lower() for indicator in job_indicators_in_text)) and
                    len(text) > 5 and len(text) < 100 and  # Reasonable title length
                    not any(generic in text.lower() for generic in ['view all', 'see all', 'explore', 'learn more', 'careers', 'join us'])):
                    job_links.append(link)
            
            # Sort by title length to prioritize specific job titles
            job_links.sort(key=lambda x: len(x.get_text().strip()), reverse=True)
            
            for link in job_links[:limit]:
                title = link.get_text(strip=True)
                job_url = urljoin(base_url, link['href'])
                
                # Skip if URL is same as base URL or too generic
                if job_url == base_url or any(generic in job_url.lower() for generic in ['/careers', '/jobs', '/career']):
                    continue
                
                # Try to fetch the actual job page content
                description = self.extract_job_page_content(job_url)
                
                # Skip if description is too generic
                if any(generic in description.lower() for generic in ['careers', 'join us', 'view open roles', 'explore opportunities']):
                    continue
                
                job_data = {
                    'title': title,
                    'company': company_name,
                    'location': 'Not specified',
                    'description': description,
                    'job_url': job_url,
                    'source': f'{company_name} Careers',
                    'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if self.is_ai_ml_related(job_data) and len(description) > 200:  # Ensure substantial content
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