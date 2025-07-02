from pymongo import MongoClient
import ssl
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBHandler:
    """Handle MongoDB operations with SSL fix for job postings and processed signals."""
    
    def __init__(self, db_url: str, db_name: str = "JobPosting"):
        """Initialize MongoDB connection with SSL configuration."""
        self.db_url = db_url
        self.db_name = db_name
        self.client = None
        self.db = None
        
    def connect(self):
        """Establish connection to MongoDB with SSL workaround."""
        try:
            # Try multiple connection approaches
            connection_configs = [
                # Standard connection
                {},
                # SSL disabled (for testing)
                {"ssl": False},
                # SSL with certificate verification disabled
                {"ssl_cert_reqs": ssl.CERT_NONE},
                # TLS with disabled certificate verification
                {"tls": True, "tlsAllowInvalidCertificates": True},
                # Alternative SSL configuration
                {"ssl": True, "ssl_cert_reqs": ssl.CERT_NONE, "ssl_match_hostname": False}
            ]
            
            for i, config in enumerate(connection_configs):
                try:
                    logger.info(f"Trying connection method {i+1}/5...")
                    self.client = MongoClient(self.db_url, **config)
                    self.db = self.client[self.db_name]
                    
                    # Test connection
                    self.client.admin.command('ping')
                    logger.info(f"✅ Connected to MongoDB database: {self.db_name} (method {i+1})")
                    return True
                    
                except Exception as e:
                    logger.debug(f"Connection method {i+1} failed: {e}")
                    if self.client:
                        self.client.close()
                        self.client = None
                    continue
            
            logger.error("❌ All connection methods failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("🔌 Disconnected from MongoDB")
    
    def get_scraped_jobs(self, collection_name: str = "ScrapedJobs", limit: Optional[int] = None) -> List[Dict]:
        """Retrieve scraped jobs from MongoDB."""
        try:
            collection = self.db[collection_name]
            
            if limit:
                jobs = list(collection.find().limit(limit))
            else:
                jobs = list(collection.find())
            
            logger.info(f"📥 Retrieved {len(jobs)} jobs from {collection_name}")
            return jobs
            
        except Exception as e:
            logger.error(f"❌ Error retrieving jobs from {collection_name}: {e}")
            return []
    
    def save_processed_jobs(self, jobs: List[Dict], collection_name: str = "ProcessedJobs") -> bool:
        """Save processed jobs with signals to MongoDB."""
        try:
            if not jobs:
                logger.warning("⚠️ No jobs to save")
                return False
                
            collection = self.db[collection_name]
            
            # Insert processed jobs
            result = collection.insert_many(jobs)
            logger.info(f"✅ Inserted {len(result.inserted_ids)} processed jobs into {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving processed jobs to {collection_name}: {e}")
            return False

# Convenience function for direct use with SSL fix
def connect_to_mongo_with_ssl_fix(db_url: str, db_name: str = "JobPosting") -> Optional[MongoDBHandler]:
    """Create and connect to MongoDB handler with SSL workarounds."""
    handler = MongoDBHandler(db_url, db_name)
    if handler.connect():
        return handler
    return None