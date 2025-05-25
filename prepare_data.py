#!/usr/bin/env python3
"""
Data preparation script for MapLeads
Initializes the location database from ZIP code data
"""

import pandas as pd
import sqlite3
from pathlib import Path
import sys

def prepare_location_database():
    """Prepare the location database from uszips.csv"""
    
    data_dir = Path(__file__).parent / 'data'
    csv_path = data_dir / 'uszips.csv'
    db_path = data_dir / 'locations.db'
    
    if not csv_path.exists():
        print("❌ Error: uszips.csv not found in data directory")
        print("\nTo get ZIP code data:")
        print("1. Download from: https://simplemaps.com/data/us-zips")
        print("2. Place the uszips.csv file in the data/ directory")
        print("3. Run this script again")
        sys.exit(1)
    
    print("📍 Loading ZIP code data...")
    
    # Load CSV
    try:
        df = pd.read_csv(csv_path, dtype={'zip': str})
        print(f"✅ Loaded {len(df)} ZIP codes")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        sys.exit(1)
    
    # Rename columns to match our schema
    column_mapping = {
        'state_id': 'state',
        'county_name': 'county'
    }
    df = df.rename(columns=column_mapping)
    
    # Ensure required columns exist
    required_columns = ['zip', 'city', 'state', 'lat', 'lng', 'population']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Error: Missing required columns: {missing_columns}")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)
    
    # Create SQLite database
    print("💾 Creating location database...")
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Drop existing table if it exists
            conn.execute("DROP TABLE IF EXISTS locations")
            
            # Create table with indexes
            df.to_sql('locations', conn, if_exists='replace', index=False)
            
            # Create indexes for better performance
            print("📇 Creating indexes...")
            conn.execute('CREATE INDEX IF NOT EXISTS idx_state ON locations(state)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_population ON locations(population)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_city ON locations(city)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_zip ON locations(zip)')
            
            # Verify data
            count = conn.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
            print(f"✅ Database created with {count} locations")
            
            # Show sample data
            print("\n📊 Sample locations:")
            sample = conn.execute("""
                SELECT city, state, population 
                FROM locations 
                WHERE population > 100000 
                ORDER BY population DESC 
                LIMIT 5
            """).fetchall()
            
            for city, state, pop in sample:
                print(f"   {city}, {state} - Population: {pop:,}")
    
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)
    
    print("\n✅ Location database ready!")
    print(f"📁 Database saved to: {db_path}")

if __name__ == "__main__":
    print("MapLeads Data Preparation\n")
    prepare_location_database()
