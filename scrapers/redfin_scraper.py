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

class RedfinScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.redfin.com"
    
    def search(self, location: str, min_price: float, max_price: float) -> List[Property]:
        """Search for properties on Redfin with the given criteria"""
        properties = []
        
        # Format the location for the URL
        formatted_location = self._format_location(location)
        
        # Create the search URL
        search_url = f"{self.base_url}/city/{formatted_location}"
        
        # For Redfin, we'll use Selenium since it's heavily JavaScript-based
        driver = self._init_selenium()
        
        try:
            # Navigate to the search page
            driver.get(search_url)
            
            # Wait for the page to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".HomeCardContainer"))
            )
            
            # Apply price filter if needed
            if min_price > 0 or max_price < float('inf'):
                # This is where we would add code to interact with the Redfin price filters
                # For now, we'll just search the basic location
                pass
            
            # Get the page source and parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find all property cards
            property_cards = soup.select(".HomeCardContainer")
            
            for card in property_cards:
                try:
                    # Extract the price
                    price_elem = card.select_one(".homecardV2Price")
                    if not price_elem:
                        continue
                    
                    price_text = price_elem.text.strip()
                    price = float(re.sub(r'[^\d.]', '', price_text))
                    
                    # Check if price is within range
                    if price < min_price or price > max_price:
                        continue
                    
                    # Extract the address
                    address_elem = card.select_one(".homeAddressV2")
                    if not address_elem:
                        continue
                    
                    full_address = address_elem.text.strip()
                    address_parts = self._parse_address(full_address)
                    
                    # Extract the URL
                    link_elem = card.select_one("a.homeCardV2__")
                    if not link_elem:
                        continue
                    
                    property_url = link_elem.get('href')
                    if not property_url.startswith('http'):
                        property_url = self.base_url + property_url
                    
                    # Extract beds/baths/sqft
                    stats_elem = card.select_one(".HomeStatsV2")
                    beds, baths, sqft = 0, 0, None
                    
                    if stats_elem:
                        stats_text = stats_elem.text.strip()
                        beds, baths, sqft = self._parse_stats(stats_text)
                    
                    # Create property data dictionary
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
                        'source': 'redfin'
                    }
                    
                    # Generate a unique ID
                    property_id = self._generate_property_id(property_data)
                    
                    # Create the Property object
                    prop = Property(
                        id=property_id,
                        source='redfin',
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
                    print(f"Error parsing Redfin property card: {e}")
                    continue
                
        except Exception as e:
            print(f"Error searching Redfin: {e}")
        
        finally:
            # Clean up
            if self.driver:
                self.close()
        
        return properties
    
    def _format_location(self, location: str) -> str:
        """Format a location string for Redfin URL"""
        # Typically Redfin uses city-state format
        parts = location.split(',')
        
        if len(parts) >= 2:
            city = parts[0].strip().lower().replace(' ', '-')
            state = parts[1].strip().lower().replace(' ', '-')
            return f"{city}/{state}"
        else:
            # Just use the whole string
            return location.lower().replace(' ', '-').replace(',', '/')
    
    def _parse_address(self, address_text: str) -> Dict[str, str]:
        """Parse an address from Redfin"""
        parts = {'address': '', 'city': '', 'state': '', 'zip': ''}
        
        try:
            # Try to match a typical US address format
            pattern = r"(.*?),\s*(.*?),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)"
            match = re.match(pattern, address_text)
            
            if match:
                parts['address'] = match.group(1).strip()
                parts['city'] = match.group(2).strip()
                parts['state'] = match.group(3).strip()
                parts['zip'] = match.group(4).strip()
            else:
                # If we can't parse the full address, just store what we have
                parts['address'] = address_text
        except Exception:
            parts['address'] = address_text
            
        return parts
    
    def _parse_stats(self, stats_text: str) -> tuple:
        """Parse beds, baths, and square footage from stats text"""
        beds, baths, sqft = 0, 0, None
        
        try:
            # Try to extract beds
            beds_match = re.search(r'(\d+(?:\.\d+)?)\s*Beds?', stats_text, re.IGNORECASE)
            if beds_match:
                beds = float(beds_match.group(1))
            
            # Try to extract baths
            baths_match = re.search(r'(\d+(?:\.\d+)?)\s*Baths?', stats_text, re.IGNORECASE)
            if baths_match:
                baths = float(baths_match.group(1))
            
            # Try to extract square footage
            sqft_match = re.search(r'([\d,]+)\s*Sq\s*Ft', stats_text, re.IGNORECASE)
            if sqft_match:
                sqft = float(sqft_match.group(1).replace(',', ''))
        except Exception:
            pass
            
        return beds, baths, sqft
