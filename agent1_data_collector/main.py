#!/usr/bin/env python3
"""
Agent 1: Multi-Source Data Collection Agent
Scrapes job postings from LinkedIn, Indeed, Glassdoor, AngelList, and company career pages
Implements rate limiting, proxy rotation, and data quality checks as required
"""

import json
import datetime
import os
import time
import argparse
import logging
from typing import List, Dict
from pymongo import MongoClient
from dotenv import load_dotenv
import ssl

# Import all scrapers
from scrapers.linkedin_scraper import scrape_linkedin_jobs
from scrapers.indeed_scraper import scrape_indeed_jobs
from scrapers.glassdoor_scraper import scrape_glassdoor_jobs
from scrapers.angellist_scraper import scrape_angellist_jobs
from scrapers.company_careers_scraper import scrape_company_careers
from scraper import scrape_page  # Original RemoteOK scraper
from proxy_manager import create_proxy_manager, create_rate_limiter
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiSourceJobCollector:
    def __init__(self, use_proxies=True, jobs_per_source=10):
        self.jobs_per_source = jobs_per_source
        self.proxy_manager = create_proxy_manager() if use_proxies else None
        self.rate_limiter = create_rate_limiter()
        self.all_jobs = []
        
        # Source configuration
        self.sources = {
            'remoteok': {'enabled': True, 'priority': 1},
            'indeed': {'enabled': True, 'priority': 2},
            'angellist': {'enabled': True, 'priority': 3},
            'glassdoor': {'enabled': True, 'priority': 4},
            'linkedin': {'enabled': True, 'priority': 5},
            'company_careers': {'enabled': True, 'priority': 6}
        }
    
    def collect_from_all_sources(self):
        """Collect jobs from all configured sources"""
        logger.info("Starting multi-source job collection...")
        logger.info(f"Target: {self.jobs_per_source} jobs per source")
        
        total_collected = 0
        
        # Sort sources by priority
        sorted_sources = sorted(self.sources.items(), key=lambda x: x[1]['priority'])
        
        for source_name, config in sorted_sources:
            if not config['enabled']:
                logger.info(f"Skipping {source_name} (disabled)")
                continue
            
            logger.info(f"\n{'='*50}")
            logger.info(f"COLLECTING FROM: {source_name.upper()}")
            logger.info(f"{'='*50}")
            
            try:
                # Rate limit before each source
                self.rate_limiter.wait_for_site(source_name)
                
                # Get proxy list for this source
                proxy_list = None
                if self.proxy_manager and self.proxy_manager.working_proxies:
                    proxy_list = self.proxy_manager.working_proxies
                
                # Collect from source
                jobs = self.collect_from_source(source_name, proxy_list)
                
                if jobs:
                    logger.info(f"✅ Collected {len(jobs)} jobs from {source_name}")
                    self.all_jobs.extend(jobs)
                    total_collected += len(jobs)
                else:
                    logger.warning(f"⚠️ No jobs collected from {source_name}")
                
            except Exception as e:
                logger.error(f"❌ Error collecting from {source_name}: {e}")
                continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"COLLECTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total jobs collected: {total_collected}")
        logger.info(f"Sources attempted: {len([s for s in self.sources.values() if s['enabled']])}")
        
        return self.all_jobs
    
    def collect_from_source(self, source_name, proxy_list=None):
        """Collect jobs from a specific source"""
        try:
            if source_name == 'remoteok':
                return self.collect_remoteok(proxy_list)
            elif source_name == 'indeed':
                return scrape_indeed_jobs(
                    query="AI machine learning",
                    location="remote",
                    limit=self.jobs_per_source,
                    proxy_list=proxy_list
                )
            elif source_name == 'linkedin':
                return scrape_linkedin_jobs(
                    keywords="artificial intelligence machine learning",
                    location="",
                    limit=self.jobs_per_source,
                    proxy_list=proxy_list
                )
            elif source_name == 'glassdoor':
                return scrape_glassdoor_jobs(
                    keyword="AI machine learning",
                    location="",
                    limit=self.jobs_per_source,
                    proxy_list=proxy_list
                )
            elif source_name == 'angellist':
                return scrape_angellist_jobs(
                    role="machine-learning-engineer",
                    location="",
                    limit=self.jobs_per_source,
                    proxy_list=proxy_list
                )
            elif source_name == 'company_careers':
                return scrape_company_careers(
                    limit_per_company=2,  # Lower limit since we scrape many companies
                    proxy_list=proxy_list
                )
            else:
                logger.warning(f"Unknown source: {source_name}")
                return []
                
        except Exception as e:
            logger.error(f"Error in {source_name} scraper: {e}")
            return []
    
    def collect_remoteok(self, proxy_list=None):
        """Collect from RemoteOK (original implementation)"""
        try:
            url = "https://remoteok.com/remote-ai-jobs"
            html = scrape_page(url)
            
            if html:
                jobs = self.extract_remoteok_jobs(html)
                return jobs[:self.jobs_per_source]
            
        except Exception as e:
            logger.error(f"Error collecting from RemoteOK: {e}")
        
        return []
    
    def extract_remoteok_jobs(self, html):
        """Extract jobs from RemoteOK HTML (from original implementation)"""
        soup = BeautifulSoup(html, "html.parser")
        job_cards = soup.find_all("tr", class_="job")
        jobs = []

        for idx, job in enumerate(job_cards):
            try:
                title_elem = job.find("h2", itemprop="title")
                company_elem = job.find("h3", itemprop="name")
                location_elem = job.find("div", class_="location")
                link_elem = job.get("data-href")

                date = datetime.datetime.now().strftime("%Y-%m-%d")
                detail_url = f"https://remoteok.com{link_elem}" if link_elem else None

                full_description = "No Description Found"
                if detail_url:
                    try:
                        detail_html = scrape_page(detail_url)
                        detail_soup = BeautifulSoup(detail_html, "html.parser")
                        desc_div = detail_soup.find("div", {"class": "description"}) or \
                                   detail_soup.find("div", {"id": "job-description"})
                        if desc_div:
                            full_description = desc_div.get_text(separator="\n", strip=True)
                        time.sleep(1)  # Rate limiting
                    except:
                        pass

                job_info = {
                    "title": title_elem.get_text(strip=True) if title_elem else None,
                    "company": company_elem.get_text(strip=True) if company_elem else None,
                    "location": self.remove_emojis(location_elem.get_text(strip=True)).strip() if location_elem else "Remote",
                    "description": full_description,
                    "job_url": detail_url,
                    "source": "RemoteOK",
                    "scraped_date": date
                }
                
                if job_info["title"] and job_info["company"]:
                    jobs.append(job_info)

            except Exception as e:
                logger.warning(f"Error parsing RemoteOK job card: {e}")
                continue

        return jobs
    
    def remove_emojis(self, text):
        """Remove emojis from text"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE,
        )
        return emoji_pattern.sub(r'', text)
    
    def apply_data_quality_checks(self):
        """Apply data quality checks to collected jobs"""
        logger.info("Applying data quality checks...")
        
        original_count = len(self.all_jobs)
        cleaned_jobs = []
        
        for job in self.all_jobs:
            # Quality checks
            if not job.get('title') or len(job['title']) < 3:
                continue
            
            if not job.get('company') or len(job['company']) < 2:
                continue
            
            # Standardize fields
            job['title'] = job['title'].strip()
            job['company'] = job['company'].strip()
            job['location'] = job.get('location', '').strip() or 'Remote'
            job['description'] = job.get('description', '').strip()
            
            # Add metadata
            job['data_quality_checked'] = True
            job['collection_date'] = datetime.datetime.now().isoformat()
            
            cleaned_jobs.append(job)
        
        self.all_jobs = cleaned_jobs
        
        logger.info(f"Data quality check complete:")
        logger.info(f"  Original jobs: {original_count}")
        logger.info(f"  After quality check: {len(cleaned_jobs)}")
        logger.info(f"  Removed: {original_count - len(cleaned_jobs)}")
        
        return self.all_jobs
    
    def save_to_mongo(self, db_url, db_name="JobPosting", collection_name="ScrapedJobs"):
        """Save jobs to MongoDB with connection handling"""
        try:
            # Multiple connection methods to handle SSL issues
            connection_configs = [
                {"tls": True, "tlsAllowInvalidCertificates": True},
                {"ssl": True, "ssl_cert_reqs": ssl.CERT_NONE},
                {}  # fallback
            ]
            
            client = None
            for config in connection_configs:
                try:
                    client = MongoClient(db_url, **config)
                    client.admin.command('ping')  # Test connection
                    logger.info("MongoDB connection successful!")
                    break
                except Exception as e:
                    if client:
                        client.close()
                    continue
            
            if not client:
                logger.error("Failed to connect to MongoDB with all methods")
                return False
                
            db = client[db_name]
            collection = db[collection_name]

            if self.all_jobs:
                # Clear existing data and insert new
                collection.delete_many({})
                collection.insert_many(self.all_jobs)
                logger.info(f"✅ Inserted {len(self.all_jobs)} jobs into MongoDB.")
                client.close()
                return True
            else:
                logger.warning("No jobs to insert.")
                client.close()
                return False
                
        except Exception as e:
            logger.error(f"MongoDB error: {e}")
            return False
    
    def save_to_json(self, filename="scraped_jobs_multi_source.json"):
        """Save jobs to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.all_jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved {len(self.all_jobs)} jobs to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return False
    
    def print_collection_summary(self):
        """Print summary of collection results"""
        print(f"\n{'='*70}")
        print("MULTI-SOURCE JOB COLLECTION SUMMARY")
        print(f"{'='*70}")
        
        if not self.all_jobs:
            print("No jobs collected.")
            return
        
        # Count by source
        source_counts = {}
        for job in self.all_jobs:
            source = job.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print(f"Total Jobs Collected: {len(self.all_jobs)}")
        print(f"Collection Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\nJobs by Source:")
        for source, count in sorted(source_counts.items()):
            print(f"  • {source}: {count} jobs")
        
        # Show sample jobs
        print(f"\nSample Jobs:")
        for i, job in enumerate(self.all_jobs[:3], 1):
            print(f"  {i}. {job.get('title', 'No Title')} at {job.get('company', 'No Company')}")
            print(f"     Source: {job.get('source', 'Unknown')}")
        
        print(f"{'='*70}")

