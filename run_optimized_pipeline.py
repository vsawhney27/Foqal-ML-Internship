#!/usr/bin/env python3
"""
Optimized ML Pipeline - No Redundancies
Single execution path with consolidated outputs
"""

import os
import sys
import json
import logging
import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_optimized_pipeline():
    """Run optimized pipeline with no redundant operations"""
    logger.info("🚀 Starting Optimized ML Pipeline")
    start_time = datetime.datetime.now()
    
    try:
        # Step 1: Data Collection (Agent 1)
        logger.info("📥 Running Data Collection...")
        sys.path.append('agent1_data_collector')
        from agent1_data_collector.main import main as agent1_main
        agent1_main()
        
        # Step 2: ML Signal Processing (Agent 2) - Only ML version
        logger.info("🤖 Running ML Signal Processing...")
        result = os.system('python3 agent2_signal_processor/ml_processor.py')
        if result != 0:
            raise Exception("Agent 2 ML processing failed")
        
        # Step 3: ML Insight Generation (Agent 3) - Only ML version  
        logger.info("🧠 Running ML Insight Generation...")
        result = os.system('python3 agent3_insight_generator/ml_insights.py')
        if result != 0:
            raise Exception("Agent 3 ML insights failed")
        
        # Consolidate outputs (no duplicates)
        logger.info("📁 Consolidating outputs...")
        ensure_single_output_location()
        
        execution_time = datetime.datetime.now() - start_time
        logger.info(f"✅ Optimized pipeline completed in {execution_time}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Optimized pipeline failed: {e}")
        return False

def ensure_single_output_location():
    """Ensure all outputs are in single location"""
    main_outputs = {
        'output/signals_output.json': 'agent2_signal_processor/output/signals_output.json',
        'output/signal_statistics.json': 'agent2_signal_processor/output/signal_statistics.json',
        'output/company_insights.json': 'agent3_insight_generator/output/company_insights.json',
        'output/industry_trends.json': 'agent3_insight_generator/output/industry_trends.json'
    }
    
    os.makedirs('output', exist_ok=True)
    
    for main_file, source_file in main_outputs.items():
        if os.path.exists(source_file) and not os.path.exists(main_file):
            shutil.copy2(source_file, main_file)

if __name__ == "__main__":
    run_optimized_pipeline()
