#!/usr/bin/env python3
"""
ML-Enhanced Insight Generation Agent
Uses clustering and predictive models for business intelligence
"""

import json
import datetime
import os
import logging
import sys
import numpy as np
from typing import List, Dict, Any
from collections import defaultdict

# Add ml_models to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ml_models.clustering import CompanyClusterer, OpportunityScorer
from ml_models.predictive import HiringTrendPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, dict):
        return {str(key): convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

class MLInsightGenerator:
    """ML-enhanced business insight generation"""
    
    def __init__(self, use_ml: bool = True):
        self.use_ml = use_ml
        self.ml_models_available = False
        
        if use_ml:
            try:
                self.company_clusterer = CompanyClusterer(n_clusters=5)
                self.opportunity_scorer = OpportunityScorer()
                self.trend_predictor = HiringTrendPredictor()
                logger.info("ML insight models initialized successfully")
            except Exception as e:
                logger.warning(f"ML insight models failed to initialize: {e}")
                logger.info("Falling back to rule-based insights")
                self.use_ml = False
    
    def train_ml_models(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Train ML models for insight generation"""
        if not self.use_ml or len(jobs) < 10:
            return {'status': 'skipped', 'reason': 'ML disabled or insufficient data'}
        
        try:
            training_results = {}
            
            # Train company clustering
            logger.info("Training company clustering model...")
            company_clusters = self.company_clusterer.fit_predict(jobs)
            cluster_characteristics = self.company_clusterer.get_cluster_characteristics(jobs, company_clusters)
            
            training_results['company_clustering'] = {
                'clusters_created': len(set(company_clusters.values())),
                'companies_clustered': len(company_clusters),
                'clustering_quality': self.company_clusterer.clustering_stats,
                'cluster_assignments': company_clusters
            }
            
            # Train opportunity scorer
            logger.info("Training opportunity scoring model...")
            scoring_results = self.opportunity_scorer.fit(jobs)
            training_results['opportunity_scorer'] = scoring_results
            
            # Train trend predictor
            logger.info("Training trend prediction models...")
            trend_results = self.trend_predictor.fit(jobs)
            training_results['trend_predictor'] = trend_results
            
            self.ml_models_available = True
            logger.info("✅ ML insight models trained successfully")
            return training_results
            
        except Exception as e:
            logger.error(f"ML insight training failed: {e}")
            self.use_ml = False
            return {'status': 'failed', 'error': str(e)}
    
    def generate_ml_company_clusters(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Generate company clusters using ML"""
        if not self.ml_models_available:
            return self._generate_rule_based_clusters(jobs)
        
        try:
            # Get cluster assignments
            company_clusters = self.company_clusterer.fit_predict(jobs)
            cluster_characteristics = self.company_clusterer.get_cluster_characteristics(jobs, company_clusters)
            
            # Convert to insight format
            cluster_insights = {}
            for cluster_id, characteristics in cluster_characteristics.items():
                companies = characteristics['companies']
                avg_volume = characteristics['avg_hiring_volume']
                urgency_ratio = characteristics['avg_urgency_ratio']
                top_tech = characteristics['top_technologies']
                
                # Generate cluster description
                if urgency_ratio > 0.5:
                    cluster_type = "High-Urgency Hirers"
                elif avg_volume > 3:
                    cluster_type = "Volume Hirers"
                elif top_tech:
                    dominant_tech = list(top_tech.keys())[0]
                    cluster_type = f"{dominant_tech} Specialists"
                else:
                    cluster_type = "Standard Hirers"
                
                cluster_insights[f"cluster_{cluster_id}"] = {
                    'type': cluster_type,
                    'companies': companies,
                    'characteristics': {
                        'avg_hiring_volume': round(avg_volume, 1),
                        'urgency_ratio': round(urgency_ratio, 3),
                        'top_technologies': dict(list(top_tech.items())[:3]),
                        'common_pain_points': characteristics['common_pain_points']
                    },
                    'business_opportunity': self._assess_cluster_opportunity(characteristics)
                }
            
            return {
                'clustering_method': 'ml_kmeans',
                'cluster_insights': cluster_insights,
                'quality_metrics': self.company_clusterer.clustering_stats
            }
            
        except Exception as e:
            logger.warning(f"ML clustering failed: {e}, falling back to rule-based")
            return self._generate_rule_based_clusters(jobs)
    
    def generate_ml_opportunity_scores(self, jobs: List[Dict]) -> List[Dict[str, Any]]:
        """Generate opportunity scores using ML"""
        if not self.ml_models_available:
            return self._generate_rule_based_opportunities(jobs)
        
        try:
            # Get ML opportunity scores
            opportunities = self.opportunity_scorer.score_opportunities(jobs)
            
            # Enhance with additional business logic
            enhanced_opportunities = []
            for opp in opportunities:
                # Add service recommendations based on ML features
                services = self._recommend_services_ml(opp)
                
                # Add contact timing based on urgency
                timing = self._determine_contact_timing_ml(opp)
                
                enhanced_opp = {
                    'company': opp['company'],
                    'opportunity_score': opp['opportunity_score'],
                    'priority_level': opp['priority_level'],
                    'job_count': opp['job_count'],
                    'ml_feature_scores': opp['feature_scores'],
                    'recommended_services': services,
                    'contact_timing': timing,
                    'business_insights': self._generate_business_insights_ml(opp),
                    'scoring_method': 'ml_ensemble'
                }
                enhanced_opportunities.append(enhanced_opp)
            
            return enhanced_opportunities
            
        except Exception as e:
            logger.warning(f"ML opportunity scoring failed: {e}, falling back to rule-based")
            return self._generate_rule_based_opportunities(jobs)
    
    def generate_ml_trend_predictions(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Generate trend predictions using ML"""
        if not self.ml_models_available:
            return self._generate_rule_based_trends(jobs)
        
        try:
            # Current trend analysis
            trend_analysis = self.trend_predictor.analyze_trend_patterns(jobs)
            
            # Future predictions
            future_trends = self.trend_predictor.predict_trends(days_ahead=14)
            
            # Feature importance
            feature_importance = self.trend_predictor.get_feature_importance()
            
            return {
                'current_trends': trend_analysis,
                'future_predictions': future_trends,
                'trend_drivers': feature_importance,
                'prediction_method': 'ml_time_series',
                'confidence_level': 'high' if len(jobs) > 50 else 'medium'
            }
            
        except Exception as e:
            logger.warning(f"ML trend prediction failed: {e}, falling back to rule-based")
            return self._generate_rule_based_trends(jobs)
    
    def _assess_cluster_opportunity(self, characteristics: Dict) -> str:
        """Assess business opportunity for a cluster"""
        urgency_ratio = characteristics['avg_urgency_ratio']
        avg_volume = characteristics['avg_hiring_volume']
        pain_points = characteristics['common_pain_points']
        
        if urgency_ratio > 0.6 and avg_volume > 2:
            return "High - Urgent scaling needs"
        elif len(pain_points) > 2:
            return "Medium - Technical transformation needed"
        elif avg_volume > 4:
            return "Medium - Volume hiring indicates growth"
        else:
            return "Low - Standard hiring patterns"
    
    def _recommend_services_ml(self, opportunity: Dict) -> List[str]:
        """Recommend services based on ML feature analysis"""
        services = []
        feature_scores = opportunity.get('feature_scores', {})
        
        # High tech adoption score
        if feature_scores.get('tech_adoption', 0) > 0.7:
            services.extend(['Technical Consulting', 'Architecture Review'])
        
        # High hiring velocity
        if feature_scores.get('hiring_velocity', 0) > 0.8:
            services.extend(['Rapid Team Building', 'Technical Recruiting'])
        
        # Pain points detected
        if feature_scores.get('pain_points', 0) > 0.5:
            services.extend(['Legacy System Modernization', 'Technical Debt Reduction'])
        
        # Scaling signals
        if feature_scores.get('scaling_signals', 0) > 0.6:
            services.extend(['DevOps Consulting', 'Infrastructure Scaling'])
        
        return services[:3] if services else ['General Technical Consulting']
    
    def _determine_contact_timing_ml(self, opportunity: Dict) -> str:
        """Determine optimal contact timing based on ML insights"""
        priority = opportunity.get('priority_level', 'Low')
        feature_scores = opportunity.get('feature_scores', {})
        
        if priority == 'High' and feature_scores.get('hiring_velocity', 0) > 0.8:
            return 'Immediately (within 24 hours)'
        elif priority == 'High':
            return 'Within 3 days'
        elif priority == 'Medium':
            return 'Within 1 week'
        else:
            return 'Within 2 weeks'
    
    def _generate_business_insights_ml(self, opportunity: Dict) -> List[str]:
        """Generate business insights using ML analysis"""
        insights = []
        company = opportunity['company']
        score = opportunity['opportunity_score']
        features = opportunity.get('feature_scores', {})
        
        # Insight based on overall score
        if score >= 80:
            insights.append(f"{company} shows exceptional growth indicators with {score}% opportunity score")
        elif score >= 60:
            insights.append(f"{company} demonstrates solid expansion signals with {score}% opportunity score")
        
        # Feature-specific insights
        if features.get('hiring_velocity', 0) > 0.7:
            insights.append(f"{company} is in rapid hiring mode, indicating urgent scaling needs")
        
        if features.get('tech_adoption', 0) > 0.6:
            insights.append(f"{company} is heavily investing in new technologies, suggesting modernization initiatives")
        
        return insights[:2]  # Return top 2 insights
    
    def _generate_rule_based_clusters(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Fallback rule-based clustering"""
        # Group companies by hiring volume
        company_jobs = defaultdict(list)
        for job in jobs:
            company = job.get('company', 'Unknown')
            if company != 'Unknown':
                company_jobs[company].append(job)
        
        clusters = {
            'high_volume': {'companies': [], 'type': 'Volume Hirers'},
            'urgent_hirers': {'companies': [], 'type': 'Urgent Hirers'},
            'tech_focused': {'companies': [], 'type': 'Technology Specialists'},
            'standard': {'companies': [], 'type': 'Standard Hirers'}
        }
        
        for company, jobs_list in company_jobs.items():
            job_count = len(jobs_list)
            urgent_count = sum(1 for job in jobs_list if job.get('urgent_hiring_language', []))
            tech_count = sum(len(job.get('technology_adoption', [])) for job in jobs_list)
            
            if job_count >= 3:
                clusters['high_volume']['companies'].append(company)
            elif urgent_count >= 2:
                clusters['urgent_hirers']['companies'].append(company)
            elif tech_count >= 5:
                clusters['tech_focused']['companies'].append(company)
            else:
                clusters['standard']['companies'].append(company)
        
        return {
            'clustering_method': 'rule_based',
            'cluster_insights': clusters,
            'quality_metrics': {'method': 'heuristic'}
        }
    
    def _generate_rule_based_opportunities(self, jobs: List[Dict]) -> List[Dict[str, Any]]:
        """Fallback rule-based opportunity scoring"""
        company_jobs = defaultdict(list)
        for job in jobs:
            company = job.get('company', 'Unknown')
            if company != 'Unknown':
                company_jobs[company].append(job)
        
        opportunities = []
        for company, jobs_list in company_jobs.items():
            job_count = len(jobs_list)
            urgent_count = sum(1 for job in jobs_list if job.get('urgent_hiring_language', []))
            tech_count = sum(len(job.get('technology_adoption', [])) for job in jobs_list)
            
            # Simple scoring
            score = min(100, (job_count * 10) + (urgent_count * 20) + (tech_count * 2))
            
            if score >= 70:
                priority = 'High'
            elif score >= 40:
                priority = 'Medium'
            else:
                priority = 'Low'
            
            opportunities.append({
                'company': company,
                'opportunity_score': score,
                'priority_level': priority,
                'job_count': job_count,
                'scoring_method': 'rule_based'
            })
        
        return sorted(opportunities, key=lambda x: x['opportunity_score'], reverse=True)
    
    def _generate_rule_based_trends(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Fallback rule-based trend analysis"""
        from collections import Counter
        
        # Technology trends
        all_tech = []
        for job in jobs:
            all_tech.extend(job.get('technology_adoption', []))
        tech_trends = Counter(all_tech).most_common(10)
        
        # Urgency trends
        urgent_jobs = [job for job in jobs if job.get('urgent_hiring_language', [])]
        urgency_rate = len(urgent_jobs) / len(jobs) * 100 if jobs else 0
        
        return {
            'current_trends': {
                'technology_trends': dict(tech_trends),
                'urgency_rate': round(urgency_rate, 2),
                'total_companies': len(set(job.get('company') for job in jobs))
            },
            'prediction_method': 'rule_based',
            'confidence_level': 'low'
        }
    
    def generate_comprehensive_insights_ml(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive ML-powered business insights"""
        logger.info("Generating comprehensive ML insights...")
        
        # Train models if not already trained
        if self.use_ml and not self.ml_models_available:
            training_results = self.train_ml_models(jobs)
        
        # Generate all insights
        cluster_analysis = self.generate_ml_company_clusters(jobs)
        opportunity_scores = self.generate_ml_opportunity_scores(jobs)
        trend_predictions = self.generate_ml_trend_predictions(jobs)
        
        # Combine into comprehensive report
        comprehensive_insights = {
            'analysis_date': datetime.datetime.now().isoformat(),
            'analysis_method': 'ml_enhanced' if self.ml_models_available else 'rule_based',
            'total_jobs_analyzed': len(jobs),
            'total_companies_analyzed': len(set(job.get('company') for job in jobs if job.get('company') != 'Unknown')),
            
            'company_clustering': cluster_analysis,
            'opportunity_rankings': opportunity_scores[:15],  # Top 15 opportunities
            'market_trends': trend_predictions,
            
            'executive_summary': {
                'high_priority_opportunities': len([opp for opp in opportunity_scores if opp['priority_level'] == 'High']),
                'avg_opportunity_score': round(sum(opp['opportunity_score'] for opp in opportunity_scores) / len(opportunity_scores), 1) if opportunity_scores else 0,
                'companies_in_urgent_hiring': len([opp for opp in opportunity_scores if 'urgent' in str(opp).lower()]),
                'ml_confidence': 'high' if self.ml_models_available and len(jobs) > 50 else 'medium'
            }
        }
        
        return comprehensive_insights

def main():
    """Main execution for ML-enhanced insight generation"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize ML insight generator
    ml_insights = MLInsightGenerator(use_ml=True)
    
    try:
        # Load processed signals from Agent 2
        jobs = []
        input_paths = [
            "../agent2_signal_processor/output/signals_output.json",
            "agent2_signal_processor/output/signals_output.json",
            "../output/signals_output.json",
            "output/signals_output.json"
        ]
        
        for path in input_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    jobs = json.load(f)
                logger.info(f"Loaded {len(jobs)} processed jobs from {path}")
                break
        
        if not jobs:
            logger.error("No processed job data found. Please run Agent 2 first.")
            return
        
        # Generate comprehensive insights
        insights = ml_insights.generate_comprehensive_insights_ml(jobs)
        
        # Convert numpy types for JSON serialization
        insights = convert_numpy_types(insights)
        
        # Save results
        os.makedirs("output", exist_ok=True)
        
        # Save ML insights
        with open("output/ml_company_insights.json", 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        
        # Save in traditional format for backward compatibility
        traditional_insights = []
        for opp in insights['opportunity_rankings']:
            traditional_insight = {
                'company': opp['company'],
                'insights': opp.get('business_insights', [f"{opp['company']} shows {opp['priority_level'].lower()} priority opportunity"]),
                'job_count': opp['job_count'],
                'opportunity_score': opp['opportunity_score'],
                'timestamp': insights['analysis_date']
            }
            traditional_insights.append(traditional_insight)
        
        with open("output/company_insights.json", 'w', encoding='utf-8') as f:
            json.dump(traditional_insights, f, indent=2, ensure_ascii=False)
        
        # Save industry trends
        market_trends = convert_numpy_types(insights['market_trends'])
        with open("output/industry_trends.json", 'w', encoding='utf-8') as f:
            json.dump(market_trends, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "="*70)
        print("ML-ENHANCED BUSINESS INSIGHTS GENERATED")
        print("="*70)
        exec_summary = insights['executive_summary']
        print(f"Companies Analyzed: {insights['total_companies_analyzed']}")
        print(f"High Priority Opportunities: {exec_summary['high_priority_opportunities']}")
        print(f"Average Opportunity Score: {exec_summary['avg_opportunity_score']}%")
        print(f"Analysis Method: {insights['analysis_method']}")
        print(f"ML Confidence: {exec_summary['ml_confidence']}")
        print("="*70)
        print("✅ ML-enhanced insight generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Insight generation failed: {e}")
        raise

if __name__ == "__main__":
    main()