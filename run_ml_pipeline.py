#!/usr/bin/env python3
"""
ML-Enhanced Job Intelligence Pipeline
Runs the complete ML pipeline with all agents using machine learning models
"""

import os
import sys
import json
import logging
import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_agent1_data_collection():
    """Run Agent 1 - Data Collection"""
    logger.info("🔄 Running Agent 1: Data Collection...")
    
    try:
        # Import and run Agent 1
        sys.path.append('agent1_data_collector')
        from agent1_data_collector.main import main as agent1_main
        
        # Run data collection
        agent1_main()
        
        # Verify output
        if os.path.exists('agent1_data_collector/scraped_jobs.json'):
            with open('agent1_data_collector/scraped_jobs.json', 'r') as f:
                jobs = json.load(f)
            logger.info(f"✅ Agent 1 completed: {len(jobs)} jobs collected")
            return True
        else:
            logger.error("❌ Agent 1 failed: No output file found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Agent 1 failed: {e}")
        return False

def run_agent2_ml_signal_processing():
    """Run Agent 2 - ML-Enhanced Signal Processing"""
    logger.info("🤖 Running Agent 2: ML-Enhanced Signal Processing...")
    
    try:
        # Change to agent2 directory
        original_dir = os.getcwd()
        os.chdir('agent2_signal_processor')
        
        # Import and run ML processor
        from ml_processor import main as ml_processor_main
        
        # Run ML signal processing
        ml_processor_main()
        
        # Return to original directory
        os.chdir(original_dir)
        
        # Verify output
        if os.path.exists('agent2_signal_processor/output/signals_output.json'):
            with open('agent2_signal_processor/output/signals_output.json', 'r') as f:
                processed_jobs = json.load(f)
            logger.info(f"✅ Agent 2 completed: {len(processed_jobs)} jobs processed with ML")
            return True
        else:
            logger.error("❌ Agent 2 failed: No output file found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Agent 2 failed: {e}")
        return False

def run_agent3_ml_insights():
    """Run Agent 3 - ML-Enhanced Insight Generation"""
    logger.info("🧠 Running Agent 3: ML-Enhanced Insight Generation...")
    
    try:
        # Change to agent3 directory
        original_dir = os.getcwd()
        os.chdir('agent3_insight_generator')
        
        # Import and run ML insights
        from ml_insights import main as ml_insights_main
        
        # Run ML insight generation
        ml_insights_main()
        
        # Return to original directory
        os.chdir(original_dir)
        
        # Verify output
        if os.path.exists('agent3_insight_generator/output/company_insights.json'):
            with open('agent3_insight_generator/output/company_insights.json', 'r') as f:
                insights = json.load(f)
            logger.info(f"✅ Agent 3 completed: {len(insights)} company insights generated with ML")
            return True
        else:
            logger.error("❌ Agent 3 failed: No output file found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Agent 3 failed: {e}")
        return False

def run_complete_ml_pipeline():
    """Run the complete ML-enhanced pipeline"""
    logger.info("🚀 Starting Complete ML-Enhanced Job Intelligence Pipeline")
    logger.info("="*60)
    
    start_time = datetime.datetime.now()
    
    # Pipeline status
    pipeline_status = {
        'agent1_data_collection': False,
        'agent2_ml_processing': False,
        'agent3_ml_insights': False,
        'pipeline_success': False
    }
    
    try:
        # Step 1: Data Collection
        pipeline_status['agent1_data_collection'] = run_agent1_data_collection()
        if not pipeline_status['agent1_data_collection']:
            logger.error("Pipeline stopped: Agent 1 failed")
            return pipeline_status
        
        # Step 2: ML Signal Processing
        pipeline_status['agent2_ml_processing'] = run_agent2_ml_signal_processing()
        if not pipeline_status['agent2_ml_processing']:
            logger.error("Pipeline stopped: Agent 2 failed")
            return pipeline_status
        
        # Step 3: ML Insight Generation
        pipeline_status['agent3_ml_insights'] = run_agent3_ml_insights()
        if not pipeline_status['agent3_ml_insights']:
            logger.error("Pipeline stopped: Agent 3 failed")
            return pipeline_status
        
        # Step 4: Generate Summary Report
        generate_pipeline_summary()
        
        pipeline_status['pipeline_success'] = True
        
        # Calculate execution time
        end_time = datetime.datetime.now()
        execution_time = end_time - start_time
        
        logger.info("="*60)
        logger.info("🎉 ML-Enhanced Pipeline Completed Successfully!")
        logger.info(f"⏱️  Total Execution Time: {execution_time}")
        logger.info("="*60)
        
        return pipeline_status
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return pipeline_status

