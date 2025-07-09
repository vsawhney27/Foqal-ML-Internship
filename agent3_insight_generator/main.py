#!/usr/bin/env python3
"""
Agent 3: Insight Generator
Analyzes processed signals from Agent 2 and generates business development insights

Follows the same simple pattern as Agent 1 and Agent 2 for consistency.
"""

from pymongo import MongoClient
import json
import datetime
import os
from collections import Counter, defaultdict
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_processed_signals_from_mongo(db_url, db_name="JobPosting", collection_name="ProcessedJobs"):
    """Load processed signals from MongoDB - same pattern as other agents"""
    client = MongoClient(db_url)
    db = client[db_name]
    collection = db[collection_name]
    
    signals = list(collection.find())
    print(f"📥 Loaded {len(signals)} processed job signals from MongoDB")
    client.close()
    return signals

def save_insights_to_mongo(insights, db_url, db_name="JobPosting", collection_name="insights"):
    """Save insights to MongoDB - same pattern as other agents"""
    client = MongoClient(db_url)
    db = client[db_name]
    collection = db[collection_name]
    
    if insights:
        # Clear existing insights
        collection.delete_many({})
        collection.insert_many(insights)
        print(f"✅ Inserted {len(insights)} company insights into MongoDB")
    else:
        print("⚠️ No insights to insert")
    
    client.close()

def analyze_company_hiring_patterns(company_jobs: List[Dict]) -> List[str]:
    """Analyze hiring patterns for a single company"""
    insights = []
    
    # Analyze job volume and urgency
    job_count = len(company_jobs)
    urgent_jobs = [job for job in company_jobs if job.get('urgent_hiring_language', [])]
    urgent_percentage = (len(urgent_jobs) / job_count) * 100 if job_count > 0 else 0
    
    # Analyze technologies
    all_tech = []
    for job in company_jobs:
        all_tech.extend(job.get('technology_adoption', []))
    tech_counter = Counter(all_tech)
    top_tech = tech_counter.most_common(3)
    
    # Analyze roles and departments
    titles = [job.get('title', '').lower() for job in company_jobs]
    role_patterns = {
        'senior': sum(1 for title in titles if 'senior' in title),
        'engineer': sum(1 for title in titles if 'engineer' in title),
        'developer': sum(1 for title in titles if 'developer' in title),
        'data': sum(1 for title in titles if any(word in title for word in ['data', 'analyst', 'scientist'])),
        'ai_ml': sum(1 for title in titles if any(word in title for word in ['ai', 'ml', 'machine learning', 'artificial intelligence'])),
        'frontend': sum(1 for title in titles if any(word in title for word in ['frontend', 'front-end', 'react', 'angular', 'vue'])),
        'backend': sum(1 for title in titles if any(word in title for word in ['backend', 'back-end', 'api'])),
        'devops': sum(1 for title in titles if any(word in title for word in ['devops', 'infrastructure', 'cloud', 'deployment'])),
        'security': sum(1 for title in titles if 'security' in title)
    }
    
    # Analyze budget signals
    salary_jobs = [job for job in company_jobs if job.get('budget_signals', {}).get('salary_ranges', [])]
    equity_jobs = [job for job in company_jobs if job.get('budget_signals', {}).get('equity_mentions', [])]
    
    # Analyze pain points
    all_pain_points = []
    for job in company_jobs:
        all_pain_points.extend(job.get('pain_points', []))
    pain_counter = Counter(all_pain_points)
    
    # Generate insights based on analysis
    
    # 1. Hiring volume and urgency insights
    if job_count >= 3:
        if urgent_percentage >= 75:
            insights.append(f"is in aggressive hiring mode with {job_count} open positions, {urgent_percentage:.0f}% marked as urgent, indicating rapid scaling or critical staffing needs")
        elif job_count >= 5:
            insights.append(f"is expanding significantly with {job_count} open positions across multiple roles, suggesting strong growth trajectory")
        else:
            insights.append(f"is actively hiring for {job_count} positions, indicating steady growth and team expansion")
    elif urgent_percentage >= 50:
        insights.append("has urgent hiring needs, suggesting either rapid growth or critical skill gaps that need immediate filling")
    
    # 2. Technology and specialization insights
    if top_tech:
        tech_focus = ", ".join([f"{tech} ({count} roles)" for tech, count in top_tech])
        if any(tech.lower() in ['ai', 'ml', 'tensorflow', 'pytorch', 'machine learning'] for tech, _ in top_tech):
            insights.append(f"is heavily investing in AI/ML capabilities, with focus on {tech_focus}")
        elif any(tech.lower() in ['aws', 'azure', 'gcp', 'kubernetes', 'docker'] for tech, _ in top_tech):
            insights.append(f"is prioritizing cloud infrastructure and DevOps, with emphasis on {tech_focus}")
        elif len(set(tech for tech, _ in top_tech)) >= 3:
            insights.append(f"is building diverse technical capabilities across {tech_focus}")
    
    # 3. Role-specific insights
    if role_patterns['senior'] >= 2:
        insights.append("is prioritizing senior-level hires, suggesting complex technical challenges or leadership expansion")
    
    if role_patterns['ai_ml'] >= 2:
        insights.append("is making significant investments in AI/ML talent, indicating strategic focus on artificial intelligence capabilities")
    
    if role_patterns['security'] >= 1:
        insights.append("is strengthening security capabilities, potentially due to compliance requirements or security incidents")
    
    if role_patterns['data'] >= 2:
        insights.append("is building strong data analytics capabilities, suggesting data-driven decision making initiatives")
    
    # 4. Budget and compensation insights
    if len(equity_jobs) >= 2:
        insights.append("is offering equity compensation across multiple roles, indicating startup growth phase or retention strategy")
    
    if len(salary_jobs) >= job_count * 0.8:  # 80% of jobs have salary info
        insights.append("is transparent about compensation, suggesting competitive hiring market or employer branding strategy")
    
    # 5. Technical debt and modernization insights
    legacy_mentions = pain_counter.get('legacy', 0) + pain_counter.get('modernize', 0) + pain_counter.get('technical debt', 0)
    if legacy_mentions >= 2:
        insights.append("is undergoing significant technical modernization, with multiple roles focused on legacy system updates and technical debt reduction")
    
    # 6. Scale and performance insights
    scale_mentions = pain_counter.get('scalability issues', 0) + pain_counter.get('performance issues', 0)
    if scale_mentions >= 1:
        insights.append("is facing scaling challenges, hiring talent to address performance and infrastructure bottlenecks")
    
    return insights[:2]  # Return top 2 insights to avoid overwhelming

