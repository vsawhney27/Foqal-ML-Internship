#!/usr/bin/env python3
"""
Production Runner for Agent 2: Signal Processing Agent
Processes job postings from Agent 1 and extracts BD signals
"""

import sys
import os
import subprocess
from datetime import datetime

def check_agent1_data():
    """Check if Agent 1 has provided data"""
    agent1_dir = os.path.join(os.path.dirname(__file__), "agent1_data_collector")
    jobs_file = os.path.join(agent1_dir, "scraped_jobs.json")
    
    if not os.path.exists(jobs_file):
        print("ERROR: No scraped jobs found from Agent 1")
        print("Please run Agent 1 first: python run_agent1_production.py")
        return False
    
    print("✓ Agent 1 data found")
    return True

def run_agent2():
    """Run Agent 2 signal processing"""
    print("="*60)
    print("AGENT 2: PRODUCTION SIGNAL PROCESSING")
    print("="*60)
    
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    if not check_agent1_data():
        return False
    
    try:
        # Change to agent2 directory and run main.py
        agent2_dir = os.path.join(os.path.dirname(__file__), "agent2_signal_processor")
        
        print("\nProcessing signals from job postings...")
        print("Extracting: Technology stacks, Urgent hiring, Budget signals, Pain points")
        
        # Run the signal processor
        result = subprocess.run([
            sys.executable, "main.py"
        ], cwd=agent2_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: Agent 2 completed successfully")
            print("\nOutput:")
            print(result.stdout)
            
            # Check if signals were processed
            output_dir = os.path.join(agent2_dir, "output")
            signals_file = os.path.join(output_dir, "signals_output.json")
            stats_file = os.path.join(output_dir, "signal_statistics.json")
            
            if os.path.exists(signals_file):
                print(f"✓ Processed signals saved to: {signals_file}")
            if os.path.exists(stats_file):
                print(f"✓ Signal statistics saved to: {stats_file}")
            
            print("\nAgent 2 Status: READY FOR AGENT 3")
            return True
        else:
            print("ERROR: Agent 2 failed")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to run Agent 2: {e}")
        return False

if __name__ == "__main__":
    print("Starting Production Signal Processing Pipeline...")
    
    success = run_agent2()
    
    if success:
        print("\n" + "="*60)
        print("AGENT 2 COMPLETED SUCCESSFULLY") 
        print("="*60)
        print("Ready to run Agent 3 for business intelligence")
        print("Command: python run_agent3_production.py")
    else:
        print("\n" + "="*60)
        print("AGENT 2 FAILED")
        print("="*60)
        print("Check error messages above and retry")
        sys.exit(1)