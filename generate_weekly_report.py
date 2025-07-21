#!/usr/bin/env python3
"""
Weekly BD Intelligence Report Generator
Automated weekly analysis with trend comparison
"""
import json
import os
import datetime
from collections import Counter, defaultdict

def load_previous_week_data():
    """Load previous week's data for comparison"""
    try:
        with open("data/weekly_archive/previous_week.json", "r") as f:
            return json.load(f)
    except:
        return None

def archive_current_week_data():
    """Archive current week's data"""
    os.makedirs("data/weekly_archive", exist_ok=True)
    
    # Load current data
    try:
        with open("data/business_intelligence.json", "r") as f:
            current_data = json.load(f)
        
        # Save as previous week for next time
        with open("data/weekly_archive/previous_week.json", "w") as f:
            json.dump({
                "date": datetime.datetime.now().isoformat(),
                "data": current_data
            }, f, indent=2)
        
        return current_data
    except:
        return []

def compare_weekly_trends(current_data, previous_data):
    """Compare current week vs previous week"""
    if not previous_data:
        return {"message": "No previous week data for comparison"}
    
    prev_companies = set(item['company'] for item in previous_data.get('data', []))
    current_companies = set(item['company'] for item in current_data)
    
    new_companies = current_companies - prev_companies
    lost_companies = prev_companies - current_companies
    
    # Compare high priority opportunities
    prev_high_priority = len([item for item in previous_data.get('data', []) 
                             if item.get('priority_level') == 'High'])
    current_high_priority = len([item for item in current_data 
                                if item.get('priority_level') == 'High'])
    
    return {
        "new_companies": list(new_companies),
        "lost_companies": list(lost_companies),
        "high_priority_change": current_high_priority - prev_high_priority,
        "total_companies_change": len(current_companies) - len(prev_companies)
    }

def identify_new_opportunities(current_data, previous_data):
    """Identify new high-value opportunities this week"""
    new_opportunities = []
    
    if not previous_data:
        # All current high-priority are "new"
        new_opportunities = [item for item in current_data 
                           if item.get('priority_level') == 'High']
    else:
        prev_companies = set(item['company'] for item in previous_data.get('data', []))
        
        for item in current_data:
            if (item.get('priority_level') == 'High' and 
                item['company'] not in prev_companies):
                new_opportunities.append(item)
    
    return new_opportunities

def analyze_market_shifts():
    """Analyze technology and market trend shifts"""
    try:
        with open("data/market_intelligence.json", "r") as f:
            market_data = json.load(f)
        
        hot_tech = market_data.get('hot_technologies', [])[:5]
        pain_points = market_data.get('top_market_pain_points', [])[:3]
        
        return {
            "trending_technologies": hot_tech,
            "market_pain_points": pain_points,
            "urgency_rate": market_data.get('market_urgency_rate', 0),
            "ai_adoption_rate": market_data.get('ai_ml_adoption_rate', 0)
        }
    except:
        return {}

def generate_recommended_actions(new_opportunities, trends):
    """Generate specific recommended actions for BD team"""
    actions = []
    
    # Actions based on new opportunities
    for opp in new_opportunities[:3]:  # Top 3
        company = opp['company']
        services = opp.get('recommended_services', [])[:2]
        timing = opp.get('contact_timing', 'Within 2 weeks')
        
        actions.append({
            "action": f"Contact {company} immediately",
            "rationale": f"High-priority opportunity ({opp['opportunity_score']} score)",
            "recommended_services": services,
            "timing": timing,
            "contact_method": "Direct outreach via LinkedIn + email"
        })
    
    # Actions based on market trends
    if trends.get('urgency_rate', 0) > 40:
        actions.append({
            "action": "Prepare rapid-deployment service packages",
            "rationale": f"Market urgency rate at {trends['urgency_rate']:.1f}%",
            "timing": "This week",
            "contact_method": "Update sales materials and proposals"
        })
    
    # Technology-specific actions
    trending_tech = trends.get('trending_technologies', [])
    if trending_tech:
        top_tech = trending_tech[0][0] if trending_tech[0] else "AI/ML"
        actions.append({
            "action": f"Develop {top_tech} case studies and expertise marketing",
            "rationale": f"{top_tech} is most in-demand technology",
            "timing": "Next 2 weeks",
            "contact_method": "Content marketing and thought leadership"
        })
    
    return actions

