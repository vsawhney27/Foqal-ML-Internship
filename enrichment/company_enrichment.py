import logging
from typing import Optional
from models.company_profile import CompanyProfile
from providers.linkedin_html import LinkedInProvider
from providers.about_page_scrape import AboutPageProvider


logger = logging.getLogger(__name__)


def enrich_company(profile: CompanyProfile) -> CompanyProfile:
    """
    Enrich company profile with additional data from various providers.
    
    - Try to fill employee_count, employee_bucket, revenue_usd, hq_country, hq_state.
    - Providers (pluggable): linkedin_html, about_page_scrape.
    - Normalize LinkedIn size buckets to numeric ranges.
    - Never hard-fail on provider errors; return best-effort.
    
    Args:
        profile: Initial CompanyProfile with at least company_name
        
    Returns:
        Enriched CompanyProfile with available data filled in
    """
    enriched_profile = profile.copy()
    
    # Initialize providers
    linkedin_provider = LinkedInProvider()
    about_page_provider = AboutPageProvider()
    
    # Try LinkedIn enrichment first
    try:
        linkedin_data = linkedin_provider.enrich_company(profile.company_name, profile.domain)
        if linkedin_data:
            if not enriched_profile.employee_count and linkedin_data.get('employee_count'):
                enriched_profile.employee_count = linkedin_data['employee_count']
            if not enriched_profile.employee_bucket and linkedin_data.get('employee_bucket'):
                enriched_profile.employee_bucket = linkedin_data['employee_bucket']
            if not enriched_profile.hq_country and linkedin_data.get('hq_country'):
                enriched_profile.hq_country = linkedin_data['hq_country']
            if not enriched_profile.hq_state and linkedin_data.get('hq_state'):
                enriched_profile.hq_state = linkedin_data['hq_state']
            
            enriched_profile.sources['linkedin'] = linkedin_data
            logger.info(f"LinkedIn enrichment successful for {profile.company_name}")
    except Exception as e:
        logger.warning(f"LinkedIn enrichment failed for {profile.company_name}: {e}")
        enriched_profile.sources['linkedin'] = {'error': str(e)}
    
    # Try About page enrichment
    try:
        about_data = about_page_provider.enrich_company(profile.company_name, profile.domain)
        if about_data:
            if not enriched_profile.hq_country and about_data.get('hq_country'):
                enriched_profile.hq_country = about_data['hq_country']
            if not enriched_profile.hq_state and about_data.get('hq_state'):
                enriched_profile.hq_state = about_data['hq_state']
            if not enriched_profile.employee_count and about_data.get('employee_count'):
                enriched_profile.employee_count = about_data['employee_count']
            
            enriched_profile.sources['about_page'] = about_data
            logger.info(f"About page enrichment successful for {profile.company_name}")
    except Exception as e:
        logger.warning(f"About page enrichment failed for {profile.company_name}: {e}")
        enriched_profile.sources['about_page'] = {'error': str(e)}
    
    return enriched_profile


def normalize_employee_bucket(bucket: str) -> Optional[int]:
    """
    Normalize LinkedIn employee size buckets to approximate numeric ranges.
    
    Args:
        bucket: LinkedIn size bucket (e.g., "201–500", "51-200")
        
    Returns:
        Approximate employee count (midpoint of range)
    """
    if not bucket:
        return None
    
    # Common LinkedIn formats
    bucket_map = {
        "1-10": 5,
        "11-50": 30,
        "51-200": 125,
        "201-500": 350,
        "501-1000": 750,
        "1001-5000": 3000,
        "5001-10000": 7500,
        "10000+": 15000,
        "10,001+": 15000,
    }
    
    # Try direct mapping first
    if bucket in bucket_map:
        return bucket_map[bucket]
    
    # Try to parse range manually
    try:
        if '–' in bucket or '-' in bucket:
            separator = '–' if '–' in bucket else '-'
            parts = bucket.replace(',', '').split(separator)
            if len(parts) == 2:
                start = int(parts[0])
                if parts[1].endswith('+'):
                    # For ranges like "10000+", use start * 1.5 as estimate
                    return int(start * 1.5)
                else:
                    end = int(parts[1])
                    return (start + end) // 2
    except (ValueError, IndexError):
        logger.warning(f"Could not parse employee bucket: {bucket}")
    
    return None