def generate_pipeline_summary():
    """Generate a summary of the ML pipeline results"""
    logger.info("📊 Generating Pipeline Summary...")
    
    try:
        summary = {
            'pipeline_execution_date': datetime.datetime.now().isoformat(),
            'pipeline_type': 'ml_enhanced',
            'agents_executed': ['data_collection', 'ml_signal_processing', 'ml_insight_generation']
        }
        
        # Load results from each agent
        # Agent 1 results
        if os.path.exists('agent1_data_collector/scraped_jobs.json'):
            with open('agent1_data_collector/scraped_jobs.json', 'r') as f:
                raw_jobs = json.load(f)
            summary['data_collection'] = {
                'jobs_collected': len(raw_jobs),
                'sources': list(set(job.get('source', 'Unknown') for job in raw_jobs))
            }
        
        # Agent 2 results
        if os.path.exists('agent2_signal_processor/output/ml_signal_statistics.json'):
            with open('agent2_signal_processor/output/ml_signal_statistics.json', 'r') as f:
                ml_stats = json.load(f)
            summary['ml_signal_processing'] = {
                'jobs_processed': ml_stats.get('total_jobs_processed', 0),
                'processing_method': ml_stats.get('processing_method', 'unknown'),
                'ml_insights': ml_stats.get('ml_insights', {})
            }
        
        # Agent 3 results
        if os.path.exists('agent3_insight_generator/output/ml_company_insights.json'):
            with open('agent3_insight_generator/output/ml_company_insights.json', 'r') as f:
                ml_insights = json.load(f)
            summary['ml_insight_generation'] = {
                'companies_analyzed': ml_insights.get('total_companies_analyzed', 0),
                'high_priority_opportunities': ml_insights.get('executive_summary', {}).get('high_priority_opportunities', 0),
                'analysis_method': ml_insights.get('analysis_method', 'unknown'),
                'ml_confidence': ml_insights.get('executive_summary', {}).get('ml_confidence', 'unknown')
            }
        
        # Save summary
        os.makedirs('ml_output', exist_ok=True)
        with open('ml_output/pipeline_summary.json', 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "="*70)
        print("ML-ENHANCED PIPELINE SUMMARY")
        print("="*70)
        print(f"Execution Date: {summary['pipeline_execution_date'][:19]}")
        print(f"Pipeline Type: {summary['pipeline_type']}")
        
        if 'data_collection' in summary:
            dc = summary['data_collection']
            print(f"\n📥 Data Collection:")
            print(f"   Jobs Collected: {dc['jobs_collected']}")
            print(f"   Sources: {', '.join(dc['sources'])}")
        
        if 'ml_signal_processing' in summary:
            sp = summary['ml_signal_processing']
            print(f"\n🤖 ML Signal Processing:")
            print(f"   Jobs Processed: {sp['jobs_processed']}")
            print(f"   Method: {sp['processing_method']}")
            if 'ml_insights' in sp and sp['ml_insights']:
                ml_insights = sp['ml_insights']
                print(f"   ML Urgency Score: {ml_insights.get('avg_ml_urgency_score', 'N/A')}")
                print(f"   Model Coverage: {ml_insights.get('ml_model_coverage', 'N/A')}%")
        
        if 'ml_insight_generation' in summary:
            ig = summary['ml_insight_generation']
            print(f"\n🧠 ML Insight Generation:")
            print(f"   Companies Analyzed: {ig['companies_analyzed']}")
            print(f"   High Priority Opportunities: {ig['high_priority_opportunities']}")
            print(f"   Analysis Method: {ig['analysis_method']}")
            print(f"   ML Confidence: {ig['ml_confidence']}")
        
        print(f"\n📁 Results saved to: ml_output/pipeline_summary.json")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")

def check_ml_dependencies():
    """Check if ML dependencies are installed"""
    logger.info("🔍 Checking ML dependencies...")
    
    required_packages = [
        'sklearn',
        'nltk',
        'joblib',
        'scipy',
        'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"⚠️  Missing ML packages: {', '.join(missing_packages)}")
        logger.info("Install missing packages with: pip install -r requirements.txt")
        return False
    else:
        logger.info("✅ All ML dependencies are available")
        return True

def main():
    """Main execution function"""
    print("\n🤖 ML-Enhanced Job Intelligence System")
    print("Transforming job posting data into actionable business intelligence using machine learning")
    print("="*80)
    
    # Check dependencies
    if not check_ml_dependencies():
        print("\n❌ Missing ML dependencies. Please install requirements:")
        print("pip install -r requirements.txt")
        return
    
    # Run pipeline
    try:
        results = run_complete_ml_pipeline()
        
        if results['pipeline_success']:
            print("\n🎯 Pipeline completed successfully!")
            print("\n📊 View results:")
            print("   • Dashboard: streamlit run dashboard.py")
            print("   • ML Insights: ml_output/pipeline_summary.json")
            print("   • Agent outputs in respective output/ directories")
        else:
            print("\n❌ Pipeline encountered errors. Check logs above.")
            
    except KeyboardInterrupt:
        logger.info("\n⏹️  Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"\n💥 Pipeline failed with error: {e}")

if __name__ == "__main__":
    main()