# Foqal Business Development Intelligence System
## Complete Documentation for Scaling and Operations

### System Overview

The Foqal BD Intelligence System is a production-ready, 3-agent pipeline that automatically identifies business development opportunities from job posting data.

### Architecture

```
Data Sources → Agent 1 → Agent 2 → Agent 3 → Business Intelligence
 ↓ ↓ ↓ ↓ ↓
Job Portals → Scraper → Processor → Analyzer → BD Reports
```

#### Agent 1: Data Collection
- **Purpose**: Scrape job postings from multiple sources
- **Current Sources**: RemoteOK, Enhanced samples (Anthropic, OpenAI, etc.)
- **Output**: `data/scraped_jobs.json`
- **Key Features**: 
 - ScrapingDog API integration
 - Rate limiting and error handling
 - Metadata enrichment (dates, sources)

#### Agent 2: Signal Processing
- **Purpose**: Extract BD signals from job descriptions
- **Signals Extracted**:
 - Technology adoption (PyTorch, Kubernetes, etc.)
 - Urgent hiring language ("ASAP", "immediate")
 - Budget indicators (salary ranges, equity)
 - Pain points (legacy systems, technical debt)
- **Output**: `data/processed_jobs.json`, `data/signal_statistics.json`

#### Agent 3: Business Intelligence
- **Purpose**: Generate actionable BD insights
- **Intelligence Generated**:
 - Company opportunity scores
 - Service recommendations
 - Market trend analysis
 - Priority-ranked prospect list
- **Output**: `data/business_intelligence.json`, `data/market_intelligence.json`

### Quick Start

#### Option 1: Complete Pipeline
```bash
python3 run_complete_pipeline.py
```

#### Option 2: Individual Agents
```bash
# Run agents sequentially
python3 run_agent1_production.py
python3 run_agent2_production.py 
python3 run_agent3_production.py
```

### Weekly Automation

#### Setup Cron Job for Weekly Reports
```bash
# Add to crontab (crontab -e)
0 9 * * 1 cd /path/to/project && python3 generate_weekly_report.py
```

#### Weekly Report Features
- Trend comparison vs previous week
- New high-priority opportunities
- Market shift analysis
- Recommended actions

### Configuration

#### Environment Variables
```bash
# .env file
SCRAPINGDOG_API_KEY=your_api_key_here
MONGODB_URL=your_mongodb_connection_string
OPENAI_API_KEY=optional_for_enhanced_analysis
```

#### Agent Configuration
- **Agent 1**: Edit `run_agent1_production.py` for different job sites
- **Agent 2**: Modify signal patterns in `agent2_signal_processor/`
- **Agent 3**: Adjust scoring algorithm in `run_agent3_production.py`

### Scaling the System

#### Adding New Data Sources

1. **LinkedIn Jobs API**:
```python
# Add to Agent 1
def scrape_linkedin_jobs(api_key, search_terms):
 # Implementation for LinkedIn
 pass
```

2. **Indeed API**:
```python
# Add to Agent 1 
def scrape_indeed_jobs(publisher_id, search_terms):
 # Implementation for Indeed
 pass
```

3. **Company Career Pages**:
```python
# Add to Agent 1
def scrape_company_careers(company_urls):
 # Implementation for direct company scraping
 pass
```

#### Enhancing Signal Processing

1. **Add New Signal Types**:
```python
# Add to Agent 2
def extract_department_signals(description):
 # Extract hiring patterns by department
 pass

def extract_seniority_patterns(description):
 # Identify senior + junior hiring pairs
 pass
```

2. **Industry-Specific Analysis**:
```python
# Add to Agent 3
def analyze_by_industry(companies):
 # Industry-specific opportunity analysis
 pass
```

#### Performance Optimization

1. **Parallel Processing**:
```python
# Add to pipeline
from concurrent.futures import ThreadPoolExecutor

def parallel_agent_execution():
 with ThreadPoolExecutor(max_workers=3) as executor:
 # Run agents in parallel where possible
 pass
```

2. **Caching Strategy**:
```python
# Add Redis caching
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)
```

3. **Database Optimization**:
```python
# Add database indexing
def setup_mongodb_indexes():
 collection.create_index([("company", 1), ("scraped_date", -1)])
```

