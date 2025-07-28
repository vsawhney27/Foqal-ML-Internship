#!/usr/bin/env python3
"""
Agent 2: Signal Processing Agent - Simple Version
Follows the same pattern as Agent 1 but processes signals from job postings
"""

from pymongo import MongoClient
import json
import datetime
import re
import os
from collections import Counter
from typing import List, Dict, Any

def load_jobs_from_mongo(db_url, db_name="JobPosting", collection_name="ScrapedJobs"):
    """Load jobs from MongoDB with SSL handling"""
    import ssl
    
    # Multiple connection methods to handle SSL issues
    connection_configs = [
        {"tls": True, "tlsAllowInvalidCertificates": True, "serverSelectionTimeoutMS": 5000},
        {"tlsInsecure": True, "serverSelectionTimeoutMS": 5000},
        {"serverSelectionTimeoutMS": 5000}  # fallback
    ]
    
    client = None
    for config in connection_configs:
        try:
            print(f"Trying MongoDB connection with config: {config}")
            client = MongoClient(db_url, **config)
            client.admin.command('ping')  # Test connection
            print("MongoDB connection successful!")
            break
        except Exception as e:
            print(f"Connection attempt failed: {e}")
            if client:
                client.close()
            continue
    
    if not client:
        raise Exception("Failed to connect to MongoDB with all methods")
    
    db = client[db_name]
    collection = db[collection_name]
    
    jobs = list(collection.find())
    print(f"Loaded {len(jobs)} jobs from MongoDB")
    client.close()
    return jobs

def save_to_mongo(processed_jobs, db_url, db_name="JobPosting", collection_name="ProcessedJobs"):
    """Save processed jobs to MongoDB with SSL handling"""
    import ssl
    
    # Multiple connection methods to handle SSL issues
    connection_configs = [
        {"tls": True, "tlsAllowInvalidCertificates": True, "serverSelectionTimeoutMS": 5000},
        {"tlsInsecure": True, "serverSelectionTimeoutMS": 5000},
        {"serverSelectionTimeoutMS": 5000}  # fallback
    ]
    
    client = None
    for config in connection_configs:
        try:
            print(f"Trying MongoDB connection with config: {config}")
            client = MongoClient(db_url, **config)
            client.admin.command('ping')  # Test connection
            print("MongoDB connection successful!")
            break
        except Exception as e:
            print(f"Connection attempt failed: {e}")
            if client:
                client.close()
            continue
    
    if not client:
        raise Exception("Failed to connect to MongoDB with all methods")
    
    db = client[db_name]
    collection = db[collection_name]
    
    if processed_jobs:
        # Clear existing processed jobs
        collection.delete_many({})
        collection.insert_many(processed_jobs)
        print(f"Inserted {len(processed_jobs)} processed jobs into MongoDB.")
    else:
        print("No processed jobs to insert.")
    
    client.close()

