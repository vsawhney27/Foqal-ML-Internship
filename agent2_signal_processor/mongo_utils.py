from pymongo import MongoClient
from typing import List, Dict, Optional
import logging
import ssl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBHandler:
 """Handle MongoDB operations for job postings and processed signals."""
 
 def __init__(self, db_url: str, db_name: str = "JobPosting"):
 """Initialize MongoDB connection."""
 self.db_url = db_url
 self.db_name = db_name
 self.client = None
 self.db = None
 
 def connect(self):
 """Establish connection to MongoDB with SSL handling."""
 try:
 # Multiple connection methods to handle SSL issues (from Agent 1)
 connection_configs = [
 {"tls": True, "tlsAllowInvalidCertificates": True, "serverSelectionTimeoutMS": 5000},
 {"tlsInsecure": True, "serverSelectionTimeoutMS": 5000},
 {"serverSelectionTimeoutMS": 5000}  # fallback
 ]
 
 self.client = None
 for config in connection_configs:
 try:
 logger.info(f" Trying MongoDB connection with config: {config}")
 self.client = MongoClient(self.db_url, **config)
 self.client.admin.command('ping')  # Test connection
 logger.info(" MongoDB connection successful!")
 break
 except Exception as e:
 logger.warning(f" Connection attempt failed: {e}")
 if self.client:
 self.client.close()
 continue
 
 if not self.client:
 logger.error(" Failed to connect to MongoDB with all methods")
 return False
 
 self.db = self.client[self.db_name]
 logger.info(f" Connected to MongoDB database: {self.db_name}")
 return True
 
 except Exception as e:
 logger.error(f" Failed to connect to MongoDB: {e}")
 return False
 
 def disconnect(self):
 """Close MongoDB connection."""
 if self.client:
 self.client.close()
 logger.info(" Disconnected from MongoDB")
 
 def get_scraped_jobs(self, collection_name: str = "ScrapedJobs", limit: Optional[int] = None) -> List[Dict]:
 """Retrieve scraped jobs from MongoDB."""
 try:
 collection = self.db[collection_name]
 
 if limit:
 jobs = list(collection.find().limit(limit))
 else:
 jobs = list(collection.find())
 
 logger.info(f" Retrieved {len(jobs)} jobs from {collection_name}")
 return jobs
 
 except Exception as e:
 logger.error(f" Error retrieving jobs from {collection_name}: {e}")
 return []
 
 def save_processed_jobs(self, jobs: List[Dict], collection_name: str = "ProcessedJobs") -> bool:
 """Save processed jobs with signals to MongoDB."""
 try:
 if not jobs:
 logger.warning(" No jobs to save")
 return False
 
 collection = self.db[collection_name]
 
 # Clear existing processed jobs (optional - remove if you want to append)
 # collection.delete_many({})
 # logger.info(f" Cleared existing data from {collection_name}")
 
 # Insert processed jobs
 result = collection.insert_many(jobs)
 logger.info(f" Inserted {len(result.inserted_ids)} processed jobs into {collection_name}")
 return True
 
 except Exception as e:
 logger.error(f" Error saving processed jobs to {collection_name}: {e}")
 return False
 
 def get_processed_jobs(self, collection_name: str = "ProcessedJobs", limit: Optional[int] = None) -> List[Dict]:
 """Retrieve processed jobs from MongoDB."""
 try:
 collection = self.db[collection_name]
 
 if limit:
 jobs = list(collection.find().limit(limit))
 else:
 jobs = list(collection.find())
 
 logger.info(f" Retrieved {len(jobs)} processed jobs from {collection_name}")
 return jobs
 
 except Exception as e:
 logger.error(f" Error retrieving processed jobs from {collection_name}: {e}")
 return []
 
 def get_collection_stats(self, collection_name: str) -> Dict:
 """Get statistics for a collection."""
 try:
 collection = self.db[collection_name]
 stats = {
 'total_documents': collection.count_documents({}),
 'collection_name': collection_name,
 'database_name': self.db_name
 }
 
 # Get sample document structure
 sample_doc = collection.find_one()
 if sample_doc:
 stats['sample_fields'] = list(sample_doc.keys())
 
 return stats
 
 except Exception as e:
 logger.error(f" Error getting stats for {collection_name}: {e}")
 return {}
 
 def update_processed_job(self, job_id: str, updates: Dict, collection_name: str = "ProcessedJobs") -> bool:
 """Update a single processed job."""
 try:
 collection = self.db[collection_name]
 result = collection.update_one(
 {"_id": job_id},
 {"$set": updates}
 )
 
 if result.modified_count > 0:
 logger.info(f" Updated job {job_id}")
 return True
 else:
 logger.warning(f" No documents updated for job {job_id}")
 return False
 
 except Exception as e:
 logger.error(f" Error updating job {job_id}: {e}")
 return False
 
 def delete_collection(self, collection_name: str) -> bool:
 """Delete an entire collection (use with caution)."""
 try:
 self.db[collection_name].drop()
 logger.info(f" Dropped collection: {collection_name}")
 return True
 
 except Exception as e:
 logger.error(f" Error dropping collection {collection_name}: {e}")
 return False

# Convenience functions for direct use
def connect_to_mongo(db_url: str, db_name: str = "JobPosting") -> Optional[MongoDBHandler]:
 """Create and connect to MongoDB handler."""
 handler = MongoDBHandler(db_url, db_name)
 if handler.connect():
 return handler
 return None

def get_jobs_from_mongo(db_url: str, collection_name: str = "ScrapedJobs", limit: Optional[int] = None) -> List[Dict]:
 """Quick function to get jobs from MongoDB."""
 handler = connect_to_mongo(db_url)
 if handler:
 jobs = handler.get_scraped_jobs(collection_name, limit)
 handler.disconnect()
 return jobs
 return []

def save_jobs_to_mongo(jobs: List[Dict], db_url: str, collection_name: str = "ProcessedJobs") -> bool:
 """Quick function to save jobs to MongoDB."""
 handler = connect_to_mongo(db_url)
 if handler:
 success = handler.save_processed_jobs(jobs, collection_name)
 handler.disconnect()
 return success
 return False