#!/usr/bin/env python3
"""
US Mid-Market Opportunities Dashboard Page
Shows filtered job postings from mid-sized US companies
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml
from pathlib import Path
import sys
import os
from typing import Dict, Any

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(
    page_title="US Mid-Market Opportunities",
    page_icon="🎯",
    layout="wide"
)

@st.cache_data
def load_config() -> Dict[str, Any]:
    """Load configuration from filters.yml"""
    config_path = project_root / "configs" / "filters.yml"
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.error("Configuration file not found. Please ensure configs/filters.yml exists.")
        return {}
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return {}

@st.cache_data
def load_us_mid_market_data() -> pd.DataFrame:
    """Load US mid-market filtered data with fallback to remote URL"""
    
    # Try local file first
    local_file = project_root / "data" / "exports" / "us_mid_market_postings.parquet"
    
    if local_file.exists():
        try:
            df = pd.read_parquet(local_file)
            st.success(f"✅ Loaded {len(df)} jobs from local file")
            return df
        except Exception as e:
            st.warning(f"Error reading local parquet file: {e}")
    
    # Try remote URL from secrets
    try:
        remote_url = st.secrets.get("DATA_EXPORT_URL")
        if remote_url:
            df = pd.read_parquet(remote_url)
            st.success(f"✅ Loaded {len(df)} jobs from remote URL")
            return df
    except Exception as e:
        st.warning(f"Error loading from remote URL: {e}")
    
    # Return empty dataframe if no data available
    st.error("No data available. Please run: `make export_us_mid_market` or set DATA_EXPORT_URL in Streamlit secrets.")
    return pd.DataFrame()

def flatten_filter_reasons(reasons: Dict[str, Any]) -> str:
    """Convert filter reasons dict to human-readable string"""
    if not reasons:
        return "No filtering applied"
    
    # Extract key reasons
    reason_parts = []
    
    if reasons.get('geo.country'):
        reason_parts.append("US location")
    if reasons.get('geo.state_abbrev'):
        reason_parts.append("US state")
    if reasons.get('geo.remote_text'):
        reason_parts.append("US remote auth")
    if reasons.get('geo.tz_hint'):
        reason_parts.append("US timezone")
    if reasons.get('size.emp_ok'):
        emp_count = reasons.get('size.emp_count', 'N/A')
        reason_parts.append(f"employees ({emp_count})")
    if reasons.get('size.rev_ok'):
        revenue = reasons.get('size.revenue', 0)
        if revenue:
            reason_parts.append(f"revenue (${revenue/1000000:.0f}M)")
    if reasons.get('inconclusive_soft_gate'):
        reason_parts.append("soft signals")
    
    return " + ".join(reason_parts) if reason_parts else "Other criteria"

def show_kpis(df: pd.DataFrame):
    """Display key performance indicators"""
    if df.empty:
        return
        
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_roles = len(df)
        st.metric("Total Roles", f"{total_roles:,}")
    
    with col2:
        companies_count = df['company'].nunique()
        st.metric("Unique Companies", f"{companies_count:,}")
    
    with col3:
        if 'parsed_location_state' in df.columns:
            top_state = df['parsed_location_state'].value_counts().index[0] if not df['parsed_location_state'].isna().all() else "N/A"
            top_state_count = df['parsed_location_state'].value_counts().iloc[0] if not df['parsed_location_state'].isna().all() else 0
            st.metric("Top State", f"{top_state} ({top_state_count})")
        else:
            st.metric("Top State", "N/A")
    
    with col4:
        if 'enriched_employee_count' in df.columns:
            avg_size = df['enriched_employee_count'].mean()
            if pd.notna(avg_size):
                st.metric("Avg Company Size", f"{avg_size:.0f} employees")
            else:
                st.metric("Avg Company Size", "N/A")
        else:
            st.metric("Avg Company Size", "N/A")

def show_visualizations(df: pd.DataFrame):
    """Show data visualizations"""
    if df.empty:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Jobs by State")
        if 'parsed_location_state' in df.columns and not df['parsed_location_state'].isna().all():
            state_counts = df['parsed_location_state'].value_counts().head(10)
            fig = px.bar(
                x=state_counts.values,
                y=state_counts.index,
                orientation='h',
                title="Top 10 States by Job Count"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No state data available for visualization")
    
    with col2:
        st.subheader("Companies by Size")
        if 'enriched_employee_count' in df.columns and not df['enriched_employee_count'].isna().all():
            # Create size buckets
            df_with_size = df.dropna(subset=['enriched_employee_count'])
            df_with_size['size_bucket'] = pd.cut(
                df_with_size['enriched_employee_count'], 
                bins=[0, 50, 100, 250, 500, 1000], 
                labels=['<50', '50-100', '101-250', '251-500', '501-1000']
            )
            size_counts = df_with_size['size_bucket'].value_counts()
            
            fig = px.pie(
                values=size_counts.values,
                names=size_counts.index,
                title="Distribution by Company Size"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No company size data available for visualization")

def main():
    """Main dashboard function"""
    st.title("🎯 US Mid-Market Opportunities")
    st.markdown("Filtered job postings from mid-sized US companies (50-999 employees or $10M-$1B revenue)")
    
    # Sidebar with configuration
    with st.sidebar:
        st.header("Filter Configuration")
        
        config = load_config()
        if config and 'filters' in config:
            st.subheader("Geographic Filters")
            geo_config = config['filters'].get('geo', {})
            st.write(f"**Countries:** {', '.join(geo_config.get('include_countries', []))}")
            st.write(f"**Remote Work:** {'✅ Enabled' if geo_config.get('include_remote_if_eligible') else '❌ Disabled'}")
            
            st.subheader("Company Size Filters")
            size_config = config['filters'].get('company_size', {})
            st.write(f"**Employees:** {size_config.get('employee_min', 0):,} - {size_config.get('employee_max', 0):,}")
            st.write(f"**Revenue:** ${size_config.get('revenue_min_usd', 0)/1000000:.0f}M - ${size_config.get('revenue_max_usd', 0)/1000000:.0f}M")
            st.write(f"**Logic:** {size_config.get('decision_logic', 'N/A')}")
            
            with st.expander("View Full Config"):
                st.json(config)
        else:
            st.error("Could not load filter configuration")
    
    # Load and display data
    df = load_us_mid_market_data()
    
    if df.empty:
        st.warning("No data to display. Please ensure the export file exists or configure DATA_EXPORT_URL.")
        return
    
    # Add flattened reason codes column for auditability
    if 'filter_reasons' in df.columns:
        df['reason_codes'] = df['filter_reasons'].apply(
            lambda x: flatten_filter_reasons(x) if isinstance(x, dict) else "No reasons available"
        )
    else:
        df['reason_codes'] = "No filtering applied"
    
    # Show KPIs
    show_kpis(df)
    
    # Filters
    st.header("Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        # State filter
        if 'parsed_location_state' in df.columns:
            available_states = sorted([s for s in df['parsed_location_state'].unique() if pd.notna(s)])
            selected_states = st.multiselect(
                "Select States",
                options=available_states,
                default=available_states[:5] if len(available_states) > 5 else available_states
            )
        else:
            selected_states = []
    
    with col2:
        # Text search
        search_term = st.text_input("Search by Title or Company", placeholder="e.g. engineer, tech")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_states and 'parsed_location_state' in df.columns:
        filtered_df = filtered_df[filtered_df['parsed_location_state'].isin(selected_states)]
    
    if search_term:
        mask = (
            filtered_df['title'].str.contains(search_term, case=False, na=False) |
            filtered_df['company'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Show updated metrics for filtered data
    if len(filtered_df) != len(df):
        st.info(f"Showing {len(filtered_df)} of {len(df)} total jobs after filtering")
    
    # Visualizations
    show_visualizations(filtered_df)
    
    # Data table
    st.header("Job Listings")
    
    # Prepare display columns
    display_columns = ['title', 'company', 'location', 'department', 'source', 'reason_codes']
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    
    if available_columns:
        # Make table more readable
        display_df = filtered_df[available_columns].copy()
        
        # Rename columns for better display
        column_names = {
            'title': 'Job Title',
            'company': 'Company', 
            'location': 'Location',
            'department': 'Department',
            'source': 'Source',
            'reason_codes': 'Filter Reason Codes'
        }
        
        display_df = display_df.rename(columns=column_names)
        
        # Show the table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.error("Required columns not found in data")
    
    # Download button
    if not filtered_df.empty:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"us_mid_market_jobs_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()