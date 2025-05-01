import time
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from config.settings import USER_AGENT, REQUEST_TIMEOUT, REQUEST_DELAY
from models.property import Property

class BaseScraper(ABC):
    def __init__(self):
        self.session = self._init_session()
        self.driver = None

    def _init_session(self) -> requests.Session:
        """Initialize a requests session with headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        return session

    def _init_selenium(self) -> Optional[webdriver.Chrome]:
        """Initialize Selenium WebDriver for JavaScript-heavy sites"""
        if self.driver is None:
            try:
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument(f"user-agent={USER_AGENT}")

                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                print(f"Failed to initialize Selenium: {e}")
                print("Falling back to requests-only mode")
                self.driver = None

        return self.driver

    def is_selenium_available(self) -> bool:
        """Check if Selenium/Chrome is available"""
        try:
            driver = self._init_selenium()
            return driver is not None
        except:
            return False

    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make an HTTP request with error handling and rate limiting"""
        try:
            time.sleep(REQUEST_DELAY)  # Rate limiting
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error for {url}: {e}")
            return None

    def _generate_property_id(self, property_data: Dict[str, Any]) -> str:
        """Generate a unique ID for a property based on its data"""
        id_string = f"{property_data.get('address', '')}-{property_data.get('city', '')}-{property_data.get('zip_code', '')}"
        return hashlib.md5(id_string.encode()).hexdigest()

    def close(self):
        """Close any open resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    @abstractmethod
    def search(self, location: str, min_price: float, max_price: float) -> List[Property]:
        """Search for properties with the given criteria"""
        pass
