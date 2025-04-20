from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Property:
    id: str
    source: str  # Which site this was scraped from
    url: str
    address: str
    city: str
    state: str
    zip_code: str
    price: float
    bedrooms: float
    bathrooms: float
    square_feet: Optional[float] = None
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    property_type: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    date_listed: Optional[datetime] = None
    date_scraped: datetime = datetime.now()
    
    def to_dict(self):
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'source': self.source,
            'url': self.url,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'price': self.price,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'square_feet': self.square_feet,
            'lot_size': self.lot_size,
            'year_built': self.year_built,
            'property_type': self.property_type,
            'description': self.description,
            'features': ','.join(self.features) if self.features else None,
            'image_urls': ','.join(self.image_urls) if self.image_urls else None,
            'date_listed': self.date_listed.isoformat() if self.date_listed else None,
            'date_scraped': self.date_scraped.isoformat()
        }
