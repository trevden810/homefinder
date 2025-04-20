from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import tempfile
from datetime import datetime
import csv

from scrapers.zillow_scraper import ZillowScraper
from scrapers.realtor_scraper import RealtorScraper
from scrapers.redfin_scraper import RedfinScraper
from database.db_handler import DatabaseHandler
from models.property import Property
from config.settings import DEFAULT_LOCATION, DEFAULT_MIN_PRICE, DEFAULT_MAX_PRICE
from utils.helpers import format_price, format_address, validate_price_range

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Create templates directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'), exist_ok=True)

# Global variable to store the latest search results
current_properties = []

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle property search requests"""
    global current_properties
    
    # Get search parameters
    data = request.json
    location = data.get('location', DEFAULT_LOCATION)
    min_price = float(data.get('minPrice', DEFAULT_MIN_PRICE))
    max_price = float(data.get('maxPrice', DEFAULT_MAX_PRICE))
    min_beds = float(data.get('bedrooms', 0)) if data.get('bedrooms') else None
    min_baths = float(data.get('bathrooms', 0)) if data.get('bathrooms') else None
    sources = data.get('sources', ['zillow', 'realtor', 'redfin'])
    
    # Validate price range
    price_range = validate_price_range(min_price, max_price)
    min_price = price_range['min_price']
    max_price = price_range['max_price']
    
    # Initialize scrapers and database
    properties = []
    db = DatabaseHandler()
    
    try:
        # Scrape from each selected source
        if 'zillow' in sources:
            try:
                zillow = ZillowScraper()
                zillow_properties = zillow.search(location, min_price, max_price)
                
                # Save to database
                for prop in zillow_properties:
                    db.insert_property(prop)
                    
                properties.extend(zillow_properties)
                zillow.close()
                
            except Exception as e:
                print(f"Error scraping Zillow: {e}")
        
        if 'realtor' in sources:
            try:
                realtor = RealtorScraper()
                realtor_properties = realtor.search(location, min_price, max_price)
                
                # Save to database
                for prop in realtor_properties:
                    db.insert_property(prop)
                    
                properties.extend(realtor_properties)
                
            except Exception as e:
                print(f"Error scraping Realtor.com: {e}")
        
        if 'redfin' in sources:
            try:
                redfin = RedfinScraper()
                redfin_properties = redfin.search(location, min_price, max_price)
                
                # Save to database
                for prop in redfin_properties:
                    db.insert_property(prop)
                    
                properties.extend(redfin_properties)
                redfin.close()
                
            except Exception as e:
                print(f"Error scraping Redfin: {e}")
        
        # Filter properties
        filtered_properties = properties
        
        if min_beds is not None:
            filtered_properties = [p for p in filtered_properties if p.bedrooms >= min_beds]
            
        if min_baths is not None:
            filtered_properties = [p for p in filtered_properties if p.bathrooms >= min_baths]
        
        # Store results for export
        current_properties = filtered_properties
        
        # Convert to dictionaries for JSON response
        property_dicts = [prop.to_dict() for prop in filtered_properties]
        
        return jsonify({
            'success': True,
            'count': len(property_dicts),
            'properties': property_dicts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/export/<format_type>')
def export(format_type):
    """Export properties to CSV or JSON"""
    global current_properties
    
    if not current_properties:
        return jsonify({
            'success': False,
            'error': 'No properties to export. Perform a search first.'
        })
    
    try:
        if format_type == 'csv':
            # Create a temp file
            fd, path = tempfile.mkstemp(suffix='.csv')
            
            with os.fdopen(fd, 'w', newline='', encoding='utf-8') as csvfile:
                # Get all possible fields
                fieldnames = [
                    'id', 'source', 'url', 'address', 'city', 'state', 'zip_code',
                    'price', 'bedrooms', 'bathrooms', 'square_feet', 'lot_size',
                    'year_built', 'property_type', 'description', 'features',
                    'image_urls', 'date_listed', 'date_scraped'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for prop in current_properties:
                    writer.writerow(prop.to_dict())
            
            return send_file(path, as_attachment=True, download_name=f'properties_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            
        elif format_type == 'json':
            # Create a temp file
            fd, path = tempfile.mkstemp(suffix='.json')
            
            with os.fdopen(fd, 'w', encoding='utf-8') as jsonfile:
                # Convert all properties to dictionaries
                property_dicts = [prop.to_dict() for prop in current_properties]
                
                json.dump(property_dicts, jsonfile, indent=2)
            
            return send_file(path, as_attachment=True, download_name=f'properties_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported export format: {format_type}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Export error: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