def analyze_industry_trends(all_signals: List[Dict]) -> Dict[str, Any]:
    """Analyze trends across all companies (stretch goal)"""
    
    # Technology trends
    all_tech = []
    for signal in all_signals:
        all_tech.extend(signal.get('technology_adoption', []))
    
    tech_trends = Counter(all_tech).most_common(10)
    
    # Urgent hiring trends
    urgent_companies = set()
    for signal in all_signals:
        if signal.get('urgent_hiring_language', []):
            urgent_companies.add(signal.get('company', 'Unknown'))
    
    # Budget trends
    salary_mentions = []
    for signal in all_signals:
        salary_mentions.extend(signal.get('budget_signals', {}).get('salary_ranges', []))
    
    # Pain point trends
    all_pain_points = []
    for signal in all_signals:
        all_pain_points.extend(signal.get('pain_points', []))
    
    pain_trends = Counter(all_pain_points).most_common(5)
    
    return {
        'top_technologies': tech_trends,
        'urgent_hiring_companies_count': len(urgent_companies),
        'total_companies': len(set(signal.get('company', 'Unknown') for signal in all_signals)),
        'top_pain_points': pain_trends,
        'analysis_date': datetime.datetime.now().isoformat()
    }

def generate_company_insights(processed_signals: List[Dict]) -> List[Dict]:
    """Generate insights for each company"""
    
    # Group signals by company
    company_jobs = defaultdict(list)
    for signal in processed_signals:
        company = signal.get('company', 'Unknown')
        if company != 'Unknown':
            company_jobs[company].append(signal)
    
    insights = []
    current_time = datetime.datetime.now().isoformat()
    
    print(f"🔍 Analyzing {len(company_jobs)} companies...")
    
    for company, jobs in company_jobs.items():
        print(f"📊 Analyzing {company} ({len(jobs)} jobs)")
        
        company_insights = analyze_company_hiring_patterns(jobs)
        
        if company_insights:
            insight_doc = {
                "company": company,
                "insights": [f"{company} {insight}" for insight in company_insights],
                "job_count": len(jobs),
                "timestamp": current_time,
                "analysis_metadata": {
                    "total_technologies": len(set(tech for job in jobs for tech in job.get('technology_adoption', []))),
                    "urgent_jobs": len([job for job in jobs if job.get('urgent_hiring_language', [])]),
                    "budget_transparency": len([job for job in jobs if job.get('budget_signals', {}).get('salary_ranges', [])]),
                    "pain_points_mentioned": len([job for job in jobs if job.get('pain_points', [])])
                }
            }
            
            insights.append(insight_doc)
            
            # Print insights for review
            print(f"   💡 Generated {len(company_insights)} insights:")
            for insight in insight_doc['insights']:
                print(f"      • {insight}")
    
    return insights

