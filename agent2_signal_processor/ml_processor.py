#!/usr/bin/env python3
"""
ML-Enhanced Signal Processing Agent
Uses trained ML models for signal detection with rule-based fallback
"""

import json
import datetime
import os
import logging
from typing import List, Dict, Any
from collections import Counter
import sys

# Add ml_models to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ml_models.text_classifier import UrgencyClassifier, TechStackClassifier
from ml_models.feature_engineering import JobFeatureExtractor
from signals import (  # Fallback to rule-based methods
    extract_technology_adoption,
    extract_urgent_hiring_language, 
    extract_budget_signals,
    extract_pain_points,
    extract_skills_mentioned
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLSignalProcessor:
    """ML-Enhanced signal processor with rule-based fallback"""
    
    def __init__(self, use_ml: bool = True):
        self.use_ml = use_ml
        self.ml_models_available = False
        
        if use_ml:
            try:
                self.urgency_classifier = UrgencyClassifier()
                self.tech_classifier = TechStackClassifier()
                self.feature_extractor = JobFeatureExtractor()
                logger.info("ML models initialized successfully")
            except Exception as e:
                logger.warning(f"ML models failed to initialize: {e}")
                logger.info("Falling back to rule-based processing")
                self.use_ml = False
    
    def train_models(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Train ML models on job data"""
        if not self.use_ml or len(jobs) < 10:
            return {'status': 'skipped', 'reason': 'ML disabled or insufficient data'}
        
        try:
            training_results = {}
            
            # Train urgency classifier
            logger.info("Training urgency classifier...")
            urgency_results = self.urgency_classifier.train(jobs)
            training_results['urgency_classifier'] = urgency_results
            
            # Train technology classifier
            logger.info("Training technology classifier...")
            tech_results = self.tech_classifier.train(jobs)
            training_results['tech_classifier'] = tech_results
            
            # Extract features for future use
            logger.info("Extracting features...")
            features = self.feature_extractor.extract_all_features(jobs)
            training_results['feature_extraction'] = {
                'n_features': features['combined_features'].shape[1],
                'n_samples': features['combined_features'].shape[0]
            }
            
            self.ml_models_available = True
            logger.info("✅ ML models trained successfully")
            return training_results
            
        except Exception as e:
            logger.error(f"ML training failed: {e}")
            logger.info("Falling back to rule-based processing")
            self.use_ml = False
            return {'status': 'failed', 'error': str(e)}
    
    def process_urgency_ml(self, descriptions: List[str]) -> List[Dict[str, Any]]:
        """Process urgency using ML with rule-based fallback"""
        results = []
        
        if self.use_ml and self.ml_models_available:
            try:
                # ML approach
                ml_urgency_scores = self.urgency_classifier.predict_proba(descriptions)
                ml_urgency_classes = self.urgency_classifier.predict(descriptions)
                
                for i, desc in enumerate(descriptions):
                    # Combine ML with rule-based for robustness
                    rule_based_signals = extract_urgent_hiring_language(desc)
                    
                    result = {
                        'ml_urgency_score': ml_urgency_scores[i],
                        'ml_urgency_class': ml_urgency_classes[i],
                        'rule_based_signals': rule_based_signals,
                        'combined_urgency': ml_urgency_scores[i] > 0.5 or len(rule_based_signals) > 0,
                        'confidence': 'high' if ml_urgency_scores[i] > 0.7 or len(rule_based_signals) > 2 else 'medium'
                    }
                    results.append(result)
                
                logger.info(f"Processed urgency using ML for {len(descriptions)} jobs")
                return results
                
            except Exception as e:
                logger.warning(f"ML urgency processing failed: {e}, falling back to rule-based")
        
        # Rule-based fallback
        for desc in descriptions:
            rule_based_signals = extract_urgent_hiring_language(desc)
            result = {
                'ml_urgency_score': 1.0 if rule_based_signals else 0.0,
                'ml_urgency_class': 1 if rule_based_signals else 0,
                'rule_based_signals': rule_based_signals,
                'combined_urgency': len(rule_based_signals) > 0,
                'confidence': 'rule_based'
            }
            results.append(result)
        
        return results
    
    def process_technology_ml(self, descriptions: List[str]) -> List[Dict[str, Any]]:
        """Process technology adoption using ML with rule-based fallback"""
        results = []
        
        if self.use_ml and self.ml_models_available:
            try:
                # ML approach
                ml_tech_categories = self.tech_classifier.predict_tech_categories(descriptions)
                ml_tech_extraction = self.tech_classifier.extract_technologies_ml(descriptions)
                
                for i, desc in enumerate(descriptions):
                    # Combine with rule-based
                    rule_based_tech = extract_technology_adoption(desc)
                    
                    result = {
                        'ml_tech_categories': ml_tech_categories[i],
                        'ml_tech_extraction': ml_tech_extraction[i],
                        'rule_based_tech': rule_based_tech,
                        'combined_tech': list(set(ml_tech_extraction[i] + rule_based_tech)),
                        'confidence': 'high' if len(ml_tech_extraction[i]) > 2 else 'medium'
                    }
                    results.append(result)
                
                logger.info(f"Processed technology using ML for {len(descriptions)} jobs")
                return results
                
            except Exception as e:
                logger.warning(f"ML technology processing failed: {e}, falling back to rule-based")
        
        # Rule-based fallback
        for desc in descriptions:
            rule_based_tech = extract_technology_adoption(desc)
            result = {
                'ml_tech_categories': {},
                'ml_tech_extraction': rule_based_tech,
                'rule_based_tech': rule_based_tech,
                'combined_tech': rule_based_tech,
                'confidence': 'rule_based'
            }
            results.append(result)
        
        return results
    
    def process_job_signals_ml(self, job: Dict) -> Dict:
        """Process all signals for a single job using ML + rule-based approach"""
        description = job.get('description', '')
        
        # Process using ML where available
        urgency_result = self.process_urgency_ml([description])[0]
        tech_result = self.process_technology_ml([description])[0]
        
        # Rule-based processing for other signals (can be enhanced with ML later)
        budget_signals = extract_budget_signals(description)
        pain_points = extract_pain_points(description)
        skills_mentioned = extract_skills_mentioned(description)
        
        # Create enhanced job record
        processed_job = job.copy()
        
        # ML-enhanced signals
        processed_job.update({
            'ml_enhanced_signals': {
                'urgency_analysis': urgency_result,
                'technology_analysis': tech_result,
                'processing_method': 'ml_hybrid' if self.use_ml and self.ml_models_available else 'rule_based',
                'processing_date': datetime.datetime.now().isoformat()
            },
            
            # Backward compatibility - maintain original field names
            'urgent_hiring_language': urgency_result['rule_based_signals'],
            'technology_adoption': tech_result['combined_tech'],
            'budget_signals': budget_signals,
            'pain_points': pain_points,
            'skills_mentioned': skills_mentioned,
            
            # New ML fields
            'ml_urgency_score': urgency_result['ml_urgency_score'],
            'ml_confidence_scores': {
                'urgency': urgency_result['confidence'],
                'technology': tech_result['confidence']
            }
        })
        
        return processed_job
    
    def process_jobs_batch_ml(self, jobs: List[Dict]) -> List[Dict]:
        """Process multiple jobs efficiently using batch ML processing"""
        logger.info(f"Processing {len(jobs)} jobs with ML-enhanced signal detection...")
        
        # First, train models if using ML and not already trained
        if self.use_ml and not self.ml_models_available and len(jobs) >= 10:
            logger.info("Training ML models on current dataset...")
            training_results = self.train_models(jobs)
            if training_results.get('status') != 'failed':
                self.ml_models_available = True
        
        processed_jobs = []
        
        # Extract all descriptions for batch processing
        descriptions = [job.get('description', '') for job in jobs]
        
        # Batch ML processing
        if self.use_ml and self.ml_models_available:
            try:
                urgency_results = self.process_urgency_ml(descriptions)
                tech_results = self.process_technology_ml(descriptions)
            except Exception as e:
                logger.error(f"Batch ML processing failed: {e}")
                urgency_results = [{'ml_urgency_score': 0, 'rule_based_signals': []} for _ in descriptions]
                tech_results = [{'combined_tech': []} for _ in descriptions]
        else:
            # Rule-based batch processing
            urgency_results = []
            tech_results = []
            for desc in descriptions:
                urgency_results.append({
                    'ml_urgency_score': 0,
                    'rule_based_signals': extract_urgent_hiring_language(desc)
                })
                tech_results.append({
                    'combined_tech': extract_technology_adoption(desc)
                })
        
        # Process each job
        for i, job in enumerate(jobs):
            try:
                description = job.get('description', '')
                
                # Get batch results
                urgency_result = urgency_results[i]
                tech_result = tech_results[i]
                
                # Process other signals
                budget_signals = extract_budget_signals(description)
                pain_points = extract_pain_points(description)
                skills_mentioned = extract_skills_mentioned(description)
                
                # Create processed job
                processed_job = job.copy()
                processed_job.update({
                    'urgent_hiring_language': urgency_result.get('rule_based_signals', []),
                    'technology_adoption': tech_result.get('combined_tech', []),
                    'budget_signals': budget_signals,
                    'pain_points': pain_points,
                    'skills_mentioned': skills_mentioned,
                    'ml_urgency_score': urgency_result.get('ml_urgency_score', 0),
                    'processing_method': 'ml_hybrid' if self.use_ml and self.ml_models_available else 'rule_based',
                    'signal_processing_date': datetime.datetime.now().isoformat()
                })
                
                processed_jobs.append(processed_job)
                
                # Log progress
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(jobs)} jobs")
                    
            except Exception as e:
                logger.error(f"Error processing job {i + 1}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(processed_jobs)} jobs using {'ML-hybrid' if self.use_ml and self.ml_models_available else 'rule-based'} approach")
        return processed_jobs
    
    def generate_enhanced_statistics(self, processed_jobs: List[Dict]) -> Dict:
        """Generate statistics including ML insights"""
        if not processed_jobs:
            return {}
        
        stats = {
            'total_jobs_processed': len(processed_jobs),
            'processing_date': datetime.datetime.now().isoformat(),
            'processing_method': 'ml_hybrid' if self.use_ml and self.ml_models_available else 'rule_based'
        }
        
        # Traditional statistics (for backward compatibility)
        all_technologies = []
        for job in processed_jobs:
            all_technologies.extend(job.get('technology_adoption', []))
        
        tech_counter = Counter(all_technologies)
        urgent_jobs = [job for job in processed_jobs if job.get('urgent_hiring_language', [])]
        
        stats.update({
            'top_technologies': dict(tech_counter.most_common(10)),
            'urgent_jobs_count': len(urgent_jobs),
            'urgent_percentage': round((len(urgent_jobs) / len(processed_jobs)) * 100, 2)
        })
        
        # ML-enhanced statistics
        if self.use_ml and self.ml_models_available:
            ml_urgency_scores = [job.get('ml_urgency_score', 0) for job in processed_jobs]
            high_confidence_predictions = [job for job in processed_jobs 
                                         if job.get('ml_confidence_scores', {}).get('urgency') == 'high']
            
            stats['ml_insights'] = {
                'avg_ml_urgency_score': round(sum(ml_urgency_scores) / len(ml_urgency_scores), 3),
                'high_confidence_predictions': len(high_confidence_predictions),
                'ml_model_coverage': round((len([s for s in ml_urgency_scores if s > 0]) / len(processed_jobs)) * 100, 2)
            }
        
        return stats

def main():
    """Main execution for ML-enhanced signal processing"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize ML processor
    ml_processor = MLSignalProcessor(use_ml=True)
    
    try:
        # Load jobs from Agent 1 output
        jobs = []
        input_paths = [
            "../agent1_data_collector/scraped_jobs.json",
            "agent1_data_collector/scraped_jobs.json",
            "../scraped_jobs.json"
        ]
        
        for path in input_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    jobs = json.load(f)
                logger.info(f"Loaded {len(jobs)} jobs from {path}")
                break
        
        if not jobs:
            logger.error("No job data found. Please run Agent 1 first.")
            return
        
        # Process jobs with ML
        processed_jobs = ml_processor.process_jobs_batch_ml(jobs)
        
        if not processed_jobs:
            logger.error("No jobs were processed successfully.")
            return
        
        # Generate enhanced statistics
        stats = ml_processor.generate_enhanced_statistics(processed_jobs)
        
        # Save results
        os.makedirs("output", exist_ok=True)
        
        # Save processed jobs
        with open("output/ml_signals_output.json", 'w', encoding='utf-8') as f:
            json.dump(processed_jobs, f, indent=2, ensure_ascii=False)
        
        # Save statistics
        with open("output/ml_signal_statistics.json", 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # Also save in traditional format for backward compatibility
        with open("output/signals_output.json", 'w', encoding='utf-8') as f:
            json.dump(processed_jobs, f, indent=2, ensure_ascii=False)
        
        with open("output/signal_statistics.json", 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "="*70)
        print("ML-ENHANCED SIGNAL PROCESSING COMPLETE")
        print("="*70)
        print(f"Jobs Processed: {stats['total_jobs_processed']}")
        print(f"Processing Method: {stats['processing_method']}")
        print(f"Urgent Jobs Detected: {stats['urgent_jobs_count']} ({stats['urgent_percentage']}%)")
        
        if 'ml_insights' in stats:
            ml_insights = stats['ml_insights']
            print(f"Average ML Urgency Score: {ml_insights['avg_ml_urgency_score']}")
            print(f"High Confidence Predictions: {ml_insights['high_confidence_predictions']}")
            print(f"ML Model Coverage: {ml_insights['ml_model_coverage']}%")
        
        print("="*70)
        print("✅ ML-enhanced signal processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise

if __name__ == "__main__":
    main()