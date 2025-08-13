#!/usr/bin/env python3
"""
Automated Data Refresh Script
Runs the ML pipeline every hour to keep dashboard data fresh with real, live data
"""

import os
import sys
import time
import logging
import schedule
import subprocess
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def refresh_live_data():
    """Run the complete ML pipeline to refresh data"""
    logger.info("🔄 Starting automated data refresh...")
    
    try:
        # Change to project directory
        project_dir = "/Users/veersawhney/Downloads/Foqal Internship ML Project"
        os.chdir(project_dir)
        
        # Run the ML pipeline in virtual environment
        logger.info("Running ML pipeline for fresh data...")
        result = subprocess.run([
            'bash', '-c', 
            'source venv/bin/activate && python3 run_ml_pipeline.py'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✅ Data refresh completed successfully")
            logger.info(f"Pipeline output: {result.stdout[-500:]}")  # Last 500 chars
            
            # Update timestamp file
            with open('data_last_updated.txt', 'w') as f:
                f.write(f"Last updated: {datetime.now().isoformat()}\n")
                f.write(f"Status: SUCCESS\n")
                f.write(f"Jobs processed: Check output files\n")
            
            return True
        else:
            logger.error(f"❌ Data refresh failed: {result.stderr}")
            with open('data_last_updated.txt', 'w') as f:
                f.write(f"Last attempted: {datetime.now().isoformat()}\n")
                f.write(f"Status: FAILED\n")
                f.write(f"Error: {result.stderr}\n")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Data refresh timed out after 5 minutes")
        return False
    except Exception as e:
        logger.error(f"❌ Data refresh failed with error: {e}")
        return False

def validate_data_freshness():
    """Check if data is fresh and valid"""
    try:
        # Check if output files exist and are recent (within 2 hours)
        output_files = [
            'output/company_insights.json',
            'output/signals_output.json',
            'output/industry_trends.json'
        ]
        
        for file_path in output_files:
            if not os.path.exists(file_path):
                logger.warning(f"Missing output file: {file_path}")
                return False
            
            file_age = time.time() - os.path.getmtime(file_path)
            if file_age > 7200:  # 2 hours in seconds
                logger.warning(f"Data file {file_path} is {file_age/3600:.1f} hours old")
                return False
        
        logger.info("✅ All data files are fresh and present")
        return True
        
    except Exception as e:
        logger.error(f"Error validating data freshness: {e}")
        return False

def run_continuous_refresh():
    """Run the automated refresh system"""
    logger.info("🚀 Starting automated data refresh system")
    logger.info("Schedule: Every hour")
    logger.info("Data source: Real job postings from RemoteOK, Greenhouse, Lever")
    
    # Initial data refresh
    logger.info("Running initial data refresh...")
    if not validate_data_freshness():
        logger.info("Data is stale, running refresh...")
        refresh_live_data()
    
    # Schedule hourly refreshes
    schedule.every().hour.do(refresh_live_data)
    
    # Also schedule validation every 30 minutes
    schedule.every(30).minutes.do(validate_data_freshness)
    
    logger.info("✅ Automated refresh system started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("🛑 Automated refresh system stopped by user")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once for testing
        logger.info("Running single data refresh...")
        success = refresh_live_data()
        sys.exit(0 if success else 1)
    else:
        # Run continuously
        run_continuous_refresh()