def create_sample_processed_signals():
    """Create sample data for testing when MongoDB is unavailable"""
    return [
        {
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "location": "Remote",
            "technology_adoption": ["Python", "AWS", "Docker", "PostgreSQL"],
            "urgent_hiring_language": ["asap", "urgent"],
            "budget_signals": {"salary_ranges": ["$120k-150k"], "equity_mentions": []},
            "pain_points": ["legacy system", "modernize"],
            "scraped_date": "2024-01-15"
        },
        {
            "title": "Machine Learning Engineer",
            "company": "TechCorp", 
            "location": "Remote",
            "technology_adoption": ["Python", "TensorFlow", "AWS", "Kubernetes"],
            "urgent_hiring_language": ["immediate"],
            "budget_signals": {"salary_ranges": ["$160k-200k"], "equity_mentions": ["equity"]},
            "pain_points": ["scalability issues"],
            "scraped_date": "2024-01-15"
        },
        {
            "title": "React Frontend Engineer",
            "company": "StartupInc",
            "location": "San Francisco", 
            "technology_adoption": ["React", "TypeScript", "Node.js"],
            "urgent_hiring_language": ["start this week"],
            "budget_signals": {"salary_ranges": ["€80k-100k"], "equity_mentions": ["equity", "stock options"]},
            "pain_points": ["legacy code", "performance issues"],
            "scraped_date": "2024-01-15"
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudCorp",
            "location": "New York",
            "technology_adoption": ["Kubernetes", "Docker", "AWS", "Jenkins"],
            "urgent_hiring_language": ["urgent"],
            "budget_signals": {"salary_ranges": ["$140k"], "equity_mentions": []},
            "pain_points": ["scalability issues", "modernize"],
            "scraped_date": "2024-01-15"
        },
        {
            "title": "Data Scientist",
            "company": "DataCorp",
            "location": "Boston",
            "technology_adoption": ["Python", "TensorFlow", "AWS"],
            "urgent_hiring_language": ["asap"],
            "budget_signals": {"salary_ranges": ["$140k-180k"], "equity_mentions": ["stock options"]},
            "pain_points": ["modernize"],
            "scraped_date": "2024-01-15"
        },
        {
            "title": "Security Engineer",
            "company": "SecureTech",
            "location": "Seattle",
            "technology_adoption": ["Python", "AWS", "Linux"],
            "urgent_hiring_language": ["start this week"],
            "budget_signals": {"salary_ranges": ["$130k-160k"], "equity_mentions": []},
            "pain_points": ["modernize"],
            "scraped_date": "2024-01-15"
        }
    ]

def save_to_files(insights: List[Dict], industry_trends: Dict, output_dir: str = "output"):
    """Save results to JSON files"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save company insights
    insights_file = os.path.join(output_dir, "company_insights.json")
    with open(insights_file, 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)
    
    # Save industry trends
    trends_file = os.path.join(output_dir, "industry_trends.json")
    with open(trends_file, 'w', encoding='utf-8') as f:
        json.dump(industry_trends, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved insights to {output_dir}/")

def print_insights_summary(insights: List[Dict], industry_trends: Dict):
    """Print a summary of generated insights"""
    print("\n" + "="*70)
    print("📊 BUSINESS DEVELOPMENT INSIGHTS SUMMARY")
    print("="*70)
    
    print(f"🏢 Companies Analyzed: {len(insights)}")
    print(f"🕒 Analysis Date: {insights[0]['timestamp'] if insights else 'N/A'}")
    
    print(f"\n💡 KEY COMPANY INSIGHTS:")
    for insight_doc in insights:
        company = insight_doc['company']
        job_count = insight_doc['job_count']
        print(f"\n🏢 {company} ({job_count} jobs analyzed):")
        for insight in insight_doc['insights']:
            print(f"   • {insight}")
    
    print(f"\n🌐 INDUSTRY TRENDS:")
    print(f"   • Top Technologies: {', '.join([f'{tech} ({count})' for tech, count in industry_trends['top_technologies'][:5]])}")
    print(f"   • Companies with Urgent Hiring: {industry_trends['urgent_hiring_companies_count']}/{industry_trends['total_companies']}")
    print(f"   • Top Pain Points: {', '.join([f'{pain} ({count})' for pain, count in industry_trends['top_pain_points'][:3]])}")
    
    print("="*70)

def main():
    """Main execution function"""
    # MongoDB URL - same as other agents
    MONGO_URL = os.getenv("MONGODB_URL", "mongodb+srv://adityabramhe7:C3kg0TDi21QaKOAM@jobposting.tgcylyz.mongodb.net/")
    
    print("🚀 Starting Business Development Insight Generator (Agent 3)...")
    
    try:
        # Load processed signals from MongoDB
        try:
            processed_signals = load_processed_signals_from_mongo(MONGO_URL)
        except Exception as e:
            print(f"⚠️ MongoDB connection failed: {e}")
            print("🔄 Using sample data instead...")
            processed_signals = create_sample_processed_signals()
        
        if not processed_signals:
            print("❌ No processed signals found. Make sure Agent 2 has run successfully.")
            return
        
        # Generate company insights
        company_insights = generate_company_insights(processed_signals)
        
        if not company_insights:
            print("❌ No insights were generated.")
            return
        
        # Analyze industry trends (stretch goal)
        industry_trends = analyze_industry_trends(processed_signals)
        
        # Save to MongoDB
        try:
            save_insights_to_mongo(company_insights, MONGO_URL)
        except Exception as e:
            print(f"⚠️ MongoDB save failed: {e}")
            print("💾 Results saved to files instead")
        
        # Save to files
        save_to_files(company_insights, industry_trends)
        
        # Print summary
        print_insights_summary(company_insights, industry_trends)
        
        print(f"\n✅ Generated {len(company_insights)} company insights successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Check that Agent 2 has processed job signals")

if __name__ == "__main__":
    main()