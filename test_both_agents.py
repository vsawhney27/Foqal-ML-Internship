#!/usr/bin/env python3
"""
Test both Agent 1 and Agent 2 to see what's actually working
"""

import sys
import os

def test_agent1_dependencies():
    """Test if Agent 1 can run at all"""
    print("🔍 Testing Agent 1...")
    try:
        # Try importing Agent 1's dependencies
        import requests
        import pymongo
        from bs4 import BeautifulSoup
        print("✅ Agent 1 dependencies: OK")
        
        # Check if API key is set
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("SCRAPINGDOG_API_KEY")
        
        if api_key:
            print("✅ ScrapingDog API key: Found")
        else:
            print("❌ ScrapingDog API key: Missing")
            print("   💡 This is why Agent 1 scraping fails")
        
        return True
    except ImportError as e:
        print(f"❌ Agent 1 dependencies: {e}")
        return False

def test_agent1_mongodb():
    """Test if Agent 1 can connect to MongoDB"""
    print("\n🔍 Testing Agent 1 MongoDB connection...")
    try:
        from pymongo import MongoClient
        MONGO_URL = "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/"
        
        client = MongoClient(MONGO_URL)
        db = client["JobPosting"]
        collection = db["ScrapedJobs"]
        
        # Test connection
        client.admin.command('ping')
        print("✅ Agent 1 MongoDB connection: OK")
        
        # Check for existing data
        count = collection.count_documents({})
        print(f"📊 Existing jobs in MongoDB: {count}")
        
        if count > 0:
            sample = collection.find_one()
            print(f"📋 Sample job: {sample.get('title', 'No title')}")
        
        client.close()
        return True, count
        
    except Exception as e:
        print(f"❌ Agent 1 MongoDB connection: {e}")
        return False, 0

def test_agent2_functionality():
    """Test if Agent 2 can process signals"""
    print("\n🔍 Testing Agent 2 signal processing...")
    try:
        sys.path.append('agent2_signal_processor')
        from main_with_sample import extract_technology_adoption, extract_urgent_hiring_language
        
        # Test with sample text
        test_text = "Python developer needed ASAP for AWS migration project. Salary $100k."
        
        tech = extract_technology_adoption(test_text)
        urgent = extract_urgent_hiring_language(test_text)
        
        print(f"✅ Agent 2 signal processing: OK")
        print(f"   • Found technologies: {tech}")
        print(f"   • Found urgent signals: {urgent}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent 2 signal processing: {e}")
        return False

def main():
    print("🧪 TESTING BOTH AGENTS")
    print("="*50)
    
    # Test Agent 1
    agent1_deps = test_agent1_dependencies()
    agent1_mongo, job_count = test_agent1_mongodb()
    
    # Test Agent 2
    agent2_ok = test_agent2_functionality()
    
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    
    print(f"🤖 Agent 1 Status:")
    print(f"   • Dependencies: {'✅ OK' if agent1_deps else '❌ FAIL'}")
    print(f"   • MongoDB: {'✅ OK' if agent1_mongo else '❌ FAIL'}")
    print(f"   • API Key: {'❌ MISSING' if not os.getenv('SCRAPINGDOG_API_KEY') else '✅ OK'}")
    print(f"   • Existing Data: {job_count} jobs")
    
    print(f"\n🤖 Agent 2 Status:")
    print(f"   • Signal Processing: {'✅ OK' if agent2_ok else '❌ FAIL'}")
    print(f"   • MongoDB: {'✅ OK' if agent1_mongo else '❌ FAIL'} (same as Agent 1)")
    
    print(f"\n💡 Issues Found:")
    if not os.getenv('SCRAPINGDOG_API_KEY'):
        print("   • Agent 1 needs ScrapingDog API key for scraping")
    if not agent1_mongo:
        print("   • Both agents have MongoDB SSL connection issues")
    if job_count == 0:
        print("   • No existing job data in MongoDB")
    
    print(f"\n🎯 Recommendations:")
    if job_count > 0:
        print("   • Agent 2 can work with existing MongoDB data")
    else:
        print("   • Agent 2 sample mode is working perfectly")
    
    if not agent1_mongo:
        print("   • Fix MongoDB SSL connection for both agents")
    
    if not os.getenv('SCRAPINGDOG_API_KEY'):
        print("   • Get ScrapingDog API key for Agent 1 scraping")

if __name__ == "__main__":
    main()