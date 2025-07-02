import re
from typing import List, Dict, Any
from collections import Counter

def extract_technology_adoption(description: str) -> List[str]:
    """Extract technology stack keywords from job description."""
    if not description:
        return []
    
    # Comprehensive technology keywords
    tech_keywords = [
        # Programming Languages
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'C#', 'PHP', 'Ruby', 'Swift', 'Kotlin',
        'Scala', 'R', 'MATLAB', 'Perl', 'Dart', 'Elixir', 'Haskell', 'Clojure',
        
        # Frameworks & Libraries
        'React', 'Angular', 'Vue', 'Django', 'Flask', 'FastAPI', 'Spring', 'Express', 'Node.js', 'Next.js',
        'Laravel', 'Rails', 'ASP.NET', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy',
        
        # Cloud & Infrastructure
        'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Jenkins',
        'GitLab CI', 'GitHub Actions', 'CircleCI', 'Helm', 'Istio', 'OpenShift',
        
        # Databases
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra', 'DynamoDB', 'Neo4j',
        'InfluxDB', 'CouchDB', 'SQLite', 'Oracle', 'SQL Server', 'MariaDB',
        
        # DevOps & Tools
        'Git', 'Linux', 'Nginx', 'Apache', 'Grafana', 'Prometheus', 'ELK Stack', 'Splunk', 'Datadog',
        'New Relic', 'Jira', 'Confluence', 'Slack', 'Postman', 'Swagger',
        
        # AI/ML/Data
        'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'MLOps', 'Data Science',
        'Big Data', 'Spark', 'Hadoop', 'Kafka', 'Airflow', 'dbt', 'Snowflake', 'Databricks',
        
        # Frontend
        'HTML', 'CSS', 'SASS', 'LESS', 'Bootstrap', 'Tailwind', 'Material-UI', 'Ant Design',
        
        # Mobile
        'React Native', 'Flutter', 'iOS', 'Android', 'Xamarin',
        
        # Other
        'Microservices', 'REST API', 'GraphQL', 'gRPC', 'Blockchain', 'Solidity', 'Web3'
    ]
    
    found_tech = []
    description_lower = description.lower()
    
    for tech in tech_keywords:
        # Use word boundaries for more accurate matching
        pattern = r'\b' + re.escape(tech.lower()) + r'\b'
        if re.search(pattern, description_lower):
            found_tech.append(tech)
    
    return found_tech

def extract_urgent_hiring_language(description: str) -> List[str]:
    """Detect urgent hiring phrases in job description."""
    if not description:
        return []
    
    urgent_patterns = [
        r'\basap\b',
        r'\bimmediate\b',
        r'\bstart now\b',
        r'\bstart immediately\b',
        r'\burgent\b',
        r'\brushing\b',
        r'\bquickly\b',
        r'\bfast.track\b',
        r'\bexpedite\b',
        r'\bhiring now\b',
        r'\bstart monday\b',
        r'\bstart this week\b',
        r'\bneed someone now\b',
        r'\bfill immediately\b',
        r'\bhigh priority\b',
        r'\btime.sensitive\b',
        r'\bcan you start\b'
    ]
    
    found_phrases = []
    description_lower = description.lower()
    
    for pattern in urgent_patterns:
        matches = re.findall(pattern, description_lower)
        found_phrases.extend(matches)
    
    return list(set(found_phrases))  # Remove duplicates

