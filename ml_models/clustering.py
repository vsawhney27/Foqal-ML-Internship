#!/usr/bin/env python3
"""
Clustering and Scoring Models for Company Opportunity Analysis
Uses unsupervised ML to identify patterns and score opportunities
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from collections import defaultdict
import joblib

class CompanyClusterer:
    """Cluster companies based on hiring patterns and characteristics"""
    
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # Keep 95% of variance
        self.is_fitted = False
        self.cluster_labels = []
        
    def _extract_company_features(self, jobs: List[Dict]) -> Tuple[List[str], np.ndarray]:
        """Extract features for each company from their job postings"""
        company_data = defaultdict(list)
        
        # Group jobs by company
        for job in jobs:
            company = job.get('company', 'Unknown')
            if company != 'Unknown':
                company_data[company].append(job)
        
        companies = list(company_data.keys())
        features = []
        
        for company in companies:
            company_jobs = company_data[company]
            
            # Hiring volume features
            total_jobs = len(company_jobs)
            urgent_jobs = sum(1 for job in company_jobs if job.get('urgent_hiring_language', []))
            urgent_ratio = urgent_jobs / total_jobs if total_jobs > 0 else 0
            
            # Technology diversity
            all_tech = []
            for job in company_jobs:
                all_tech.extend(job.get('technology_adoption', []))
            unique_tech = len(set(all_tech))
            tech_mentions = len(all_tech)
            
            # Department diversity
            departments = set(job.get('department', 'Unknown') for job in company_jobs)
            dept_diversity = len(departments)
            
            # Pain points
            all_pain_points = []
            for job in company_jobs:
                all_pain_points.extend(job.get('pain_points', []))
            pain_points_count = len(all_pain_points)
            unique_pain_points = len(set(all_pain_points))
            
            # Budget signals
            jobs_with_salary = sum(1 for job in company_jobs 
                                 if job.get('budget_signals', {}).get('salary_ranges', []))
            jobs_with_equity = sum(1 for job in company_jobs 
                                 if job.get('budget_signals', {}).get('equity_mentions', []))
            
            salary_transparency = jobs_with_salary / total_jobs if total_jobs > 0 else 0
            equity_ratio = jobs_with_equity / total_jobs if total_jobs > 0 else 0
            
            # Company size indicators (based on hiring patterns)
            avg_description_length = np.mean([len(job.get('description', '')) for job in company_jobs])
            
            company_features = [
                total_jobs,
                urgent_ratio,
                unique_tech,
                tech_mentions,
                dept_diversity,
                pain_points_count,
                unique_pain_points,
                salary_transparency,
                equity_ratio,
                avg_description_length
            ]
            
            features.append(company_features)
        
        return companies, np.array(features)
    
    def fit_predict(self, jobs: List[Dict]) -> Dict[str, int]:
        """Cluster companies and return cluster assignments"""
        companies, features = self._extract_company_features(jobs)
        
        if len(companies) < self.n_clusters:
            # Adjust number of clusters if we have fewer companies
            self.n_clusters = max(2, len(companies))
            self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Apply PCA for dimensionality reduction
        features_pca = self.pca.fit_transform(features_scaled)
        
        # Fit clustering
        cluster_labels = self.kmeans.fit_predict(features_pca)
        
        # Calculate silhouette score
        if len(set(cluster_labels)) > 1:
            silhouette_avg = silhouette_score(features_pca, cluster_labels)
        else:
            silhouette_avg = 0
        
        self.cluster_labels = cluster_labels
        self.is_fitted = True
        
        # Return company-cluster mapping
        company_clusters = dict(zip(companies, cluster_labels))
        
        self.clustering_stats = {
            'silhouette_score': silhouette_avg,
            'n_companies': len(companies),
            'n_clusters': len(set(cluster_labels)),
            'cluster_sizes': {i: sum(1 for x in cluster_labels if x == i) 
                            for i in set(cluster_labels)}
        }
        
        return company_clusters
    
    def get_cluster_characteristics(self, jobs: List[Dict], company_clusters: Dict[str, int]) -> Dict[int, Dict]:
        """Analyze characteristics of each cluster"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before analyzing clusters")
        
        cluster_chars = defaultdict(lambda: {
            'companies': [],
            'avg_hiring_volume': 0,
            'avg_urgency_ratio': 0,
            'top_technologies': [],
            'common_pain_points': [],
            'salary_transparency': 0
        })
        
        # Group companies by cluster
        for company, cluster_id in company_clusters.items():
            cluster_chars[cluster_id]['companies'].append(company)
        
        # Analyze each cluster
        for cluster_id in cluster_chars.keys():
            cluster_companies = cluster_chars[cluster_id]['companies']
            cluster_jobs = [job for job in jobs if job.get('company') in cluster_companies]
            
            if not cluster_jobs:
                continue
            
            # Calculate cluster statistics
            companies_in_cluster = len(cluster_companies)
            total_jobs = len(cluster_jobs)
            
            # Hiring volume
            cluster_chars[cluster_id]['avg_hiring_volume'] = total_jobs / companies_in_cluster
            
            # Urgency ratio
            urgent_jobs = sum(1 for job in cluster_jobs if job.get('urgent_hiring_language', []))
            cluster_chars[cluster_id]['avg_urgency_ratio'] = urgent_jobs / total_jobs if total_jobs > 0 else 0
            
            # Technology analysis
            all_tech = []
            for job in cluster_jobs:
                all_tech.extend(job.get('technology_adoption', []))
            tech_counter = pd.Series(all_tech).value_counts()
            cluster_chars[cluster_id]['top_technologies'] = tech_counter.head(5).to_dict()
            
            # Pain points
            all_pain_points = []
            for job in cluster_jobs:
                all_pain_points.extend(job.get('pain_points', []))
            pain_counter = pd.Series(all_pain_points).value_counts()
            cluster_chars[cluster_id]['common_pain_points'] = pain_counter.head(3).to_dict()
            
            # Salary transparency
            jobs_with_salary = sum(1 for job in cluster_jobs 
                                 if job.get('budget_signals', {}).get('salary_ranges', []))
            cluster_chars[cluster_id]['salary_transparency'] = jobs_with_salary / total_jobs if total_jobs > 0 else 0
        
        return dict(cluster_chars)

