#!/usr/bin/env python3
"""
Feature Engineering Pipeline for Job Intelligence System
Converts raw job postings into ML-ready features
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
import re
import nltk
from collections import Counter

class JobFeatureExtractor:
    """Extract ML features from job postings"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_fitted = False
        
    def extract_text_features(self, jobs: List[Dict]) -> np.ndarray:
        """Extract TF-IDF features from job descriptions"""
        descriptions = [job.get('description', '') for job in jobs]
        
        if not self.is_fitted:
            tfidf_features = self.tfidf_vectorizer.fit_transform(descriptions)
        else:
            tfidf_features = self.tfidf_vectorizer.transform(descriptions)
            
        return tfidf_features.toarray()
    
    def extract_categorical_features(self, jobs: List[Dict]) -> np.ndarray:
        """Extract and encode categorical features"""
        categorical_features = []
        
        for job in jobs:
            features = {
                'company': job.get('company', 'Unknown'),
                'location': job.get('location', 'Unknown'),
                'department': job.get('department', 'Unknown'),
                'source': job.get('source', 'Unknown')
            }
            categorical_features.append(features)
        
        df = pd.DataFrame(categorical_features)
        encoded_features = []
        
        for column in df.columns:
            if column not in self.label_encoders:
                self.label_encoders[column] = LabelEncoder()
                encoded = self.label_encoders[column].fit_transform(df[column].astype(str))
            else:
                # Handle unseen categories
                known_classes = self.label_encoders[column].classes_
                df[column] = df[column].apply(lambda x: x if x in known_classes else 'Unknown')
                encoded = self.label_encoders[column].transform(df[column].astype(str))
            
            encoded_features.append(encoded.reshape(-1, 1))
        
        return np.hstack(encoded_features)
    
    def extract_numerical_features(self, jobs: List[Dict]) -> np.ndarray:
        """Extract numerical features from job postings"""
        numerical_features = []
        
        for job in jobs:
            description = job.get('description', '')
            
            # Length-based features
            desc_length = len(description)
            word_count = len(description.split())
            
            # Complexity features
            avg_word_length = np.mean([len(word) for word in description.split()]) if description.split() else 0
            unique_words = len(set(description.lower().split()))
            
            # Engagement features
            exclamation_count = description.count('!')
            question_count = description.count('?')
            caps_ratio = sum(1 for c in description if c.isupper()) / len(description) if description else 0
            
            # Requirement features
            requirements_keywords = ['required', 'must', 'essential', 'mandatory', 'preferred']
            requirements_count = sum(description.lower().count(keyword) for keyword in requirements_keywords)
            
            # Benefits features
            benefits_keywords = ['benefit', 'insurance', 'vacation', 'pto', 'equity', 'stock', 'bonus']
            benefits_count = sum(description.lower().count(keyword) for keyword in benefits_keywords)
            
            features = [
                desc_length,
                word_count,
                avg_word_length,
                unique_words,
                exclamation_count,
                question_count,
                caps_ratio,
                requirements_count,
                benefits_count
            ]
            
            numerical_features.append(features)
        
        numerical_array = np.array(numerical_features)
        
        if not self.is_fitted:
            numerical_array = self.scaler.fit_transform(numerical_array)
        else:
            numerical_array = self.scaler.transform(numerical_array)
            
        return numerical_array
    
    def extract_all_features(self, jobs: List[Dict]) -> Dict[str, np.ndarray]:
        """Extract all feature types"""
        text_features = self.extract_text_features(jobs)
        categorical_features = self.extract_categorical_features(jobs)
        numerical_features = self.extract_numerical_features(jobs)
        
        # Combine all features
        combined_features = np.hstack([
            text_features,
            categorical_features,
            numerical_features
        ])
        
        self.is_fitted = True
        
        return {
            'text_features': text_features,
            'categorical_features': categorical_features,
            'numerical_features': numerical_features,
            'combined_features': combined_features
        }
    
    def get_feature_names(self) -> List[str]:
        """Get names of all extracted features"""
        feature_names = []
        
        # TF-IDF feature names
        if hasattr(self.tfidf_vectorizer, 'feature_names_out_'):
            feature_names.extend(self.tfidf_vectorizer.get_feature_names_out())
        
        # Categorical feature names
        categorical_names = ['company_encoded', 'location_encoded', 'department_encoded', 'source_encoded']
        feature_names.extend(categorical_names)
        
        # Numerical feature names
        numerical_names = [
            'desc_length', 'word_count', 'avg_word_length', 'unique_words',
            'exclamation_count', 'question_count', 'caps_ratio',
            'requirements_count', 'benefits_count'
        ]
        feature_names.extend(numerical_names)
        
        return feature_names