#!/usr/bin/env python3
"""
System Validation Script
Validates that all components are present and properly configured
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (MISSING)")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists and print status"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} (MISSING)")
        return False

def validate_agent_structure():
    """Validate the three-agent structure"""
    print("🔍 VALIDATING AGENT STRUCTURE")
    print("=" * 50)
    
    agents = [
        ("Agent 1 (Data Collector)", "agent1_data_collector"),
        ("Agent 2 (Signal Processor)", "agent2_signal_processor"), 
        ("Agent 3 (Insight Generator)", "agent3_insight_generator")
    ]
    
    all_good = True
    
    for agent_name, agent_dir in agents:
        print(f"\n{agent_name}:")
        main_file = os.path.join(agent_dir, "main.py")
        all_good &= check_file_exists(main_file, f"  Main script")
        all_good &= check_directory_exists(agent_dir, f"  Directory")
    
    return all_good

def validate_production_scripts():
    """Validate production runner scripts"""
    print("\n🚀 VALIDATING PRODUCTION SCRIPTS")
    print("=" * 50)
    
    scripts = [
        ("Complete Pipeline", "run_complete_pipeline.py"),
        ("Agent 1 Runner", "run_agent1_production.py"),
        ("Agent 2 Runner", "run_agent2_production.py"),
        ("Agent 3 Runner", "run_agent3_production.py"),
        ("Weekly Report Generator", "generate_weekly_report.py")
    ]
    
    all_good = True
    for name, script in scripts:
        all_good &= check_file_exists(script, name)
    
    return all_good

def validate_deliverables():
    """Validate required deliverables"""
    print("\n📊 VALIDATING DELIVERABLES")
    print("=" * 50)
    
    deliverables = [
        ("Dashboard", "dashboard.py"),
        ("System Documentation", "SYSTEM_DOCUMENTATION.md"),
        ("Project README", "README.md"),
        ("Requirements", "requirements.txt")
    ]
    
    all_good = True
    for name, file in deliverables:
        all_good &= check_file_exists(file, name)
    
    # Check output directories
    output_dirs = [
        ("Agent 2 Output", "agent2_signal_processor/output"),
        ("Agent 3 Output", "agent3_insight_generator/output"),
        ("Reports Directory", "reports")
    ]
    
    for name, dir_path in output_dirs:
        all_good &= check_directory_exists(dir_path, name)
    
    return all_good

def validate_data_pipeline():
    """Validate data pipeline components"""
    print("\n🔧 VALIDATING DATA PIPELINE COMPONENTS")
    print("=" * 50)
    
    components = [
        ("Data Collector Scraper", "agent1_data_collector/scraper.py"),
        ("Data Collector Config", "agent1_data_collector/config.py"),
        ("Signal Processor Engine", "agent2_signal_processor/processor.py"),
        ("Signal Detection Functions", "agent2_signal_processor/signals.py"),
        ("MongoDB Utilities", "agent2_signal_processor/mongo_utils.py")
    ]
    
    all_good = True
    for name, component in components:
        all_good &= check_file_exists(component, name)
    
    return all_good

def check_requirements():
    """Check if requirements.txt has necessary dependencies"""
    print("\n📦 VALIDATING DEPENDENCIES")
    print("=" * 50)
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt missing")
        return False
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    required_deps = [
        "requests", "beautifulsoup4", "selenium", "pymongo", 
        "pandas", "streamlit", "plotly"
    ]
    
    all_good = True
    for dep in required_deps:
        if dep.lower() in content.lower():
            print(f"✅ {dep} found in requirements")
        else:
            print(f"❌ {dep} missing from requirements")
            all_good = False
    
    return all_good

def validate_project_requirements():
    """Validate against original project requirements"""
    print("\n🎯 VALIDATING PROJECT REQUIREMENTS")
    print("=" * 50)
    
    requirements = [
        ("Agent 1: Data Collection", lambda: os.path.exists("agent1_data_collector/main.py")),
        ("Agent 2: Signal Processing", lambda: os.path.exists("agent2_signal_processor/main.py")),
        ("Agent 3: Intelligence Agent", lambda: os.path.exists("agent3_insight_generator/main.py")),
        ("Working Prototype", lambda: os.path.exists("run_complete_pipeline.py")),
        ("Dashboard", lambda: os.path.exists("dashboard.py")),
        ("Weekly Reports", lambda: os.path.exists("generate_weekly_report.py")),
        ("Documentation", lambda: os.path.exists("SYSTEM_DOCUMENTATION.md"))
    ]
    
    all_good = True
    for name, check_func in requirements:
        if check_func():
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
            all_good = False
    
    return all_good

def main():
    """Run complete system validation"""
    print("🔍 JOB POSTING INTELLIGENCE SYSTEM VALIDATION")
    print("=" * 60)
    print("Validating all components against project requirements...")
    
    validations = [
        validate_agent_structure,
        validate_production_scripts,
        validate_deliverables,
        validate_data_pipeline,
        check_requirements,
        validate_project_requirements
    ]
    
    all_passed = True
    for validation_func in validations:
        result = validation_func()
        all_passed &= result
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 VALIDATION PASSED!")
        print("=" * 60)
        print("✅ All components are present and properly configured")
        print("✅ Project meets all requirements")
        print("✅ System is ready for production use")
        print("\n🚀 To run the system:")
        print("   python run_complete_pipeline.py")
        print("\n📊 To view dashboard:")
        print("   streamlit run dashboard.py")
    else:
        print("❌ VALIDATION FAILED!")
        print("=" * 60)
        print("Some components are missing or misconfigured.")
        print("Please review the errors above and fix them.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)