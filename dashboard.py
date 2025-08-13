#!/usr/bin/env python3
"""
Business Development Intelligence Dashboard
Streamlit app showing top opportunities and trends from the job posting analysis
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="BD Intelligence Dashboard",
    page_icon="📈",
    layout="wide"
)

def load_data():
    """Load data from agent outputs with fallback to sample data"""
    data = {
        'company_insights': [],
        'industry_trends': {},
        'signal_statistics': {},
        'signals_data': []
    }
    
    data_loaded = False
    
    # Load company insights (from main output directory)
    insights_file = "output/company_insights.json"
    if os.path.exists(insights_file):
        try:
            with open(insights_file, 'r') as f:
                data['company_insights'] = json.load(f)
                data_loaded = True
        except Exception as e:
            st.warning(f"Could not load company insights: {e}")
    
    # Load industry trends
    trends_file = "output/industry_trends.json"
    if os.path.exists(trends_file):
        try:
            with open(trends_file, 'r') as f:
                data['industry_trends'] = json.load(f)
                data_loaded = True
        except Exception as e:
            st.warning(f"Could not load industry trends: {e}")
    
    # Load signal statistics
    stats_file = "output/signal_statistics.json"
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r') as f:
                data['signal_statistics'] = json.load(f)
                data_loaded = True
        except Exception as e:
            st.warning(f"Could not load signal statistics: {e}")
    
    # Load raw signals data
    signals_file = "output/signals_output.json"
    if os.path.exists(signals_file):
        try:
            with open(signals_file, 'r') as f:
                data['signals_data'] = json.load(f)
                data_loaded = True
        except Exception as e:
            st.warning(f"Could not load signals data: {e}")
    
    # No sample data fallback - require real data
    if not data_loaded:
        st.error("❌ No data available. Please run the job analysis pipeline to generate data:")
        st.code("""
