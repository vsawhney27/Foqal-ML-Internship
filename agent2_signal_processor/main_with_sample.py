#!/usr/bin/env python3
"""
Agent 2: Signal Processing Agent - Working with Sample Data
Simple version that follows Agent 1 pattern but works with sample data when MongoDB is unavailable
"""

from pymongo import MongoClient
import json
import datetime
import re
import os
from collections import Counter
from typing import List, Dict, Any

def create_sample_jobs():
    """Create sample job data for testing when MongoDB is unavailable"""
    return [
        {
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "location": "Remote",
            "description": """We are urgently seeking a Senior Python Developer with 5+ years experience. 
            Must have AWS, Docker, Kubernetes experience. Salary: $120,000-$150,000. 
            You'll help modernize our legacy systems and reduce technical debt. 
            Tech stack: Python, Django, Flask, PostgreSQL, Redis, React, Node.js.
            Start ASAP - this is a high priority hire!""",
            "detail_url": "https://example.com/job1",
            "scraped_date": "2024-01-15"
        },
        {
            "title": "React Frontend Engineer",
            "company": "StartupInc",
            "location": "San Francisco",
            "description": """Immediate opening for React developer! €80,000-100,000 salary + equity.
            Work with TypeScript, Node.js, GraphQL. Help us scale our platform and fix performance issues.
            Legacy codebase migration project. Must start this week!""",
            "detail_url": "https://example.com/job2",
            "scraped_date": "2024-01-15"
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudCorp",
            "location": "New York",
            "description": """Kubernetes expert needed! $85/hour + $140k base salary.
            Docker, Jenkins, Grafana, Prometheus experience required.
            Help us solve scalability issues and modernize infrastructure.
            Urgent hire for growing team.""",
            "detail_url": "https://example.com/job3",
            "scraped_date": "2024-01-15"
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AIStartup",
            "location": "Austin",
            "description": """TensorFlow and PyTorch expert wanted. $160k-200k + equity.
            Python, AWS, MLOps experience. Work on cutting-edge AI products.
            Help migrate from legacy ML infrastructure to modern stack.
            Immediate start needed.""",
            "detail_url": "https://example.com/job4",
            "scraped_date": "2024-01-15"
        },
        {
            "title": "Full Stack Developer",
            "company": "Enterprise Corp",
            "location": "Remote",
            "description": """Full stack role: React + Python/Django. £75,000 salary.
            PostgreSQL, AWS, Docker required. Legacy system integration work.
            Immediate start needed for critical project. Help us modernize our technical debt.""",
            "detail_url": "https://example.com/job5",
            "scraped_date": "2024-01-15"
        },
        {
            "title": "Data Scientist",
            "company": "DataCorp",
            "location": "Boston",
            "description": """Senior Data Scientist position. $140k-180k + stock options.
            Python, R, Scikit-learn, TensorFlow experience. Work with big data pipelines.
            Help us modernize our analytics infrastructure and solve scalability issues.
            Rushing to fill this role - start ASAP!""",
            "detail_url": "https://example.com/job6",
            "scraped_date": "2024-01-15"
        },
        {
            "title": "Backend Developer",
            "company": "FinTech Solutions",
            "location": "London",
            "description": """Backend developer needed urgently! Java, Spring Boot, Microservices.
            £60k-80k salary + equity. Work on financial systems and payment processing.
            Help replace legacy monolith with modern architecture.
            Must start immediately - high priority project.""",
            "detail_url": "https://example.com/job7",
            "scraped_date": "2024-01-15"
        },
        {
            "title": "Security Engineer",
            "company": "SecureTech",
            "location": "Seattle",
            "description": """Cybersecurity specialist wanted. $130k-160k + benefits.
            Python, Linux, AWS security experience. Help us modernize security infrastructure.
            Work on vulnerability assessment and penetration testing.
            Urgent need - start this week!""",
            "detail_url": "https://example.com/job8",
            "scraped_date": "2024-01-15"
        }
    ]