def extract_technology_adoption(description: str) -> List[str]:
    """Extract technology stack keywords from job description"""
    if not description:
        return []
    
    # Multi-word technologies should be checked first (longer matches take priority)
    tech_keywords = [
        # Multi-word technologies first
        'React Native', 'Vue.js', 'Angular.js', 'Next.js', 'Node.js', 'Express.js',
        'Spring Boot', 'Django REST', 'FastAPI', 'GitLab CI', 'GitHub Actions',
        'Google Cloud Platform', 'Amazon Web Services', 'Microsoft Azure',
        'REST API', 'GraphQL API', 'Machine Learning', 'Artificial Intelligence',
        'DevOps Engineer', 'Full Stack', 'Front End', 'Back End', 'End-to-End',
        'CI/CD', 'ML/AI', 'AI/ML', 'Technical Debt', 'Legacy System',
        'Cloud Computing', 'Data Science', 'Big Data', 'Real Time',
        # Single-word technologies
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'C#', 'PHP', 'Ruby', 'Kotlin', 'Swift', 'Scala',
        'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Express', 'Laravel', 'Rails',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'Ansible',
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Neo4j', 'DynamoDB', 'Cassandra',
        'Git', 'Linux', 'Ubuntu', 'Nginx', 'Apache', 'Grafana', 'Prometheus', 'Kafka', 'Spark', 'Hadoop',
        'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'OpenCV', 'Keras',
        'HTML', 'CSS', 'Bootstrap', 'Tailwind', 'SASS', 'LESS', 'GraphQL', 'Microservices',
        'Blockchain', 'Solidity', 'Ethereum', 'Bitcoin', 'Crypto', 'NFT', 'DeFi'
    ]
    
    # Normalize the description: handle Unicode characters and clean text
    import unicodedata
    description_clean = unicodedata.normalize('NFKD', description).encode('ascii', 'ignore').decode('ascii')
    description_lower = description_clean.lower()
    
    found_tech = []
    
    # Check for technologies, prioritizing longer matches
    for tech in tech_keywords:
        tech_lower = tech.lower()
        # Use word boundaries but handle common variations
        patterns = [
            r'\b' + re.escape(tech_lower) + r'\b',  # Exact match
            r'\b' + re.escape(tech_lower.replace(' ', '')) + r'\b',  # No spaces (e.g., "reactnative")
            r'\b' + re.escape(tech_lower.replace(' ', '-')) + r'\b',  # Hyphenated (e.g., "react-native")
            r'\b' + re.escape(tech_lower.replace(' ', '_')) + r'\b',  # Underscored
            r'\b' + re.escape(tech_lower.replace('.', '')) + r'\b',   # No dots (e.g., "nodejs")
        ]
        
        for pattern in patterns:
            if re.search(pattern, description_lower) and tech not in found_tech:
                found_tech.append(tech)
                break
    
    return found_tech

def extract_urgent_hiring_language(description: str) -> List[str]:
    """Detect urgent hiring phrases"""
    if not description:
        return []
    
    # Normalize description to handle Unicode characters
    import unicodedata
    description_clean = unicodedata.normalize('NFKD', description).encode('ascii', 'ignore').decode('ascii')
    description_lower = description_clean.lower()
    
    # Expanded urgent hiring patterns with more variations
    urgent_patterns = [
        # Direct urgency terms
        r'\basap\b', r'\bimmediate\b', r'\bimmediately\b', r'\burgent\b', r'\brushing\b', 
        r'\bquickly\b', r'\bfast.track\b', r'\bexpedited\b', r'\bhigh.priority\b',
        
        # Hiring timeline urgency
        r'\bstart now\b', r'\bstart immediately\b', r'\bhire immediately\b', r'\bhiring now\b',
        r'\bready to hire\b', r'\bstart monday\b', r'\bstart this week\b', r'\bthis month\b',
        r'\bfill.*position.*quickly\b', r'\bneed.*someone.*asap\b',
        
        # Business urgency indicators  
        r'\bcritical.*hire\b', r'\bcritical.*need\b', r'\bmust.*fill.*soon\b',
        r'\bbackfill.*urgent\b', r'\bstaffing.*emergency\b', r'\bgap.*needs.*filling\b',
        
        # Project urgency
        r'\bproject.*starts.*soon\b', r'\bdeadline.*approaching\b', r'\btight.*timeline\b',
        r'\btime.sensitive\b', r'\bmission.critical\b', r'\bcannot.*delay\b',
        
        # Growth/scaling urgency
        r'\brapid.*growth\b', r'\bscaling.*team\b', r'\bexpanding.*quickly\b',
        r'\bgrowing.*fast\b', r'\baggressive.*hiring\b', r'\bmultiple.*positions\b'
    ]
    
    found_phrases = []
    
    for pattern in urgent_patterns:
        matches = re.findall(pattern, description_lower, re.IGNORECASE | re.DOTALL)
        if matches:
            # Convert back to readable format
            readable_phrase = pattern.replace(r'\b', '').replace(r'.*', ' ').replace('.', ' ')
            found_phrases.extend([readable_phrase.strip()])
    
    return list(set([phrase for phrase in found_phrases if phrase]))

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
    equity_keywords = ['equity', 'stock options', 'rsu', 'ownership', 'shares']
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
        r'\bmanual process\b', r'\bscalability issues\b', r'\bperformance issues\b'
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
    
    print(f"Processing {len(jobs)} jobs for BD signals...")
    
    for idx, job in enumerate(jobs, 1):
        try:
            title = job.get('title', 'Unknown')
            company = job.get('company', 'Unknown')
            print(f"Processing job {idx}/{len(jobs)}: {title} at {company}")
            
            processed_job = process_job_signals(job)
            processed_jobs.append(processed_job)
            
            # Show some findings
            tech_count = len(processed_job.get('technology_adoption', []))
            urgent_count = len(processed_job.get('urgent_hiring_language', []))
            pain_count = len(processed_job.get('pain_points', []))
            
            print(f"   Found: {tech_count} technologies, {urgent_count} urgent signals, {pain_count} pain points")
            
        except Exception as e:
            print(f"Error processing job {idx}: {e}")
            continue
    
    print(f"Successfully processed {len(processed_jobs)} jobs")
    return processed_jobs

