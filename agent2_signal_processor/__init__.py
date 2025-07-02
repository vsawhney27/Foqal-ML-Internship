"""
Agent 2: Signal Processing Agent
Job Posting Intelligence System for BD Signals

This module processes job postings and extracts business development signals.
"""

from .processor import SignalProcessor, main
from .signals import (
    extract_technology_adoption,
    extract_urgent_hiring_language,
    extract_budget_signals,
    extract_pain_points,
    extract_skills_mentioned,
    calculate_hiring_volume_by_company,
    process_job_signals
)
from .mongo_utils import MongoDBHandler, connect_to_mongo, get_jobs_from_mongo, save_jobs_to_mongo

__version__ = "1.0.0"
__author__ = "Job Posting Intelligence System"

__all__ = [
    'SignalProcessor',
    'main',
    'extract_technology_adoption',
    'extract_urgent_hiring_language',
    'extract_budget_signals',
    'extract_pain_points',
    'extract_skills_mentioned',
    'calculate_hiring_volume_by_company',
    'process_job_signals',
    'MongoDBHandler',
    'connect_to_mongo',
    'get_jobs_from_mongo',
    'save_jobs_to_mongo'
]