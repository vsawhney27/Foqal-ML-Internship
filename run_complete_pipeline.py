#!/usr/bin/env python3
"""
Complete BD Intelligence Pipeline Runner
Executes all three agents in sequence for business development intelligence
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def run_command(command, description, timeout=600):
    """Run a command with real-time output and return success status"""
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Timeout: {timeout} seconds")
    print("-" * 60)
    
    try:
        # Run with real-time output - no capture, direct output
        process = subprocess.Popen(
            command, 
            shell=True
        )
        
        # Wait for completion with timeout
        try:
            return_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            print(f"\n⏰ TIMEOUT: {description} exceeded {timeout} seconds")
            process.kill()
            return False
        
        if return_code == 0:
            print(f"\n✅ SUCCESS: {description}")
            return True
        else:
            print(f"\n❌ FAILED: {description} (exit code: {return_code})")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {description} - {e}")
        return False

def main():
    """Run the complete pipeline"""
    print("🚀 STARTING COMPLETE JOB POSTING INTELLIGENCE PIPELINE")
    print(f"Pipeline started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Run Agent 1 (Data Collection)
    success = run_command(
        f"{sys.executable} run_agent1_production.py",
        "Agent 1 - Data Collection",
        timeout=300  # 5 minutes timeout
    )
    if not success:
        print("\n❌ Pipeline failed at Agent 1")
        return False
    
    # Step 2: Run Agent 2 (Signal Processing)
    success = run_command(
        f"{sys.executable} run_agent2_production.py", 
        "Agent 2 - Signal Processing",
        timeout=180  # 3 minutes timeout
    )
    if not success:
        print("\n❌ Pipeline failed at Agent 2")
        return False
    
    # Step 3: Run Agent 3 (Intelligence Generation)
    success = run_command(
        f"{sys.executable} run_agent3_production.py",
        "Agent 3 - Intelligence Generation",
        timeout=120  # 2 minutes timeout
    )
    if not success:
        print("\n❌ Pipeline failed at Agent 3")
        return False
    
    # Step 4: Generate weekly report
    success = run_command(
        f"{sys.executable} generate_weekly_report.py",
        "Weekly Report Generation",
        timeout=60  # 1 minute timeout
    )
    # Don't fail pipeline if report generation fails
    
    print(f"\n{'='*80}")
    print("🎉 COMPLETE PIPELINE FINISHED SUCCESSFULLY!")
    print(f"{'='*80}")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show what was generated
    print("\n📊 GENERATED OUTPUTS:")
    
    outputs = [
        ("Raw scraped jobs", "agent1_data_collector/scraped_jobs.json"),
        ("Processed signals", "agent2_signal_processor/output/signals_output.json"),
        ("Signal statistics", "agent2_signal_processor/output/signal_statistics.json"),
        ("Company insights", "agent3_insight_generator/output/company_insights.json"),
        ("Industry trends", "agent3_insight_generator/output/industry_trends.json"),
        ("Weekly reports", "reports/weekly/")
    ]
    
    for name, path in outputs:
        if os.path.exists(path):
            print(f"✅ {name}: {path}")
        else:
            print(f"⚠️  {name}: {path} (not found)")
    
    # Option to launch dashboard
    print(f"\n{'='*60}")
    print("🖥️  DASHBOARD OPTIONS")
    print(f"{'='*60}")
    print("To view the dashboard, run:")
    print("  streamlit run dashboard.py")
    print("\nOr run individual agents:")
    print("  python run_agent1_production.py")
    print("  python run_agent2_production.py")
    print("  python run_agent3_production.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)