def generate_statistics(processed_jobs: List[Dict]) -> Dict:
    """Generate summary statistics"""
    if not processed_jobs:
        return {}
    
    print("Generating statistics...")
    
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
    print("JOB POSTING SIGNAL PROCESSING SUMMARY")
    print("="*60)
    
    print(f"Total Jobs Processed: {stats['total_jobs_processed']}")
    print(f"Processing Date: {stats['processing_date']}")
    
    print(f"\nTOP TECHNOLOGIES:")
    for tech, count in stats['top_technologies'].items():
        print(f"   • {tech}: {count} mentions")
    
    print(f"\nURGENT HIRING:")
    print(f"   • Jobs with urgent language: {stats['urgent_jobs_count']}")
    print(f"   • Percentage: {stats['urgent_percentage']}%")
    
    print(f"\nBUDGET SIGNALS:")
    print(f"   • Jobs with salary info: {stats['jobs_with_salary']}")
    print(f"   • Jobs with equity: {stats['jobs_with_equity']}")
    
    print(f"\nTOP PAIN POINTS:")
    for pain, count in stats['top_pain_points'].items():
        print(f"   • {pain}: {count} mentions")
    
    print(f"\nCOMPANY HIRING VOLUME:")
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
    
    print(f"Saved results to {output_dir}/")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # MongoDB URL from environment
    MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    
    print("Starting Signal Processing Agent (Agent 2)...")
    
    try:
        # Load jobs from MongoDB or JSON fallback
        jobs = []
        try:
            jobs = load_jobs_from_mongo(MONGO_URL)
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            print("Attempting to load from JSON file...")
            
            # Try to load from agent1 output with multiple paths
            possible_paths = [
                "../agent1_data_collector/scraped_jobs.json",
                "agent1_data_collector/scraped_jobs.json",
                "./agent1_data_collector/scraped_jobs.json"
            ]
            
            json_loaded = False
            for json_file in possible_paths:
                if os.path.exists(json_file):
                    with open(json_file, 'r') as f:
                        jobs = json.load(f)
                    print(f"✅ Loaded {len(jobs)} jobs from JSON file")
                    json_loaded = True
                    break
            
            if not json_loaded:
                print("❌ No JSON file found either")
        
        if not jobs:
            print("No jobs found in MongoDB or JSON. Make sure Agent 1 has run successfully.")
            exit(1)
        
        # Process jobs for signals
        processed_jobs = process_jobs(jobs)
        
        if not processed_jobs:
            print("No jobs were processed successfully.")
            exit(1)
        
        # Generate statistics
        stats = generate_statistics(processed_jobs)
        
        # Save to files first (always works)
        save_to_files(processed_jobs, stats)
        
        # Try to save to MongoDB (may fail)
        try:
            save_to_mongo(processed_jobs, MONGO_URL)
            print("✅ Successfully saved to MongoDB")
        except Exception as mongo_error:
            print(f"⚠️ MongoDB save failed: {mongo_error}")
            print("📁 Data saved to JSON files instead")
        
        # Print summary
        print_summary(stats)
        
        print("\n✅ Signal processing completed successfully!")
        print(f"📊 Processed {len(processed_jobs)} jobs")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        print("Make sure input data is available")