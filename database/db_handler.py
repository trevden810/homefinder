import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from config.settings import DATABASE_PATH
from models.property import Property

class DatabaseHandler:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self._ensure_db_exists()
        
    def _ensure_db_exists(self):
        """Create the database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create properties table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            url TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            price REAL NOT NULL,
            bedrooms REAL NOT NULL,
            bathrooms REAL NOT NULL,
            square_feet REAL,
            lot_size REAL,
            year_built INTEGER,
            property_type TEXT,
            description TEXT,
            features TEXT,
            image_urls TEXT,
            date_listed TEXT,
            date_scraped TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_property(self, property_data: Property) -> bool:
        """Insert a new property or update if it already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = property_data.to_dict()
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data.keys()])
        values = tuple(data.values())
        
        try:
            cursor.execute(f'''
            INSERT OR REPLACE INTO properties ({columns})
            VALUES ({placeholders})
            ''', values)
            
            conn.commit()
            result = True
        except Exception as e:
            print(f"Error inserting property: {e}")
            conn.rollback()
            result = False
        finally:
            conn.close()
            
        return result
    
    def get_properties(self, 
                      location: Optional[str] = None, 
                      min_price: Optional[float] = None, 
                      max_price: Optional[float] = None, 
                      min_beds: Optional[float] = None,
                      min_baths: Optional[float] = None) -> List[Dict[str, Any]]:
        """Retrieve properties with optional filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM properties WHERE 1=1"
        params = []
        
        if location:
            query += " AND (city LIKE ? OR state LIKE ? OR zip_code LIKE ?)"
            params.extend([f"%{location}%", f"%{location}%", f"%{location}%"])
            
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)
            
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
            
        if min_beds is not None:
            query += " AND bedrooms >= ?"
            params.append(min_beds)
            
        if min_baths is not None:
            query += " AND bathrooms >= ?"
            params.append(min_baths)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            data = dict(row)
            
            # Convert string lists back to actual lists
            if data['features']:
                data['features'] = data['features'].split(',')
            
            if data['image_urls']:
                data['image_urls'] = data['image_urls'].split(',')
                
            result.append(data)
        
        conn.close()
        return result
