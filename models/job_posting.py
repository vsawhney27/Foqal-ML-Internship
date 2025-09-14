from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    description: str
    department: Optional[str] = None
    job_url: str
    source: str
    scraped_date: str
    
    # New location fields for filtering
    location_country: Optional[str] = None
    location_state: Optional[str] = None
    is_remote: bool = False
    work_auth_text: Optional[str] = None  # raw sentence(s) if present
    tz_hints: List[str] = []              # e.g., ["CST","PST"]