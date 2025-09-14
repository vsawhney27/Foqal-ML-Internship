import requests
import re
import logging
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class AboutPageProvider:
    """
    Provider to extract company information from company about/contact pages.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def enrich_company(self, company_name: str, domain: Optional[str] = None) -> Optional[Dict]:
        """
        Extract company data from about/contact pages.
        
        Args:
            company_name: Company name to search for
            domain: Company domain to scrape
            
        Returns:
            Dictionary with extracted company data or None if not found
        """
        if not domain:
            logger.info(f"No domain provided for {company_name}, skipping about page scrape")
            return None
            
        try:
            # Try to find and scrape about/contact pages
            about_pages = self._find_about_pages(domain)
            
            if not about_pages:
                logger.info(f"No about pages found for {domain}")
                return None
            
            # Extract company data from pages
            return self._extract_company_data_from_pages(about_pages, company_name)
            
        except Exception as e:
            logger.error(f"About page enrichment failed for {company_name}: {e}")
            return None
    
    def _find_about_pages(self, domain: str) -> List[str]:
        """
        Find potential about/contact pages for the domain.
        """
        base_url = f"https://{domain}" if not domain.startswith('http') else domain
        
        # Common about page paths
        potential_paths = [
            '/about',
            '/about-us',
            '/about/',
            '/company',
            '/contact',
            '/contact-us',
            '/contact/',
            '/team',
            '/our-story',
            '/who-we-are',
        ]
        
        valid_pages = []
        
        for path in potential_paths:
            try:
                url = urljoin(base_url, path)
                response = self.session.get(url, timeout=10, allow_redirects=True)
                
                if response.status_code == 200 and len(response.text) > 1000:  # Reasonable content size
                    valid_pages.append(response.url)
                    logger.info(f"Found valid about page: {response.url}")
                    
            except requests.RequestException as e:
                logger.debug(f"Failed to access {url}: {e}")
                continue
        
        # Also try the homepage if no specific about pages found
        if not valid_pages:
            try:
                response = self.session.get(base_url, timeout=10)
                if response.status_code == 200:
                    valid_pages.append(response.url)
                    logger.info(f"Using homepage: {response.url}")
            except requests.RequestException as e:
                logger.warning(f"Failed to access homepage {base_url}: {e}")
        
        return valid_pages
    
    def _extract_company_data_from_pages(self, page_urls: List[str], company_name: str) -> Dict:
        """
        Extract company information from the given pages.
        """
        data = {
            'sources': page_urls,
            'hq_country': None,
            'hq_state': None,
            'employee_count': None,
        }
        
        for url in page_urls:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                text_content = soup.get_text()
                
                # Extract location info
                if not data['hq_country'] or not data['hq_state']:
                    location_info = self._extract_location_info(text_content, soup)
                    if location_info:
                        if not data['hq_country'] and location_info.get('hq_country'):
                            data['hq_country'] = location_info['hq_country']
                        if not data['hq_state'] and location_info.get('hq_state'):
                            data['hq_state'] = location_info['hq_state']
                
                # Extract employee count
                if not data['employee_count']:
                    employee_count = self._extract_employee_count(text_content)
                    if employee_count:
                        data['employee_count'] = employee_count
                
                # Stop if we have all the data we need
                if data['hq_country'] and data['employee_count']:
                    break
                    
            except Exception as e:
                logger.warning(f"Failed to extract data from {url}: {e}")
                continue
        
        return data if any(v for k, v in data.items() if k != 'sources') else None
    
    def _extract_location_info(self, text_content: str, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract headquarters location from page content.
        """
        # US states for matching
        us_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID',
            'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT',
            'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI',
            'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'
        }
        
        # Full state names for matching
        us_state_names = {
            'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut',
            'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa',
            'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan',
            'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire',
            'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio',
            'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota',
            'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia',
            'wisconsin', 'wyoming', 'district of columbia'
        }
        
        # Patterns to look for headquarters/office locations
        location_patterns = [
            r'headquarters?[:\s]+([^.\n]+)',
            r'headquartered in[:\s]+([^.\n]+)',
            r'based in[:\s]+([^.\n]+)',
            r'located in[:\s]+([^.\n]+)',
            r'office[:\s]+([^.\n]+)',
            r'address[:\s]*:?\s*([^.\n]+)',
        ]
        
        result = {'hq_country': None, 'hq_state': None}
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                location = match.strip().lower()
                
                # Check for US indicators
                if any(indicator in location for indicator in ['united states', 'usa', 'us']):
                    result['hq_country'] = 'US'
                    
                    # Look for state
                    for state in us_states:
                        if state.lower() in location or f" {state.lower()}" in location:
                            result['hq_state'] = state
                            break
                    
                    if not result['hq_state']:
                        for state_name in us_state_names:
                            if state_name in location:
                                # Convert to abbreviation (simplified mapping)
                                state_abbrev = self._get_state_abbreviation(state_name)
                                if state_abbrev:
                                    result['hq_state'] = state_abbrev
                                break
                    
                    if result['hq_country'] and result['hq_state']:
                        return result
                
                # Check for state-only patterns (likely US)
                for state in us_states:
                    if f" {state.lower()}" in location or location.endswith(state.lower()):
                        result['hq_country'] = 'US'
                        result['hq_state'] = state
                        return result
        
        # Check structured data (schema.org)
        structured_location = self._extract_structured_location(soup)
        if structured_location:
            result.update(structured_location)
        
        return result if result['hq_country'] else None
    
    def _extract_employee_count(self, text_content: str) -> Optional[int]:
        """
        Extract employee count from page content.
        """
        # Patterns to match employee count mentions
        employee_patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s+employees?',
            r'team of\s+(\d{1,3}(?:,\d{3})*)',
            r'staff of\s+(\d{1,3}(?:,\d{3})*)',
            r'(\d{1,3}(?:,\d{3})*)\s+people',
            r'over\s+(\d{1,3}(?:,\d{3})*)\s+employees?',
            r'more than\s+(\d{1,3}(?:,\d{3})*)\s+employees?',
            r'(\d{1,3}(?:,\d{3})*)\+\s+employees?',
        ]
        
        for pattern in employee_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                try:
                    count_str = matches[0].replace(',', '')
                    count = int(count_str)
                    # Reasonable bounds check
                    if 1 <= count <= 100000:
                        return count
                except ValueError:
                    continue
        
        return None
    
    def _extract_structured_location(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract location from structured data (JSON-LD, microdata, etc.).
        """
        result = {}
        
        # Check JSON-LD structured data
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            try:
                import json
                data = json.loads(script.string)
                
                # Handle both single objects and lists
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                # Look for Organization schema
                if data.get('@type') in ['Organization', 'Corporation', 'Company']:
                    address = data.get('address', {})
                    if isinstance(address, dict):
                        country = address.get('addressCountry')
                        state = address.get('addressRegion')
                        
                        if country == 'US' or country == 'United States':
                            result['hq_country'] = 'US'
                            if state and len(state) == 2:
                                result['hq_state'] = state.upper()
                        
                        break
                        
            except (json.JSONDecodeError, KeyError):
                continue
        
        return result if result else None
    
    def _get_state_abbreviation(self, state_name: str) -> Optional[str]:
        """
        Convert full state name to abbreviation.
        """
        state_map = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
            'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
            'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
            'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
            'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY', 'district of columbia': 'DC'
        }
        
        return state_map.get(state_name.lower())