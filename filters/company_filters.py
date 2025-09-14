from typing import Dict, Tuple
from models.company_profile import CompanyProfile
from models.job_posting import JobPosting


US_STATES = {"AL","AK","AZ","AR","CA","CO","CT","DC","DE","FL","GA","HI","IA","ID",
             "IL","IN","KS","KY","LA","MA","MD","ME","MI","MN","MO","MS","MT",
             "NC","ND","NE","NH","NJ","NM","NV","NY","OH","OK","OR","PA","RI",
             "SC","SD","TN","TX","UT","VA","VT","WA","WI","WV","WY"}


def is_us_geo(job: JobPosting, cfg) -> Tuple[bool, Dict]:
    """
    Check if job posting is for a US-based position.
    
    Args:
        job: JobPosting object
        cfg: Configuration object with filters
        
    Returns:
        Tuple of (is_us_geo: bool, reasons: dict)
    """
    reasons = {}
    is_us = False
    
    # Direct country match
    if job.location_country == "US": 
        reasons["country"] = True
        is_us = True
    
    # State-only locations like "Austin, TX" (likely US)
    if job.location_state and job.location_state.upper() in US_STATES:
        reasons["state_abbrev"] = True
        is_us = True
    
    # Remote job with US eligibility
    filters_config = cfg.filters if hasattr(cfg, 'filters') else cfg
    if job.is_remote and filters_config["geo"]["include_remote_if_eligible"]:
        text = (job.work_auth_text or "").lower()
        allowed = [p.lower() for p in filters_config["geo"]["allowed_remote_phrases"]]
        
        # Check for explicit US remote work authorization phrases
        if any(p in text for p in allowed):
            reasons["remote_text"] = True
            is_us = True
        
        # Check for US timezone hints as soft signals
        us_timezones = filters_config["geo"]["us_timezones"]
        if any(tz in (job.tz_hints or []) for tz in us_timezones):
            reasons["tz_hint"] = True
            is_us = True
    
    return is_us, reasons


def is_mid_market(company: CompanyProfile, cfg) -> Tuple[bool, Dict]:
    """
    Check if company meets mid-market size criteria.
    
    Args:
        company: CompanyProfile object
        cfg: Configuration object with filters
        
    Returns:
        Tuple of (is_mid_market: bool, reasons: dict)
    """
    reasons = {}
    
    # Get configuration parameters
    filters_config = cfg.filters if hasattr(cfg, 'filters') else cfg
    emp_min = filters_config["company_size"]["employee_min"]
    emp_max = filters_config["company_size"]["employee_max"]
    rev_min = filters_config["company_size"]["revenue_min_usd"]
    rev_max = filters_config["company_size"]["revenue_max_usd"]
    decision_logic = filters_config["company_size"]["decision_logic"]
    
    # Check employee count criteria
    emp_ok = False
    if company.employee_count is not None:
        emp_ok = emp_min <= company.employee_count <= emp_max
    
    # Check revenue criteria
    rev_ok = False
    if company.revenue_usd is not None:
        rev_ok = rev_min <= company.revenue_usd <= rev_max
    
    # Store individual checks in reasons
    reasons["emp_ok"] = emp_ok
    reasons["rev_ok"] = rev_ok
    reasons["mode"] = decision_logic
    reasons["emp_count"] = company.employee_count
    reasons["revenue"] = company.revenue_usd
    
    # Apply decision logic
    if decision_logic == "employees_only":
        result = emp_ok
    elif decision_logic == "revenue_only":
        result = rev_ok
    elif decision_logic == "employees_or_revenue":
        result = emp_ok or rev_ok
    elif decision_logic == "employees_and_revenue":
        result = emp_ok and rev_ok
    else:
        result = False
    
    reasons["final_result"] = result
    return result, reasons


