import sqlite3
import os
from typing import List, Dict

def create_database(db_path="data/jobs.db"):
    """Create the SQLite database and jobs table if they don't exist."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            url TEXT UNIQUE,
            posting_date TEXT,
            source TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_jobs(jobs: List[Dict], db_path="data/jobs.db"):
    """Insert job data into the SQLite database, skipping duplicates."""
    create_database(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for job in jobs:
        cursor.execute('''
            INSERT OR IGNORE INTO jobs (title, company, location, description, url, posting_date, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            job.get('title'),
            job.get('company'),
            job.get('location'),
            job.get('description'),
            job.get('url'),
            job.get('posting_date'),
            job.get('source')
        ))
    
    conn.commit()
    conn.close()

def get_jobs(db_path="data/jobs.db", limit=None):
    """Retrieve jobs from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if limit:
        cursor.execute('SELECT * FROM jobs LIMIT ?', (limit,))
    else:
        cursor.execute('SELECT * FROM jobs')
    
    jobs = cursor.fetchall()
    conn.close()
    
    return jobs

def get_job_count(db_path="data/jobs.db"):
    """Get the total number of jobs in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM jobs')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count