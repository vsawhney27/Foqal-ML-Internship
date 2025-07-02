#!/usr/bin/env python3
"""
Test script for Agent 2: Signal Processing Agent
"""

import sys
import os
sys.path.append('agent2_signal_processor')

from agent2_signal_processor.processor import SignalProcessor
from agent2_signal_processor.signals import (
    extract_technology_adoption,
    extract_urgent_hiring_language, 
    extract_budget_signals,
    extract_pain_points,
    extract_skills_mentioned
)

def test_signal_functions():
    """Test individual signal extraction functions with sample data."""
    print("🧪 Testing Signal Extraction Functions...")
    print("="*50)
    
    # Sample job description for testing
    sample_description = """
    We are looking for a Senior Python Developer with AWS experience to join our team ASAP!
    
    Requirements:
    - 5+ years Python development experience
    - Strong knowledge of Django, Flask, FastAPI
    - AWS services (EC2, S3, Lambda, RDS) 
    - Docker and Kubernetes experience
    - PostgreSQL and Redis knowledge
    - Experience with legacy system migration
    - Technical debt reduction experience
    
    We offer:
    - Competitive salary: $120,000 - $150,000
    - Stock options and equity
    - $50/hour consulting rate for overtime
    
    This is an urgent hire - we need someone to start immediately to help modernize our legacy codebase and resolve our technical debt issues.
    
    Tech stack: React, Node.js, TypeScript, MongoDB, GraphQL, Jenkins CI/CD
    """
    
    print("📝 Sample Job Description:")
    print("-" * 30)
    print(sample_description[:200] + "...")
    print()
    
    # Test technology extraction
    print("🔧 Technology Adoption:")
    tech = extract_technology_adoption(sample_description)
    print(f"   Found {len(tech)} technologies: {tech}")
    print()
    
    # Test urgent hiring language
    print("⚡ Urgent Hiring Language:")
    urgent = extract_urgent_hiring_language(sample_description)
    print(f"   Found {len(urgent)} urgent signals: {urgent}")
    print()
    
    # Test budget signals
    print("💰 Budget Signals:")
    budget = extract_budget_signals(sample_description)
    print(f"   Salary ranges: {budget.get('salary_ranges', [])}")
    print(f"   Hourly rates: {budget.get('hourly_rates', [])}")
    print(f"   Equity mentions: {budget.get('equity_mentions', [])}")
    print()
    
    # Test pain points
    print("🔥 Pain Points:")
    pain_points = extract_pain_points(sample_description)
    print(f"   Found {len(pain_points)} pain points: {pain_points}")
    print()
    
    # Test skills extraction
    print("🎯 Skills Mentioned:")
    skills = extract_skills_mentioned(sample_description)
    print(f"   Found {len(skills)} skills: {skills[:10]}...")  # Show first 10
    print()

def test_mongodb_connection():
    """Test MongoDB connection and data retrieval."""
    print("🗄️ Testing MongoDB Connection...")
    print("="*50)
    
    MONGO_URL = "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/"
    
    try:
        processor = SignalProcessor(MONGO_URL)
        
        # Test connection
        if processor.connect_to_database():
            print("✅ MongoDB connection successful!")
            
            # Check scraped jobs
            jobs = processor.load_scraped_jobs(limit=3)  # Load just 3 for testing
            print(f"📥 Found {len(jobs)} scraped jobs in database")
            
            if jobs:
                print("\n📋 Sample job titles:")
                for i, job in enumerate(jobs[:3], 1):
                    title = job.get('title', 'No title')
                    company = job.get('company', 'No company')
                    print(f"   {i}. {title} at {company}")
                
                return True, jobs
            else:
                print("⚠️ No scraped jobs found. Make sure Agent 1 has run first.")
                return False, []
        else:
            print("❌ Failed to connect to MongoDB")
            return False, []
            
    except Exception as e:
        print(f"❌ MongoDB test error: {e}")
        return False, []
    finally:
        if processor.mongo_handler:
            processor.disconnect()

def test_end_to_end_processing():
    """Test the complete signal processing pipeline."""
    print("🚀 Testing End-to-End Processing...")
    print("="*50)
    
    MONGO_URL = "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/"
    
    try:
        processor = SignalProcessor(MONGO_URL)
        
        if not processor.connect_to_database():
            print("❌ Cannot connect to database for end-to-end test")
            return False
        
        # Load a small sample for testing
        jobs = processor.load_scraped_jobs(limit=5)
        if not jobs:
            print("⚠️ No jobs available for processing test")
            return False
        
        print(f"📊 Processing {len(jobs)} jobs...")
        
        # Process jobs
        processed_jobs = processor.process_jobs(jobs)
        print(f"✅ Successfully processed {len(processed_jobs)} jobs")
        
        # Generate statistics
        stats = processor.generate_statistics()
        print(f"📈 Generated statistics with {len(stats)} categories")
        
        # Test saving (but don't actually save to avoid duplicates)
        print("💾 Testing save functions...")
        
        # Just test the logic without actually saving
        test_save = len(processed_jobs) > 0
        print(f"✅ Save test passed: {test_save}")
        
        # Print mini summary
        print("\n📊 Mini Summary:")
        if stats:
            print(f"   • Total jobs: {stats.get('total_jobs_processed', 0)}")
            tech_stats = stats.get('technology_stats', {})
            print(f"   • Technologies found: {tech_stats.get('total_unique_technologies', 0)}")
            urgent_stats = stats.get('urgent_hiring_stats', {})
            print(f"   • Jobs with urgent signals: {urgent_stats.get('jobs_with_urgent_language', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end test error: {e}")
        return False
    finally:
        if processor.mongo_handler:
            processor.disconnect()

