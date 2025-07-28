#!/usr/bin/env python3
"""
Proxy Manager for Web Scraping
Handles proxy rotation and validation for scraping job sites
"""

import requests
import random
import time
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self, proxy_list=None, validate_on_init=True):
        self.proxy_list = proxy_list or self.get_free_proxies()
        self.working_proxies = []
        self.failed_proxies = set()
        self.current_proxy_index = 0
        self.lock = threading.Lock()
        
        if validate_on_init and self.proxy_list:
            self.validate_proxies()
    
    def get_free_proxies(self):
        """Get list of free public proxies (for demonstration)"""
        # Note: In production, use paid proxy services for reliability
        free_proxies = [
            "8.210.25.171:80",
            "20.111.54.16:8123", 
            "103.127.1.130:80",
            "190.97.225.37:999",
            "103.148.72.192:80"
        ]
        
        logger.info(f"Using {len(free_proxies)} free proxies (consider paid proxies for production)")
        return free_proxies
    
    def validate_proxies(self, timeout=10):
        """Validate which proxies are working"""
        logger.info(f"Validating {len(self.proxy_list)} proxies...")
        
        def test_proxy(proxy):
            try:
                proxies = {
                    'http': f'http://{proxy}',
                    'https': f'https://{proxy}'
                }
                
                response = requests.get(
                    'http://httpbin.org/ip',
                    proxies=proxies,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    return proxy
                    
            except Exception as e:
                logger.debug(f"Proxy {proxy} failed validation: {e}")
                
            return None
        
        # Test proxies concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(test_proxy, self.proxy_list))
        
        self.working_proxies = [proxy for proxy in results if proxy is not None]
        
        logger.info(f"Found {len(self.working_proxies)} working proxies out of {len(self.proxy_list)}")
        
        if not self.working_proxies:
            logger.warning("No working proxies found - scraping without proxies")
    
    def get_next_proxy(self):
        """Get next proxy in rotation"""
        with self.lock:
            if not self.working_proxies:
                return None
            
            proxy = self.working_proxies[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.working_proxies)
            
            return proxy
    
    def get_random_proxy(self):
        """Get random proxy from working list"""
        if not self.working_proxies:
            return None
        
        return random.choice(self.working_proxies)
    
    def mark_proxy_failed(self, proxy):
        """Mark a proxy as failed and remove from working list"""
        with self.lock:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                self.failed_proxies.add(proxy)
                logger.warning(f"Proxy {proxy} marked as failed")
    
    def get_proxy_dict(self, proxy):
        """Convert proxy string to requests proxy dict"""
        if not proxy:
            return None
        
        return {
            'http': f'http://{proxy}',
            'https': f'https://{proxy}'
        }
    
    def test_proxy_with_site(self, proxy, test_url="http://httpbin.org/ip"):
        """Test proxy with specific site"""
        try:
            proxies = self.get_proxy_dict(proxy)
            response = requests.get(test_url, proxies=proxies, timeout=10)
            return response.status_code == 200
        except:
            return False

class RateLimiter:
    def __init__(self, min_delay=1, max_delay=5, per_site_limits=None):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.per_site_limits = per_site_limits or {}
        self.last_request_times = {}
        self.lock = threading.Lock()
    
    def wait_for_site(self, site_name):
        """Wait appropriate time for specific site"""
        with self.lock:
            site_config = self.per_site_limits.get(site_name, {})
            min_delay = site_config.get('min_delay', self.min_delay)
            max_delay = site_config.get('max_delay', self.max_delay)
            
            last_time = self.last_request_times.get(site_name, 0)
            current_time = time.time()
            
            # Calculate required delay
            elapsed = current_time - last_time
            required_delay = random.uniform(min_delay, max_delay)
            
            if elapsed < required_delay:
                wait_time = required_delay - elapsed
                logger.info(f"Rate limiting {site_name}: waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
            
            self.last_request_times[site_name] = time.time()

# Pre-configured rate limits for different sites
SITE_RATE_LIMITS = {
    'linkedin': {'min_delay': 5, 'max_delay': 15},
    'glassdoor': {'min_delay': 3, 'max_delay': 8},
    'indeed': {'min_delay': 2, 'max_delay': 6},
    'angellist': {'min_delay': 1, 'max_delay': 4},
    'company_careers': {'min_delay': 1, 'max_delay': 3},
    'remoteok': {'min_delay': 1, 'max_delay': 3}
}

def create_proxy_manager(custom_proxies=None):
    """Factory function to create proxy manager"""
    return ProxyManager(proxy_list=custom_proxies)

def create_rate_limiter():
    """Factory function to create rate limiter with site-specific limits"""
    return RateLimiter(per_site_limits=SITE_RATE_LIMITS)