import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import urllib.parse

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from models.property import Property

class RealtorScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.realtor.com"

    def search(self, location: str, min_price: float, max_price: float) -> List[Property]:
        """Search for properties on Realtor.com with the given criteria"""
        properties = []

        # Format the location for the URL (city-state format)
        formatted_location = self._format_location(location)

        # Create the search URL - use a more reliable format
        if min_price > 0 and max_price < float('inf'):
            search_url = f"{self.base_url}/homes-for-sale/{formatted_location}"
            price_param = f"price-{int(min_price)}-{int(max_price)}"
            if "?" in search_url:
                search_url += f"&{price_param}"
            else:
                search_url += f"?{price_param}"
        else:
            search_url = f"{self.base_url}/homes-for-sale/{formatted_location}"

        print(f"Searching Realtor.com with URL: {search_url}")

        # Make the request
        response = self._make_request(search_url)
        if not response:
            # Try an alternative URL format if the first one fails
            alt_search_url = f"{self.base_url}/realestateandhomes-search/{formatted_location}"
            print(f"Trying alternative Realtor.com URL: {alt_search_url}")
            response = self._make_request(alt_search_url)
            if not response:
                return properties

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the property cards - Realtor.com uses data attributes
        property_cards = soup.select("div[data-testid='property-card']")

        for card in property_cards:
            try:
                # Extract the price
                price_elem = card.select_one("span[data-testid='property-price']")
                if not price_elem:
                    continue

                price_text = price_elem.text.strip()
                price = float(re.sub(r'[^\d.]', '', price_text))

                # Extract the address
                address_elem = card.select_one("div[data-testid='property-address']")
                if not address_elem:
                    continue

                full_address = address_elem.text.strip()
                address_parts = self._parse_address(full_address)

                # Extract the URL
                link_elem = card.select_one("a[data-testid='property-anchor']")
                if not link_elem:
                    continue

                property_url = link_elem.get('href')
                if not property_url.startswith('http'):
                    property_url = self.base_url + property_url

                # Extract beds/baths/sqft
                beds_elem = card.select_one("li[data-testid='property-meta-beds']")
                baths_elem = card.select_one("li[data-testid='property-meta-baths']")
                sqft_elem = card.select_one("li[data-testid='property-meta-sqft']")

                beds = float(beds_elem.select_one("span").text) if beds_elem else 0
                baths = float(baths_elem.select_one("span").text) if baths_elem else 0

                sqft = None
                if sqft_elem:
                    sqft_text = sqft_elem.select_one("span").text
                    sqft_match = re.search(r'([\d,]+)', sqft_text)
                    if sqft_match:
                        sqft = float(sqft_match.group(1).replace(',', ''))

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
                    'source': 'realtor'
                }

                # Generate a unique ID
                property_id = self._generate_property_id(property_data)

                # Create the Property object
                prop = Property(
                    id=property_id,
                    source='realtor',
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
                print(f"Error parsing Realtor.com property card: {e}")
                continue

        return properties

    def _format_location(self, location: str) -> str:
        """Format a location string for Realtor.com URL"""
        # Attempt to extract city and state
        parts = location.split(',')

        if len(parts) >= 2:
            city = parts[0].strip().lower().replace(' ', '-')
            state = parts[1].strip().lower().replace(' ', '-')

            # Handle common state abbreviations
            state_abbr_map = {
                'alabama': 'al', 'alaska': 'ak', 'arizona': 'az', 'arkansas': 'ar',
                'california': 'ca', 'colorado': 'co', 'connecticut': 'ct', 'delaware': 'de',
                'florida': 'fl', 'georgia': 'ga', 'hawaii': 'hi', 'idaho': 'id',
                'illinois': 'il', 'indiana': 'in', 'iowa': 'ia', 'kansas': 'ks',
                'kentucky': 'ky', 'louisiana': 'la', 'maine': 'me', 'maryland': 'md',
                'massachusetts': 'ma', 'michigan': 'mi', 'minnesota': 'mn', 'mississippi': 'ms',
                'missouri': 'mo', 'montana': 'mt', 'nebraska': 'ne', 'nevada': 'nv',
                'new-hampshire': 'nh', 'new-jersey': 'nj', 'new-mexico': 'nm', 'new-york': 'ny',
                'north-carolina': 'nc', 'north-dakota': 'nd', 'ohio': 'oh', 'oklahoma': 'ok',
                'oregon': 'or', 'pennsylvania': 'pa', 'rhode-island': 'ri', 'south-carolina': 'sc',
                'south-dakota': 'sd', 'tennessee': 'tn', 'texas': 'tx', 'utah': 'ut',
                'vermont': 'vt', 'virginia': 'va', 'washington': 'wa', 'west-virginia': 'wv',
                'wisconsin': 'wi', 'wyoming': 'wy'
            }

            # If state is a full name, convert to abbreviation
            if state in state_abbr_map:
                state = state_abbr_map[state]

            # If state is already an abbreviation (2 chars), keep it
            if len(state) == 2:
                return f"{city}-{state}"
            else:
                return f"{city}-{state}"
        else:
            # Just use the whole string
            return location.lower().replace(' ', '-').replace(',', '')

    def _parse_address(self, address_text: str) -> Dict[str, str]:
        """Parse an address from Realtor.com"""
        parts = {'address': '', 'city': '', 'state': '', 'zip': ''}

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
                # If it's just a street address, store that
                parts['address'] = address_text
        except Exception:
            parts['address'] = address_text

        return parts