# Run the complete pipeline:
python3 agent1_data_collector/main.py
python3 agent2_signal_processor/main.py
cd agent3_insight_generator && python3 main.py && cd ..
python3 generate_weekly_report.py
        """)
        return {
            'company_insights': [],
            'industry_trends': {},
            'signal_statistics': {},
            'signals_data': []
        }
    
    return data

def create_technology_chart(industry_trends):
    """Create technology adoption chart"""
    # Try multiple data formats
    tech_data = None
    
    if industry_trends.get('top_technologies'):
        tech_data = industry_trends['top_technologies']
    elif industry_trends.get('current_trends', {}).get('technology_trends'):
        tech_dict = industry_trends['current_trends']['technology_trends']
        tech_data = [[k, v] for k, v in tech_dict.items()]
    
    if not tech_data:
        return None
    
    # Convert to DataFrame
    if isinstance(tech_data, dict):
        tech_data = [[k, v] for k, v in tech_data.items()]
    
    df = pd.DataFrame(tech_data, columns=['Technology', 'Mentions'])
    df = df.sort_values('Mentions', ascending=False).head(10)
    
    fig = px.bar(
        df, 
        x='Mentions', 
        y='Technology',
        orientation='h',
        title="Top Technologies in Job Postings",
        color='Mentions',
        color_continuous_scale='Blues'
    )
    fig.update_layout(height=500)
    return fig

def create_company_opportunities_chart(company_insights):
    """Create company opportunities chart"""
    if not company_insights:
        return None
    
    companies_data = []
    for insight in company_insights[:10]:  # Top 10 companies
        # Handle both old and new data formats
        urgency_score = 0
        if 'analysis_metadata' in insight:
            urgency_score = insight['analysis_metadata'].get('urgent_jobs', 0)
        elif 'urgent_jobs_count' in insight:
            urgency_score = insight['urgent_jobs_count']
        
        companies_data.append({
            'Company': insight['company'],
            'Job Count': insight['job_count'],
            'Insight Count': len(insight.get('insights', [])),
            'Opportunity Score': insight.get('opportunity_score', 0),
            'Urgency Score': urgency_score
        })
    
    df = pd.DataFrame(companies_data)
    
    fig = px.scatter(
        df,
        x='Job Count',
        y='Opportunity Score', 
        size='Insight Count',
        hover_name='Company',
        title="Company Hiring Activity vs Business Opportunities",
        labels={'Job Count': 'Number of Open Positions', 'Opportunity Score': 'ML Opportunity Score (%)'}
    )
    return fig

def create_pain_points_chart(industry_trends):
    """Create pain points visualization"""
    if not industry_trends.get('top_pain_points'):
        return None
        
    pain_data = industry_trends['top_pain_points']
    df = pd.DataFrame(pain_data, columns=['Pain Point', 'Mentions'])
    
    fig = px.pie(
        df,
        values='Mentions',
        names='Pain Point',
        title="Most Common Technical Pain Points"
    )
    return fig

def main():
    st.title("📈 Business Development Intelligence Dashboard")
    st.markdown("*Real-time insights from job posting analysis*")
    
    # Load data
    data = load_data()
    
    # Check if data is available
    if not any([data['company_insights'], data['industry_trends'], data['signal_statistics']]):
        st.error("No data available. Please run the agents first:")
        st.code("""
        python run_agent1_production.py
        python run_agent2_production.py  
        python run_agent3_production.py
        """)
        return
    
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Show last update time
    if data['industry_trends'].get('analysis_date'):
        st.sidebar.write(f"**Last Updated:** {data['industry_trends']['analysis_date'][:19]}")
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    # Key metrics
    with col1:
        companies_count = len(data['company_insights'])
        st.metric("Companies Analyzed", companies_count)
    
    with col2:
        total_jobs = sum(insight['job_count'] for insight in data['company_insights'])
        st.metric("Total Job Openings", total_jobs)
    
    with col3:
        urgent_companies = data['industry_trends'].get('urgent_hiring_companies_count', 0)
        st.metric("Companies with Urgent Hiring", urgent_companies)
    
    with col4:
        total_insights = sum(len(insight['insights']) for insight in data['company_insights'])
        st.metric("Business Insights Generated", total_insights)
    
    st.divider()
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Top Business Opportunities")
        
        if data['company_insights']:
            # Sort companies by opportunity score (descending) and job count (descending)
            sorted_insights = sorted(data['company_insights'], 
                                   key=lambda x: (x.get('opportunity_score', 0), x.get('job_count', 0)), 
                                   reverse=True)
            
            # Show top 5 company insights
            for i, insight in enumerate(sorted_insights[:5], 1):
                company = insight['company']
                job_count = insight['job_count']
                insights_list = insight.get('insights', [])
                opportunity_score = insight.get('opportunity_score', 0)
                
                # Create expanded title with opportunity score
                title = f"{i}. **{company}** ({job_count} positions)"
                if opportunity_score > 0:
                    title += f" - {opportunity_score:.1f}% opportunity score"
                
                with st.expander(title, expanded=(i <= 2)):
                    if insights_list:
                        for insight_text in insights_list:
                            st.write(f"• {insight_text}")
                    else:
                        st.write("• Company identified for business development potential")
                    
                    # Show metadata - handle both old and new format
                    col_a, col_b = st.columns(2)
                    with col_a:
                        # Try new format first, fallback to old
                        tech_count = insight.get('technology_count', 0)
                        if tech_count == 0 and 'analysis_metadata' in insight:
                            tech_count = insight['analysis_metadata'].get('total_technologies', 0)
                        st.metric("Technologies", tech_count)
                    with col_b:
                        # Try new format first, fallback to old
                        urgent_count = insight.get('urgent_jobs_count', 0)
                        if urgent_count == 0 and 'analysis_metadata' in insight:
                            urgent_count = insight['analysis_metadata'].get('urgent_jobs', 0)
                        st.metric("Urgent Jobs", urgent_count)
        else:
            st.info("No company insights available. Run Agent 3 to generate insights.")
    
    with col2:
        st.subheader("📊 Market Intelligence")
        
        # Technology trends chart
        tech_chart = create_technology_chart(data['industry_trends'])
        if tech_chart:
            st.plotly_chart(tech_chart, use_container_width=True)
        else:
            st.info("No technology trends data available.")
    
    st.divider()
    
    # Additional visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Company Opportunity Matrix")
        company_chart = create_company_opportunities_chart(data['company_insights'])
        if company_chart:
            st.plotly_chart(company_chart, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Technical Pain Points")
        pain_chart = create_pain_points_chart(data['industry_trends'])
        if pain_chart:
            st.plotly_chart(pain_chart, use_container_width=True)
    
    # Raw data section
    with st.expander("📋 View Raw Data"):
        tab1, tab2, tab3 = st.tabs(["Company Insights", "Industry Trends", "Signal Statistics"])
        
        with tab1:
            if data['company_insights']:
                st.json(data['company_insights'])
            else:
                st.info("No company insights data")
        
        with tab2:
            if data['industry_trends']:
                st.json(data['industry_trends'])
            else:
                st.info("No industry trends data")
        
        with tab3:
            if data['signal_statistics']:
                st.json(data['signal_statistics'])
            else:
                st.info("No signal statistics data")
    
    # Footer
    st.divider()
    st.markdown("*Dashboard powered by Job Posting Intelligence System*")

if __name__ == "__main__":
    main()