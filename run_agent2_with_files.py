#!/usr/bin/env python3
"""
Run Agent 2 with file-based input (no MongoDB required)
"""

import sys
import json
import os
sys.path.append('agent2_signal_processor')

from agent2_signal_processor.processor import SignalProcessor

def load_jobs_from_existing_data():
    """Load jobs from existing data files in the project."""
    possible_files = [
        "data/raw/job_postings.json",
        "data/processed/extracted_signals.json", 
        "agent1_data_collector/output.html"  # Could parse this if needed
    ]
    
    jobs = []
    
    # Check for JSON files
    for file_path in possible_files:
        if os.path.exists(file_path) and file_path.endswith('.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        jobs.extend(data)
                    elif isinstance(data, dict) and 'jobs' in data:
                        jobs.extend(data['jobs'])
                print(f"📥 Loaded {len(data)} jobs from {file_path}")
            except Exception as e:
                print(f"⚠️ Could not load {file_path}: {e}")
    
    return jobs

def run_agent2_with_files():
    """Run Agent 2 using file-based data."""
    print("🚀 Running Agent 2 with File-Based Data...")
    print("="*50)
    
    # Try to load existing data
    jobs = load_jobs_from_existing_data()
    
    # If no existing data, use enhanced mock data
    if not jobs:
        print("📝 No existing job files found, using enhanced mock data...")
        jobs = [
            {
                "title": "Senior Python Developer", 
                "company": "TechCorp",
                "location": "Remote",
                "description": """We are urgently seeking a Senior Python Developer with 5+ years experience. 
                Must have AWS, Docker, Kubernetes experience. Salary: $120,000-$150,000. 
                You'll help modernize our legacy systems and reduce technical debt. 
                Tech stack: Python, Django, Flask, PostgreSQL, Redis, React, Node.js.
                Start ASAP - this is a high priority hire!""",
                "detail_url": "https://example.com/job1",
                "scraped_date": "2024-01-15"
            },
            {
                "title": "React Frontend Engineer",
                "company": "StartupInc", 
                "location": "San Francisco",
                "description": """Immediate opening for React developer! €80,000-100,000 salary + equity.
                Work with TypeScript, Node.js, GraphQL. Help us scale our platform and fix performance issues.
                Legacy codebase migration project. Must start this week!""",
                "detail_url": "https://example.com/job2",
                "scraped_date": "2024-01-15"
            },
            {
                "title": "DevOps Engineer",
                "company": "CloudCorp",
                "location": "New York", 
                "description": """Kubernetes expert needed! $85/hour + $140k base salary.
                Docker, Jenkins, Grafana, Prometheus experience required.
                Help us solve scalability issues and modernize infrastructure.
                Urgent hire for growing team.""",
                "detail_url": "https://example.com/job3",
                "scraped_date": "2024-01-15"
            },
            {
                "title": "Machine Learning Engineer",
                "company": "AIStartup",
                "location": "Austin",
                "description": """TensorFlow and PyTorch expert wanted. $160k-200k + equity.
                Python, AWS, MLOps experience. Work on cutting-edge AI products.
                Help migrate from legacy ML infrastructure to modern stack.""",
                "detail_url": "https://example.com/job4", 
                "scraped_date": "2024-01-15"
            },
            {
                "title": "Full Stack Developer",
                "company": "Enterprise Corp",
                "location": "Remote",
                "description": """Full stack role: React + Python/Django. £75,000 salary.
                PostgreSQL, AWS, Docker required. Legacy system integration work.
                Immediate start needed for critical project.""",
                "detail_url": "https://example.com/job5",
                "scraped_date": "2024-01-15"
            }
        ]
    
    print(f"📊 Processing {len(jobs)} jobs...")
    
    # Create processor (without MongoDB connection)
    processor = SignalProcessor("file://no-connection")
    
    # Process jobs directly
    processed_jobs = processor.process_jobs(jobs)
    
    # Generate statistics  
    processor.processed_jobs = processed_jobs
    stats = processor.generate_statistics()
    
    # Save results
    processor.save_to_json("agent2_signal_processor/output")
    processor.save_to_csv("agent2_signal_processor/output") 
    
    # Print summary
    processor.print_summary()
    
    print(f"\n✅ Agent 2 completed successfully!")
    print(f"📁 Check agent2_signal_processor/output/ for results:")
    print(f"   • signals_output.json - Complete processed data")
    print(f"   • signals_output.csv - Excel-friendly format") 
    print(f"   • signal_statistics.json - Summary statistics")

if __name__ == "__main__":
    run_agent2_with_files()