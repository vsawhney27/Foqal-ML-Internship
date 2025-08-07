# ML-Enhanced Job Posting Intelligence System for BD Signals

An automated machine learning system that analyzes publicly available job postings to identify business development opportunities and predict market trends using advanced ML algorithms.

## 🎯 Core Objective

Build an automated system that looks for signals in publicly available data to identify potential business opportunities and market trends using job posting portals.

## 🤖 ML System Architecture

### Agent 1: Data Collection & Feature Engineering
- **Purpose**: Scrapes job postings and prepares ML-ready features
- **ML Capabilities**: 
  - TF-IDF vectorization of job descriptions
  - Feature extraction (text length, complexity, keyword density)
  - Data preprocessing and normalization
  - Quality scoring using statistical methods
- **Output**: ML-ready features and raw job postings

### Agent 2: ML Signal Processing Engine  
- **Purpose**: Classifies and extracts signals using trained ML models
- **ML Capabilities**:
  - **Urgency Classification**: Random Forest classifier for urgent hiring detection
  - **Technology Stack Classification**: Multi-label classification for tech stack identification
  - **Feature Importance Analysis**: Identifies key predictive features
  - **Ensemble Methods**: Combines multiple models for robust predictions
- **Output**: ML-classified signals with confidence scores

### Agent 3: ML Intelligence & Prediction Engine
- **Purpose**: Generates predictions and business insights using unsupervised ML
- **ML Capabilities**:
  - **Company Clustering**: K-means clustering to identify hiring pattern groups
  - **Opportunity Scoring**: ML-based scoring using ensemble feature weighting
  - **Trend Prediction**: Time series forecasting for hiring trends
  - **Market Intelligence**: Predictive analytics for business opportunities
- **Output**: ML-powered business insights and market predictions

## Key BD Signals Tracked

- **Scaling indicators**: Multiple similar roles, senior + junior hiring pairs
- **Technology adoption**: New tech stack mentions, cloud migration signals
- **Transformation projects**: Digital transformation, modernization keywords
- **Pain points**: Mentions of legacy systems, integration challenges
- **Budget signals**: Salary ranges, contractor vs FTE ratios

## 🚀 Quick Start

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
# MongoDB URL is already configured in the code
```

### Run ML-Enhanced Pipeline
```bash
# Run complete ML pipeline
python run_ml_pipeline.py

# Or run ML agents individually
python run_agent1_production.py  # Data collection + feature engineering
python agent2_signal_processor/ml_processor.py  # ML signal processing
python agent3_insight_generator/ml_insights.py  # ML insight generation

# Traditional pipeline (rule-based fallback)
python run_complete_pipeline.py
```

### View Dashboard
```bash
# Launch interactive dashboard
streamlit run dashboard.py
```

## 📊 Deliverables

✅ **Working prototype with data pipeline**
- Three-agent system with MongoDB integration
- Automated scraping, processing, and analysis

✅ **Dashboard showing top opportunities and trends**  
- Streamlit-based interactive dashboard
- Real-time visualization of company opportunities and market trends

✅ **Weekly signal reports with actionable insights**
- Automated report generation
- Company-specific insights and recommendations

✅ **Documentation for scaling the system**
- Complete setup and scaling documentation in `SYSTEM_DOCUMENTATION.md`

## 🧠 Machine Learning Components

### **Classification Models**
- **Urgency Classifier**: Random Forest model trained on job descriptions to detect urgent hiring needs
- **Technology Stack Classifier**: Multi-label classification for identifying technology categories
- **Feature Engineering**: TF-IDF vectorization with categorical and numerical features

### **Clustering & Scoring**
- **Company Clustering**: K-means clustering to group companies by hiring patterns
- **Opportunity Scoring**: ML ensemble model for ranking business opportunities
- **Silhouette Analysis**: Quality metrics for cluster validation

### **Predictive Analytics**
- **Trend Forecasting**: Time series models for predicting hiring volume and urgency
- **Feature Importance**: Analysis of key predictive factors for business insights
- **Market Intelligence**: Statistical modeling for competitive analysis

### **Model Performance**
- **Hybrid Approach**: ML models with rule-based fallbacks for reliability
- **Cross-validation**: 5-fold CV for model validation
- **Confidence Scoring**: Model uncertainty quantification for decision support

## 📁 Project Structure

```
├── agent1_data_collector/          # Data collection + feature engineering
│   ├── main.py                     # Main scraper logic
│   ├── scraper.py                  # Web scraping utilities
│   └── config.py                   # Configuration settings
├── agent2_signal_processor/        # ML signal processing engine
│   ├── main.py                     # Rule-based processing (fallback)
│   ├── ml_processor.py             # ML-enhanced signal processing
│   ├── processor.py                # Signal extraction engine
│   ├── signals.py                  # Signal detection functions
│   └── mongo_utils.py              # Database utilities
├── agent3_insight_generator/       # ML intelligence & prediction
│   ├── main.py                     # Rule-based insights (fallback)
│   └── ml_insights.py              # ML-powered insight generation
├── ml_models/                      # Machine learning models
│   ├── __init__.py                 # ML models package
│   ├── feature_engineering.py     # Feature extraction pipeline
│   ├── text_classifier.py         # Classification models
│   ├── clustering.py               # Clustering and scoring models
│   └── predictive.py               # Time series and prediction models
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

## 🔧 Configuration

The system is pre-configured to work out of the box with:
- RemoteOK as the job source (focusing on AI/ML roles)
- MongoDB Atlas for data storage
- JSON file backups for all data

## 📈 Sample Output

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

## 🚀 Scaling the System

See `SYSTEM_DOCUMENTATION.md` for detailed scaling instructions including:
- Adding new job sources
- Expanding signal detection
- Implementing advanced ML models
- Production deployment strategies
- Performance optimization

## 🔍 Monitoring & Maintenance

- Check `reports/weekly/` for generated insights
- Monitor data quality in dashboard
- Review MongoDB collections for data consistency
- Update scraping targets as needed

## 📝 Next Steps

1. **Expand data sources**: Add LinkedIn, Indeed, Glassdoor
2. **Enhanced ML**: Implement advanced NLP for better signal detection  
3. **Real-time alerts**: Set up automated notifications for high-priority opportunities
4. **API integration**: Build REST API for external access
5. **Advanced analytics**: Add predictive modeling for market trends

## 🤝 Contributing

This is a production-ready system for business development intelligence. Contributions should focus on:
- Adding new signal detection capabilities
- Improving data quality and accuracy
- Enhancing the dashboard with new visualizations
- Expanding to new job posting sources