### Monitoring and Alerting

#### System Health Checks
```python
def system_health_check():
 checks = {
 'agent1_data_freshness': check_data_age(),
 'agent2_processing_success': check_signal_extraction(),
 'agent3_insight_generation': check_insight_quality(),
 'api_rate_limits': check_api_status()
 }
 return checks
```

#### Alert Thresholds
- Data older than 24 hours
- Processing success rate < 95%
- High-priority opportunities > 10
- API rate limit approaching

### Dashboard Integration

#### Grafana Integration
```python
# metrics.py
def export_metrics_to_grafana():
 metrics = {
 'jobs_processed': len(processed_jobs),
 'high_priority_opportunities': count_high_priority(),
 'market_urgency_rate': calculate_urgency_rate(),
 'top_technologies': get_trending_tech()
 }
 # Send to Grafana endpoint
```

#### Slack Integration
```python
# alerts.py
def send_slack_alert(opportunities):
 if len(opportunities) > 5:
 slack_webhook_url = os.getenv('SLACK_WEBHOOK')
 # Send high-priority opportunities to Slack
```

### Testing and Quality Assurance

#### Unit Tests
```bash
# Run test suite
python3 -m pytest tests/
```

#### Data Quality Checks
```python
def validate_data_quality(jobs):
 quality_score = 0
 quality_score += check_required_fields(jobs)
 quality_score += check_signal_extraction_rate(jobs)
 quality_score += check_insight_generation_rate(jobs)
 return quality_score
```

#### Performance Benchmarks
- Agent 1: < 2 minutes for 50 jobs
- Agent 2: < 30 seconds for 50 jobs
- Agent 3: < 10 seconds for analysis
- End-to-end: < 3 minutes total

### Operational Procedures

#### Daily Operations
1. Check system health dashboard
2. Review overnight processing logs
3. Validate new high-priority opportunities
4. Update BD team on urgent alerts

#### Weekly Operations
1. Generate comprehensive market report
2. Analyze trend changes vs previous week
3. Update signal extraction patterns
4. Review and optimize system performance

#### Monthly Operations
1. Expand data source coverage
2. Enhance signal processing algorithms 
3. Validate BD impact and ROI
4. Plan system scaling initiatives

### Troubleshooting

#### Common Issues

1. **Agent 1 Scraping Failures**:
 - Check API key validity
 - Verify rate limiting compliance
 - Test alternative data sources

2. **Agent 2 Signal Extraction Issues**:
 - Review pattern matching accuracy
 - Update technology keyword lists
 - Validate data preprocessing

3. **Agent 3 Insight Quality Issues**:
 - Adjust opportunity scoring weights
 - Enhance market analysis algorithms
 - Validate business logic assumptions

#### Recovery Procedures
```python
def system_recovery():
 # Automatic fallback to cached data
 # Retry failed operations
 # Alert operations team
 pass
```

### Success Metrics

#### Technical KPIs
- System uptime: >99.5%
- Data processing accuracy: >95%
- End-to-end pipeline latency: <5 minutes
- API rate limit compliance: 100%

#### Business KPIs
- BD opportunities identified per week: >10
- Conversion rate of identified opportunities: >15%
- Time to market insight: <24 hours
- BD team satisfaction score: >4.5/5

### Future Enhancements

#### Short-term (1-3 months)
- Add LinkedIn and Indeed API integrations
- Implement real-time Slack alerts
- Create interactive web dashboard
- Add email notification system

#### Medium-term (3-6 months) 
- AI-powered opportunity scoring
- Industry-specific analysis modules
- Competitive intelligence features
- Advanced visualization dashboards

#### Long-term (6+ months)
- Machine learning prediction models
- Multi-language job posting support
- Global market expansion
- Enterprise integration APIs

### Support and Maintenance

#### Contact Information
- **Technical Lead**: [Your Contact]
- **BD Stakeholder**: [BD Team Contact] 
- **System Admin**: [Ops Contact]

#### Escalation Procedures
1. Level 1: Automated recovery attempts
2. Level 2: On-call engineer notification
3. Level 3: BD team impact assessment
4. Level 4: Executive escalation

---

**Document Version**: 1.0 
**Last Updated**: 2025-07-18 
**Next Review**: 2025-08-18