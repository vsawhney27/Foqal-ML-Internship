#!/usr/bin/env python3
"""
Agent 1: Real Job Data Collection Agent
Scrapes actual job postings with detailed descriptions from multiple sources
Focuses on getting REAL job data, not career page content
"""

import json
import datetime
import os
import time
import logging
from typing import List, Dict
from pymongo import MongoClient
from dotenv import load_dotenv
import ssl

# Import the verified real jobs only scraper
from scrapers.real_only_scraper import scrape_all_real_jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def save_to_mongodb(jobs: List[Dict], db_url: str):
    """Save jobs to MongoDB with improved SSL handling"""
    try:
        # MongoDB Atlas optimized SSL configuration
        connection_configs = [
            # MongoDB Atlas standard connection
            {
                "ssl": True,
                "ssl_ca_certs": None,
                "ssl_check_hostname": False,
                "serverSelectionTimeoutMS": 15000,
                "connectTimeoutMS": 15000,
                "socketTimeoutMS": 15000,
                "retryWrites": True
            },
            # Alternative TLS approach
            {
                "tls": True,
                "tlsAllowInvalidCertificates": True,
                "serverSelectionTimeoutMS": 15000,
                "connectTimeoutMS": 15000, 
                "socketTimeoutMS": 15000,
                "retryWrites": True
            },
            # Fallback - no SSL verification
            {
                "serverSelectionTimeoutMS": 15000,
                "connectTimeoutMS": 15000,
                "socketTimeoutMS": 15000,
                "retryWrites": True
            }
        ]
        
        # For MongoDB Atlas, try a more specific approach
        client = None
        for i, config in enumerate(connection_configs):
            try:
                logger.info(f"Trying MongoDB Atlas connection (attempt {i+1}/3)...")
                client = MongoClient(db_url, **config)
                
                # Test the connection
                client.admin.command('ping')
                logger.info("✅ MongoDB Atlas connection successful!")
                break
                
            except Exception as e:
                logger.warning(f"Connection attempt {i+1} failed: {str(e)[:200]}...")
                if client:
                    client.close()
                    client = None
                continue
        
        if not client:
            raise Exception("Failed to connect to MongoDB with all methods")
        
        # Use database and collection
        db = client["JobPosting"]
        collection = db["ScrapedJobs"]
        
        # Clear existing jobs and insert new ones
        collection.delete_many({})
        logger.info("Cleared existing jobs from MongoDB")
        
        if jobs:
            result = collection.insert_many(jobs)
            logger.info(f"Inserted {len(result.inserted_ids)} jobs into MongoDB")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"MongoDB error: {e}")
        return False

def save_to_json(jobs: List[Dict], filename: str = "scraped_jobs.json"):
    """Save jobs to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved {len(jobs)} jobs to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving to JSON: {e}")
        return False

def apply_data_quality_checks(jobs: List[Dict]) -> List[Dict]:
    """Apply data quality filtering"""
    logger.info("Applying data quality checks...")
    
    original_count = len(jobs)
    quality_jobs = []
    
    for job in jobs:
        # Check required fields
        if not all([
            job.get('title'),
            job.get('company'),
            job.get('description')
        ]):
            continue
        
        # Check description quality
        description = job.get('description', '')
        if len(description) < 100:  # Minimum description length
            continue
        
        # Check for spam indicators
        title = job.get('title', '').lower()
        spam_indicators = ['urgent', 'immediate money', 'work from home scam']
        if any(indicator in title for indicator in spam_indicators):
            continue
        
        quality_jobs.append(job)
    
    filtered_count = original_count - len(quality_jobs)
    logger.info(f"Data quality check complete:")
    logger.info(f"  Original jobs: {original_count}")
    logger.info(f"  After quality check: {len(quality_jobs)}")
    logger.info(f"  Removed: {filtered_count}")
    
    return quality_jobs

def print_collection_summary(jobs: List[Dict]):
    """Print summary of collected jobs"""
    print("\n" + "="*70)
    print("REAL JOB COLLECTION SUMMARY")
    print("="*70)
    print(f"Total Jobs Collected: {len(jobs)}")
    print(f"Collection Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Jobs by source
    sources = {}
    for job in jobs:
        source = job.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\nJobs by Source:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {source}: {count} jobs")
    
    # Sample jobs
    print(f"\nSample Jobs:")
    for i, job in enumerate(jobs[:3], 1):
        title = job.get('title', 'Unknown')
        company = job.get('company', 'Unknown')
        source = job.get('source', 'Unknown')
        print(f"  {i}. {title} at {company}")
        print(f"     Source: {source}")
    
    print("="*70)

def main():
    """Main execution function"""
    logger.info("🚀 STARTING REAL JOB DATA COLLECTION")
    logger.info("="*60)
    logger.info("Sources: Hacker News, RemoteOK, Job APIs")
    logger.info("Focus: REAL job postings with detailed descriptions - NO FAKE DATA")
    logger.info("="*60)
    
    try:
        # Scrape real jobs only - no fake data
        logger.info("Collecting REAL job postings only...")
        jobs = scrape_all_real_jobs(limit_per_source=100)
        
        if not jobs:
            logger.error("❌ No jobs were collected from any source")
            return
        
        logger.info(f"✅ Initial collection: {len(jobs)} jobs")
        
        # Apply quality checks
        quality_jobs = apply_data_quality_checks(jobs)
        
        if not quality_jobs:
            logger.error("❌ No jobs passed quality checks")
            return
        
        # Save to JSON (always works)
        json_success = save_to_json(quality_jobs)
        
        # Save to MongoDB (may fail)
        mongo_url = os.getenv("MONGODB_URL")
        mongo_success = False
        
        if mongo_url:
            try:
                mongo_success = save_to_mongodb(quality_jobs, mongo_url)
                if mongo_success:
                    logger.info("✅ Successfully saved to MongoDB")
                else:
                    logger.warning("⚠️ MongoDB save failed, but JSON saved")
            except Exception as e:
                logger.error(f"MongoDB error: {e}")
        else:
            logger.info("No MongoDB URL configured, using JSON only")
        
        # Print summary
        print_collection_summary(quality_jobs)
        
        if json_success:
            logger.info("\n✅ REAL JOB DATA COLLECTION COMPLETED SUCCESSFULLY")
            logger.info(f"📊 Collected {len(quality_jobs)} high-quality job postings")
            
            if not mongo_success:
                logger.info("⚠️ AGENT 1 COMPLETED WITH MONGODB ISSUES")
                logger.info("Jobs saved to JSON file but MongoDB storage failed.")
        else:
            logger.error("❌ CRITICAL ERROR: Could not save data")
            
    except Exception as e:
        logger.error(f"❌ Critical error in job collection: {e}")
        raise

if __name__ == "__main__":
    main()