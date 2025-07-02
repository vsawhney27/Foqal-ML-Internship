#!/usr/bin/env python3
"""
Test MongoDB connection with various SSL configurations
"""

import sys
sys.path.append('agent2_signal_processor')

from agent2_signal_processor.mongo_utils_ssl_fix import connect_to_mongo_with_ssl_fix

def test_mongodb_with_ssl_fix():
    """Test MongoDB connection with SSL workarounds."""
    print("🔧 Testing MongoDB Connection with SSL Fixes...")
    print("="*50)
    
    MONGO_URL = "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/"
    
    handler = connect_to_mongo_with_ssl_fix(MONGO_URL)
    
    if handler:
        print("✅ MongoDB connection successful with SSL fix!")
        
        # Test data retrieval
        try:
            jobs = handler.get_scraped_jobs("ScrapedJobs", limit=1)
            print(f"📥 Found {len(jobs)} jobs in database")
            
            if jobs:
                job = jobs[0]
                print(f"📋 Sample job: {job.get('title', 'No title')} at {job.get('company', 'No company')}")
                return True
            else:
                print("⚠️ No jobs found (but connection works!)")
                return True
                
        except Exception as e:
            print(f"❌ Data retrieval error: {e}")
            return False
        finally:
            handler.disconnect()
    else:
        print("❌ All SSL connection methods failed")
        return False

if __name__ == "__main__":
    success = test_mongodb_with_ssl_fix()
    
    if success:
        print("\n🎉 MongoDB connection fixed!")
        print("Now you can run: python3 agent2_signal_processor/processor.py")
    else:
        print("\n⚠️ MongoDB still having issues. Try these alternatives:")
        print("1. Use a local MongoDB instance")
        print("2. Use the mock data mode (which already works perfectly)")
        print("3. Check if Agent 1 has run and populated the database")