#!/usr/bin/env python3
"""
Real Job Scraper - Gets actual job postings with detailed descriptions
Uses multiple sources including public APIs and well-structured job sites
"""

import requests
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
import json
import re
from urllib.parse import urljoin, quote

logger = logging.getLogger(__name__)

class RealJobScraper:
    def __init__(self, delay_range=(2, 4)):
        self.delay_range = delay_range
        self.session = requests.Session()
        
        # Set realistic headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })

    def rate_limit(self):
        """Rate limiting between requests"""
        delay = random.uniform(*self.delay_range)
        logger.info(f"Rate limiting: waiting {delay:.2f} seconds")
        time.sleep(delay)

    def scrape_hacker_news_who_is_hiring(self, limit=50):
        """Scrape HN Who's Hiring threads for real job postings"""
        jobs = []
        try:
            # Get latest Who's Hiring thread
            hn_api_url = "https://hacker-news.firebaseio.com/v0/item/38655066.json"  # Recent thread
            response = self.session.get(hn_api_url)
            response.raise_for_status()
            
            thread_data = response.json()
            if not thread_data or 'kids' not in thread_data:
                logger.warning("No comments found in HN thread")
                return jobs
            
            # Get comment IDs (job postings)
            comment_ids = thread_data['kids'][:limit]  # Limit to avoid too many requests
            
            for i, comment_id in enumerate(comment_ids[:limit]):
                try:
                    # Get individual comment
                    comment_url = f"https://hacker-news.firebaseio.com/v0/item/{comment_id}.json"
                    response = self.session.get(comment_url)
                    response.raise_for_status()
                    
                    comment_data = response.json()
                    if not comment_data or 'text' not in comment_data:
                        continue
                    
                    # Parse job posting from comment text
                    job = self.parse_hn_job_post(comment_data['text'])
                    if job:
                        job.update({
                            'job_url': f"https://news.ycombinator.com/item?id={comment_id}",
                            'source': 'Hacker News Who\'s Hiring',
                            'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        jobs.append(job)
                        logger.info(f"Scraped HN job: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                    
                    # Rate limit between API calls
                    if i % 5 == 0:  # Every 5 requests
                        time.sleep(1)
                        
                except Exception as e:
                    logger.warning(f"Error processing HN comment {comment_id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping HN jobs: {e}")
        
        return jobs

    def parse_hn_job_post(self, text_html):
        """Parse job details from HN comment HTML"""
        try:
            # Remove HTML tags and decode
            soup = BeautifulSoup(text_html, 'html.parser')
            text = soup.get_text()
            
            # Extract company name (usually first line or after specific patterns)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if not lines:
                return None
            
            company = None
            title = None
            location = "Remote/Not specified"
            description = text
            
            # Common patterns for company extraction
            first_line = lines[0]
            
            # Pattern: "Company Name | Job Title | Location"
            if '|' in first_line:
                parts = [p.strip() for p in first_line.split('|')]
                if len(parts) >= 2:
                    company = parts[0]
                    title = parts[1]
                    if len(parts) >= 3:
                        location = parts[2]
            
            # Pattern: "Company Name - Job Title"
            elif ' - ' in first_line and len(first_line) < 100:
                parts = first_line.split(' - ', 1)
                company = parts[0].strip()
                title = parts[1].strip() if len(parts) > 1 else "Software Engineer"
            
            # Pattern: just company name in first line
            elif len(first_line) < 50 and any(word in first_line.lower() for word in ['inc', 'llc', 'corp', 'ltd', 'technologies', 'tech', 'labs', 'systems']):
                company = first_line
                title = "Software Engineer"  # Default
            
            # Fallback: extract from text patterns
            if not company:
                # Look for "at Company" pattern
                at_match = re.search(r'\bat\s+([A-Z][a-zA-Z\s&]+?)(?:\s|$)', text)
                if at_match:
                    company = at_match.group(1).strip()
                else:
                    company = "Tech Company"  # Fallback
            
            if not title:
                # Look for common job titles
                title_patterns = [
                    r'(senior|sr\.?)\s+(software|backend|frontend|full\s*stack)\s+engineer',
                    r'(software|backend|frontend|full\s*stack)\s+engineer',
                    r'(senior|sr\.?)\s+developer',
                    r'(python|javascript|react|node\.?js)\s+developer',
                    r'(machine learning|ml|ai)\s+engineer',
                    r'data\s+scientist',
                    r'devops\s+engineer',
                    r'product\s+manager',
                    r'engineering\s+manager'
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, text.lower())
                    if match:
                        title = match.group(0).title()
                        break
                
                if not title:
                    title = "Software Engineer"
            
            # Extract location if not found
            if location == "Remote/Not specified":
                location_patterns = [
                    r'(san francisco|sf|bay area|silicon valley)',
                    r'(new york|nyc|ny)',
                    r'(los angeles|la)',
                    r'(seattle|wa)',
                    r'(austin|tx)',
                    r'(boston|ma)',
                    r'(chicago|il)',
                    r'(remote|distributed|anywhere)',
                    r'(london|uk)',
                    r'(berlin|germany)',
                    r'(toronto|canada)'
                ]
                
                for pattern in location_patterns:
                    if re.search(pattern, text.lower()):
                        location = pattern.replace('(', '').replace(')', '').replace('|', '/').title()
                        break
            
            # Only return if we have meaningful content
            if len(description) > 100 and company and title:
                return {
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description[:2000],  # Limit description length
                    'department': self.extract_department(description)
                }
            
        except Exception as e:
            logger.warning(f"Error parsing HN job post: {e}")
        
        return None

    def scrape_remote_ok(self, limit=50):
        """Scrape RemoteOK for remote job postings"""
        jobs = []
        try:
            url = "https://remoteok.io/api"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                return jobs
            
            # Skip first item (it's usually metadata)
            job_posts = data[1:limit+1] if len(data) > 1 else data
            
            for job_data in job_posts:
                try:
                    # Filter for AI/ML/Software engineering jobs
                    if not self.is_relevant_job(job_data):
                        continue
                    
                    job = {
                        'title': job_data.get('position', 'Software Engineer'),
                        'company': job_data.get('company', 'Remote Company'),
                        'location': 'Remote',
                        'description': self.clean_description(job_data.get('description', '')),
                        'department': job_data.get('tags', [None])[0] if job_data.get('tags') else None,
                        'job_url': f"https://remoteok.io/remote-jobs/{job_data.get('id', '')}",
                        'source': 'RemoteOK',
                        'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Only add if description is substantial
                    if len(job['description']) > 100:
                        jobs.append(job)
                        logger.info(f"Scraped RemoteOK job: {job['title']} at {job['company']}")
                    
                except Exception as e:
                    logger.warning(f"Error processing RemoteOK job: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")
        
        return jobs

    def scrape_company_career_pages(self, limit=50):
        """Scrape real jobs from company career pages"""
        jobs = []
        
        # Real company career page URLs that typically have job listings
        career_sites = [
            {
                'company': 'Y Combinator', 
                'url': 'https://www.ycombinator.com/jobs',
                'selector': '.job-listing'
            },
            {
                'company': 'AngelList',
                'url': 'https://wellfound.com/jobs',
                'selector': '.job-card'
            }
        ]
        
        try:
            # First, try to get jobs from job aggregators/APIs
            jobs.extend(self.scrape_greenhouse_api(limit // 4))
            jobs.extend(self.scrape_lever_api(limit // 4))
            jobs.extend(self.scrape_workable_api(limit // 4))
            jobs.extend(self.scrape_bamboohr_api(limit // 4))
            
        except Exception as e:
            logger.error(f"Error with career page scraping: {e}")
        
        return jobs[:limit]

    def scrape_greenhouse_api(self, limit=25):
        """Scrape jobs from companies using Greenhouse ATS"""
        jobs = []
        try:
            # Companies using Greenhouse - their APIs are publicly accessible
            greenhouse_companies = [
                'airbnb', 'stripe', 'shopify', 'coinbase', 'databricks', 
                'figma', 'notion', 'linear', 'anthropic', 'openai'
            ]
            
            for company in greenhouse_companies[:min(10, len(greenhouse_companies))]:
                try:
                    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        company_jobs = data.get('jobs', [])
                        
                        for job_data in company_jobs[:5]:  # Limit per company
                            job = {
                                'title': job_data.get('title', 'Software Engineer'),
                                'company': company.title(),
                                'location': job_data.get('location', {}).get('name', 'Not specified'),
                                'description': self.clean_description(job_data.get('content', '')),
                                'department': job_data.get('departments', [{}])[0].get('name') if job_data.get('departments') else None,
                                'job_url': job_data.get('absolute_url', ''),
                                'source': f'{company.title()} Careers',
                                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if len(job['description']) > 100:
                                jobs.append(job)
                                logger.info(f"Scraped Greenhouse job: {job['title']} at {job['company']}")
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error scraping {company} from Greenhouse: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error with Greenhouse API: {e}")
        
        return jobs[:limit]

    def scrape_lever_api(self, limit=25):
        """Scrape jobs from companies using Lever ATS"""
        jobs = []
        try:
            # Companies using Lever - their APIs are publicly accessible
            lever_companies = [
                'netflix', 'uber', 'twitch', 'robinhood', 'discord', 
                'plaid', 'scale', 'vercel', 'supabase', 'planetscale'
            ]
            
            for company in lever_companies[:min(10, len(lever_companies))]:
                try:
                    url = f"https://api.lever.co/v0/postings/{company}"
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        company_jobs = response.json()
                        
                        for job_data in company_jobs[:5]:  # Limit per company
                            job = {
                                'title': job_data.get('text', 'Software Engineer'),
                                'company': company.title(),
                                'location': job_data.get('categories', {}).get('location', 'Not specified'),
                                'description': self.clean_description(job_data.get('description', '')),
                                'department': job_data.get('categories', {}).get('team') if job_data.get('categories') else None,
                                'job_url': job_data.get('applyUrl', ''),
                                'source': f'{company.title()} Careers',
                                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if len(job['description']) > 100:
                                jobs.append(job)
                                logger.info(f"Scraped Lever job: {job['title']} at {job['company']}")
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error scraping {company} from Lever: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error with Lever API: {e}")
        
        return jobs[:limit]

    def scrape_workable_api(self, limit=25):
        """Scrape jobs from companies using Workable ATS"""
        jobs = []
        try:
            # Companies using Workable - some have public APIs
            workable_companies = [
                'revolut', 'transferwise', 'typeform', 'hotjar', 'contentful'
            ]
            
            for company in workable_companies[:min(5, len(workable_companies))]:
                try:
                    url = f"https://apply.workable.com/api/v3/accounts/{company}/jobs"
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        company_jobs = data.get('results', [])
                        
                        for job_data in company_jobs[:5]:  # Limit per company
                            job = {
                                'title': job_data.get('title', 'Software Engineer'),
                                'company': company.title(),
                                'location': job_data.get('location', {}).get('city', 'Not specified'),
                                'description': self.clean_description(job_data.get('description', '')),
                                'department': job_data.get('department') if job_data.get('department') else None,
                                'job_url': job_data.get('url', ''),
                                'source': f'{company.title()} Careers',
                                'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if len(job['description']) > 100:
                                jobs.append(job)
                                logger.info(f"Scraped Workable job: {job['title']} at {job['company']}")
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error scraping {company} from Workable: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error with Workable API: {e}")
        
        return jobs[:limit]

    def scrape_bamboohr_api(self, limit=25):
        """Only scrape from verified real job APIs - no fake data"""
        jobs = []
        try:
            # Only use real job board APIs that provide actual job postings
            # We'll focus on RemoteOK which we know works with real data
            pass  # Removed all fake job generation
            
        except Exception as e:
            logger.error(f"Error with job board APIs: {e}")
        
        return jobs[:limit]

    def scrape_indeed_jobs(self, limit=50):
        """Scrape jobs from Indeed"""
        jobs = []
        try:
            # Indeed search URLs for software engineering jobs
            search_terms = ['software+engineer', 'python+developer', 'javascript+developer', 'data+scientist', 'machine+learning']
            
            for term in search_terms[:3]:  # Limit to avoid rate limiting
                try:
                    url = f"https://www.indeed.com/jobs?q={term}&l=&sort=date&limit=50"
                    response = self.session.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for job cards (Indeed's structure)
                        job_cards = soup.find_all('div', {'data-jk': True}) or soup.find_all('a', {'data-jk': True})
                        
                        for job_card in job_cards[:limit//len(search_terms)]:
                            try:
                                # Extract job details
                                title_elem = job_card.find('span', {'title': True}) or job_card.find('h2')
                                company_elem = job_card.find('span', class_='companyName') or job_card.find('a', {'data-testid': 'company-name'})
                                location_elem = job_card.find('div', {'data-testid': 'job-location'})
                                
                                title = title_elem.get('title') or title_elem.get_text() if title_elem else f"{term.replace('+', ' ').title()}"
                                company = company_elem.get_text().strip() if company_elem else "Tech Company"
                                location = location_elem.get_text().strip() if location_elem else "Not specified"
                                
                                job_id = job_card.get('data-jk', '')
                                job_url = f"https://www.indeed.com/viewjob?jk={job_id}" if job_id else ""
                                
                                job = {
                                    'title': title[:100],  # Truncate long titles
                                    'company': company[:50],
                                    'location': location[:50],
                                    'description': f"Real job posting from Indeed for {title} at {company}. Full details available on Indeed.",
                                    'department': 'Engineering',
                                    'job_url': job_url,
                                    'source': 'Indeed',
                                    'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                                }
                                
                                jobs.append(job)
                                logger.info(f"Scraped Indeed job: {job['title']} at {job['company']}")
                                
                            except Exception as e:
                                logger.warning(f"Error parsing Indeed job card: {e}")
                                continue
                    
                    time.sleep(2)  # Rate limiting for Indeed
                    
                except Exception as e:
                    logger.warning(f"Error scraping Indeed for term {term}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
        
        return jobs[:limit]

    def scrape_stackoverflow_jobs(self, limit=25):
        """Scrape jobs from Stack Overflow Jobs"""
        jobs = []
        try:
            # Stack Overflow has discontinued their job board, but let's try other tech job boards
            # Let's scrape from Dice.com instead
            url = "https://www.dice.com/jobs?q=software+engineer&location=&radius=30&radiusUnit=mi&page=1&pageSize=100"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job cards on Dice
                job_cards = soup.find_all('div', class_='search-result') or soup.find_all('article', class_='card')
                
                for job_card in job_cards[:limit]:
                    try:
                        # Extract job details from Dice
                        title_elem = job_card.find('a', class_='card-title-link') or job_card.find('h5')
                        company_elem = job_card.find('a', class_='card-company') or job_card.find('span', class_='company')
                        location_elem = job_card.find('span', class_='location')
                        
                        title = title_elem.get_text().strip() if title_elem else "Software Engineer"
                        company = company_elem.get_text().strip() if company_elem else "Tech Company"
                        location = location_elem.get_text().strip() if location_elem else "Not specified"
                        
                        job_url = title_elem.get('href', '') if title_elem and title_elem.get('href') else ""
                        if job_url and not job_url.startswith('http'):
                            job_url = "https://www.dice.com" + job_url
                        
                        job = {
                            'title': title[:100],
                            'company': company[:50],
                            'location': location[:50],
                            'description': f"Real job posting from Dice.com for {title} at {company}. Full details available on Dice.",
                            'department': 'Engineering',
                            'job_url': job_url,
                            'source': 'Dice.com',
                            'scraped_date': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        jobs.append(job)
                        logger.info(f"Scraped Dice job: {job['title']} at {job['company']}")
                        
                    except Exception as e:
                        logger.warning(f"Error parsing Dice job card: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error scraping Dice: {e}")
        
        return jobs[:limit]


    def is_relevant_job(self, job_data):
        """Check if job is relevant to our analysis (tech/AI/ML focused)"""
        relevant_keywords = [
            'engineer', 'developer', 'programmer', 'architect', 'scientist',
            'python', 'javascript', 'react', 'node', 'aws', 'ai', 'ml',
            'machine learning', 'data', 'software', 'backend', 'frontend',
            'full stack', 'devops', 'cloud', 'api'
        ]
        
        title = job_data.get('position', '').lower()
        tags = job_data.get('tags', [])
        company = job_data.get('company', '').lower()
        
        # Check title
        if any(keyword in title for keyword in relevant_keywords):
            return True
        
        # Check tags
        if tags and any(keyword in str(tags).lower() for keyword in relevant_keywords):
            return True
        
        return False

    def clean_description(self, description):
        """Clean and format job description"""
        if not description:
            return ""
        
        # Remove HTML tags
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text()
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        text = text.strip()
        
        return text

    def extract_department(self, description):
        """Extract department/team from job description"""
        department_patterns = {
            'Engineering': ['engineering', 'software', 'backend', 'frontend', 'devops'],
            'Data Science': ['data science', 'machine learning', 'ai', 'analytics'],
            'Product': ['product manager', 'product', 'pm'],
            'Design': ['designer', 'ux', 'ui', 'design'],
            'Marketing': ['marketing', 'growth', 'content'],
            'Sales': ['sales', 'business development', 'account']
        }
        
        description_lower = description.lower()
        
        for dept, keywords in department_patterns.items():
            if any(keyword in description_lower for keyword in keywords):
                return dept
        
        return None

    def scrape_all_sources(self, limit_per_source=10):
        """Scrape from all available sources"""
        all_jobs = []
        
        logger.info("Starting real job scraping from multiple sources...")
        
        # Source 1: Hacker News Who's Hiring
        logger.info("Scraping Hacker News Who's Hiring...")
        hn_jobs = self.scrape_hacker_news_who_is_hiring(limit_per_source)
        all_jobs.extend(hn_jobs)
        logger.info(f"Collected {len(hn_jobs)} jobs from Hacker News")
        
        self.rate_limit()
        
        # Source 2: RemoteOK
        logger.info("Scraping RemoteOK...")
        remote_jobs = self.scrape_remote_ok(limit_per_source)
        all_jobs.extend(remote_jobs)
        logger.info(f"Collected {len(remote_jobs)} jobs from RemoteOK")
        
        self.rate_limit()
        
        # Source 3: Career page APIs (real job postings)
        logger.info("Collecting from career page APIs...")
        api_jobs = self.scrape_company_career_pages(limit_per_source)
        all_jobs.extend(api_jobs)
        logger.info(f"Collected {len(api_jobs)} jobs from career APIs")
        
        self.rate_limit()
        
        # Source 4: Indeed job scraping
        logger.info("Collecting from Indeed...")
        indeed_jobs = self.scrape_indeed_jobs(limit_per_source)
        all_jobs.extend(indeed_jobs)
        logger.info(f"Collected {len(indeed_jobs)} jobs from Indeed")
        
        self.rate_limit()
        
        # Source 5: Stack Overflow Jobs
        logger.info("Collecting from Stack Overflow...")
        so_jobs = self.scrape_stackoverflow_jobs(limit_per_source)
        all_jobs.extend(so_jobs)
        logger.info(f"Collected {len(so_jobs)} jobs from Stack Overflow")
        
        logger.info(f"Total jobs collected: {len(all_jobs)}")
        return all_jobs

def scrape_real_jobs(limit_per_source=150):
    """Main function to scrape real job postings"""
    scraper = RealJobScraper()
    jobs = scraper.scrape_all_sources(limit_per_source)
    
    # Filter jobs to ensure quality
    quality_jobs = []
    for job in jobs:
        if (job.get('description') and len(job['description']) > 200 and 
            job.get('title') and job.get('company')):
            quality_jobs.append(job)
    
    return quality_jobs