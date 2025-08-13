from pymongo import MongoClient
from typing import List, Dict, Optional
import logging

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
            # Multiple connection methods to handle SSL issues
            connection_configs = [
                {"tls": True, "tlsAllowInvalidCertificates": True, "serverSelectionTimeoutMS": 5000},
                {"tlsInsecure": True, "serverSelectionTimeoutMS": 5000},
                {"serverSelectionTimeoutMS": 5000}  # fallback
            ]
            
            self.client = None
            for config in connection_configs:
                try:
                    logger.info(f"Trying MongoDB connection with config: {config}")
                    self.client = MongoClient(self.db_url, **config)
                    self.client.admin.command('ping')  # Test connection
                    logger.info("MongoDB connection successful!")
                    break
                except Exception as e:
                    logger.warning(f"Connection attempt failed: {e}")
                    if self.client:
                        self.client.close()
                    continue
            
            if not self.client:
                logger.error("Failed to connect to MongoDB with all methods")
                return False
            
            self.db = self.client[self.db_name]
            logger.info(f"Connected to MongoDB database: {self.db_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_scraped_jobs(self, collection_name: str = "ScrapedJobs", limit: Optional[int] = None) -> List[Dict]:
        """Retrieve scraped jobs from MongoDB."""
        try:
            collection = self.db[collection_name]
            
            if limit:
                jobs = list(collection.find().limit(limit))
            else:
                jobs = list(collection.find())
            
            logger.info(f"Retrieved {len(jobs)} jobs from {collection_name}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error retrieving jobs from {collection_name}: {e}")
            return []

# Convenience functions for direct use
def connect_to_mongo(db_url: str, db_name: str = "JobPosting") -> Optional[MongoDBHandler]:
    """Create and connect to MongoDB handler."""
    handler = MongoDBHandler(db_url, db_name)
    if handler.connect():
        return handler
    return None