def load_jobs_from_mongo(db_url, db_name="JobPosting", collection_name="ScrapedJobs"):
    """Load jobs from MongoDB - same pattern as Agent 1"""
    try:
        client = MongoClient(db_url)
        db = client[db_name]
        collection = db[collection_name]
        
        jobs = list(collection.find())
        print(f"📥 Loaded {len(jobs)} jobs from MongoDB")
        client.close()
        return jobs
    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}")
        print("🔄 Using sample data instead...")
        return create_sample_jobs()

def save_to_mongo(processed_jobs, db_url, db_name="JobPosting", collection_name="ProcessedJobs"):
    """Save processed jobs to MongoDB - same pattern as Agent 1"""
    try:
        client = MongoClient(db_url)
        db = client[db_name]
        collection = db[collection_name]
        
        if processed_jobs:
            # Clear existing processed jobs
            collection.delete_many({})
            collection.insert_many(processed_jobs)
            print(f"✅ Inserted {len(processed_jobs)} processed jobs into MongoDB.")
        else:
            print("⚠️ No processed jobs to insert.")
        
        client.close()
    except Exception as e:
        print(f"⚠️ MongoDB save failed: {e}")
        print("💾 Results saved to files instead")

def extract_technology_adoption(description: str) -> List[str]:
    """Extract technology stack keywords from job description"""
    if not description:
        return []
    
    tech_keywords = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'C#', 'PHP', 'Ruby',
        'React', 'Angular', 'Vue', 'Django', 'Flask', 'FastAPI', 'Spring', 'Express', 'Node.js',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'GitLab CI',
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Neo4j', 'DynamoDB',
        'Git', 'Linux', 'Nginx', 'Apache', 'Grafana', 'Prometheus', 'Kafka', 'Spark',
        'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'OpenCV', 'MLOps',
        'HTML', 'CSS', 'Bootstrap', 'Tailwind', 'GraphQL', 'REST API', 'Microservices'
    ]
    
    found_tech = []
    description_lower = description.lower()
    
    for tech in tech_keywords:
        if re.search(r'\b' + re.escape(tech.lower()) + r'\b', description_lower):
            found_tech.append(tech)
    
    return found_tech

def extract_urgent_hiring_language(description: str) -> List[str]:
    """Detect urgent hiring phrases"""
    if not description:
        return []
    
    urgent_patterns = [
        r'\basap\b', r'\bimmediate\b', r'\bstart now\b', r'\bstart immediately\b',
        r'\burgent\b', r'\brushing\b', r'\bquickly\b', r'\bhiring now\b',
        r'\bstart monday\b', r'\bstart this week\b', r'\bhigh priority\b',
        r'\bmust start\b', r'\bstart asap\b', r'\bfill immediately\b'
    ]
    
    found_phrases = []
    description_lower = description.lower()
    
    for pattern in urgent_patterns:
        matches = re.findall(pattern, description_lower)
        found_phrases.extend(matches)
    
    return list(set(found_phrases))

def extract_budget_signals(description: str) -> Dict[str, Any]:
    """Extract salary and budget information"""
    if not description:
        return {}
    
    budget_info = {
        'salary_ranges': [],
        'hourly_rates': [],
        'equity_mentions': [],
        'budget_phrases': []
    }
    
    # Salary patterns
    salary_patterns = [
        r'\$\d{1,3}(?:,\d{3})*(?:\s*-\s*\$?\d{1,3}(?:,\d{3})*)?k?\b',
        r'€\d{1,3}(?:,\d{3})*(?:\s*-\s*€?\d{1,3}(?:,\d{3})*)?k?\b',
        r'£\d{1,3}(?:,\d{3})*(?:\s*-\s*£?\d{1,3}(?:,\d{3})*)?k?\b'
    ]
    
    # Hourly patterns
    hourly_patterns = [
        r'\$\d{1,3}(?:\.\d{2})?(?:\s*-\s*\$?\d{1,3}(?:\.\d{2})?)?\s*/?\s*(?:hour|hr|h)\b',
        r'€\d{1,3}(?:\.\d{2})?(?:\s*-\s*€?\d{1,3}(?:\.\d{2})?)?\s*/?\s*(?:hour|hr|h)\b'
    ]
    
    description_lower = description.lower()
    
    # Extract salary ranges
    for pattern in salary_patterns:
        matches = re.findall(pattern, description, re.IGNORECASE)
        budget_info['salary_ranges'].extend(matches)
    
    # Extract hourly rates
    for pattern in hourly_patterns:
        matches = re.findall(pattern, description, re.IGNORECASE)
        budget_info['hourly_rates'].extend(matches)
    
    # Check for equity mentions
    equity_keywords = ['equity', 'stock options', 'rsu', 'ownership', 'shares', 'stock']
    for keyword in equity_keywords:
        if keyword in description_lower:
            budget_info['equity_mentions'].append(keyword)
    
    # Check for budget phrases
    budget_phrases = ['competitive salary', 'market rate', 'negotiable', 'commensurate with experience']
    for phrase in budget_phrases:
        if phrase in description_lower:
            budget_info['budget_phrases'].append(phrase)
    
    return budget_info

