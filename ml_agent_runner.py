#!/usr/bin/env python3
"""
ML-Enhanced Job Intelligence System
Combines all ML models into a production pipeline
"""

import json
import os
import datetime
import logging
from typing import List, Dict, Any

from ml_models.feature_engineering import JobFeatureExtractor
from ml_models.text_classifier import UrgencyClassifier, TechStackClassifier
from ml_models.clustering import CompanyClusterer, OpportunityScorer
from ml_models.predictive import HiringTrendPredictor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLJobIntelligenceSystem:
    """Complete ML pipeline for job posting intelligence"""
    
    def __init__(self):
        self.feature_extractor = JobFeatureExtractor()
        self.urgency_classifier = UrgencyClassifier()
        self.tech_classifier = TechStackClassifier()
        self.company_clusterer = CompanyClusterer()
        self.opportunity_scorer = OpportunityScorer()
        self.trend_predictor = HiringTrendPredictor()
        
        self.is_trained = False
        self.training_stats = {}
        
    def load_job_data(self, data_path: str = None) -> List[Dict]:
        """Load job data from various sources"""
        jobs = []
        
        # Try multiple data sources
        data_paths = [
            data_path,
            "agent2_signal_processor/output/signals_output.json",
            "output/signals_output.json",
            "scraped_jobs.json"
        ]
        
        for path in data_paths:
            if path and os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        jobs = json.load(f)
                    logger.info(f"Loaded {len(jobs)} jobs from {path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load from {path}: {e}")
                    continue
        
        if not jobs:
            logger.error("No job data found. Please run the data collection pipeline first.")
            return []
        
        return jobs
    
    def train_all_models(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Train all ML models on job data"""
        logger.info("Starting ML model training...")
        
        if len(jobs) < 10:
            raise ValueError("Insufficient data for ML training. Need at least 10 jobs.")
        
        training_results = {}
        
        try:
            # 1. Feature Engineering
            logger.info("Extracting features...")
            features = self.feature_extractor.extract_all_features(jobs)
            training_results['feature_extraction'] = {
                'n_features': features['combined_features'].shape[1],
                'n_samples': features['combined_features'].shape[0]
            }
            
            # 2. Train Urgency Classifier
            logger.info("Training urgency classification model...")
            urgency_results = self.urgency_classifier.train(jobs)
            training_results['urgency_classifier'] = urgency_results
            
            # 3. Train Technology Stack Classifier
            logger.info("Training technology classification models...")
            tech_results = self.tech_classifier.train(jobs)
            training_results['tech_classifier'] = tech_results
            
            # 4. Train Company Clustering
            logger.info("Training company clustering model...")
            company_clusters = self.company_clusterer.fit_predict(jobs)
            cluster_chars = self.company_clusterer.get_cluster_characteristics(jobs, company_clusters)
            training_results['company_clustering'] = {
                'stats': self.company_clusterer.clustering_stats,
                'clusters': len(set(company_clusters.values())),
                'cluster_characteristics': cluster_chars
            }
            
            # 5. Train Opportunity Scorer
            logger.info("Training opportunity scoring model...")
            scoring_results = self.opportunity_scorer.fit(jobs)
            training_results['opportunity_scorer'] = scoring_results
            
            # 6. Train Trend Predictor
            logger.info("Training hiring trend prediction models...")
            trend_results = self.trend_predictor.fit(jobs)
            training_results['trend_predictor'] = trend_results
            
            self.is_trained = True
            self.training_stats = training_results
            
            logger.info("✅ All ML models trained successfully!")
            return training_results
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise
    
    def process_jobs_ml(self, jobs: List[Dict]) -> List[Dict]:
        """Process jobs using trained ML models"""
        if not self.is_trained:
            raise ValueError("Models must be trained before processing jobs")
        
        logger.info(f"Processing {len(jobs)} jobs with ML models...")
        
        processed_jobs = []
        descriptions = [job.get('description', '') for job in jobs]
        
        # ML Predictions
        urgency_predictions = self.urgency_classifier.predict(descriptions)
        urgency_probabilities = self.urgency_classifier.predict_proba(descriptions)
        tech_predictions = self.tech_classifier.predict_tech_categories(descriptions)
        
        for i, job in enumerate(jobs):
            processed_job = job.copy()
            
            # Add ML predictions
            processed_job['ml_predictions'] = {
                'urgency_score': urgency_probabilities[i],
                'urgency_class': urgency_predictions[i],
                'tech_categories': tech_predictions[i],
                'processing_date': datetime.datetime.now().isoformat()
            }
            
            # Enhanced technology extraction using ML
            ml_tech_extraction = self.tech_classifier.extract_technologies_ml([descriptions[i]])
            processed_job['ml_technology_adoption'] = ml_tech_extraction[0] if ml_tech_extraction else []
            
            processed_jobs.append(processed_job)
        
        return processed_jobs
    
    def generate_ml_insights(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Generate business insights using ML models"""
        if not self.is_trained:
            raise ValueError("Models must be trained before generating insights")
        
        logger.info("Generating ML-powered business insights...")
        
        # Company clustering and analysis
        company_clusters = self.company_clusterer.fit_predict(jobs)
        cluster_characteristics = self.company_clusterer.get_cluster_characteristics(jobs, company_clusters)
        
        # Opportunity scoring
        opportunities = self.opportunity_scorer.score_opportunities(jobs)
        
        # Trend analysis and prediction
        trend_analysis = self.trend_predictor.analyze_trend_patterns(jobs)
        future_trends = self.trend_predictor.predict_trends(days_ahead=7)
        
        # Feature importance analysis
        urgency_importance = self.urgency_classifier.get_feature_importance()
        trend_importance = self.trend_predictor.get_feature_importance()
        
        ml_insights = {
            'analysis_date': datetime.datetime.now().isoformat(),
            'ml_model_performance': self.training_stats,
            'company_clusters': {
                'cluster_assignments': company_clusters,
                'cluster_characteristics': cluster_characteristics,
                'clustering_quality': self.company_clusterer.clustering_stats
            },
            'opportunity_rankings': opportunities[:10],  # Top 10 opportunities
            'market_trends': {
                'current_analysis': trend_analysis,
                'future_predictions': future_trends
            },
            'feature_insights': {
                'urgency_keywords': urgency_importance,
                'trend_drivers': trend_importance
            },
            'ml_summary': {
                'total_companies_analyzed': len(set(job.get('company') for job in jobs)),
                'high_priority_opportunities': len([opp for opp in opportunities if opp['priority_level'] == 'High']),
                'avg_opportunity_score': sum(opp['opportunity_score'] for opp in opportunities) / len(opportunities) if opportunities else 0,
                'model_confidence': {
                    'urgency_classifier': self.training_stats.get('urgency_classifier', {}).get('cv_mean', 0),
                    'clustering_quality': self.company_clusterer.clustering_stats.get('silhouette_score', 0)
                }
            }
        }
        
        return ml_insights
    
    def save_ml_results(self, processed_jobs: List[Dict], insights: Dict[str, Any], output_dir: str = "ml_output"):
        """Save ML processing results"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save processed jobs with ML predictions
        jobs_file = os.path.join(output_dir, "ml_processed_jobs.json")
        with open(jobs_file, 'w') as f:
            json.dump(processed_jobs, f, indent=2, ensure_ascii=False)
        
        # Save ML insights
        insights_file = os.path.join(output_dir, "ml_insights.json")
        with open(insights_file, 'w') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        
        # Save model training statistics
        stats_file = os.path.join(output_dir, "ml_training_stats.json")
        with open(stats_file, 'w') as f:
            json.dump(self.training_stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"ML results saved to {output_dir}/")
    
    def run_complete_ml_pipeline(self, data_path: str = None) -> Dict[str, Any]:
        """Run the complete ML pipeline"""
        logger.info("🤖 Starting ML-Enhanced Job Intelligence Pipeline")
        
        # Load data
        jobs = self.load_job_data(data_path)
        if not jobs:
            return {'error': 'No job data available'}
        
        # Train models
        training_results = self.train_all_models(jobs)
        
        # Process jobs with ML
        processed_jobs = self.process_jobs_ml(jobs)
        
        # Generate insights
        ml_insights = self.generate_ml_insights(jobs)
        
        # Save results
        self.save_ml_results(processed_jobs, ml_insights)
        
        # Summary
        summary = {
            'pipeline_status': 'completed',
            'jobs_processed': len(processed_jobs),
            'models_trained': len(training_results),
            'high_priority_opportunities': len([opp for opp in ml_insights['opportunity_rankings'] if opp['priority_level'] == 'High']),
            'completion_time': datetime.datetime.now().isoformat()
        }
        
        logger.info("✅ ML Pipeline completed successfully!")
        return summary

def main():
    """Main execution function"""
    ml_system = MLJobIntelligenceSystem()
    
    try:
        # Run complete pipeline
        results = ml_system.run_complete_ml_pipeline()
        
        print("\n" + "="*60)
        print("ML JOB INTELLIGENCE SYSTEM - RESULTS")
        print("="*60)
        print(f"Status: {results.get('pipeline_status', 'unknown')}")
        print(f"Jobs Processed: {results.get('jobs_processed', 0)}")
        print(f"Models Trained: {results.get('models_trained', 0)}")
        print(f"High Priority Opportunities: {results.get('high_priority_opportunities', 0)}")
        print(f"Completion Time: {results.get('completion_time', 'unknown')}")
        print("="*60)
        
        if results.get('pipeline_status') == 'completed':
            print("\n🎯 Check ml_output/ directory for detailed ML results")
            print("📊 ML models are now ready for production use")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()