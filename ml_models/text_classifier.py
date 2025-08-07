#!/usr/bin/env python3
"""
Text Classification Models for Signal Detection
Replaces rule-based pattern matching with ML classification
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import re
import os

class UrgencyClassifier:
    """ML model to detect urgent hiring language in job descriptions"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.is_trained = False
        
    def _create_training_labels(self, jobs: List[Dict]) -> Tuple[List[str], List[int]]:
        """Create training data from existing rule-based results"""
        descriptions = []
        labels = []
        
        # Use existing urgent_hiring_language field as ground truth
        for job in jobs:
            description = job.get('description', '')
            urgent_signals = job.get('urgent_hiring_language', [])
            
            descriptions.append(description)
            # Binary classification: urgent (1) or not urgent (0)
            labels.append(1 if len(urgent_signals) > 0 else 0)
            
        return descriptions, labels
    
    def train(self, jobs: List[Dict]) -> Dict[str, float]:
        """Train the urgency classification model"""
        descriptions, labels = self._create_training_labels(jobs)
        
        if len(set(labels)) < 2:
            # Handle case where all jobs are the same class
            print("Warning: All jobs have the same urgency label. Using balanced dummy data.")
            return {'accuracy': 0.5, 'note': 'Insufficient diverse training data'}
        
        # Vectorize text
        X = self.vectorizer.fit_transform(descriptions)
        y = np.array(labels)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5)
        
        self.is_trained = True
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    def predict(self, descriptions: List[str]) -> List[int]:
        """Predict urgency for job descriptions"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        X = self.vectorizer.transform(descriptions)
        return self.model.predict(X).tolist()
    
    def predict_proba(self, descriptions: List[str]) -> List[float]:
        """Get urgency probability scores"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        X = self.vectorizer.transform(descriptions)
        probabilities = self.model.predict_proba(X)
        # Return probability of urgent class (class 1)
        return probabilities[:, 1].tolist()
    
    def get_feature_importance(self, top_n: int = 20) -> List[Tuple[str, float]]:
        """Get most important features for urgency detection"""
        if not self.is_trained:
            return []
            
        feature_names = self.vectorizer.get_feature_names_out()
        importances = self.model.feature_importances_
        
        feature_importance = list(zip(feature_names, importances))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        return feature_importance[:top_n]

class TechStackClassifier:
    """ML model to classify and extract technology stacks from job descriptions"""
    
    def __init__(self):
        self.models = {}  # One model per technology category
        self.vectorizer = TfidfVectorizer(max_features=300, stop_words='english', ngram_range=(1, 2))
        self.tech_categories = [
            'Programming Languages',
            'Web Frameworks', 
            'Cloud Platforms',
            'Databases',
            'DevOps Tools',
            'AI/ML Libraries'
        ]
        self.is_trained = False
        
    def _categorize_technologies(self, tech_list: List[str]) -> Dict[str, List[str]]:
        """Categorize technologies into different types"""
        categories = {
            'Programming Languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'C#', 'PHP', 'Ruby', 'Swift', 'Kotlin'],
            'Web Frameworks': ['React', 'Angular', 'Vue', 'Django', 'Flask', 'Express', 'Node.js', 'Next.js', 'Laravel', 'Rails'],
            'Cloud Platforms': ['AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes'],
            'Databases': ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra', 'DynamoDB'],
            'DevOps Tools': ['Jenkins', 'GitLab CI', 'GitHub Actions', 'Terraform', 'Ansible', 'Grafana', 'Prometheus'],
            'AI/ML Libraries': ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Keras']
        }
        
        result = {cat: [] for cat in categories.keys()}
        
        for tech in tech_list:
            for category, tech_names in categories.items():
                if tech in tech_names:
                    result[category].append(tech)
                    break
                    
        return result
    
    def train(self, jobs: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Train technology stack classification models"""
        descriptions = [job.get('description', '') for job in jobs]
        
        # Vectorize all descriptions
        X = self.vectorizer.fit_transform(descriptions)
        
        results = {}
        
        for category in self.tech_categories:
            # Create binary labels for this technology category
            labels = []
            for job in jobs:
                tech_adoption = job.get('technology_adoption', [])
                categorized = self._categorize_technologies(tech_adoption)
                # Binary: does this job mention any tech in this category?
                labels.append(1 if len(categorized[category]) > 0 else 0)
            
            y = np.array(labels)
            
            if len(set(labels)) < 2:
                results[category] = {'accuracy': 0.5, 'note': 'Insufficient diverse data'}
                continue
            
            # Train model for this category
            model = LogisticRegression(random_state=42)
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            model.fit(X_train, y_train)
            
            # Evaluate
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            self.models[category] = model
            
            results[category] = {
                'train_accuracy': train_score,
                'test_accuracy': test_score
            }
        
        self.is_trained = True
        return results
    
    def predict_tech_categories(self, descriptions: List[str]) -> List[Dict[str, float]]:
        """Predict probability of each technology category for job descriptions"""
        if not self.is_trained:
            raise ValueError("Models must be trained before prediction")
            
        X = self.vectorizer.transform(descriptions)
        results = []
        
        for i in range(len(descriptions)):
            job_predictions = {}
            for category, model in self.models.items():
                prob = model.predict_proba(X[i])[0][1]  # Probability of positive class
                job_predictions[category] = prob
            results.append(job_predictions)
            
        return results
    
    def extract_technologies_ml(self, descriptions: List[str], threshold: float = 0.5) -> List[List[str]]:
        """Extract likely technologies using ML predictions"""
        category_predictions = self.predict_tech_categories(descriptions)
        
        # Technology mapping based on categories
        tech_mapping = {
            'Programming Languages': ['Python', 'JavaScript', 'Java', 'TypeScript', 'Go'],
            'Web Frameworks': ['React', 'Node.js', 'Angular', 'Vue', 'Django'],
            'Cloud Platforms': ['AWS', 'Azure', 'Docker', 'Kubernetes'],
            'Databases': ['PostgreSQL', 'MongoDB', 'Redis', 'MySQL'],
            'DevOps Tools': ['Jenkins', 'GitLab CI', 'Terraform'],
            'AI/ML Libraries': ['TensorFlow', 'PyTorch', 'Scikit-learn']
        }
        
        results = []
        for prediction in category_predictions:
            job_techs = []
            for category, probability in prediction.items():
                if probability > threshold and category in tech_mapping:
                    # Add representative technologies from this category
                    job_techs.extend(tech_mapping[category][:2])  # Top 2 from each category
            results.append(job_techs)
            
        return results