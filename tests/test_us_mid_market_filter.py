#!/usr/bin/env python3
"""
Comprehensive tests for US mid-market filtering functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.company_profile import CompanyProfile
from models.job_posting import JobPosting
from filters.company_filters import (
    is_us_geo, is_mid_market, is_us_mid_market, 
    apply_industry_exclusions, get_filter_summary
)


class MockConfig:
    """Mock configuration object for testing."""
    
    def __init__(self, filters_config=None):
        if filters_config is None:
            filters_config = {
                "geo": {
                    "include_countries": ["US"],
                    "include_remote_if_eligible": True,
                    "allowed_remote_phrases": [
                        "US only", "United States only", 
                        "authorized to work in the United States",
                        "US work authorization", "must reside in the United States",
                        "remote within the United States", "remote - US", "US-based"
                    ],
                    "us_timezones": ["EST", "EDT", "CST", "CDT", "MST", "MDT", "PST", "PDT"]
                },
                "company_size": {
                    "employee_min": 50,
                    "employee_max": 999,
                    "revenue_min_usd": 10000000,    # $10M
                    "revenue_max_usd": 1000000000,  # $1B
                    "decision_logic": "employees_or_revenue"
                },
                "exclude_industries": [],
                "inconclusive_policy": "require_soft_plus_hard"
            }
        self.filters = filters_config


class TestUSGeoFiltering:
    """Test geographic filtering for US positions."""
    
    def test_us_country_direct_match(self):
        """Test US on-site job with direct country match."""
        job = JobPosting(
            title="Software Engineer",
            company="Test Corp",
            location="San Francisco, CA",
            description="Great job",
            job_url="http://example.com",
            source="test",
            scraped_date="2025-01-01",
            location_country="US"
        )
        
        config = MockConfig()
        result, reasons = is_us_geo(job, config)
        
        assert result == True
        assert reasons["country"] == True
    
    def test_us_state_abbreviation_match(self):
        """Test location with US state abbreviation."""
        job = JobPosting(
            title="Data Scientist",
            company="Tech Inc",
            location="Austin, TX",
            description="Remote work available",
            job_url="http://example.com",
            source="test",
            scraped_date="2025-01-01",
            location_state="TX"
        )
        
        config = MockConfig()
        result, reasons = is_us_geo(job, config)
        
        assert result == True
        assert reasons["state_abbrev"] == True
    
    def test_remote_us_authorization_text(self):
        """Test remote job with US work authorization text."""
        job = JobPosting(
            title="Backend Engineer",
            company="Remote Corp",
            location="Remote",
            description="Must be authorized to work in the United States",
            job_url="http://example.com",
            source="test",
            scraped_date="2025-01-01",
            is_remote=True,
            work_auth_text="authorized to work in the United States"
        )
        
        config = MockConfig()
        result, reasons = is_us_geo(job, config)
        
        assert result == True
        assert reasons["remote_text"] == True
    
    def test_remote_us_timezone_hint(self):
        """Test remote job with US timezone hint."""
        job = JobPosting(
            title="Product Manager",
            company="Global Inc",
            location="Remote",
            description="EST timezone preferred",
            job_url="http://example.com",
            source="test",
            scraped_date="2025-01-01",
            is_remote=True,
            tz_hints=["EST"]
        )
        
        config = MockConfig()
        result, reasons = is_us_geo(job, config)
        
        assert result == True
        assert reasons["tz_hint"] == True
    
    def test_non_us_job_rejected(self):
        """Test non-US job is rejected."""
        job = JobPosting(
            title="Developer",
            company="EU Corp",
            location="London, UK",
            description="Great opportunity in London",
            job_url="http://example.com",
            source="test",
            scraped_date="2025-01-01",
            location_country="UK"
        )
        
        config = MockConfig()
        result, reasons = is_us_geo(job, config)
        
        assert result == False
        assert not any(reasons.values())


class TestMidMarketFiltering:
    """Test company size filtering for mid-market companies."""
    
    def test_employee_count_in_range(self):
        """Test company with employee count in mid-market range."""
        company = CompanyProfile(
            company_name="Mid Corp",
            employee_count=150
        )
        
        config = MockConfig()
        result, reasons = is_mid_market(company, config)
        
        assert result == True
        assert reasons["emp_ok"] == True
        assert reasons["mode"] == "employees_or_revenue"
    
    def test_revenue_in_range(self):
        """Test company with revenue in mid-market range."""
        company = CompanyProfile(
            company_name="Revenue Corp",
            revenue_usd=50000000  # $50M
        )
        
        config = MockConfig()
        result, reasons = is_mid_market(company, config)
        
        assert result == True
        assert reasons["rev_ok"] == True
    
    def test_employees_or_revenue_logic(self):
        """Test employees_or_revenue decision logic."""
        # Company with only employee count qualifying
        company1 = CompanyProfile(
            company_name="Emp Corp",
            employee_count=200,
            revenue_usd=5000000  # Too low
        )
        
        config = MockConfig()
        result, reasons = is_mid_market(company1, config)
        
        assert result == True
        assert reasons["emp_ok"] == True
        assert reasons["rev_ok"] == False
    
    def test_employees_and_revenue_logic(self):
        """Test employees_and_revenue decision logic."""
        company = CompanyProfile(
            company_name="Both Corp",
            employee_count=200,
            revenue_usd=5000000  # Too low
        )
        
        # Change config to require both
        config = MockConfig()
        config.filters["company_size"]["decision_logic"] = "employees_and_revenue"
        
        result, reasons = is_mid_market(company, config)
        
        assert result == False
        assert reasons["emp_ok"] == True
        assert reasons["rev_ok"] == False
    
    def test_employee_count_too_small(self):
        """Test company with too few employees."""
        company = CompanyProfile(
            company_name="Small Corp",
            employee_count=25  # Below 50
        )
        
        config = MockConfig()
        result, reasons = is_mid_market(company, config)
        
        assert result == False
        assert reasons["emp_ok"] == False
    
    def test_employee_count_too_large(self):
        """Test company with too many employees."""
        company = CompanyProfile(
            company_name="Large Corp",
            employee_count=1500  # Above 999
        )
        
        config = MockConfig()
        result, reasons = is_mid_market(company, config)
        
        assert result == False
        assert reasons["emp_ok"] == False


class TestUSMidMarketIntegration:
    """Test integrated US mid-market filtering."""
    
    def test_us_onsite_mid_market_accept(self):
        """US on-site + mid-market employees → accept."""
        company = CompanyProfile(
            company_name="Good Corp",
            employee_count=120
        )
        
        job = JobPosting(
            title="Engineer",
            company="Good Corp",
            location="Seattle, WA",
            description="Great job",
            job_url="http://example.com",
            source="test",
            scraped_date="2025-01-01",
            location_country="US",
            location_state="WA"
        )
        
        config = MockConfig()
        result, reasons = is_us_mid_market(company, job, config)
        
        assert result == True
        assert reasons["geo.country"] == True
        assert reasons["size.emp_ok"] == True
    
    def test_remote_us_only_unknown_employees_with_tz_accept(self):
        """Remote with 'US only' phrase + employees unknown + tz hint → accept."""
        company = CompanyProfile(
            company_name="Remote Corp",
            employee_count=None  # Unknown
        )
        
        job = JobPosting(
            title="Remote Dev",
            company="Remote Corp",
            location="Remote",
            description="US only remote position",
            job_url="http://example.com",
            source="test",
            scraped_date="2025-01-01",
            is_remote=True,
            work_auth_text="US only",
            tz_hints=["PST"]
        )
        
        config = MockConfig()
        result, reasons = is_us_mid_market(company, job, config)
        
        assert result == True
        assert reasons["geo.remote_text"] == True
        assert reasons["geo.tz_hint"] == True
        assert reasons["inconclusive_soft_gate"] == True
    
    def test_us_onsite_small_revenue_large_accept(self):
        """US on-site + small employees + large revenue with OR logic → accept."""
        company = CompanyProfile(
            company_name="Revenue Corp",
            employee_count=15,  # Too small
            revenue_usd=200000000  # $200M - good
        )
        
        job = JobPosting(
            title="Sales Rep",
            company="Revenue Corp",
            location="New York, NY",
            description="Sales position",
            job_url="http://example.com",
            source="test",
            scraped_date="2025-01-01",
            location_country="US",
            location_state="NY"
        )
        
        config = MockConfig()
        result, reasons = is_us_mid_market(company, job, config)
        
        assert result == True
        assert reasons["geo.country"] == True
        assert reasons["size.emp_ok"] == False
        assert reasons["size.rev_ok"] == True
    
    def test_non_us_mid_market_reject(self):
        """Non-US + mid-market employees → reject."""
        company = CompanyProfile(
            company_name="EU Corp",
            employee_count=500  # Good size
        )
        
        job = JobPosting(
            title="Developer",
            company="EU Corp",
            location="Berlin, Germany",
            description="European position",
            job_url="http://example.com",
            source="test",
            scraped_date="2025-01-01",
            location_country="DE"
        )
        
        config = MockConfig()
        result, reasons = is_us_mid_market(company, job, config)
        
        assert result == False
        assert not any(k.startswith("geo.") and v for k, v in reasons.items())
        assert reasons["size.emp_ok"] == True
    
    def test_us_large_company_reject(self):
        """US + large company → reject."""
        company = CompanyProfile(
            company_name="BigTech Corp",
            employee_count=1200  # Too large
        )
        
        job = JobPosting(
            title="Engineer",
            company="BigTech Corp",
            location="Mountain View, CA",
            description="Big tech job",
            job_url="http://example.com",
            source="test",
            scraped_date="2025-01-01",
            location_country="US",
            location_state="CA"
        )
        
        config = MockConfig()
        result, reasons = is_us_mid_market(company, job, config)
        
        assert result == False
        assert reasons["geo.country"] == True
        assert reasons["size.emp_ok"] == False


class TestIndustryExclusions:
    """Test industry exclusion filtering."""
    
    def test_excluded_industry_rejected(self):
        """Test company in excluded industry is rejected."""
        company = CompanyProfile(
            company_name="Crypto Corp",
            sources={
                'linkedin': {'industry': 'Cryptocurrency'}
            }
        )
        
        config = MockConfig()
        config.filters["exclude_industries"] = ["Cryptocurrency", "Gambling"]
        
        result, reasons = apply_industry_exclusions(company, config)
        
        assert result == True  # True means should exclude
        assert reasons["excluded_industry"] == "Cryptocurrency"
    
    def test_allowed_industry_accepted(self):
        """Test company in allowed industry is accepted."""
        company = CompanyProfile(
            company_name="Tech Corp",
            sources={
                'linkedin': {'industry': 'Software Development'}
            }
        )
        
        config = MockConfig()
        config.filters["exclude_industries"] = ["Cryptocurrency", "Gambling"]
        
        result, reasons = apply_industry_exclusions(company, config)
        
        assert result == False  # False means don't exclude
        assert reasons["industry_allowed"] == "Software Development"


class TestFilterSummary:
    """Test filter summary generation."""
    
    def test_comprehensive_summary(self):
        """Test comprehensive filter summary."""
        reasons = {
            "geo.country": True,
            "geo.state_abbrev": True,
            "size.emp_ok": True,
            "size.emp_count": 150,
            "size.rev_ok": False,
            "size.revenue": 5000000,
            "final_decision": True
        }
        
        summary = get_filter_summary(reasons)
        
        assert "US country" in summary
        assert "US state" in summary
        assert "employee count (150)" in summary
        assert "revenue" not in summary  # rev_ok is False
    
    def test_inconclusive_summary(self):
        """Test summary with inconclusive data."""
        reasons = {
            "geo.remote_text": True,
            "geo.tz_hint": True,
            "inconclusive_soft_gate": True,
            "final_decision": True
        }
        
        summary = get_filter_summary(reasons)
        
        assert "US remote authorization" in summary
        assert "US timezone hint" in summary
        assert "inconclusive data with soft signals" in summary


class TestTableDrivenCases:
    """Table-driven test cases as specified in requirements."""
    
    test_cases = [
        {
            "name": "US on-site + employees=120 → accept",
            "company": CompanyProfile(company_name="Test", employee_count=120),
            "job": JobPosting(
                title="Test", company="Test", location="Austin, TX", 
                description="Test", job_url="http://test.com", source="test", 
                scraped_date="2025-01-01", location_country="US", location_state="TX"
            ),
            "expected": True
        },
        {
            "name": "Remote with 'US only' phrase + employees unknown + tz hint present → accept",
            "company": CompanyProfile(company_name="Test", employee_count=None),
            "job": JobPosting(
                title="Test", company="Test", location="Remote", 
                description="US only position", job_url="http://test.com", source="test", 
                scraped_date="2025-01-01", is_remote=True, work_auth_text="US only", tz_hints=["CST"]
            ),
            "expected": True
        },
        {
            "name": "US + employees=15 + revenue=$200M with mode=employees_or_revenue → accept",
            "company": CompanyProfile(company_name="Test", employee_count=15, revenue_usd=200000000),
            "job": JobPosting(
                title="Test", company="Test", location="Boston, MA", 
                description="Test", job_url="http://test.com", source="test", 
                scraped_date="2025-01-01", location_country="US", location_state="MA"
            ),
            "expected": True
        },
        {
            "name": "Non-US + employees=500 → reject",
            "company": CompanyProfile(company_name="Test", employee_count=500),
            "job": JobPosting(
                title="Test", company="Test", location="London, UK", 
                description="Test", job_url="http://test.com", source="test", 
                scraped_date="2025-01-01", location_country="UK"
            ),
            "expected": False
        },
        {
            "name": "US + employees=1200 → reject",
            "company": CompanyProfile(company_name="Test", employee_count=1200),
            "job": JobPosting(
                title="Test", company="Test", location="San Jose, CA", 
                description="Test", job_url="http://test.com", source="test", 
                scraped_date="2025-01-01", location_country="US", location_state="CA"
            ),
            "expected": False
        }
    ]
    
    @pytest.mark.parametrize("case", test_cases, ids=[c["name"] for c in test_cases])
    def test_table_driven_cases(self, case):
        """Run table-driven test cases."""
        config = MockConfig()
        result, reasons = is_us_mid_market(case["company"], case["job"], config)
        
        assert result == case["expected"], f"Failed case: {case['name']}"


if __name__ == '__main__':
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])