def create_weekly_report():
    """Create comprehensive weekly BD intelligence report"""
    
    # Get current data
    current_data = archive_current_week_data()
    previous_data = load_previous_week_data()
    
    # Analyze trends and opportunities
    weekly_trends = compare_weekly_trends(current_data, previous_data)
    new_opportunities = identify_new_opportunities(current_data, previous_data)
    market_shifts = analyze_market_shifts()
    recommended_actions = generate_recommended_actions(new_opportunities, market_shifts)
    
    # Create report
    report = {
        "report_date": datetime.datetime.now().isoformat(),
        "report_period": "Weekly",
        "executive_summary": {
            "total_companies_analyzed": len(current_data),
            "new_high_priority_opportunities": len(new_opportunities),
            "weekly_change_in_opportunities": weekly_trends.get('high_priority_change', 0),
            "market_urgency_level": market_shifts.get('urgency_rate', 0)
        },
        "new_opportunities": new_opportunities[:5],  # Top 5
        "weekly_trends": weekly_trends,
        "market_analysis": market_shifts,
        "recommended_actions": recommended_actions,
        "next_week_focus": [
            "Follow up on high-priority contacts",
            "Monitor technology trend shifts",
            "Update service offerings based on market demands"
        ]
    }
    
    return report

def format_weekly_report_email(report):
    """Format report for email distribution"""
    
    email_body = f"""
FOQAL BD INTELLIGENCE - WEEKLY REPORT
Report Date: {datetime.datetime.now().strftime('%Y-%m-%d')}

EXECUTIVE SUMMARY:
  • Companies Analyzed: {report['executive_summary']['total_companies_analyzed']}
  • New High-Priority Opportunities: {report['executive_summary']['new_high_priority_opportunities']}
  • Weekly Change: {report['executive_summary']['weekly_change_in_opportunities']:+d}
  • Market Urgency: {report['executive_summary']['market_urgency_level']:.1f}%

NEW HIGH-PRIORITY OPPORTUNITIES:
"""
    
    for i, opp in enumerate(report['new_opportunities'], 1):
        email_body += f"""
  {i}. {opp['company']} (Score: {opp['opportunity_score']})
     Services: {', '.join(opp.get('recommended_services', [])[:2])}
     Contact: {opp.get('contact_timing', 'Within 2 weeks')}
     Insight: {opp['business_insights'][0] if opp.get('business_insights') else 'Strategic opportunity'}
"""
    
    email_body += f"""
MARKET TRENDS THIS WEEK:
  • Trending Tech: {', '.join([f'{tech} ({count})' for tech, count in report['market_analysis'].get('trending_technologies', [])[:3]])}
  • Key Pain Points: {', '.join([f'{pain} ({count})' for pain, count in report['market_analysis'].get('market_pain_points', [])[:2]])}

RECOMMENDED ACTIONS:
"""
    
    for i, action in enumerate(report['recommended_actions'], 1):
        email_body += f"""
  {i}. {action['action']}
     Rationale: {action['rationale']}
     Timing: {action['timing']}
"""
    
    email_body += f"""
NEXT WEEK FOCUS:
"""
    for focus in report['next_week_focus']:
        email_body += f"  • {focus}\n"
    
    email_body += """
---
Generated by Foqal BD Intelligence System
For questions contact: [BD Operations Team]
"""
    
    return email_body

def save_and_distribute_report():
    """Save report and prepare for distribution"""
    
    # Use existing data for report generation
    # Note: Run the pipeline manually before generating reports
    print("Using existing data for report generation...")
    
    # Generate report
    print("Generating weekly report...")
    report = create_weekly_report()
    
    # Save report files
    os.makedirs("reports/weekly", exist_ok=True)
    
    report_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Save JSON report
    with open(f"reports/weekly/bd_report_{report_date}.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Save email-formatted report
    email_report = format_weekly_report_email(report)
    with open(f"reports/weekly/bd_report_{report_date}.txt", "w") as f:
        f.write(email_report)
    
    # Print summary to console
    print("\n" + "="*60)
    print("WEEKLY BD INTELLIGENCE REPORT GENERATED")
    print("="*60)
    print(email_report)
    print("="*60)
    print(f"Reports saved:")
    print(f"  • reports/weekly/bd_report_{report_date}.json")
    print(f"  • reports/weekly/bd_report_{report_date}.txt")
    print("\nWeekly report generation completed!")
    
    return report

if __name__ == "__main__":
    save_and_distribute_report()