import requests
import re
import logging
from typing import Optional, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class LinkedInProvider:
    """
    Provider to extract company information from LinkedIn company pages.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def enrich_company(self, company_name: str, domain: Optional[str] = None) -> Optional[Dict]:
        """
        Extract company data from LinkedIn company page or search results.
        
        Args:
            company_name: Company name to search for
            domain: Optional company domain for verification
            
        Returns:
            Dictionary with extracted company data or None if not found
        """
        try:
            # Try to find LinkedIn company URL
            linkedin_url = self._find_linkedin_company_url(company_name, domain)
            if not linkedin_url:
                logger.info(f"LinkedIn company page not found for {company_name}")
                return None
            
            # Extract company data from LinkedIn page
            return self._extract_company_data(linkedin_url)
            
        except Exception as e:
            logger.error(f"LinkedIn enrichment failed for {company_name}: {e}")
            return None
    
    def _find_linkedin_company_url(self, company_name: str, domain: Optional[str] = None) -> Optional[str]:
        """
        Find LinkedIn company URL through search or direct construction.
        """
        # Try direct URL construction first
        company_slug = re.sub(r'[^a-zA-Z0-9-]', '-', company_name.lower())
        company_slug = re.sub(r'-+', '-', company_slug).strip('-')
        
        potential_urls = [
            f"https://www.linkedin.com/company/{company_slug}",
            f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}",
        ]
        
        # Add domain-based URL if available
        if domain:
            domain_name = domain.replace('www.', '').split('.')[0]
            potential_urls.append(f"https://www.linkedin.com/company/{domain_name}")
        
        for url in potential_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200 and 'linkedin.com/company/' in response.url:
                    logger.info(f"Found LinkedIn URL: {response.url}")
                    return response.url
            except requests.RequestException:
                continue
        
        # If direct URLs don't work, try search (simplified approach)
        return self._search_linkedin_company(company_name)
    
    def _search_linkedin_company(self, company_name: str) -> Optional[str]:
        """
        Search for company on LinkedIn (simplified implementation).
        """
        try:
            # Use Google search to find LinkedIn company page
            search_query = f"site:linkedin.com/company {company_name}"
            search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                # Extract LinkedIn URLs from search results (basic regex)
                linkedin_urls = re.findall(r'https://(?:www\.)?linkedin\.com/company/[^\s"]+', response.text)
                if linkedin_urls:
                    return linkedin_urls[0].split('&')[0]  # Clean URL
                    
        except Exception as e:
            logger.warning(f"LinkedIn search failed for {company_name}: {e}")
        
        return None
    
    def _extract_company_data(self, linkedin_url: str) -> Dict:
        """
        Extract company information from LinkedIn company page.
        """
        try:
            response = self.session.get(linkedin_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            data = {
                'url': linkedin_url,
                'employee_bucket': None,
                'employee_count': None,
                'hq_country': None,
                'hq_state': None,
                'industry': None,
            }
            
            # Extract employee count/bucket
            employee_info = self._extract_employee_info(soup, response.text)
            if employee_info:
                data.update(employee_info)
            
            # Extract headquarters location
            location_info = self._extract_location_info(soup, response.text)
            if location_info:
                data.update(location_info)
            
            # Extract industry
            industry = self._extract_industry(soup, response.text)
            if industry:
                data['industry'] = industry
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to extract data from {linkedin_url}: {e}")
            return {'url': linkedin_url, 'error': str(e)}
    
    def _extract_employee_info(self, soup: BeautifulSoup, html_text: str) -> Optional[Dict]:
        """
        Extract employee count and bucket information.
        """
        # Common patterns for employee count on LinkedIn
        patterns = [
            r'(\d{1,3}(?:,\d{3})*(?:-\d{1,3}(?:,\d{3})*)?)\s+employees?',
            r'(\d+(?:,\d+)*)\s*-\s*(\d+(?:,\d+)*)\s+employees?',
            r'Size[:\s]*(\d+(?:,\d+)*(?:\s*-\s*\d+(?:,\d+)*)?)\s+employees?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_text, re.IGNORECASE)
            if matches:
                bucket = matches[0] if isinstance(matches[0], str) else '-'.join(matches[0])
                bucket = bucket.strip()
                
                # Normalize employee count from bucket
                employee_count = self._normalize_employee_bucket(bucket)
                
                return {
                    'employee_bucket': bucket,
                    'employee_count': employee_count
                }
        
        return None
    
    def _extract_location_info(self, soup: BeautifulSoup, html_text: str) -> Optional[Dict]:
        """
        Extract headquarters location information.
        """
        # Look for headquarters or location patterns
        location_patterns = [
            r'Headquarters[:\s]*([^,\n]+(?:,\s*[^,\n]+)*)',
            r'Location[:\s]*([^,\n]+(?:,\s*[^,\n]+)*)',
            r'Based in[:\s]*([^,\n]+(?:,\s*[^,\n]+)*)',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, html_text, re.IGNORECASE)
            if matches:
                location = matches[0].strip()
                return self._parse_location(location)
        
        return None
    
    def _extract_industry(self, soup: BeautifulSoup, html_text: str) -> Optional[str]:
        """
        Extract industry information.
        """
        industry_patterns = [
            r'Industry[:\s]*([^\n,]+)',
            r'Sector[:\s]*([^\n,]+)',
        ]
        
        for pattern in industry_patterns:
            matches = re.findall(pattern, html_text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return None
    
    def _parse_location(self, location: str) -> Dict:
        """
        Parse location string into country and state components.
        """
        result = {'hq_country': None, 'hq_state': None}
        
        if not location:
            return result
        
        # Common US states abbreviations
        us_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID',
            'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT',
            'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI',
            'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'
        }
        
        parts = [part.strip() for part in location.split(',')]
        
        # Look for US indicators
        if any('united states' in part.lower() or 'usa' in part.lower() or 'us' == part.lower() for part in parts):
            result['hq_country'] = 'US'
            # Find state
            for part in parts:
                part = part.upper().strip()
                if part in us_states:
                    result['hq_state'] = part
                    break
        else:
            # Check if last part is a country
            if len(parts) > 1:
                potential_country = parts[-1].strip()
                if len(potential_country) == 2:  # Country code
                    result['hq_country'] = potential_country.upper()
        
        return result
    
    def _normalize_employee_bucket(self, bucket: str) -> Optional[int]:
        """
        Normalize employee bucket to approximate count.
        """
        if not bucket:
            return None
        
        # Remove commas and normalize separators
        bucket = bucket.replace(',', '').replace('–', '-').replace('−', '-')
        
        # Handle ranges like "201-500"
        if '-' in bucket:
            try:
                parts = bucket.split('-')
                start = int(parts[0])
                if len(parts) > 1 and parts[1].replace('+', '').isdigit():
                    end = int(parts[1].replace('+', ''))
                    return (start + end) // 2
                else:
                    # Handle "1000+" cases
                    return int(start * 1.5)
            except ValueError:
                pass
        
        # Handle single numbers
        try:
            if bucket.endswith('+'):
                return int(int(bucket[:-1]) * 1.5)
            else:
                return int(bucket)
        except ValueError:
            pass
        
        return None