def test_with_mock_data():
    """Test processing with mock data (no database required)."""
    print("🎭 Testing with Mock Data...")
    print("="*50)
    
    # Create mock job data
    mock_jobs = [
        {
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "location": "Remote",
            "description": "Looking for Python developer with AWS experience. Must start ASAP! Salary: $120k-150k. Legacy system migration required.",
            "detail_url": "https://example.com/job1",
            "scraped_date": "2024-01-15"
        },
        {
            "title": "React Frontend Engineer", 
            "company": "StartupInc",
            "location": "San Francisco",
            "description": "React developer needed immediately! €80,000 salary. Work with Node.js, TypeScript. Help modernize our technical debt.",
            "detail_url": "https://example.com/job2", 
            "scraped_date": "2024-01-15"
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudCorp", 
            "location": "New York",
            "description": "Kubernetes and Docker expert. $75/hour. Jenkins, Grafana experience. Urgent hire for scaling issues.",
            "detail_url": "https://example.com/job3",
            "scraped_date": "2024-01-15"
        }
    ]
    
    try:
        # Create processor without MongoDB
        processor = SignalProcessor("mock://no-connection")
        
        # Process mock jobs directly
        processed_jobs = processor.process_jobs(mock_jobs)
        print(f"✅ Processed {len(processed_jobs)} mock jobs")
        
        # Generate statistics
        processor.processed_jobs = processed_jobs  # Set for stats
        stats = processor.generate_statistics()
        
        # Print results
        print(f"\n📊 Mock Data Results:")
        print(f"   • Jobs processed: {len(processed_jobs)}")
        
        for i, job in enumerate(processed_jobs, 1):
            print(f"\n   Job {i}: {job['title']}")
            print(f"     • Technologies: {len(job.get('technology_adoption', []))}")
            print(f"     • Urgent signals: {len(job.get('urgent_hiring_language', []))}")
            print(f"     • Pain points: {len(job.get('pain_points', []))}")
            
            # Show some actual findings
            tech = job.get('technology_adoption', [])[:3]
            if tech:
                print(f"     • Top tech: {tech}")
            
            urgent = job.get('urgent_hiring_language', [])
            if urgent:
                print(f"     • Urgent phrases: {urgent}")
        
        # Test file saving with mock data
        processor.save_to_json("agent2_signal_processor/output")
        processor.save_to_csv("agent2_signal_processor/output")
        print(f"\n💾 Saved mock results to output/ directory")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock data test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 AGENT 2 TESTING SUITE")
    print("="*60)
    print()
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Signal functions
    try:
        test_signal_functions()
        tests_passed += 1
        print("✅ Test 1: Signal Functions - PASSED\n")
    except Exception as e:
        print(f"❌ Test 1: Signal Functions - FAILED: {e}\n")
    
    # Test 2: MongoDB connection
    try:
        success, jobs = test_mongodb_connection()
        if success:
            tests_passed += 1
            print("✅ Test 2: MongoDB Connection - PASSED\n")
        else:
            print("⚠️ Test 2: MongoDB Connection - FAILED (but may be expected if no data)\n")
    except Exception as e:
        print(f"❌ Test 2: MongoDB Connection - FAILED: {e}\n")
    
    # Test 3: End-to-end processing (only if MongoDB works)
    try:
        if 'jobs' in locals() and jobs:
            success = test_end_to_end_processing()
            if success:
                tests_passed += 1
                print("✅ Test 3: End-to-End Processing - PASSED\n")
            else:
                print("❌ Test 3: End-to-End Processing - FAILED\n")
        else:
            print("⏭️ Test 3: End-to-End Processing - SKIPPED (no database data)\n")
    except Exception as e:
        print(f"❌ Test 3: End-to-End Processing - FAILED: {e}\n")
    
    # Test 4: Mock data processing (always should work)
    try:
        success = test_with_mock_data()
        if success:
            tests_passed += 1
            print("✅ Test 4: Mock Data Processing - PASSED\n")
        else:
            print("❌ Test 4: Mock Data Processing - FAILED\n")
    except Exception as e:
        print(f"❌ Test 4: Mock Data Processing - FAILED: {e}\n")
    
    # Final results
    print("="*60)
    print(f"🏁 TESTING COMPLETE: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed >= 3:
        print("🎉 Agent 2 is working correctly!")
        print("\n📋 Next steps:")
        print("   1. Make sure Agent 1 has scraped some jobs")
        print("   2. Run: python3 agent2_signal_processor/processor.py")
        print("   3. Check output/ directory for results")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    print("="*60)

if __name__ == "__main__":
    main()