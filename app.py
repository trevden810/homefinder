import argparse
import csv
import json
import sys
from typing import List, Dict, Any
import time
import os

from scrapers.zillow_scraper import ZillowScraper
from scrapers.realtor_scraper import RealtorScraper
from scrapers.redfin_scraper import RedfinScraper
from database.db_handler import DatabaseHandler
from models.property import Property
from config.settings import DEFAULT_LOCATION, DEFAULT_MIN_PRICE, DEFAULT_MAX_PRICE
from utils.helpers import format_price, format_address, validate_price_range

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Real Estate Property Scraper')
    parser.add_argument('--location', type=str, default=DEFAULT_LOCATION,
                        help=f'Location to search (default: {DEFAULT_LOCATION})')
    parser.add_argument('--min-price', type=float, default=DEFAULT_MIN_PRICE,
                        help=f'Minimum price (default: {DEFAULT_MIN_PRICE})')
    parser.add_argument('--max-price', type=float, default=DEFAULT_MAX_PRICE,
                        help=f'Maximum price (default: {DEFAULT_MAX_PRICE})')
    parser.add_argument('--sources', type=str, default='zillow,realtor,redfin',
                        help='Comma-separated list of sources to scrape (default: zillow,realtor,redfin)')
    parser.add_argument('--export', type=str, choices=['csv', 'json'], 
                        help='Export results to CSV or JSON file')
    parser.add_argument('--output', type=str, default='properties',
                        help='Output filename (without extension)')
    parser.add_argument('--filter-beds', type=float, default=None,
                        help='Filter results by minimum number of bedrooms')
    parser.add_argument('--filter-baths', type=float, default=None,
                        help='Filter results by minimum number of bathrooms')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit the number of results')
    
    return parser.parse_args()

def scrape_properties(location: str, min_price: float, max_price: float, sources: List[str]) -> List[Property]:
    """Scrape properties from all specified sources"""
    all_properties = []
    
    # Validate price range
    price_range = validate_price_range(min_price, max_price)
    min_price = price_range['min_price']
    max_price = price_range['max_price']
    
    # Initialize the database handler
    db = DatabaseHandler()
    
    # Scrape from Zillow if specified
    if 'zillow' in sources:
        print(f"Scraping Zillow for properties in {location} between {format_price(min_price)} and {format_price(max_price)}...")
        
        try:
            zillow = ZillowScraper()
            zillow_properties = zillow.search(location, min_price, max_price)
            
            print(f"Found {len(zillow_properties)} properties on Zillow")
            
            # Save to database
            for prop in zillow_properties:
                db.insert_property(prop)
                
            all_properties.extend(zillow_properties)
            
            # Clean up
            zillow.close()
            
        except Exception as e:
            print(f"Error scraping Zillow: {e}")
    
    # Scrape from Realtor.com if specified
    if 'realtor' in sources:
        print(f"Scraping Realtor.com for properties in {location} between {format_price(min_price)} and {format_price(max_price)}...")
        
        try:
            realtor = RealtorScraper()
            realtor_properties = realtor.search(location, min_price, max_price)
            
            print(f"Found {len(realtor_properties)} properties on Realtor.com")
            
            # Save to database
            for prop in realtor_properties:
                db.insert_property(prop)
                
            all_properties.extend(realtor_properties)
            
        except Exception as e:
            print(f"Error scraping Realtor.com: {e}")
    
    # Scrape from Redfin if specified
    if 'redfin' in sources:
        print(f"Scraping Redfin for properties in {location} between {format_price(min_price)} and {format_price(max_price)}...")
        
        try:
            redfin = RedfinScraper()
            redfin_properties = redfin.search(location, min_price, max_price)
            
            print(f"Found {len(redfin_properties)} properties on Redfin")
            
            # Save to database
            for prop in redfin_properties:
                db.insert_property(prop)
                
            all_properties.extend(redfin_properties)
            
            # Clean up
            redfin.close()
            
        except Exception as e:
            print(f"Error scraping Redfin: {e}")
    
    return all_properties

def export_properties(properties: List[Property], format_type: str, filename: str):
    """Export properties to the specified format"""
    if format_type == 'csv':
        filename = f"{filename}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Get all possible fields
            fieldnames = [
                'id', 'source', 'url', 'address', 'city', 'state', 'zip_code',
                'price', 'bedrooms', 'bathrooms', 'square_feet', 'lot_size',
                'year_built', 'property_type', 'description', 'features',
                'image_urls', 'date_listed', 'date_scraped'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for prop in properties:
                writer.writerow(prop.to_dict())
                
        print(f"Exported {len(properties)} properties to {filename}")
        
    elif format_type == 'json':
        filename = f"{filename}.json"
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            # Convert all properties to dictionaries
            property_dicts = [prop.to_dict() for prop in properties]
            
            json.dump(property_dicts, jsonfile, indent=2)
                
        print(f"Exported {len(properties)} properties to {filename}")

def display_properties(properties: List[Property], limit: int = None):
    """Display properties in a readable format"""
    if not properties:
        print("No properties found.")
        return
    
    # Apply limit if specified
    if limit and limit > 0:
        properties = properties[:limit]
    
    print(f"\nFound {len(properties)} properties:")
    print("-" * 80)
    
    for i, prop in enumerate(properties, 1):
        print(f"Property {i}:")
        print(f"Source: {prop.source.capitalize()}")
        print(f"Address: {prop.address}, {prop.city}, {prop.state} {prop.zip_code}")
        print(f"Price: {format_price(prop.price)}")
        print(f"Beds/Baths: {prop.bedrooms}/{prop.bathrooms}")
        
        if prop.square_feet:
            print(f"Square Feet: {prop.square_feet:,.0f}")
        
        print(f"URL: {prop.url}")
        print("-" * 80)

def filter_properties(properties: List[Property], min_beds: float = None, min_baths: float = None) -> List[Property]:
    """Filter properties by criteria"""
    result = properties
    
    if min_beds is not None:
        result = [p for p in result if p.bedrooms >= min_beds]
        
    if min_baths is not None:
        result = [p for p in result if p.bathrooms >= min_baths]
    
    return result

def main():
    """Main entry point"""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Get the list of sources
    sources = [s.strip().lower() for s in args.sources.split(',')]
    
    # Scrape properties
    properties = scrape_properties(
        location=args.location,
        min_price=args.min_price,
        max_price=args.max_price,
        sources=sources
    )
    
    # Apply filters
    filtered_properties = filter_properties(
        properties=properties,
        min_beds=args.filter_beds,
        min_baths=args.filter_baths
    )
    
    # Display properties
    display_properties(filtered_properties, args.limit)
    
    # Export if requested
    if args.export:
        export_properties(filtered_properties, args.export, args.output)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
