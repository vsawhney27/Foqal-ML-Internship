#!/usr/bin/env python3
"""
Agent 2: Signal Processing Agent
Job Posting Intelligence System for BD Signals

This agent processes job postings scraped by Agent 1 and extracts business development signals.
"""

import json
import csv
import os
import datetime
import logging
from typing import List, Dict, Optional
from collections import Counter

from mongo_utils import MongoDBHandler, connect_to_mongo
from signals import (
    process_job_signals,
    calculate_hiring_volume_by_company,
    extract_technology_adoption,
    extract_urgent_hiring_language,
    extract_budget_signals,
    extract_pain_points,
    extract_skills_mentioned
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SignalProcessor:
    """Main signal processing agent for job postings."""
    
    def __init__(self, mongo_url: str, db_name: str = "JobPosting"):
        """Initialize signal processor."""
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.mongo_handler = None
        self.processed_jobs = []
        self.statistics = {}
        
    def connect_to_database(self) -> bool:
        """Connect to MongoDB."""
        self.mongo_handler = connect_to_mongo(self.mongo_url, self.db_name)
        return self.mongo_handler is not None
    
    def load_scraped_jobs(self, limit: Optional[int] = None) -> List[Dict]:
        """Load job postings from ScrapedJobs collection."""
        if not self.mongo_handler:
            logger.error("❌ MongoDB connection not established")
            return []
        
        jobs = self.mongo_handler.get_scraped_jobs("ScrapedJobs", limit)
        logger.info(f"📥 Loaded {len(jobs)} scraped jobs from database")
        return jobs
    
    def process_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Process jobs and extract BD signals."""
        logger.info(f"🔄 Processing {len(jobs)} jobs for BD signals...")
        
        processed_jobs = []
        current_date = datetime.datetime.now().isoformat()
        
        for idx, job in enumerate(jobs, 1):
            try:
                logger.info(f"📊 Processing job {idx}/{len(jobs)}: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                
                # Process signals for this job
                processed_job = process_job_signals(job)
                processed_job['signal_processing_date'] = current_date
                
                processed_jobs.append(processed_job)
                
                # Log some key findings
                tech_count = len(processed_job.get('technology_adoption', []))
                urgent_count = len(processed_job.get('urgent_hiring_language', []))
                pain_points_count = len(processed_job.get('pain_points', []))
                
                logger.info(f"   💡 Found: {tech_count} technologies, {urgent_count} urgent signals, {pain_points_count} pain points")
                
            except Exception as e:
                logger.error(f"❌ Error processing job {idx}: {e}")
                continue
        
        self.processed_jobs = processed_jobs
        logger.info(f"✅ Successfully processed {len(processed_jobs)} jobs")
        return processed_jobs
    
    def generate_statistics(self) -> Dict:
        """Generate summary statistics from processed jobs."""
        if not self.processed_jobs:
            logger.warning("⚠️ No processed jobs available for statistics")
            return {}
        
        logger.info("📈 Generating statistics...")
        
        stats = {
            'total_jobs_processed': len(self.processed_jobs),
            'processing_date': datetime.datetime.now().isoformat(),
            'technology_stats': {},
            'urgent_hiring_stats': {},
            'budget_stats': {},
            'pain_point_stats': {},
            'hiring_volume_by_company': {},
            'top_skills': {}
        }
        
        # Technology adoption statistics
        all_technologies = []
        for job in self.processed_jobs:
            all_technologies.extend(job.get('technology_adoption', []))
        
        tech_counter = Counter(all_technologies)
        stats['technology_stats'] = {
            'total_unique_technologies': len(tech_counter),
            'most_common_technologies': dict(tech_counter.most_common(10)),
            'total_technology_mentions': len(all_technologies)
        }
        
        # Urgent hiring statistics
        urgent_jobs = [job for job in self.processed_jobs if job.get('urgent_hiring_language', [])]
        stats['urgent_hiring_stats'] = {
            'jobs_with_urgent_language': len(urgent_jobs),
            'percentage_urgent': round((len(urgent_jobs) / len(self.processed_jobs)) * 100, 2)
        }
        
        # Budget signal statistics
        jobs_with_salary = [job for job in self.processed_jobs 
                           if job.get('budget_signals', {}).get('salary_ranges', [])]
        jobs_with_hourly = [job for job in self.processed_jobs 
                          if job.get('budget_signals', {}).get('hourly_rates', [])]
        jobs_with_equity = [job for job in self.processed_jobs 
                          if job.get('budget_signals', {}).get('equity_mentions', [])]
        
        stats['budget_stats'] = {
            'jobs_with_salary_info': len(jobs_with_salary),
            'jobs_with_hourly_rates': len(jobs_with_hourly),
            'jobs_with_equity': len(jobs_with_equity),
            'percentage_with_budget_info': round(
                ((len(jobs_with_salary) + len(jobs_with_hourly)) / len(self.processed_jobs)) * 100, 2
            )
        }
        
        # Pain point statistics
        all_pain_points = []
        for job in self.processed_jobs:
            all_pain_points.extend(job.get('pain_points', []))
        
        pain_counter = Counter(all_pain_points)
        jobs_with_pain_points = [job for job in self.processed_jobs if job.get('pain_points', [])]
        
        stats['pain_point_stats'] = {
            'jobs_with_pain_points': len(jobs_with_pain_points),
            'percentage_with_pain_points': round((len(jobs_with_pain_points) / len(self.processed_jobs)) * 100, 2),
            'most_common_pain_points': dict(pain_counter.most_common(5))
        }
        
        # Hiring volume by company
        stats['hiring_volume_by_company'] = calculate_hiring_volume_by_company(self.processed_jobs)
        
        # Top skills
        all_skills = []
        for job in self.processed_jobs:
            all_skills.extend(job.get('skills_mentioned', []))
        
        skills_counter = Counter(all_skills)
        stats['top_skills'] = dict(skills_counter.most_common(15))
        
        self.statistics = stats
        logger.info("✅ Statistics generated successfully")
        return stats
    
    def save_to_mongodb(self, collection_name: str = "ProcessedJobs") -> bool:
        """Save processed jobs to MongoDB."""
        if not self.mongo_handler:
            logger.error("❌ MongoDB connection not established")
            return False
        
        if not self.processed_jobs:
            logger.warning("⚠️ No processed jobs to save")
            return False
        
        success = self.mongo_handler.save_processed_jobs(self.processed_jobs, collection_name)
        if success:
            logger.info(f"✅ Saved {len(self.processed_jobs)} processed jobs to {collection_name}")
        
        return success
    
    def save_to_json(self, output_dir: str = "output") -> bool:
        """Save processed jobs and statistics to JSON files."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Save processed jobs
            jobs_file = os.path.join(output_dir, "signals_output.json")
            with open(jobs_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_jobs, f, indent=2, ensure_ascii=False)
            
            # Save statistics
            stats_file = os.path.join(output_dir, "signal_statistics.json")
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.statistics, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved JSON files to {output_dir}/")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving JSON files: {e}")
            return False
    
    def save_to_csv(self, output_dir: str = "output") -> bool:
        """Save processed jobs to CSV file."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            csv_file = os.path.join(output_dir, "signals_output.csv")
            
            if not self.processed_jobs:
                logger.warning("⚠️ No processed jobs to save to CSV")
                return False
            
            # Flatten the data for CSV
            flattened_jobs = []
            for job in self.processed_jobs:
                flattened_job = {
                    'title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'scraped_date': job.get('scraped_date', ''),
                    'signal_processing_date': job.get('signal_processing_date', ''),
                    'detail_url': job.get('detail_url', ''),
                    'technologies_count': len(job.get('technology_adoption', [])),
                    'technologies': ', '.join(job.get('technology_adoption', [])),
                    'urgent_signals_count': len(job.get('urgent_hiring_language', [])),
                    'urgent_signals': ', '.join(job.get('urgent_hiring_language', [])),
                    'pain_points_count': len(job.get('pain_points', [])),
                    'pain_points': ', '.join(job.get('pain_points', [])),
                    'skills_count': len(job.get('skills_mentioned', [])),
                    'top_skills': ', '.join(job.get('skills_mentioned', [])[:10]),  # Top 10 skills
                    'has_salary_info': bool(job.get('budget_signals', {}).get('salary_ranges', [])),
                    'has_equity': bool(job.get('budget_signals', {}).get('equity_mentions', [])),
                    'salary_ranges': ', '.join(job.get('budget_signals', {}).get('salary_ranges', [])),
                    'hourly_rates': ', '.join(job.get('budget_signals', {}).get('hourly_rates', []))
                }
                flattened_jobs.append(flattened_job)
            
            # Write CSV
            fieldnames = flattened_jobs[0].keys() if flattened_jobs else []
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_jobs)
            
            logger.info(f"✅ Saved CSV file to {csv_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving CSV file: {e}")
            return False
    
    def print_summary(self):
        """Print processing summary to console."""
        if not self.statistics:
            logger.warning("⚠️ No statistics available")
            return
        
        print("\n" + "="*60)
        print("📊 JOB POSTING SIGNAL PROCESSING SUMMARY")
        print("="*60)
        
        print(f"📈 Total Jobs Processed: {self.statistics['total_jobs_processed']}")
        print(f"🕒 Processing Date: {self.statistics['processing_date']}")
        
        print(f"\n🔧 TECHNOLOGY ADOPTION:")
        tech_stats = self.statistics['technology_stats']
        print(f"   • Unique Technologies Found: {tech_stats['total_unique_technologies']}")
        print(f"   • Total Technology Mentions: {tech_stats['total_technology_mentions']}")
        print(f"   • Top 5 Technologies:")
        for tech, count in list(tech_stats['most_common_technologies'].items())[:5]:
            print(f"     - {tech}: {count} mentions")
        
        print(f"\n⚡ URGENT HIRING SIGNALS:")
        urgent_stats = self.statistics['urgent_hiring_stats']
        print(f"   • Jobs with Urgent Language: {urgent_stats['jobs_with_urgent_language']}")
        print(f"   • Percentage: {urgent_stats['percentage_urgent']}%")
        
        print(f"\n💰 BUDGET SIGNALS:")
        budget_stats = self.statistics['budget_stats']
        print(f"   • Jobs with Salary Info: {budget_stats['jobs_with_salary_info']}")
        print(f"   • Jobs with Hourly Rates: {budget_stats['jobs_with_hourly_rates']}")
        print(f"   • Jobs with Equity: {budget_stats['jobs_with_equity']}")
        print(f"   • Percentage with Budget Info: {budget_stats['percentage_with_budget_info']}%")
        
        print(f"\n🔥 PAIN POINTS:")
        pain_stats = self.statistics['pain_point_stats']
        print(f"   • Jobs with Pain Points: {pain_stats['jobs_with_pain_points']}")
        print(f"   • Percentage: {pain_stats['percentage_with_pain_points']}%")
        print(f"   • Top Pain Points:")
        for pain, count in pain_stats['most_common_pain_points'].items():
            print(f"     - {pain}: {count} mentions")
        
        print(f"\n🏢 HIRING VOLUME BY COMPANY:")
        company_stats = self.statistics['hiring_volume_by_company']
        top_companies = sorted(company_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        for company, count in top_companies:
            print(f"   • {company}: {count} job(s)")
        
        print(f"\n🎯 TOP SKILLS:")
        top_skills = self.statistics['top_skills']
        for skill, count in list(top_skills.items())[:10]:
            print(f"   • {skill}: {count} mentions")
        
        print("="*60)
    
    def disconnect(self):
        """Disconnect from MongoDB."""
        if self.mongo_handler:
            self.mongo_handler.disconnect()

def main():
    """Main execution function."""
    # MongoDB URL from Agent 1
    MONGO_URL = "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/"
    
    logger.info("🚀 Starting Signal Processing Agent...")
    
    # Initialize processor
    processor = SignalProcessor(MONGO_URL)
    
    try:
        # Connect to database
        if not processor.connect_to_database():
            logger.error("❌ Failed to connect to database. Exiting.")
            return
        
        # Load scraped jobs
        jobs = processor.load_scraped_jobs()
        if not jobs:
            logger.error("❌ No scraped jobs found. Make sure Agent 1 has run successfully.")
            return
        
        # Process jobs for signals
        processed_jobs = processor.process_jobs(jobs)
        if not processed_jobs:
            logger.error("❌ No jobs were processed successfully.")
            return
        
        # Generate statistics
        stats = processor.generate_statistics()
        
        # Save to MongoDB
        processor.save_to_mongodb("ProcessedJobs")
        
        # Save to files
        processor.save_to_json("agent2_signal_processor/output")
        processor.save_to_csv("agent2_signal_processor/output")
        
        # Print summary
        processor.print_summary()
        
        logger.info("✅ Signal processing completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Processing interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        processor.disconnect()

if __name__ == "__main__":
    main()