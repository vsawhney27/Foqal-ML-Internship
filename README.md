# Job Posting Intelligence System for BD Signals

An automated system that analyzes publicly available job postings to identify business development opportunities and market trends.

## Core Objective

Build an automated system that looks for signals in publicly available data to identify potential business opportunities and market trends using job posting portals.

## System Architecture

### Agent 1: Data Collection Agent
- **Purpose**: Scrapes job postings from remote job sites
- **Capabilities**: 
  - Scrapes RemoteOK AI jobs with rate limiting
  - Handles data quality checks and metadata extraction
  - Stores raw data with posting date, company, location, etc.
- **Output**: Raw job postings in MongoDB and JSON format

### Agent 2: Signal Processing Agent  
- **Purpose**: Analyzes job descriptions for business signals
- **Capabilities**:
  - Identifies technology stack mentions
  - Detects hiring volume patterns by company/department
  - Extracts skill requirements and budget indicators
  - Flags urgent hiring language ("immediate start", "ASAP")
- **Output**: Processed signals with extracted intelligence

### Agent 3: Intelligence Agent
- **Purpose**: Correlates patterns into actionable business insights
- **Capabilities**:
  - Correlates hiring patterns with potential service needs
  - Identifies companies scaling specific departments
  - Maps technology adoption trends across industries  
  - Generates alerts for high-priority opportunities
- **Output**: Business development insights and recommendations

## Key BD Signals Tracked

- **Scaling indicators**: Multiple similar roles, senior + junior hiring pairs
- **Technology adoption**: New tech stack mentions, cloud migration signals
- **Transformation projects**: Digital transformation, modernization keywords
- **Pain points**: Mentions of legacy systems, integration challenges
- **Budget signals**: Salary ranges, contractor vs FTE ratios

## Quick Start

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
# MongoDB URL is already configured in the code
```

### Run Complete Pipeline
```bash
# Run all agents in sequence
python run_complete_pipeline.py

# Or run agents individually
python run_agent1_production.py  # Data collection
python run_agent2_production.py  # Signal processing  
python run_agent3_production.py  # Intelligence generation
```

### View Dashboard
```bash
# Launch interactive dashboard
streamlit run dashboard.py
```

## Deliverables

**Working prototype with data pipeline**
- Three-agent system with MongoDB integration
- Automated scraping, processing, and analysis

**Dashboard showing top opportunities and trends**  
- Streamlit-based interactive dashboard
- Real-time visualization of company opportunities and market trends

**Weekly signal reports with actionable insights**
- Automated report generation
- Company-specific insights and recommendations

**Documentation for scaling the system**
- Complete setup and scaling documentation in `SYSTEM_DOCUMENTATION.md`

## Project Structure

```
├── agent1_data_collector/          # Data collection agent
│   ├── main.py                     # Main scraper logic
│   ├── scraper.py                  # Web scraping utilities
│   └── config.py                   # Configuration settings
├── agent2_signal_processor/        # Signal processing agent  
│   ├── main.py                     # Main processing logic
│   ├── processor.py                # Signal extraction engine
│   ├── signals.py                  # Signal detection functions
│   └── mongo_utils.py              # Database utilities
├── agent3_insight_generator/       # Intelligence agent
│   └── main.py                     # Insight generation logic
├── data/                           # Data storage directory
├── reports/                        # Generated reports
├── dashboard.py                    # Streamlit dashboard
├── run_complete_pipeline.py        # Full pipeline runner
├── run_agent1_production.py        # Agent 1 runner
├── run_agent2_production.py        # Agent 2 runner
├── run_agent3_production.py        # Agent 3 runner
├── generate_weekly_report.py       # Report generator
├── requirements.txt                # Python dependencies
└── SYSTEM_DOCUMENTATION.md         # Detailed documentation
```

## Configuration

The system is pre-configured to work out of the box with:
- RemoteOK as the job source (focusing on AI/ML roles)
- MongoDB Atlas for data storage
- JSON file backups for all data

## Sample Output

### Company Insights Example
```json
{
  "company": "TechCorp",
  "insights": [
    "TechCorp is in aggressive hiring mode with 5 open positions, 80% marked as urgent, indicating rapid scaling",
    "TechCorp is heavily investing in AI/ML capabilities, with focus on Python (4 roles), TensorFlow (3 roles)"
  ],
  "job_count": 5,
  "analysis_metadata": {
    "total_technologies": 12,
    "urgent_jobs": 4,
    "budget_transparency": 5
  }
}
```

### Dashboard Features
- Company opportunity matrix
- Technology adoption trends  
- Market intelligence summaries
- Pain point analysis
- Real-time metrics

## Scaling the System

See `SYSTEM_DOCUMENTATION.md` for detailed scaling instructions including:
- Adding new job sources
- Expanding signal detection
- Implementing advanced ML models
- Production deployment strategies
- Performance optimization

## Monitoring & Maintenance

- Check `reports/weekly/` for generated insights
- Monitor data quality in dashboard
- Review MongoDB collections for data consistency
- Update scraping targets as needed

## Next Steps

1. **Expand data sources**: Add LinkedIn, Indeed, Glassdoor
2. **Enhanced ML**: Implement advanced NLP for better signal detection  
3. **Real-time alerts**: Set up automated notifications for high-priority opportunities
4. **API integration**: Build REST API for external access
5. **Advanced analytics**: Add predictive modeling for market trends

## Contributing

This is a production-ready system for business development intelligence. Contributions should focus on:
- Adding new signal detection capabilities
- Improving data quality and accuracy
- Enhancing the dashboard with new visualizations
- Expanding to new job posting sources# Production-ready system
