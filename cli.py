#!/usr/bin/env python3
"""
CLI for the Job Analysis ML Project with US Mid-Market Filtering
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import yaml
import pandas as pd
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.company_profile import CompanyProfile
from models.job_posting import JobPosting
from enrichment.company_enrichment import enrich_company
from filters.company_filters import is_us_mid_market, apply_industry_exclusions, get_filter_summary


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration handler for the filtering system."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = project_root / "configs" / "filters.yml"
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
    
    @property
    def filters(self):
        return self._config['filters']


def load_job_data(input_file: str) -> List[Dict[str, Any]]:
    """Load job data from JSON file."""
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_job_posting(job_data: Dict[str, Any]) -> JobPosting:
    """Parse job data into JobPosting object with location extraction."""
    # Extract location information from existing data
    location = job_data.get('location', '')
    is_remote = 'remote' in location.lower()
    
    # Simple location parsing (can be enhanced)
    location_country = None
    location_state = None
    work_auth_text = None
    tz_hints = []
    
    description = job_data.get('description', '')
    
    # Extract US location indicators
    if 'US' in location or 'United States' in location:
        location_country = 'US'
    
    # Extract state from location string
    us_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID',
        'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT',
        'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI',
        'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'
    }
    
    for state in us_states:
        if f', {state}' in location or f' {state}' in location:
            location_state = state
            location_country = 'US'
            break
    
    # Extract work authorization text
    auth_phrases = [
        'authorized to work in the United States',
        'US work authorization',
        'must reside in the United States',
        'US only',
        'United States only'
    ]
    
    for phrase in auth_phrases:
        if phrase.lower() in description.lower():
            work_auth_text = phrase
            break
    
    # Extract timezone hints
    timezones = ['EST', 'EDT', 'CST', 'CDT', 'MST', 'MDT', 'PST', 'PDT']
    for tz in timezones:
        if tz in description:
            tz_hints.append(tz)
    
    return JobPosting(
        title=job_data.get('title', ''),
        company=job_data.get('company', ''),
        location=location,
        description=description,
        department=job_data.get('department'),
        job_url=job_data.get('job_url', ''),
        source=job_data.get('source', ''),
        scraped_date=job_data.get('scraped_date', ''),
        location_country=location_country,
        location_state=location_state,
        is_remote=is_remote,
        work_auth_text=work_auth_text,
        tz_hints=tz_hints
    )


def create_company_profile(job: JobPosting) -> CompanyProfile:
    """Create company profile from job posting."""
    # Extract domain from company name (simplified)
    company_name = job.company
    domain = None
    
    # Simple domain extraction (can be enhanced)
    if '.' in company_name.lower():
        domain = company_name.lower()
    else:
        # Generate potential domain
        domain = f"{company_name.lower().replace(' ', '').replace(',', '')}.com"
    
    return CompanyProfile(
        company_name=company_name,
        domain=domain
    )


def export_filtered_jobs(
    input_file: str,
    output_file: str,
    config: Config,
    only_us_mid_market: bool = False,
    include_reasons: bool = True,
    enrich_companies: bool = False
) -> Dict[str, int]:
    """
    Export filtered job postings to specified format.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output file
        config: Configuration object
        only_us_mid_market: Whether to filter for US mid-market companies only
        include_reasons: Whether to include filtering reason codes
        enrich_companies: Whether to enrich companies (may be slow)
    
    Returns:
        Dictionary with processing statistics
    """
    logger.info(f"Loading job data from {input_file}")
    raw_jobs = load_job_data(input_file)
    
    processed_jobs = []
    stats = {
        'total_jobs': len(raw_jobs),
        'accepted_jobs': 0,
        'rejected_jobs': 0,
        'enrichment_attempts': 0,
        'enrichment_successes': 0
    }
    
    # Track unique companies for enrichment caching
    company_profiles = {}
    
    logger.info(f"Processing {len(raw_jobs)} job postings...")
    
    for i, job_data in enumerate(raw_jobs):
        try:
            job = parse_job_posting(job_data)
            
            # Get or create company profile
            company_key = job.company.lower()
            if company_key not in company_profiles:
                company_profile = create_company_profile(job)
                
                # Enrich company data if requested
                if enrich_companies:
                    logger.info(f"Enriching company data for {job.company}")
                    stats['enrichment_attempts'] += 1
                    try:
                        enriched_profile = enrich_company(company_profile)
                        company_profiles[company_key] = enriched_profile
                        if any(enriched_profile.sources.values()):
                            stats['enrichment_successes'] += 1
                    except Exception as e:
                        logger.warning(f"Enrichment failed for {job.company}: {e}")
                        company_profiles[company_key] = company_profile
                else:
                    company_profiles[company_key] = company_profile
            
            company_profile = company_profiles[company_key]
            
            # Apply filtering
            accept_job = True
            reasons = {}
            
            if only_us_mid_market:
                accept_job, reasons = is_us_mid_market(company_profile, job, config)
                
                # Also check industry exclusions
                if accept_job:
                    exclude_job, exclusion_reasons = apply_industry_exclusions(company_profile, config)
                    if exclude_job:
                        accept_job = False
                        reasons.update(exclusion_reasons)
            
            # Prepare output record
            output_record = job_data.copy()
            
            # Add enriched company data
            if company_profile.employee_count:
                output_record['enriched_employee_count'] = company_profile.employee_count
            if company_profile.employee_bucket:
                output_record['enriched_employee_bucket'] = company_profile.employee_bucket
            if company_profile.hq_country:
                output_record['enriched_hq_country'] = company_profile.hq_country
            if company_profile.hq_state:
                output_record['enriched_hq_state'] = company_profile.hq_state
            
            # Add parsing results
            output_record['parsed_location_country'] = job.location_country
            output_record['parsed_location_state'] = job.location_state
            output_record['parsed_is_remote'] = job.is_remote
            output_record['parsed_work_auth_text'] = job.work_auth_text
            output_record['parsed_tz_hints'] = job.tz_hints
            
            # Add filtering results
            if include_reasons:
                output_record['filter_result'] = accept_job
                output_record['filter_reasons'] = reasons
                output_record['filter_summary'] = get_filter_summary(reasons)
            
            if accept_job or not only_us_mid_market:
                processed_jobs.append(output_record)
                if accept_job:
                    stats['accepted_jobs'] += 1
                else:
                    stats['rejected_jobs'] += 1
            else:
                stats['rejected_jobs'] += 1
            
            # Progress update
            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1}/{len(raw_jobs)} jobs")
                
        except Exception as e:
            logger.error(f"Error processing job {i}: {e}")
            continue
    
    # Export processed jobs
    logger.info(f"Exporting {len(processed_jobs)} jobs to {output_file}")
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_file.endswith('.parquet'):
        df = pd.DataFrame(processed_jobs)
        df.to_parquet(output_file, index=False)
    elif output_file.endswith('.csv'):
        df = pd.DataFrame(processed_jobs)
        df.to_csv(output_file, index=False)
    else:
        # Default to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_jobs, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Export completed: {stats}")
    return stats


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Job Analysis ML Project CLI with US Mid-Market Filtering'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export filtered job data')
    export_parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input JSON file with job data'
    )
    export_parser.add_argument(
        '--out', '-o',
        required=True,
        help='Output file path (supports .json, .csv, .parquet)'
    )
    export_parser.add_argument(
        '--only-us-mid-market',
        action='store_true',
        help='Filter for US mid-market companies only'
    )
    export_parser.add_argument(
        '--config', '-c',
        help='Path to configuration file (default: configs/filters.yml)'
    )
    export_parser.add_argument(
        '--no-reasons',
        action='store_true',
        help='Exclude filtering reason codes from output'
    )
    export_parser.add_argument(
        '--enrich',
        action='store_true',
        help='Enrich companies with external data (slower)'
    )
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview filtered results')
    preview_parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input JSON file with job data'
    )
    preview_parser.add_argument(
        '--limit', '-l',
        type=int,
        default=5,
        help='Number of jobs to preview (default: 5)'
    )
    preview_parser.add_argument(
        '--only-us-mid-market',
        action='store_true',
        help='Filter for US mid-market companies only'
    )
    preview_parser.add_argument(
        '--config', '-c',
        help='Path to configuration file (default: configs/filters.yml)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load configuration
    try:
        config = Config(args.config)
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return 1
    
    if args.command == 'export':
        try:
            stats = export_filtered_jobs(
                input_file=args.input,
                output_file=args.out,
                config=config,
                only_us_mid_market=args.only_us_mid_market,
                include_reasons=not args.no_reasons,
                enrich_companies=args.enrich
            )
            
            print("\n=== Export Summary ===")
            print(f"Total jobs processed: {stats['total_jobs']}")
            print(f"Accepted jobs: {stats['accepted_jobs']}")
            print(f"Rejected jobs: {stats['rejected_jobs']}")
            if args.enrich:
                print(f"Company enrichment: {stats['enrichment_successes']}/{stats['enrichment_attempts']} successful")
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return 1
    
    elif args.command == 'preview':
        try:
            # Create temporary output file for preview
            temp_output = f"/tmp/preview_{datetime.now().timestamp()}.json"
            
            stats = export_filtered_jobs(
                input_file=args.input,
                output_file=temp_output,
                config=config,
                only_us_mid_market=args.only_us_mid_market,
                include_reasons=True,
                enrich_companies=False  # Don't enrich for preview
            )
            
            # Load and display preview
            with open(temp_output, 'r') as f:
                preview_data = json.load(f)
            
            print(f"\n=== Preview: First {args.limit} jobs ===")
            for i, job in enumerate(preview_data[:args.limit]):
                print(f"\n{i+1}. {job['title']} at {job['company']}")
                print(f"   Location: {job['location']}")
                if 'filter_summary' in job:
                    print(f"   Filter: {job['filter_summary']}")
                if job.get('filter_result', True):
                    print("   ✅ ACCEPTED")
                else:
                    print("   ❌ REJECTED")
            
            print(f"\n=== Summary ===")
            print(f"Total: {stats['total_jobs']}, Accepted: {stats['accepted_jobs']}, Rejected: {stats['rejected_jobs']}")
            
            # Clean up temp file
            os.unlink(temp_output)
            
        except Exception as e:
            logger.error(f"Preview failed: {e}")
            return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())