def extract_pain_points(description: str) -> List[str]:
    """Detect pain points and challenges"""
    if not description:
        return []
    
    pain_patterns = [
        r'\blegacy system\b', r'\blegacy code\b', r'\blegacy\b', r'\btechnical debt\b',
        r'\btech debt\b', r'\brefactor\b', r'\bmodernize\b', r'\bmigrat\w+\b',
        r'\bupgrade\b', r'\breplace\b', r'\boutdated\b', r'\bintegration issues\b',
        r'\bmanual process\b', r'\bscalability issues\b', r'\bperformance issues\b',
        r'\bmonolith\b', r'\bvulnerability\b', r'\bsecurity\b'
    ]
    
    found_pain_points = []
    description_lower = description.lower()
    
    for pattern in pain_patterns:
        matches = re.findall(pattern, description_lower)
        found_pain_points.extend(matches)
    
    return list(set(found_pain_points))

def process_job_signals(job: Dict) -> Dict:
    """Process all signals for a single job"""
    description = job.get('description', '')
    
    # Extract all signals
    technology_adoption = extract_technology_adoption(description)
    urgent_hiring_language = extract_urgent_hiring_language(description)
    budget_signals = extract_budget_signals(description)
    pain_points = extract_pain_points(description)
    
    # Create processed job with all original data plus signals
    processed_job = job.copy()
    processed_job.update({
        'technology_adoption': technology_adoption,
        'urgent_hiring_language': urgent_hiring_language,
        'budget_signals': budget_signals,
        'pain_points': pain_points,
        'signal_processing_date': datetime.datetime.now().isoformat()
    })
    
    return processed_job

def process_jobs(jobs: List[Dict]) -> List[Dict]:
    """Process all jobs and extract signals"""
    processed_jobs = []
    
    print(f"🔄 Processing {len(jobs)} jobs for BD signals...")
    
    for idx, job in enumerate(jobs, 1):
        try:
            title = job.get('title', 'Unknown')
            company = job.get('company', 'Unknown')
            print(f"📊 Processing job {idx}/{len(jobs)}: {title} at {company}")
            
            processed_job = process_job_signals(job)
            processed_jobs.append(processed_job)
            
            # Show some findings
            tech_count = len(processed_job.get('technology_adoption', []))
            urgent_count = len(processed_job.get('urgent_hiring_language', []))
            pain_count = len(processed_job.get('pain_points', []))
            
            print(f"   💡 Found: {tech_count} technologies, {urgent_count} urgent signals, {pain_count} pain points")
            
        except Exception as e:
            print(f"❌ Error processing job {idx}: {e}")
            continue
    
    print(f"✅ Successfully processed {len(processed_jobs)} jobs")
    return processed_jobs

