from pydantic import BaseModel
from typing import Optional


class CompanyProfile(BaseModel):
    company_name: str
    domain: Optional[str] = None
    hq_country: Optional[str] = None
    hq_state: Optional[str] = None
    employee_count: Optional[int] = None
    employee_bucket: Optional[str] = None  # e.g., "51-200","201-500","501-1000"
    revenue_usd: Optional[float] = None
    sources: dict = {}  # {"linkedin": {...}, "about_page": {...}}