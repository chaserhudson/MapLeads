#!/usr/bin/env python3
"""
Debug database to see what's actually in there
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.database import Database
    
    print("🔍 MapLeads Database Debug")
    print("=" * 40)
    
    db = Database()
    
    # Check total businesses
    stats = db.get_statistics()
    print(f"📊 Total businesses in database: {stats['total_businesses']}")
    print(f"📊 New this week: {stats['new_this_week']}")
    print(f"📊 New this month: {stats['new_this_month']}")
    print(f"📊 Categories: {stats['categories_count']}")
    print("")
    
    # Get recent businesses
    print("🕒 Recent businesses (last 10):")
    recent = db.get_recent_businesses(10)
    
    if recent:
        for i, business in enumerate(recent, 1):
            print(f"{i}. {business['name']} - {business['city']}, {business['state']}")
            print(f"   Phone: {business['phone']}")
            print(f"   First seen: {business['first_seen']}")
            print(f"   Category: {business['category']}")
            print("")
    else:
        print("❌ No businesses found in get_recent_businesses()")
    
    # Check raw database content
    print("🗃️ Raw database check:")
    import sqlite3
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM businesses")
        count = cursor.fetchone()[0]
        print(f"Raw count: {count} businesses")
        
        if count > 0:
            cursor = conn.execute("SELECT name, city, state, first_seen FROM businesses ORDER BY first_seen DESC LIMIT 5")
            rows = cursor.fetchall()
            print("Sample businesses:")
            for row in rows:
                print(f"  {row[0]} - {row[1]}, {row[2]} (first_seen: {row[3]})")
        
        # Check if first_seen column has valid dates
        cursor = conn.execute("SELECT first_seen FROM businesses WHERE first_seen IS NOT NULL LIMIT 5")
        dates = cursor.fetchall()
        print(f"Sample first_seen values: {dates}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()