def extract_budget_signals(description: str) -> Dict[str, Any]:
    """Extract salary ranges and budget information from job description."""
    if not description:
        return {}
    
    budget_info = {
        'salary_ranges': [],
        'hourly_rates': [],
        'equity_mentions': [],
        'budget_phrases': []
    }
    
    # Salary range patterns
    salary_patterns = [
        r'\$\d{1,3}(?:,\d{3})*(?:\s*-\s*\$?\d{1,3}(?:,\d{3})*)?k?\b',  # $120k, $80,000-$120,000
        r'€\d{1,3}(?:,\d{3})*(?:\s*-\s*€?\d{1,3}(?:,\d{3})*)?k?\b',     # €80k, €60,000-€80,000
        r'£\d{1,3}(?:,\d{3})*(?:\s*-\s*£?\d{1,3}(?:,\d{3})*)?k?\b',     # £60k, £45,000-£60,000
        r'\d{1,3}(?:,\d{3})*\s*-\s*\d{1,3}(?:,\d{3})*\s*(?:USD|EUR|GBP|CAD)\b'  # 80,000-120,000 USD
    ]
    
    # Hourly rate patterns
    hourly_patterns = [
        r'\$\d{1,3}(?:\.\d{2})?(?:\s*-\s*\$?\d{1,3}(?:\.\d{2})?)?\s*/?\s*(?:hour|hr|h)\b',  # $50/hour, $40-60/hr
        r'€\d{1,3}(?:\.\d{2})?(?:\s*-\s*€?\d{1,3}(?:\.\d{2})?)?\s*/?\s*(?:hour|hr|h)\b',
        r'£\d{1,3}(?:\.\d{2})?(?:\s*-\s*£?\d{1,3}(?:\.\d{2})?)?\s*/?\s*(?:hour|hr|h)\b'
    ]
    
    # Equity patterns
    equity_patterns = [
        r'\bequity\b',
        r'\bstock options\b',
        r'\brsus?\b',
        r'\bownership\b',
        r'\bshares\b',
        r'\bvesting\b'
    ]
    
    # Budget-related phrases
    budget_phrases = [
        r'\bcompetitive salary\b',
        r'\bmarket rate\b',
        r'\bcommensurate with experience\b',
        r'\bdepending on experience\b',
        r'\bnegotiable\b',
        r'\btop of market\b',
        r'\babove market\b'
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
    
    # Extract equity mentions
    for pattern in equity_patterns:
        if re.search(pattern, description_lower):
            budget_info['equity_mentions'].append(pattern.strip('\\b'))
    
    # Extract budget phrases
    for pattern in budget_phrases:
        if re.search(pattern, description_lower):
            budget_info['budget_phrases'].append(pattern.strip('\\b'))
    
    return budget_info

def extract_pain_points(description: str) -> List[str]:
    """Detect mentions of legacy systems, technical debt, and pain points."""
    if not description:
        return []
    
    pain_point_patterns = [
        r'\blegacy system\b',
        r'\blegacy code\b',
        r'\blegacy\b',
        r'\btechnical debt\b',
        r'\btech debt\b',
        r'\bmaintenance\b',
        r'\brefactor\b',
        r'\bmodernize\b',
        r'\bmigrat\w+\b',
        r'\bupgrade\b',
        r'\breplace\b',
        r'\bold system\b',
        r'\boutdated\b',
        r'\bobsolete\b',
        r'\bdeprecated\b',
        r'\bintegration issues\b',
        r'\bintegration challenges\b',
        r'\bdata silos\b',
        r'\bmanual process\b',
        r'\binefficient\b',
        r'\bscalability issues\b',
        r'\bperformance issues\b',
        r'\btechnical challenges\b',
        r'\barchitecture\b',
        r'\bredesign\b',
        r'\brevamp\b'
    ]
    
    found_pain_points = []
    description_lower = description.lower()
    
    for pattern in pain_point_patterns:
        matches = re.findall(pattern, description_lower)
        found_pain_points.extend(matches)
    
    return list(set(found_pain_points))  # Remove duplicates

def extract_skills_mentioned(description: str) -> List[str]:
    """Extract commonly mentioned skills from job description."""
    if not description:
        return []
    
    # Skills beyond just technology
    skills_keywords = [
        # Technical Skills
        'API development', 'Database design', 'System architecture', 'Code review', 'Testing',
        'Unit testing', 'Integration testing', 'Debugging', 'Performance optimization',
        'Security', 'Scalability', 'Monitoring', 'Logging', 'Documentation',
        
        # Soft Skills
        'Leadership', 'Communication', 'Problem solving', 'Team collaboration', 'Mentoring',
        'Project management', 'Agile', 'Scrum', 'Kanban', 'Planning', 'Analytical thinking',
        
        # Domain Knowledge
        'Financial services', 'Healthcare', 'E-commerce', 'Gaming', 'Education',
        'Marketing', 'Sales', 'Customer service', 'Product management', 'Business analysis',
        
        # Methodologies
        'CI/CD', 'DevOps', 'MLOps', 'DataOps', 'Automation', 'Quality assurance',
        'Code quality', 'Best practices', 'Design patterns', 'SOLID principles'
    ]
    
    found_skills = []
    description_lower = description.lower()
    
    for skill in skills_keywords:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, description_lower):
            found_skills.append(skill)
    
    # Also include technology from the tech extraction
    tech_skills = extract_technology_adoption(description)
    found_skills.extend(tech_skills)
    
    return list(set(found_skills))  # Remove duplicates

def calculate_hiring_volume_by_company(jobs: List[Dict]) -> Dict[str, int]:
    """Calculate hiring volume per company."""
    company_counts = Counter()
    
    for job in jobs:
        company = job.get('company', 'Unknown')
        if company and company != 'Unknown':
            company_counts[company] += 1
    
    return dict(company_counts)

def process_job_signals(job: Dict) -> Dict:
    """Process all signals for a single job posting."""
    description = job.get('description', '')
    
    signals = {
        'technology_adoption': extract_technology_adoption(description),
        'urgent_hiring_language': extract_urgent_hiring_language(description),
        'budget_signals': extract_budget_signals(description),
        'pain_points': extract_pain_points(description),
        'skills_mentioned': extract_skills_mentioned(description),
        'signal_processing_date': None  # Will be set in processor.py
    }
    
    # Combine original job data with signals
    processed_job = job.copy()
    processed_job.update(signals)
    
    return processed_job