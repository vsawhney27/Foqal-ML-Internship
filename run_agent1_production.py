#!/usr/bin/env python3
"""
Production Runner for Agent 1: Data Collection Agent
Scrapes job postings and stores them in MongoDB for further processing
"""

import sys
import os
import subprocess
from datetime import datetime

def run_agent1():
    """Run Agent 1 data collection"""
    print("="*60)
    print("AGENT 1: PRODUCTION DATA COLLECTION")
    print("="*60)
    
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Change to agent1 directory and run main.py
        agent1_dir = os.path.join(os.path.dirname(__file__), "agent1_data_collector")
        
        print("\nRunning Agent 1 data scraper...")
        print("Target: RemoteOK AI Jobs")
        
        # Run the scraper
        result = subprocess.run([
            sys.executable, "main.py"
        ], cwd=agent1_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: Agent 1 completed successfully")
            print("\nOutput:")
            print(result.stdout)
            
            # Check if jobs were collected
            jobs_file = os.path.join(agent1_dir, "scraped_jobs.json")
            if os.path.exists(jobs_file):
                print(f"✓ Jobs saved to: {jobs_file}")
            
            print("\nAgent 1 Status: READY FOR AGENT 2")
            return True
        else:
            print("ERROR: Agent 1 failed")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to run Agent 1: {e}")
        return False

if __name__ == "__main__":
    print("Starting Production Data Collection Pipeline...")
    
    success = run_agent1()
    
    if success:
        print("\n" + "="*60)
        print("AGENT 1 COMPLETED SUCCESSFULLY")
        print("="*60)
        print("Ready to run Agent 2 for signal processing")
        print("Command: python run_agent2_production.py")
    else:
        print("\n" + "="*60)
        print("AGENT 1 FAILED")
        print("="*60)
        print("Check error messages above and retry")
        sys.exit(1)