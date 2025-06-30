"""
Working Wellfound Job Scraper Demo
Since Wellfound has strong anti-bot protection, this demonstrates 
the structure with mock data and shows how it would work.
"""
import time
import random
from typing import List, Dict, Any

# Mock job data to demonstrate the scraper output structure
MOCK_JOBS = [
    {
        "title": "Senior Python Developer",
        "company": "TechStart Inc",
        "location": "Remote",
        "url": "https://wellfound.com/jobs/123456",
        "description": """We're looking for a Senior Python Developer to join our fast-growing team. 
        
Requirements:
- 5+ years Python experience
- Experience with Django/Flask
- AWS cloud knowledge
- Docker containerization
- RESTful API development

We offer competitive salary, equity, and the chance to work on cutting-edge technology.
Join our rapidly expanding team and make an impact!""",
        "posting_date": "N/A",
        "source": "Wellfound"
    },
    {
        "title": "Full Stack Engineer",
        "company": "DataCorp",
        "location": "Remote",
        "url": "https://wellfound.com/jobs/789012", 
        "description": """Immediate hire needed for Full Stack Engineer position.

Tech Stack:
- React frontend
- Node.js backend  
- PostgreSQL database
- AWS infrastructure
- TypeScript

Competitive salary package with benefits. Fast-paced startup environment.""",
        "posting_date": "N/A",
        "source": "Wellfound"
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudTech Solutions",
        "location": "Remote",
        "url": "https://wellfound.com/jobs/345678",
        "description": """Looking for DevOps Engineer to scale our infrastructure.

Requirements:
- Kubernetes expertise
- AWS/GCP experience
- CI/CD pipelines
- Terraform/Infrastructure as Code
- Docker containers

$120k-$150k salary range plus equity. Urgent hiring for growing team.""",
        "posting_date": "N/A", 
        "source": "Wellfound"
    }
]

def extract_job_signals_demo(description: str) -> Dict[str, Any]:
    """Demo function showing how job signals would be extracted"""
    # This would normally use your Ollama integration
    tech_stack = []
    urgency = False
    budget_indicators = []
    
    # Simple keyword extraction for demo
    tech_keywords = ["python", "react", "aws", "docker", "kubernetes", "node.js", "postgresql", "typescript", "django", "flask"]
    urgency_keywords = ["immediate", "urgent", "asap", "fast-paced", "rapidly", "quickly"]
    budget_keywords = ["competitive salary", "$", "equity", "benefits", "salary range"]
    
    desc_lower = description.lower()
    
    for tech in tech_keywords:
        if tech in desc_lower:
            tech_stack.append(tech.title())
    
    urgency = any(keyword in desc_lower for keyword in urgency_keywords)
    
    for budget in budget_keywords:
        if budget in desc_lower:
            budget_indicators.append(budget)
    
    return {
        "tech_stack": tech_stack,
        "urgency": urgency,
        "budget_indicators": budget_indicators
    }

def collect_jobs_demo(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Demo version that shows what the real scraper would return.
    In production, this would use Selenium to scrape actual jobs.
    """
    print("[INFO] Starting Wellfound job collection (DEMO MODE)")
    print("[INFO] Note: Using mock data due to Wellfound's anti-bot protection")
    
    jobs = []
    
    # Simulate scraping process
    for i, job in enumerate(MOCK_JOBS):
        if len(jobs) >= limit:
            break
            
        print(f"[INFO] Processing job {i+1}/{min(len(MOCK_JOBS), limit)}")
        
        # Simulate rate limiting
        time.sleep(random.uniform(1, 2))
        
        # Add job signals extraction
        signals = extract_job_signals_demo(job["description"])
        job_with_signals = job.copy()
        job_with_signals["extracted_signals"] = signals
        
        jobs.append(job_with_signals)
        print(f"[SUCCESS] Scraped job: {job['title']} at {job['company']}")
        
        # Simulate longer processing
        time.sleep(random.uniform(0.5, 1))
    
    print(f"[INFO] Successfully collected {len(jobs)} jobs")
    return jobs

def main():
    """Main function to demonstrate the scraper"""
    print("=" * 60)
    print("WELLFOUND JOB SCRAPER DEMO")
    print("=" * 60)
    
    jobs = collect_jobs_demo(limit=3)
    
    print("\n" + "=" * 60)
    print("SCRAPED JOBS WITH SIGNALS")
    print("=" * 60)
    
    for i, job in enumerate(jobs, 1):
        print(f"\n--- JOB {i} ---")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"URL: {job['url']}")
        print(f"Tech Stack: {job['extracted_signals']['tech_stack']}")
        print(f"Urgency: {job['extracted_signals']['urgency']}")
        print(f"Budget Indicators: {job['extracted_signals']['budget_indicators']}")
        print(f"Description Preview: {job['description'][:150]}...")

if __name__ == "__main__":
    main()