def main():
    """Main execution function with full multi-source collection"""
    load_dotenv()  # Load environment variables
    
    parser = argparse.ArgumentParser(description="Multi-source job collection agent")
    parser.add_argument("--jobs-per-source", type=int, default=5, help="Jobs to collect per source")
    parser.add_argument("--no-proxies", action="store_true", help="Disable proxy usage")
    parser.add_argument("--sources", nargs="+", 
                       choices=['remoteok', 'indeed', 'linkedin', 'glassdoor', 'angellist', 'company_careers'],
                       help="Specify which sources to use")
    args = parser.parse_args()
    
    print("🚀 STARTING MULTI-SOURCE DATA COLLECTION AGENT")
    print("="*60)
    print("Sources: LinkedIn, Indeed, Glassdoor, AngelList, Company Career Pages")
    print("Features: Rate limiting, Proxy rotation, Data quality checks")
    print("="*60)
    
    # Initialize collector
    collector = MultiSourceJobCollector(
        use_proxies=not args.no_proxies,
        jobs_per_source=args.jobs_per_source
    )
    
    # Configure sources if specified
    if args.sources:
        for source in collector.sources:
            collector.sources[source]['enabled'] = source in args.sources
    
    try:
        # Collect from all sources
        jobs = collector.collect_from_all_sources()
        
        if not jobs:
            logger.error("No jobs collected from any source!")
            return
        
        # Apply data quality checks
        clean_jobs = collector.apply_data_quality_checks()
        
        # Save to files
        collector.save_to_json("scraped_jobs.json")  # Keep same filename for compatibility
        
        # Save to MongoDB
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
        mongo_success = collector.save_to_mongo(mongo_url)
        
        # Print summary
        collector.print_collection_summary()
        
        if mongo_success:
            print("\n✅ AGENT 1 COMPLETED SUCCESSFULLY!")
            print(f"Collected and stored {len(clean_jobs)} jobs from multiple sources.")
            print("Ready for Agent 2 signal processing.")
        else:
            print("\n⚠️ AGENT 1 COMPLETED WITH MONGODB ISSUES")
            print("Jobs saved to JSON file but MongoDB storage failed.")
        
    except KeyboardInterrupt:
        logger.info("Collection interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()