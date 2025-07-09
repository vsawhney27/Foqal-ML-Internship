#!/usr/bin/env python3
"""
Test MongoDB Atlas connection with proper SSL configuration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent2_signal_processor'))

try:
    from pymongo import MongoClient
    import ssl
    
    print("🔧 Testing MongoDB Atlas Connection...")
    print("="*50)
    
    # Original connection string from Agent 1
    MONGO_URL = "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/"
    
    # Try the exact configuration that works in Agent 1
    try:
        print("🔄 Attempting connection with Agent 1 configuration...")
        client = MongoClient(MONGO_URL)
        db = client["JobPosting"]
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Test data retrieval
        collection = db["ScrapedJobs"]
        job_count = collection.count_documents({})
        print(f"📊 Found {job_count} jobs in ScrapedJobs collection")
        
        if job_count > 0:
            # Get a sample job
            sample_job = collection.find_one()
            if sample_job:
                print(f"📋 Sample job: {sample_job.get('title', 'No title')} at {sample_job.get('company', 'No company')}")
                print(f"🗓️ Scraped date: {sample_job.get('scraped_date', 'No date')}")
        
        client.close()
        print("\n🎉 MongoDB Atlas connection test PASSED!")
        print("✅ Agent 2 can now connect to MongoDB successfully!")
        
    except Exception as e:
        print(f"❌ Basic connection failed: {e}")
        
        # Try alternative approaches
        alt_configs = [
            # Try without SSL verification
            {"ssl": False},
            # Try with different SSL options
            {"ssl": True, "ssl_cert_reqs": ssl.CERT_NONE},
            # Try with TLS
            {"tls": True, "tlsAllowInvalidCertificates": True},
            # Try with specific TLS version
            {"tls": True, "tlsInsecure": True},
        ]
        
        for i, config in enumerate(alt_configs, 1):
            try:
                print(f"🔄 Trying alternative method {i}...")
                client = MongoClient(MONGO_URL, **config)
                db = client["JobPosting"]
                
                # Test connection
                client.admin.command('ping')
                print(f"✅ Alternative method {i} successful!")
                
                # Test data retrieval
                collection = db["ScrapedJobs"]
                job_count = collection.count_documents({})
                print(f"📊 Found {job_count} jobs in ScrapedJobs collection")
                
                client.close()
                print("\n🎉 MongoDB Atlas connection test PASSED!")
                sys.exit(0)
                
            except Exception as e2:
                print(f"❌ Alternative method {i} failed: {e2}")
                if client:
                    client.close()
                continue
        
        print("\n❌ All connection methods failed")
        print("💡 This might be a network/firewall issue.")
        print("💡 Let's check if Agent 1 can connect...")
        
        # Test if Agent 1 connection still works
        try:
            print("\n🔄 Testing Agent 1 connection method...")
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent1_data_collector'))
            
            # Try to import Agent 1's connection
            from agent1_data_collector.main import save_to_mongo
            
            # Test with empty data (just to test connection)
            save_to_mongo([], MONGO_URL, db_name="JobPosting", collection_name="TestConnection")
            print("✅ Agent 1 connection method works!")
            
        except Exception as e3:
            print(f"❌ Agent 1 connection also failing: {e3}")
            print("💡 The MongoDB server might be down or credentials changed")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Try: pip install pymongo dnspython")
except Exception as e:
    print(f"❌ Unexpected error: {e}")