def generate_statistics(processed_jobs: List[Dict]) -> Dict:
    """Generate summary statistics"""
    if not processed_jobs:
        return {}
    
    print("📈 Generating statistics...")
    
    # Technology stats
    all_technologies = []
    for job in processed_jobs:
        all_technologies.extend(job.get('technology_adoption', []))
    
    tech_counter = Counter(all_technologies)
    
    # Urgent hiring stats
    urgent_jobs = [job for job in processed_jobs if job.get('urgent_hiring_language', [])]
    
    # Budget stats
    jobs_with_salary = [job for job in processed_jobs 
                       if job.get('budget_signals', {}).get('salary_ranges', [])]
    jobs_with_equity = [job for job in processed_jobs 
                       if job.get('budget_signals', {}).get('equity_mentions', [])]
    
    # Pain point stats
    all_pain_points = []
    for job in processed_jobs:
        all_pain_points.extend(job.get('pain_points', []))
    
    pain_counter = Counter(all_pain_points)
    
    # Company hiring volume
    company_counter = Counter()
    for job in processed_jobs:
        company = job.get('company', 'Unknown')
        if company != 'Unknown':
            company_counter[company] += 1
    
    stats = {
        'total_jobs_processed': len(processed_jobs),
        'processing_date': datetime.datetime.now().isoformat(),
        'top_technologies': dict(tech_counter.most_common(10)),
        'urgent_jobs_count': len(urgent_jobs),
        'urgent_percentage': round((len(urgent_jobs) / len(processed_jobs)) * 100, 2),
        'jobs_with_salary': len(jobs_with_salary),
        'jobs_with_equity': len(jobs_with_equity),
        'top_pain_points': dict(pain_counter.most_common(5)),
        'company_hiring_volume': dict(company_counter.most_common(10))
    }
    
    return stats

def print_summary(stats: Dict):
    """Print processing summary"""
    print("\n" + "="*60)
    print("📊 JOB POSTING SIGNAL PROCESSING SUMMARY")
    print("="*60)
    
    print(f"📈 Total Jobs Processed: {stats['total_jobs_processed']}")
    print(f"🕒 Processing Date: {stats['processing_date']}")
    
    print(f"\n🔧 TOP TECHNOLOGIES:")
    for tech, count in stats['top_technologies'].items():
        print(f"   • {tech}: {count} mentions")
    
    print(f"\n⚡ URGENT HIRING:")
    print(f"   • Jobs with urgent language: {stats['urgent_jobs_count']}")
    print(f"   • Percentage: {stats['urgent_percentage']}%")
    
    print(f"\n💰 BUDGET SIGNALS:")
    print(f"   • Jobs with salary info: {stats['jobs_with_salary']}")
    print(f"   • Jobs with equity: {stats['jobs_with_equity']}")
    
    print(f"\n🔥 TOP PAIN POINTS:")
    for pain, count in stats['top_pain_points'].items():
        print(f"   • {pain}: {count} mentions")
    
    print(f"\n🏢 COMPANY HIRING VOLUME:")
    for company, count in stats['company_hiring_volume'].items():
        print(f"   • {company}: {count} job(s)")
    
    print("="*60)

def save_to_files(processed_jobs: List[Dict], stats: Dict, output_dir: str = "output"):
    """Save results to JSON and CSV files"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save processed jobs
    jobs_file = os.path.join(output_dir, "signals_output.json")
    with open(jobs_file, 'w', encoding='utf-8') as f:
        # Convert any MongoDB ObjectId to string
        for job in processed_jobs:
            if '_id' in job:
                job['_id'] = str(job['_id'])
        json.dump(processed_jobs, f, indent=2, ensure_ascii=False)
    
    # Save statistics
    stats_file = os.path.join(output_dir, "signal_statistics.json")
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved results to {output_dir}/")

if __name__ == "__main__":
    # MongoDB URL - same as Agent 1
    MONGO_URL = "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/"
    
    print("🚀 Starting Signal Processing Agent (Agent 2)...")
    
    try:
        # Load jobs from MongoDB (or use sample data if connection fails)
        jobs = load_jobs_from_mongo(MONGO_URL)
        
        if not jobs:
            print("❌ No jobs found. Using sample data...")
            jobs = create_sample_jobs()
        
        # Process jobs for signals
        processed_jobs = process_jobs(jobs)
        
        if not processed_jobs:
            print("❌ No jobs were processed successfully.")
            exit(1)
        
        # Generate statistics
        stats = generate_statistics(processed_jobs)
        
        # Save to MongoDB (if available)
        save_to_mongo(processed_jobs, MONGO_URL)
        
        # Save to files
        save_to_files(processed_jobs, stats)
        
        # Print summary
        print_summary(stats)
        
        print("\n✅ Signal processing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Check the output files for results")