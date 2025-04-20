import re
from typing import Dict, Any, List

def format_price(price: float) -> str:
    """Format a price as currency"""
    return f"${price:,.2f}"

def format_address(property_data: Dict[str, Any]) -> str:
    """Format a complete address from components"""
    parts = [
        property_data.get('address', ''),
        property_data.get('city', ''),
        property_data.get('state', ''),
        property_data.get('zip_code', '')
    ]
    
    # Filter out empty parts
    parts = [p for p in parts if p]
    
    # Join with commas
    return f"{parts[0]}, {', '.join(parts[1:])}" if parts else ""

def clean_text(text: str) -> str:
    """Clean text by removing excessive whitespace"""
    if not text:
        return ""
    
    # Replace all whitespace with a single space
    return re.sub(r'\s+', ' ', text).strip()

def extract_zip_code(text: str) -> str:
    """Extract a ZIP code from text"""
    zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
    match = re.search(zip_pattern, text)
    
    return match.group(0) if match else ""

def validate_price_range(min_price: float, max_price: float) -> Dict[str, float]:
    """Validate and adjust price range if needed"""
    result = {
        'min_price': min_price if min_price >= 0 else 0,
        'max_price': max_price if max_price > 0 else 1000000
    }
    
    # Ensure min_price is less than max_price
    if result['min_price'] >= result['max_price']:
        result['min_price'] = 0
    
    return result
