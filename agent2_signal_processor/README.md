# Agent 2: Signal Processing Agent

## Overview
This agent processes job postings scraped by Agent 1 and extracts key business development signals for competitive intelligence and market analysis.

## Features

### Signal Extraction
- **Technology Adoption**: Detects 100+ technology keywords (Python, AWS, Kubernetes, etc.)
- **Urgent Hiring Language**: Finds phrases like "ASAP", "immediate", "start now"
- **Budget Signals**: Extracts salary ranges, hourly rates, and equity mentions
- **Pain Points**: Identifies legacy systems, technical debt, integration issues
- **Skills Analysis**: Comprehensive skill extraction and analysis
- **Hiring Volume**: Tracks job postings per company

### Data Processing
- MongoDB integration for data persistence
- Statistical analysis and reporting
- Export to JSON and CSV formats
- Real-time processing logs

## Project Structure
```
agent2_signal_processor/
 processor.py # Main processing logic
 signals.py # Signal extraction functions
 mongo_utils.py # MongoDB utilities
 output/ # Generated output files
 requirements.txt # Dependencies
 __init__.py # Module initialization
 README.md # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure MongoDB connection (same as Agent 1):
 - Uses the MongoDB URL from Agent 1's configuration
 - Connects to `JobPosting.ScrapedJobs` collection

## Usage

### Run the Complete Pipeline
```bash
python processor.py
```

### Use as Module
```python
from agent2_signal_processor import SignalProcessor

# Initialize processor
processor = SignalProcessor("mongodb://your-mongo-url")

# Connect and process
processor.connect_to_database()
jobs = processor.load_scraped_jobs()
processed_jobs = processor.process_jobs(jobs)
stats = processor.generate_statistics()

# Save results
processor.save_to_mongodb()
processor.save_to_json()
processor.save_to_csv()

processor.print_summary()
processor.disconnect()
```

### Individual Signal Functions
```python
from agent2_signal_processor.signals import (
 extract_technology_adoption,
 extract_urgent_hiring_language,
 extract_budget_signals,
 extract_pain_points
)

# Extract specific signals
description = "Looking for Python developer with AWS experience. Urgent hire needed!"
tech = extract_technology_adoption(description)
urgent = extract_urgent_hiring_language(description)
budget = extract_budget_signals(description)
pain_points = extract_pain_points(description)
```

## Output Files

### JSON Output (`output/signals_output.json`)
Complete processed jobs with all extracted signals

### CSV Output (`output/signals_output.csv`)
Flattened data suitable for analysis in Excel/Google Sheets

### Statistics (`output/signal_statistics.json`)
Summary statistics including:
- Technology adoption trends
- Urgent hiring percentages
- Budget signal analysis
- Pain point frequency
- Company hiring volumes

## MongoDB Collections

### Input: `JobPosting.ScrapedJobs`
Jobs scraped by Agent 1 with fields:
- `title`, `company`, `location`
- `description`, `detail_url`
- `scraped_date`

### Output: `JobPosting.ProcessedJobs`
Enhanced jobs with signal fields:
- All original fields from ScrapedJobs
- `technology_adoption`: List of technologies found
- `urgent_hiring_language`: List of urgent phrases
- `budget_signals`: Dict with salary/equity info
- `pain_points`: List of pain point mentions
- `skills_mentioned`: List of skills found
- `signal_processing_date`: Processing timestamp

## Signal Types

### 1. Technology Adoption
Detects 100+ keywords across categories:
- **Languages**: Python, Java, JavaScript, Go, Rust, etc.
- **Frameworks**: React, Django, Spring, TensorFlow, etc.
- **Cloud**: AWS, Azure, GCP, Docker, Kubernetes, etc.
- **Databases**: PostgreSQL, MongoDB, Redis, etc.
- **Tools**: Git, Jenkins, Grafana, etc.

### 2. Urgent Hiring Language
Patterns like:
- "ASAP", "immediate", "start now"
- "urgent", "rushing", "quickly"
- "start Monday", "start this week"
- "high priority", "time-sensitive"

### 3. Budget Signals
Extracts:
- **Salary ranges**: $120k, €80,000, £60k
- **Hourly rates**: $50/hour, €40/hr
- **Equity**: stock options, RSUs, vesting
- **Budget phrases**: competitive salary, market rate

### 4. Pain Points
Identifies:
- Legacy systems, technical debt
- Integration challenges, data silos
- Manual processes, scalability issues
- Architecture redesign needs

### 5. Skills Analysis
Combines technical and soft skills:
- Technical skills from technology extraction
- Methodologies: Agile, CI/CD, DevOps
- Domain expertise: fintech, healthcare, etc.
- Soft skills: leadership, communication

## Integration with Agent 1

This agent seamlessly integrates with Agent 1:
1. Reads from the same MongoDB database
2. Uses identical connection configuration
3. Processes the exact job schema from Agent 1
4. Adds value without modifying original data

## Logging and Monitoring

The agent provides comprehensive logging:
- Connection status and database stats
- Processing progress with job-by-job updates
- Signal extraction counts per job
- Error handling and recovery
- Final statistics and summary

## Performance

- Processes 100+ jobs in under 30 seconds
- Memory efficient with streaming processing
- Regex-optimized for fast text analysis
- Parallel-ready architecture for scaling

## Next Steps

This agent can be extended to:
- Real-time signal monitoring
- Machine learning signal classification
- Integration with business intelligence tools
- Automated alert systems for high-value signals
- API endpoints for downstream applications