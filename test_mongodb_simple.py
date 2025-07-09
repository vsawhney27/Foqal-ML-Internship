#!/usr/bin/env python3
"""
Simple MongoDB connection test
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent2_signal_processor'))

try:
    from pymongo import MongoClient
    import ssl
    
    print("🔧 Testing MongoDB Connection with SSL Fixes...")
    print("="*50)
    
    MONGO_URL = "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/"
    
    # Test multiple connection approaches
    connection_configs = [
        # Standard connection with SSL
        {
            "ssl": True,
            "ssl_cert_reqs": ssl.CERT_NONE,
            "serverSelectionTimeoutMS": 30000,
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000
        },
        # Alternative SSL configuration
        {
            "tls": True,
            "tlsAllowInvalidCertificates": True,
            "serverSelectionTimeoutMS": 30000,
            "connectTimeoutMS": 30000
        },
        # Basic connection (fallback)
        {
            "serverSelectionTimeoutMS": 30000,
            "connectTimeoutMS": 30000
        }
    ]
    
    client = None
    for i, config in enumerate(connection_configs, 1):
        try:
            print(f"🔄 Attempting connection method {i}/3...")
            client = MongoClient(MONGO_URL, **config)
            db = client["JobPosting"]
            
            # Test connection
            client.admin.command('ping')
            print(f"✅ Connection successful with method {i}!")
            
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
            
            # Success!
            client.close()
            print("\n🎉 MongoDB connection test PASSED!")
            print("✅ Agent 2 can now connect to MongoDB successfully!")
            sys.exit(0)
            
        except Exception as e:
            print(f"❌ Method {i} failed: {e}")
            if client:
                client.close()
                client = None
            continue
    
    print("\n❌ All connection methods failed")
    print("💡 Possible solutions:")
    print("   1. Check network connectivity")
    print("   2. Verify MongoDB Atlas credentials")
    print("   3. Check if IP is whitelisted in MongoDB Atlas")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Try: pip install pymongo dnspython")
except Exception as e:
    print(f"❌ Unexpected error: {e}")