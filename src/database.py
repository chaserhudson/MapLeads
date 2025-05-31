"""
Database management for MapLeads using SQLite
Simple, file-based database that requires no setup
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd

class Database:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection"""
        if db_path is None:
            data_dir = Path(__file__).parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / 'mapleads.db'
        
        self.db_path = db_path
        self.init_database()
        self._init_locations()
    
    def init_database(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS businesses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE,
                    category TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    latitude REAL,
                    longitude REAL,
                    website TEXT,
                    reviews TEXT,
                    rating REAL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source_url TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_phone ON businesses(phone)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON businesses(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_first_seen ON businesses(first_seen)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_city_state ON businesses(city, state)')
            
            # Scan history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    categories TEXT,
                    locations TEXT,
                    businesses_found INTEGER,
                    new_businesses INTEGER,
                    duration_seconds INTEGER
                )
            ''')
            
            conn.commit()
    
    def _init_locations(self):
        """Initialize location data from ZIP codes"""
        locations_db = Path(__file__).parent.parent / 'data' / 'locations.db'
        
        # Only create if it doesn't exist
        if not locations_db.exists():
            zip_csv = Path(__file__).parent.parent / 'data' / 'uszips.csv'
            
            if zip_csv.exists():
                # Load ZIP data into a separate SQLite table
                df = pd.read_csv(zip_csv, dtype={'zip': str})
                
                # Rename columns to match our needs
                df = df.rename(columns={
                    'state_id': 'state',
                    'county_name': 'county'
                })
                
                with sqlite3.connect(locations_db) as conn:
                    df.to_sql('locations', conn, if_exists='replace', index=False)
                    
                    # Create indexes
                    conn.execute('CREATE INDEX IF NOT EXISTS idx_state ON locations(state)')
                    conn.execute('CREATE INDEX IF NOT EXISTS idx_population ON locations(population)')
                    conn.execute('CREATE INDEX IF NOT EXISTS idx_city ON locations(city)')
    
    def business_exists(self, phone: str) -> bool:
        """Check if a business with this phone number already exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT 1 FROM businesses WHERE phone = ?', (phone,))
            return cursor.fetchone() is not None
    
    def add_business(self, business_data: Dict) -> int:
        """Add a new business to the database"""
        # Convert metadata dict to JSON string
        metadata = business_data.get('metadata', {})
        if isinstance(metadata, dict):
            metadata = json.dumps(metadata)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO businesses (
                    name, phone, category, address, city, state, zip_code,
                    latitude, longitude, website, reviews, rating, source_url, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                business_data.get('name'),
                business_data.get('phone'),
                business_data.get('category'),
                business_data.get('address'),
                business_data.get('city'),
                business_data.get('state'),
                business_data.get('zip_code'),
                business_data.get('latitude'),
                business_data.get('longitude'),
                business_data.get('website'),
                business_data.get('reviews'),
                business_data.get('rating'),
                business_data.get('source_url'),
                metadata
            ))
            conn.commit()
            return cursor.lastrowid
    
    def update_last_seen(self, phone: str):
        """Update the last_seen timestamp for a business"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'UPDATE businesses SET last_seen = CURRENT_TIMESTAMP WHERE phone = ?',
                (phone,)
            )
            conn.commit()
    
    def get_businesses_since_days(self, days: int) -> List[Dict]:
        """Get all businesses discovered in the last N days"""
        since_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM businesses 
                WHERE first_seen >= ? 
                ORDER BY first_seen DESC
            ''', (since_date,))
            
            rows = cursor.fetchall()
            
            # Convert to dict and parse dates
            results = []
            for row in rows:
                business = dict(row)
                # Parse timestamp strings to datetime objects
                if business.get('first_seen'):
                    business['first_seen'] = datetime.fromisoformat(business['first_seen'])
                if business.get('last_seen'):
                    business['last_seen'] = datetime.fromisoformat(business['last_seen'])
                results.append(business)
            
            return results
    
    def get_recent_businesses(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get the most recently discovered businesses"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM businesses 
                ORDER BY first_seen DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            
            # Convert to dict and parse dates
            results = []
            for row in rows:
                business = dict(row)
                # Parse timestamp strings to datetime objects
                if business.get('first_seen'):
                    business['first_seen'] = datetime.fromisoformat(business['first_seen'])
                if business.get('last_seen'):
                    business['last_seen'] = datetime.fromisoformat(business['last_seen'])
                results.append(business)
            
            return results
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Total businesses
            total = conn.execute('SELECT COUNT(*) FROM businesses').fetchone()[0]
            
            # New this week
            week_ago = datetime.now() - timedelta(days=7)
            new_week = conn.execute(
                'SELECT COUNT(*) FROM businesses WHERE first_seen >= ?',
                (week_ago,)
            ).fetchone()[0]
            
            # New this month
            month_ago = datetime.now() - timedelta(days=30)
            new_month = conn.execute(
                'SELECT COUNT(*) FROM businesses WHERE first_seen >= ?',
                (month_ago,)
            ).fetchone()[0]
            
            # Categories count
            categories = conn.execute(
                'SELECT COUNT(DISTINCT category) FROM businesses'
            ).fetchone()[0]
            
            return {
                'total_businesses': total,
                'new_this_week': new_week,
                'new_this_month': new_month,
                'categories_count': categories
            }
    
    def add_scan_record(self, categories: List[str], locations: Dict, 
                       businesses_found: int, new_businesses: int, 
                       duration_seconds: int):
        """Record a scan in history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO scan_history (
                    categories, locations, businesses_found, 
                    new_businesses, duration_seconds
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                json.dumps(categories),
                json.dumps(locations),
                businesses_found,
                new_businesses,
                duration_seconds
            ))
            conn.commit()
    
    def get_locations_for_filters(self, states: Optional[List[str]] = None,
                                 cities: Optional[List[str]] = None,
                                 min_population: int = 0) -> List[Dict]:
        """Get locations matching the specified filters"""
        locations_db = Path(__file__).parent.parent / 'data' / 'locations.db'
        
        if not locations_db.exists():
            # Fallback to some default locations
            return [
                {'city': 'New York', 'state': 'NY', 'lat': 40.7128, 'lng': -74.0060},
                {'city': 'Los Angeles', 'state': 'CA', 'lat': 34.0522, 'lng': -118.2437},
                {'city': 'Chicago', 'state': 'IL', 'lat': 41.8781, 'lng': -87.6298},
            ]
        
        with sqlite3.connect(locations_db) as conn:
            conn.row_factory = sqlite3.Row
            
            # Build query
            query = 'SELECT * FROM locations WHERE population >= ?'
            params = [min_population]
            
            if states:
                placeholders = ','.join(['?' for _ in states])
                query += f' AND state IN ({placeholders})'
                params.extend(states)
            
            if cities:
                placeholders = ','.join(['?' for _ in cities])
                query += f' AND city IN ({placeholders})'
                params.extend(cities)
            
            query += ' ORDER BY population DESC'
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
