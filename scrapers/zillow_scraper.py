import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import urllib.parse

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scrapers.base_scraper import BaseScraper
from models.property import Property

class ZillowScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.zillow.com"

    def search(self, location: str, min_price: float, max_price: float) -> List[Property]:
        """Search for properties on Zillow with the given criteria"""
        properties = []

        # Encode the location for the URL
        encoded_location = urllib.parse.quote(location)

        # Create the search URL
        search_url = f"{self.base_url}/homes/for_sale/{encoded_location}/{int(min_price)}-{int(max_price)}_price/"

        # Try to use Selenium if available, otherwise fall back to requests
        if self.is_selenium_available():
            # For Zillow, we'll use Selenium since it's heavily JavaScript-based
            driver = self._init_selenium()
            if driver:
                try:
                    driver.get(search_url)

                    # Wait for the search results to load
                    try:
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".property-card-data"))
                        )
                    except Exception as e:
                        print(f"Error waiting for Zillow results to load: {e}")
                        # If we timeout waiting for elements, still try to parse what we have

                    # Get the page source and parse with BeautifulSoup
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                except Exception as e:
                    print(f"Error using Selenium for Zillow: {e}")
                    # Fall back to requests
                    response = self._make_request(search_url)
                    if response:
                        soup = BeautifulSoup(response.text, 'html.parser')
                    else:
                        return properties
            else:
                # Fall back to requests
                response = self._make_request(search_url)
                if response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                else:
                    return properties
        else:
            # Fall back to requests
            response = self._make_request(search_url)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
            else:
                return properties

        # Find all property cards
        property_cards = soup.select("div[data-test='property-card']")

        for card in property_cards:
            try:
                # Extract basic information
                price_elem = card.select_one(".property-card-price")
                address_elem = card.select_one("address")
                link_elem = card.select_one("a.property-card-link")
                details_elem = card.select_one(".property-card-details")

                if not all([price_elem, address_elem, link_elem, details_elem]):
                    continue

                # Parse the data
                price_text = price_elem.text.strip()
                price = float(re.sub(r'[^\d.]', '', price_text))

                full_address = address_elem.text.strip()
                address_parts = self._parse_address(full_address)

                # Get the property URL
                property_url = link_elem.get('href')
                if not property_url.startswith('http'):
                    property_url = self.base_url + property_url

                # Extract beds/baths/sqft
                details_text = details_elem.text.strip()
                beds, baths, sqft = self._parse_details(details_text)

                # Create a property object
                property_data = {
                    'address': address_parts['address'],
                    'city': address_parts['city'],
                    'state': address_parts['state'],
                    'zip_code': address_parts['zip'],
                    'price': price,
                    'bedrooms': beds,
                    'bathrooms': baths,
                    'square_feet': sqft,
                    'url': property_url,
                    'source': 'zillow'
                }

                # Generate a unique ID
                property_id = self._generate_property_id(property_data)

                # Create the Property object
                prop = Property(
                    id=property_id,
                    source='zillow',
                    url=property_url,
                    address=address_parts['address'],
                    city=address_parts['city'],
                    state=address_parts['state'],
                    zip_code=address_parts['zip'],
                    price=price,
                    bedrooms=beds,
                    bathrooms=baths,
                    square_feet=sqft,
                    date_scraped=datetime.now()
                )

                properties.append(prop)

            except Exception as e:
                print(f"Error parsing property card: {e}")
                continue

        return properties

    def _parse_address(self, address_text: str) -> Dict[str, str]:
        """Parse an address into components"""
        # Example: "123 Main St, Anytown, CA 12345"
        parts = {'address': '', 'city': '', 'state': '', 'zip': ''}

        if not address_text:
            return parts

        try:
            # First try to match a typical US address format
            pattern = r"(.*?),\s*(.*?),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)"
            match = re.match(pattern, address_text)

            if match:
                parts['address'] = match.group(1).strip()
                parts['city'] = match.group(2).strip()
                parts['state'] = match.group(3).strip()
                parts['zip'] = match.group(4).strip()
            else:
                # Try a simpler pattern
                pattern = r"(.*?),\s*(.*?),\s*([A-Z]{2})"
                match = re.match(pattern, address_text)
                if match:
                    parts['address'] = match.group(1).strip()
                    parts['city'] = match.group(2).strip()
                    parts['state'] = match.group(3).strip()
                else:
                    # If we can't parse it, just store the whole address
                    parts['address'] = address_text
        except Exception as e:
            print(f"Error parsing address '{address_text}': {e}")
            parts['address'] = address_text or ''

        return parts

    def _parse_details(self, details_text: str) -> tuple:
        """Parse beds, baths, and square footage from details text"""
        beds, baths, sqft = 0, 0, None

        if not details_text:
            return beds, baths, sqft

        try:
            # Try to extract beds
            beds_match = re.search(r'(\d+(?:\.\d+)?)\s*bd', details_text)
            if beds_match:
                beds = float(beds_match.group(1))

            # Try to extract baths
            baths_match = re.search(r'(\d+(?:\.\d+)?)\s*ba', details_text)
            if baths_match:
                baths = float(baths_match.group(1))

            # Try to extract square footage
            sqft_match = re.search(r'([\d,]+)\s*sqft', details_text)
            if sqft_match:
                sqft = float(sqft_match.group(1).replace(',', ''))
        except Exception as e:
            print(f"Error parsing details '{details_text}': {e}")

        return beds, baths, sqft
