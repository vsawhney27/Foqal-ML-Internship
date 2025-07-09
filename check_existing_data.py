#!/usr/bin/env python3
"""
Check if there's existing data in MongoDB
"""

import sys
sys.path.append('agent1_data_collector')

try:
    from pymongo import MongoClient
    
    MONGO_URL = "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/"
    
    print("🔍 Checking for existing data in MongoDB...")
    
    client = MongoClient(MONGO_URL)
    db = client["JobPosting"]
    collection = db["ScrapedJobs"]
    
    # Check if there are any jobs
    job_count = collection.count_documents({})
    print(f"📊 Found {job_count} jobs in ScrapedJobs collection")
    
    if job_count > 0:
        # Get a sample job to see the structure
        sample_job = collection.find_one()
        print(f"📋 Sample job structure:")
        for key, value in sample_job.items():
            if key != '_id':
                print(f"   • {key}: {str(value)[:100]}...")
        
        # Get all jobs for Agent 2
        all_jobs = list(collection.find())
        print(f"✅ Retrieved {len(all_jobs)} jobs for Agent 2")
        
        # Save to file as backup
        import json
        with open('existing_jobs.json', 'w') as f:
            # Convert ObjectId to string for JSON serialization
            for job in all_jobs:
                if '_id' in job:
                    job['_id'] = str(job['_id'])
            json.dump(all_jobs, f, indent=2)
        
        print(f"💾 Saved existing jobs to existing_jobs.json")
        
    else:
        print("⚠️ No jobs found in MongoDB")
        print("💡 Agent 1 needs to run successfully first")
    
    client.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 This might be the same SSL issue affecting Agent 2")