class OpportunityScorer:
    """ML-based opportunity scoring using ensemble methods"""
    
    def __init__(self):
        self.feature_weights = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def _extract_opportunity_features(self, company_jobs: List[Dict], company: str) -> np.ndarray:
        """Extract features for opportunity scoring"""
        if not company_jobs:
            return np.zeros(12)
        
        total_jobs = len(company_jobs)
        
        # Hiring velocity features
        urgent_jobs = sum(1 for job in company_jobs if job.get('urgent_hiring_language', []))
        urgency_score = urgent_jobs / total_jobs
        
        # Technology adoption features
        all_tech = []
        for job in company_jobs:
            all_tech.extend(job.get('technology_adoption', []))
        
        tech_diversity = len(set(all_tech))
        tech_volume = len(all_tech)
        
        # High-value technology indicators
        high_value_tech = ['AI', 'ML', 'Machine Learning', 'AWS', 'Kubernetes', 'React', 'Python']
        high_value_count = sum(1 for tech in all_tech if tech in high_value_tech)
        high_value_ratio = high_value_count / len(all_tech) if all_tech else 0
        
        # Department scaling
        departments = [job.get('department', 'Unknown') for job in company_jobs]
        dept_diversity = len(set(departments))
        engineering_jobs = sum(1 for dept in departments if 'engineer' in dept.lower())
        engineering_ratio = engineering_jobs / total_jobs
        
        # Pain points (opportunity indicators)
        all_pain_points = []
        for job in company_jobs:
            all_pain_points.extend(job.get('pain_points', []))
        pain_points_count = len(all_pain_points)
        
        # Budget indicators
        jobs_with_salary = sum(1 for job in company_jobs 
                             if job.get('budget_signals', {}).get('salary_ranges', []))
        jobs_with_equity = sum(1 for job in company_jobs 
                             if job.get('budget_signals', {}).get('equity_mentions', []))
        
        budget_transparency = jobs_with_salary / total_jobs
        equity_offering = jobs_with_equity / total_jobs
        
        # Job description quality (indicates serious hiring)
        avg_desc_length = np.mean([len(job.get('description', '')) for job in company_jobs])
        
        features = np.array([
            total_jobs,
            urgency_score,
            tech_diversity,
            tech_volume,
            high_value_ratio,
            dept_diversity,
            engineering_ratio,
            pain_points_count,
            budget_transparency,
            equity_offering,
            avg_desc_length / 1000,  # Normalize
            min(total_jobs / 10, 1.0)  # Volume cap feature
        ])
        
        return features
    
    def fit(self, jobs: List[Dict]) -> Dict[str, float]:
        """Learn optimal feature weights from data patterns"""
        company_data = defaultdict(list)
        
        # Group jobs by company
        for job in jobs:
            company = job.get('company', 'Unknown')
            if company != 'Unknown':
                company_data[company].append(job)
        
        companies = list(company_data.keys())
        features_matrix = []
        
        # Extract features for all companies
        for company in companies:
            company_jobs = company_data[company]
            features = self._extract_opportunity_features(company_jobs, company)
            features_matrix.append(features)
        
        features_matrix = np.array(features_matrix)
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features_matrix)
        
        # Use PCA to determine feature importance
        pca = PCA()
        pca.fit(features_scaled)
        
        # Weight features based on PCA loadings and business logic
        feature_importance = np.abs(pca.components_[0])  # First principal component
        
        # Apply business logic weighting
        business_weights = np.array([
            0.2,  # total_jobs
            0.25, # urgency_score - high importance
            0.15, # tech_diversity
            0.1,  # tech_volume
            0.2,  # high_value_ratio - high importance
            0.1,  # dept_diversity
            0.15, # engineering_ratio
            0.15, # pain_points_count
            0.1,  # budget_transparency
            0.05, # equity_offering
            0.05, # avg_desc_length
            0.1   # volume_cap
        ])
        
        # Combine PCA weights with business weights
        self.feature_weights = 0.6 * business_weights + 0.4 * feature_importance
        self.feature_weights = self.feature_weights / np.sum(self.feature_weights)  # Normalize
        
        self.is_fitted = True
        
        # Return fit statistics
        explained_variance_ratio = pca.explained_variance_ratio_[0]
        
        return {
            'explained_variance': explained_variance_ratio,
            'n_companies': len(companies),
            'feature_weights_learned': True
        }
    
    def score_opportunities(self, jobs: List[Dict]) -> List[Dict[str, Any]]:
        """Score all company opportunities using ML approach"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before scoring")
        
        company_data = defaultdict(list)
        
        # Group jobs by company
        for job in jobs:
            company = job.get('company', 'Unknown')
            if company != 'Unknown':
                company_data[company].append(job)
        
        opportunities = []
        
        for company, company_jobs in company_data.items():
            # Extract features
            features = self._extract_opportunity_features(company_jobs, company)
            features_scaled = self.scaler.transform(features.reshape(1, -1))[0]
            
            # Calculate weighted score
            opportunity_score = np.dot(features_scaled, self.feature_weights)
            
            # Normalize to 0-100 scale
            opportunity_score = max(0, min(100, opportunity_score * 100))
            
            # Determine priority level
            if opportunity_score >= 80:
                priority = 'High'
            elif opportunity_score >= 60:
                priority = 'Medium'
            else:
                priority = 'Low'
            
            opportunities.append({
                'company': company,
                'opportunity_score': round(opportunity_score, 2),
                'priority_level': priority,
                'job_count': len(company_jobs),
                'feature_scores': {
                    'hiring_velocity': features[1],
                    'tech_adoption': features[4],
                    'scaling_signals': features[0],
                    'pain_points': features[7]
                }
            })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return opportunities