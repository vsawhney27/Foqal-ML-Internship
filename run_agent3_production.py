#!/usr/bin/env python3
"""
Production Runner for Agent 3: Business Development Intelligence Generator
Analyzes signals from Agent 2 and generates actionable BD insights
"""

import sys
import os
import subprocess
from datetime import datetime

def check_agent2_data():
    """Check if Agent 2 has provided processed signals"""
    agent2_dir = os.path.join(os.path.dirname(__file__), "agent2_signal_processor")
    signals_file = os.path.join(agent2_dir, "output", "signals_output.json")
    
    if not os.path.exists(signals_file):
        print("ERROR: No processed signals found from Agent 2")
        print("Please run Agent 2 first: python run_agent2_production.py")
        return False
    
    print("✓ Agent 2 processed signals found")
    return True

def run_agent3():
    """Run Agent 3 insight generation"""
    print("="*60)
    print("AGENT 3: BUSINESS DEVELOPMENT INTELLIGENCE")
    print("="*60)
    
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    if not check_agent2_data():
        return False
    
    try:
        # Change to agent3 directory and run main.py
        agent3_dir = os.path.join(os.path.dirname(__file__), "agent3_insight_generator")
        
        print("\nGenerating business development insights...")
        print("Analyzing: Company hiring patterns, Technology trends, Market opportunities")
        
        # Run the insight generator
        result = subprocess.run([
            sys.executable, "main.py"
        ], cwd=agent3_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: Agent 3 completed successfully")
            print("\nOutput:")
            print(result.stdout)
            
            # Check if insights were generated
            output_dir = os.path.join(agent3_dir, "output")
            insights_file = os.path.join(output_dir, "company_insights.json")
            trends_file = os.path.join(output_dir, "industry_trends.json")
            
            if os.path.exists(insights_file):
                print(f"✓ Company insights saved to: {insights_file}")
            if os.path.exists(trends_file):
                print(f"✓ Industry trends saved to: {trends_file}")
            
            print("\nAgent 3 Status: INTELLIGENCE GENERATED")
            return True
        else:
            print("ERROR: Agent 3 failed")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to run Agent 3: {e}")
        return False

def generate_executive_summary():
    """Generate a brief executive summary"""
    print("\n" + "="*80)
    print("EXECUTIVE BUSINESS DEVELOPMENT INTELLIGENCE REPORT")
    print("="*80)
    
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check what data is available
    agent3_dir = os.path.join(os.path.dirname(__file__), "agent3_insight_generator")
    insights_file = os.path.join(agent3_dir, "output", "company_insights.json")
    
    if os.path.exists(insights_file):
        try:
            import json
            with open(insights_file, 'r') as f:
                insights = json.load(f)
            
            print(f"\nCOMPANIES ANALYZED: {len(insights)}")
            print("\nTOP BUSINESS OPPORTUNITIES:")
            
            # Show first 3 company insights
            for i, company_insight in enumerate(insights[:3], 1):
                company = company_insight.get('company', 'Unknown')
                job_count = company_insight.get('job_count', 0)
                insights_list = company_insight.get('insights', [])
                
                print(f"\n{i}. {company} ({job_count} open positions)")
                for insight in insights_list[:2]:  # Show top 2 insights
                    print(f"   • {insight}")
                
        except Exception as e:
            print(f"Could not load insights: {e}")
    
    print(f"\nSTRATEGIC RECOMMENDATIONS:")
    print("   • Focus on companies with urgent hiring and technology transformation signals")
    print("   • Target high-growth companies showing multiple role expansions")
    print("   • Prioritize companies with budget transparency and equity offerings")
    
    print("="*80)

if __name__ == "__main__":
    print("Starting Production Business Intelligence Pipeline...")
    
    success = run_agent3()
    
    if success:
        generate_executive_summary()
        
        print("\n" + "="*60)
        print("AGENT 3 COMPLETED SUCCESSFULLY")
        print("Business development intelligence generated!")
        print("="*60)
        print("Check output files for detailed insights and trends")
    else:
        print("\n" + "="*60)
        print("AGENT 3 FAILED")
        print("="*60)
        print("Check error messages above and retry")
        sys.exit(1)