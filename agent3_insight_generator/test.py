#!/usr/bin/env python3
"""
Simple test of Agent 3 insight generation logic
"""

import json
import datetime
import os
from collections import Counter, defaultdict

def analyze_company_hiring_patterns(company_jobs):
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
        'ai_ml': sum(1 for title in titles if any(word in title for word in ['ai', 'ml', 'machine learning', 'data scientist'])),
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
    if job_count >= 2:
        if urgent_percentage >= 75:
            insights.append(f"is in aggressive hiring mode with {job_count} open positions, {urgent_percentage:.0f}% marked as urgent, indicating rapid scaling or critical staffing needs")
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
        elif len(set(tech for tech, _ in top_tech)) >= 2:
            insights.append(f"is building diverse technical capabilities across {tech_focus}")
    
    # 3. Role-specific insights
    if role_patterns['senior'] >= 1:
        insights.append("is prioritizing senior-level hires, suggesting complex technical challenges or leadership expansion")
    
    if role_patterns['ai_ml'] >= 1:
        insights.append("is making investments in AI/ML talent, indicating strategic focus on artificial intelligence capabilities")
    
    if role_patterns['security'] >= 1:
        insights.append("is strengthening security capabilities, potentially due to compliance requirements or security incidents")
    
    # 4. Budget and compensation insights
    if len(equity_jobs) >= 1:
        insights.append("is offering equity compensation, indicating startup growth phase or retention strategy")
    
    # 5. Technical debt and modernization insights
    legacy_mentions = pain_counter.get('legacy', 0) + pain_counter.get('modernize', 0) + pain_counter.get('technical debt', 0)
    if legacy_mentions >= 1:
        insights.append("is undergoing technical modernization, with roles focused on legacy system updates and technical debt reduction")
    
    return insights[:2]  # Return top 2 insights

def generate_company_insights(processed_signals):
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

def analyze_industry_trends(all_signals):
    """Analyze trends across all companies"""
    
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

def print_insights_summary(insights, industry_trends):
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
    """Test Agent 3 with Agent 2 data"""
    print("🧪 Testing Agent 3 Insight Generation...")
    
    # Load Agent 2 output
    agent2_output_file = "../agent2_signal_processor/output/signals_output.json"
    
    if os.path.exists(agent2_output_file):
        print(f"📥 Loading Agent 2 output from {agent2_output_file}")
        with open(agent2_output_file, 'r') as f:
            processed_signals = json.load(f)
    else:
        print("📝 Using sample data (Agent 2 output not found)")
        processed_signals = [
            {
                "title": "Senior Python Developer",
                "company": "TechCorp",
                "location": "Remote",
                "technology_adoption": ["Python", "AWS"],
                "urgent_hiring_language": ["asap"],
                "budget_signals": {"salary_ranges": ["$120k"], "equity_mentions": []},
                "pain_points": ["legacy system", "migration", "legacy"],
                "scraped_date": "2024-01-15"
            },
            {
                "title": "React Frontend Engineer",
                "company": "StartupInc",
                "location": "San Francisco",
                "technology_adoption": ["TypeScript", "React", "Node.js"],
                "urgent_hiring_language": [],
                "budget_signals": {"salary_ranges": ["€80,000"], "equity_mentions": []},
                "pain_points": ["modernize", "technical debt"],
                "scraped_date": "2024-01-15"
            },
            {
                "title": "DevOps Engineer",
                "company": "CloudCorp",
                "location": "New York",
                "technology_adoption": ["Docker", "Kubernetes", "Jenkins"],
                "urgent_hiring_language": ["urgent"],
                "budget_signals": {"salary_ranges": [], "equity_mentions": []},
                "pain_points": [],
                "scraped_date": "2024-01-15"
            }
        ]
    
    print(f"📊 Processing {len(processed_signals)} job signals...")
    
    # Generate insights
    company_insights = generate_company_insights(processed_signals)
    industry_trends = analyze_industry_trends(processed_signals)
    
    # Print summary
    print_insights_summary(company_insights, industry_trends)
    
    # Save results
    os.makedirs("output", exist_ok=True)
    
    with open("output/company_insights.json", 'w') as f:
        json.dump(company_insights, f, indent=2)
    
    with open("output/industry_trends.json", 'w') as f:
        json.dump(industry_trends, f, indent=2)
    
    print(f"\n✅ Agent 3 test completed successfully!")
    print(f"📁 Results saved to output/ directory")

if __name__ == "__main__":
    main()