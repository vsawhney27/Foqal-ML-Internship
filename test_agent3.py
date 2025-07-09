#!/usr/bin/env python3
"""
Test Agent 3 with existing Agent 2 output data
"""

import json
import sys
import os

def test_agent3_with_agent2_data():
    """Test Agent 3 using Agent 2's output"""
    print("🧪 Testing Agent 3 with Agent 2 output data...")
    
    # Load Agent 2 output
    agent2_output_file = "agent2_signal_processor/output/signals_output.json"
    
    if not os.path.exists(agent2_output_file):
        print(f"❌ Agent 2 output file not found: {agent2_output_file}")
        return False
    
    try:
        with open(agent2_output_file, 'r') as f:
            processed_signals = json.load(f)
        
        print(f"📥 Loaded {len(processed_signals)} processed signals from Agent 2")
        
        # Import Agent 3 functions (without MongoDB dependency)
        sys.path.append('.')
        
        # Mock pymongo to avoid import error
        import importlib.util
        spec = importlib.util.spec_from_loader("pymongo", loader=None)
        pymongo = importlib.util.module_from_spec(spec)
        sys.modules["pymongo"] = pymongo
        
        # Create mock MongoClient
        class MockMongoClient:
            def __init__(self, *args, **kwargs):
                pass
            def close(self):
                pass
        
        pymongo.MongoClient = MockMongoClient
        
        # Now import Agent 3 functions
        from agent3_insight_generator import (
            generate_company_insights, 
            analyze_industry_trends,
            print_insights_summary
        )
        
        # Generate insights
        print("🔍 Generating company insights...")
        company_insights = generate_company_insights(processed_signals)
        
        print("🌐 Analyzing industry trends...")
        industry_trends = analyze_industry_trends(processed_signals)
        
        # Print results
        print_insights_summary(company_insights, industry_trends)
        
        # Save results
        os.makedirs("output", exist_ok=True)
        
        with open("output/company_insights.json", 'w') as f:
            json.dump(company_insights, f, indent=2)
        
        with open("output/industry_trends.json", 'w') as f:
            json.dump(industry_trends, f, indent=2)
        
        print(f"\n✅ Agent 3 test completed successfully!")
        print(f"📁 Results saved to output/ directory")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_agent3_with_agent2_data()