def is_us_mid_market(company: CompanyProfile, job: JobPosting, cfg) -> Tuple[bool, Dict]:
    """
    Check if company and job posting meet US mid-market criteria.
    
    Args:
        company: CompanyProfile object
        job: JobPosting object
        cfg: Configuration object with filters
        
    Returns:
        Tuple of (passes_filter: bool, reasons: dict)
    """
    reasons = {}
    
    # Check geographic eligibility
    geo_ok, geo_reasons = is_us_geo(job, cfg)
    reasons.update({f"geo.{k}": v for k, v in geo_reasons.items()})
    
    # Check company size eligibility
    size_ok, size_reasons = is_mid_market(company, cfg)
    reasons.update({f"size.{k}": v for k, v in size_reasons.items()})
    
    # Handle inconclusive enrichment policy
    if not size_ok and company.employee_count is None and company.revenue_usd is None:
        filters_config = cfg.filters if hasattr(cfg, 'filters') else cfg
        policy = filters_config.get("inconclusive_policy", "require_soft_plus_hard")
        
        if policy == "require_soft_plus_hard":
            # Accept only if we have US geo + at least one soft signal
            has_soft_signals = any(
                k in ["geo.tz_hint"] and v 
                for k, v in reasons.items()
            )
            has_hard_signals = any(
                k in ["geo.country", "geo.state_abbrev", "geo.remote_text"] and v 
                for k, v in reasons.items()
            )
            
            inconclusive_ok = geo_ok and has_soft_signals and has_hard_signals
            reasons["inconclusive_soft_gate"] = inconclusive_ok
            reasons["has_soft_signals"] = has_soft_signals
            reasons["has_hard_signals"] = has_hard_signals
            
            if inconclusive_ok:
                return True, reasons
    
    # Final decision: both geo and size must pass
    final_result = geo_ok and size_ok
    reasons["final_decision"] = final_result
    
    return final_result, reasons


def apply_industry_exclusions(company: CompanyProfile, cfg) -> Tuple[bool, Dict]:
    """
    Check if company should be excluded based on industry.
    
    Args:
        company: CompanyProfile object
        cfg: Configuration object with filters
        
    Returns:
        Tuple of (should_exclude: bool, reasons: dict)
    """
    reasons = {}
    filters_config = cfg.filters if hasattr(cfg, 'filters') else cfg
    excluded_industries = filters_config.get("exclude_industries", [])
    
    if not excluded_industries:
        reasons["no_exclusions"] = True
        return False, reasons
    
    # Extract industry from enrichment sources
    company_industry = None
    if hasattr(company, 'sources') and company.sources:
        for source, data in company.sources.items():
            if isinstance(data, dict) and 'industry' in data:
                company_industry = data['industry']
                break
    
    if not company_industry:
        reasons["no_industry_data"] = True
        return False, reasons
    
    # Check for exclusions (case-insensitive partial matching)
    for excluded in excluded_industries:
        if excluded.lower() in company_industry.lower():
            reasons["excluded_industry"] = excluded
            reasons["company_industry"] = company_industry
            return True, reasons
    
    reasons["industry_allowed"] = company_industry
    return False, reasons


def get_filter_summary(reasons: Dict) -> str:
    """
    Generate human-readable summary of filter results.
    
    Args:
        reasons: Reasons dictionary from filtering functions
        
    Returns:
        String summary of why job was accepted/rejected
    """
    summary_parts = []
    
    # Geographic reasons
    if reasons.get("geo.country"):
        summary_parts.append("US country")
    if reasons.get("geo.state_abbrev"):
        summary_parts.append("US state")
    if reasons.get("geo.remote_text"):
        summary_parts.append("US remote authorization")
    if reasons.get("geo.tz_hint"):
        summary_parts.append("US timezone hint")
    
    # Size reasons
    if reasons.get("size.emp_ok"):
        summary_parts.append(f"employee count ({reasons.get('size.emp_count', 'N/A')})")
    if reasons.get("size.rev_ok"):
        revenue = reasons.get('size.revenue', 0)
        summary_parts.append(f"revenue (${revenue/1000000:.1f}M)")
    
    # Special cases
    if reasons.get("inconclusive_soft_gate"):
        summary_parts.append("inconclusive data with soft signals")
    
    if reasons.get("excluded_industry"):
        summary_parts.append(f"EXCLUDED: {reasons['excluded_industry']} industry")
    
    if not summary_parts:
        return "No matching criteria"
    
    return " + ".join(summary_parts)