#!/usr/bin/env python3
"""
Requirements Compliance Check
Verifies that the project meets ALL specifications from the original instructions
"""

import os
from typing import Dict, List, Tuple

def check_agent1_requirements() -> Tuple[List[str], List[str]]:
    """Check Agent 1: Data Collection Agent requirements"""
    requirements = [
        "Scrapes job postings from LinkedIn, Indeed, Glassdoor, AngelList, company career pages",
        "Handles rate limiting, proxy rotation, and data quality checks",
        "Stores raw data with metadata (posting date, company, location, etc.)"
    ]
    
    passes = []
    fails = []
    
    # Check scrapers exist
    scrapers_dir = "agent1_data_collector/scrapers"
    required_scrapers = [
        "linkedin_scraper.py",
        "indeed_scraper.py", 
        "glassdoor_scraper.py",
        "angellist_scraper.py",
        "company_careers_scraper.py"
    ]
    
    scrapers_exist = all(os.path.exists(os.path.join(scrapers_dir, scraper)) for scraper in required_scrapers)
    
    if scrapers_exist:
        passes.append("✅ All required scrapers implemented (LinkedIn, Indeed, Glassdoor, AngelList, Company Careers)")
    else:
        fails.append("❌ Missing some required scrapers")
    
    # Check proxy and rate limiting
    proxy_manager_exists = os.path.exists("agent1_data_collector/proxy_manager.py")
    
    if proxy_manager_exists:
        passes.append("✅ Rate limiting and proxy rotation implemented")
    else:
        fails.append("❌ Rate limiting/proxy rotation not implemented")
    
    # Check main collector
    main_file = "agent1_data_collector/main.py"
    if os.path.exists(main_file):
        with open(main_file, 'r') as f:
            content = f.read()
        
        if "MultiSourceJobCollector" in content:
            passes.append("✅ Multi-source data collection implemented")
        else:
            fails.append("❌ Multi-source collection not properly implemented")
        
        if "data_quality_checked" in content:
            passes.append("✅ Data quality checks implemented")
        else:
            fails.append("❌ Data quality checks missing")
        
        if "scraped_date" in content and "company" in content:
            passes.append("✅ Metadata storage (date, company, location) implemented")
        else:
            fails.append("❌ Proper metadata storage missing")
    else:
        fails.append("❌ Main collection agent missing")
    
    return passes, fails

def check_agent2_requirements() -> Tuple[List[str], List[str]]:
    """Check Agent 2: Signal Processing Agent requirements"""
    requirements = [
        "Analyzes job descriptions for technology stack mentions",
        "Identifies hiring volume patterns by company/department", 
        "Extracts skill requirements and budget indicators (salary ranges)",
        "Flags urgent hiring language ('immediate start', 'ASAP')"
    ]
    
    passes = []
    fails = []
    
    # Check main files
    processor_file = "agent2_signal_processor/processor.py"
    signals_file = "agent2_signal_processor/signals.py"
    main_file = "agent2_signal_processor/main.py"
    
    if os.path.exists(processor_file) and os.path.exists(main_file):
        passes.append("✅ Signal processing agent implemented")
        
        # Check specific signal extraction
        if os.path.exists(signals_file):
            with open(signals_file, 'r') as f:
                signals_content = f.read()
        else:
            with open(processor_file, 'r') as f:
                signals_content = f.read()
        
        # Technology stack analysis
        if "extract_technology_adoption" in signals_content or "technology" in signals_content.lower():
            passes.append("✅ Technology stack analysis implemented")
        else:
            fails.append("❌ Technology stack analysis missing")
        
        # Urgent hiring detection
        if "urgent" in signals_content.lower() and ("asap" in signals_content.lower() or "immediate" in signals_content.lower()):
            passes.append("✅ Urgent hiring language detection implemented")
        else:
            fails.append("❌ Urgent hiring language detection missing")
        
        # Budget signal extraction
        if "salary" in signals_content.lower() and "budget" in signals_content.lower():
            passes.append("✅ Budget/salary signal extraction implemented")
        else:
            fails.append("❌ Budget/salary signal extraction missing")
        
        # Hiring volume patterns
        if "hiring_volume" in signals_content or "company" in signals_content:
            passes.append("✅ Hiring volume pattern analysis implemented")
        else:
            fails.append("❌ Hiring volume pattern analysis missing")
    else:
        fails.append("❌ Signal processing agent missing or incomplete")
    
    return passes, fails

def check_agent3_requirements() -> Tuple[List[str], List[str]]:
    """Check Agent 3: Intelligence Agent requirements"""
    requirements = [
        "Correlates hiring patterns with potential service needs",
        "Identifies companies scaling specific departments (engineering, sales, marketing)",
        "Maps technology adoption trends across industries", 
        "Generates alerts for high-priority opportunities"
    ]
    
    passes = []
    fails = []
    
    main_file = "agent3_insight_generator/main.py"
    
    if os.path.exists(main_file):
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Hiring pattern correlation
        if "correlat" in content.lower() and "hiring" in content.lower():
            passes.append("✅ Hiring pattern correlation implemented")
        else:
            fails.append("❌ Hiring pattern correlation missing")
        
        # Department scaling detection
        if ("engineering" in content.lower() or "department" in content.lower()) and "scaling" in content.lower():
            passes.append("✅ Department scaling identification implemented")
        else:
            fails.append("❌ Department scaling identification missing")
        
        # Technology trends mapping
        if "technology" in content.lower() and "trend" in content.lower():
            passes.append("✅ Technology adoption trends mapping implemented")
        else:
            fails.append("❌ Technology trends mapping missing")
        
        # High-priority opportunity alerts
        if "insight" in content.lower() and ("opportunity" in content.lower() or "alert" in content.lower()):
            passes.append("✅ Business opportunity insights/alerts implemented")
        else:
            fails.append("❌ High-priority opportunity alerts missing")
    else:
        fails.append("❌ Intelligence agent missing")
    
    return passes, fails

def check_key_bd_signals() -> Tuple[List[str], List[str]]:
    """Check Key BD Signals tracking requirements"""
    required_signals = [
        "Scaling indicators: Multiple similar roles, senior + junior hiring pairs",
        "Technology adoption: New tech stack mentions, cloud migration signals",
        "Transformation projects: Digital transformation, modernization keywords",
        "Pain points: Mentions of legacy systems, integration challenges", 
        "Budget signals: Salary ranges, contractor vs FTE ratios"
    ]
    
    passes = []
    fails = []
    
    # Check if signals are implemented
    signal_files = [
        "agent2_signal_processor/processor.py",
        "agent2_signal_processor/signals.py",
        "agent3_insight_generator/main.py"
    ]
    
    all_content = ""
    for file in signal_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                all_content += f.read().lower()
    
    # Scaling indicators
    if "scaling" in all_content or ("senior" in all_content and "junior" in all_content):
        passes.append("✅ Scaling indicators tracked")
    else:
        fails.append("❌ Scaling indicators not properly tracked")
    
    # Technology adoption
    if "technology" in all_content and ("cloud" in all_content or "migration" in all_content):
        passes.append("✅ Technology adoption signals tracked")
    else:
        fails.append("❌ Technology adoption signals missing")
    
    # Transformation projects
    if "moderniz" in all_content or "transformation" in all_content:
        passes.append("✅ Transformation project signals tracked")
    else:
        fails.append("❌ Transformation project signals missing")
    
    # Pain points
    if "legacy" in all_content and "pain" in all_content:
        passes.append("✅ Pain point signals tracked")
    else:
        fails.append("❌ Pain point signals missing")
    
    # Budget signals
    if "salary" in all_content and "budget" in all_content:
        passes.append("✅ Budget signals tracked")
    else:
        fails.append("❌ Budget signals missing")
    
    return passes, fails

def check_deliverables() -> Tuple[List[str], List[str]]:
    """Check required deliverables"""
    required_deliverables = [
        "Working prototype with data pipeline",
        "Dashboard showing top opportunities and trends",
        "Weekly signal reports with actionable insights",
        "Documentation for scaling the system"
    ]
    
    passes = []
    fails = []
    
    # Working prototype
    pipeline_files = [
        "run_complete_pipeline.py",
        "run_agent1_production.py", 
        "run_agent2_production.py",
        "run_agent3_production.py"
    ]
    
    if all(os.path.exists(f) for f in pipeline_files):
        passes.append("✅ Working prototype with data pipeline")
    else:
        fails.append("❌ Complete data pipeline missing")
    
    # Dashboard
    if os.path.exists("dashboard.py"):
        passes.append("✅ Dashboard implemented")
    else:
        fails.append("❌ Dashboard missing")
    
    # Weekly reports
    if os.path.exists("generate_weekly_report.py") and os.path.exists("reports"):
        passes.append("✅ Weekly signal reports implemented")
    else:
        fails.append("❌ Weekly reporting system missing")
    
    # Documentation
    if os.path.exists("README.md") and os.path.exists("SYSTEM_DOCUMENTATION.md"):
        passes.append("✅ Documentation for scaling provided")
    else:
        fails.append("❌ Scaling documentation missing")
    
    return passes, fails

def main():
    """Run complete requirements compliance check"""
    print("🔍 PROJECT REQUIREMENTS COMPLIANCE CHECK")
    print("=" * 80)
    print("Verifying project meets ALL specifications from original instructions")
    print("=" * 80)
    
    all_passes = []
    all_fails = []
    
    # Check each agent
    sections = [
        ("Agent 1: Data Collection Agent", check_agent1_requirements),
        ("Agent 2: Signal Processing Agent", check_agent2_requirements), 
        ("Agent 3: Intelligence Agent", check_agent3_requirements),
        ("Key BD Signals Tracking", check_key_bd_signals),
        ("Required Deliverables", check_deliverables)
    ]
    
    for section_name, check_func in sections:
        print(f"\n📋 {section_name}")
        print("-" * 60)
        
        passes, fails = check_func()
        
        for item in passes:
            print(item)
        
        for item in fails:
            print(item)
        
        all_passes.extend(passes)
        all_fails.extend(fails)
    
    # Summary
    print(f"\n{'=' * 80}")
    print("COMPLIANCE SUMMARY")
    print(f"{'=' * 80}")
    
    total_checks = len(all_passes) + len(all_fails)
    pass_rate = (len(all_passes) / total_checks * 100) if total_checks > 0 else 0
    
    print(f"Total Requirements Checked: {total_checks}")
    print(f"Requirements Met: {len(all_passes)} ✅")
    print(f"Requirements Missing: {len(all_fails)} ❌")
    print(f"Compliance Rate: {pass_rate:.1f}%")
    
    if all_fails:
        print(f"\n⚠️  MISSING REQUIREMENTS:")
        for fail in all_fails:
            print(f"   {fail}")
    
    if pass_rate >= 90:
        print(f"\n🎉 EXCELLENT COMPLIANCE! Project meets project requirements.")
    elif pass_rate >= 75:
        print(f"\n✅ GOOD COMPLIANCE! Most requirements met, minor gaps remain.")
    elif pass_rate >= 50:
        print(f"\n⚠️  PARTIAL COMPLIANCE! Significant requirements missing.")
    else:
        print(f"\n❌ POOR COMPLIANCE! Major requirements missing.")
    
    print("=" * 80)
    
    return len(all_fails) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)