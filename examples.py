#!/usr/bin/env python3
"""
Example script showing how to use MapLeads programmatically
"""

from src.database import Database
from src.scraper import MapLeadsScraper

def find_new_restaurants_in_texas():
    """Example: Find new restaurants in major Texas cities"""
    
    # Initialize database
    db = Database()
    
    # Create scraper
    scraper = MapLeadsScraper(db, headless=True)
    
    # Configuration for Texas restaurants
    config = {
        'monitoring': {
            'categories': ['restaurant', 'cafe', 'food truck'],
            'locations': {
                'states': ['TX'],
                'cities': None,
                'min_population': 100000  # Major cities only
            },
            'max_urls': 50
        }
    }
    
    # Run scan
    print("🔍 Searching for new restaurants in Texas...")
    new_businesses = scraper.scan(config['monitoring'])
    
    if new_businesses:
        print(f"\n✅ Found {len(new_businesses)} new restaurants!")
        
        # Display results
        for biz in new_businesses[:5]:  # Show first 5
            print(f"\n📍 {biz['name']}")
            print(f"   Phone: {biz['phone']}")
            print(f"   Category: {biz['category']}")
            print(f"   Reviews: {biz['reviews']}")
            if biz.get('website'):
                print(f"   Website: {biz['website']}")
    else:
        print("No new restaurants found in this scan.")

def find_new_gyms_without_reviews():
    """Example: Find brand new gyms (no reviews yet)"""
    
    db = Database()
    scraper = MapLeadsScraper(db, headless=True)
    
    # Configuration
    config = {
        'monitoring': {
            'categories': ['gym', 'fitness center', 'yoga studio'],
            'locations': {
                'states': ['CA', 'NY', 'FL'],
                'min_population': 50000
            },
            'max_urls': 30
        }
    }
    
    # Notification config with filter for businesses without reviews
    notification_config = {
        'notifications': {
            'filters': {
                'only_without_reviews': True  # Only new businesses
            }
        }
    }
    
    print("🏋️ Searching for brand new gyms...")
    new_businesses = scraper.scan(config['monitoring'])
    
    # Filter businesses without reviews (new businesses)
    filtered = [b for b in new_businesses if b.get('reviews', '').lower() in ['no reviews', '']]
    
    if filtered:
        print(f"\n✅ Found {len(filtered)} brand new gyms with no reviews yet!")
        for gym in filtered:
            print(f"\n🆕 {gym['name']} - {gym['city']}, {gym['state']}")
            print(f"   Phone: {gym['phone']}")

def monitor_specific_city():
    """Example: Monitor all new businesses in a specific city"""
    
    db = Database()
    scraper = MapLeadsScraper(db, headless=True)
    
    config = {
        'monitoring': {
            'categories': ['restaurant', 'store', 'service'],
            'locations': {
                'cities': ['Austin'],
                'states': ['TX']
            },
            'max_urls': 20
        }
    }
    
    print("🌆 Monitoring new businesses in Austin, TX...")
    new_businesses = scraper.scan(config['monitoring'])
    
    # Group by category
    by_category = {}
    for biz in new_businesses:
        cat = biz.get('category', 'Unknown')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(biz)
    
    # Show summary
    print(f"\n📊 New businesses by category:")
    for category, businesses in by_category.items():
        print(f"   {category}: {len(businesses)} new")

if __name__ == "__main__":
    print("MapLeads Examples\n")
    print("1. Find new restaurants in Texas")
    print("2. Find brand new gyms (no reviews)")
    print("3. Monitor specific city")
    
    choice = input("\nSelect example (1-3): ")
    
    if choice == "1":
        find_new_restaurants_in_texas()
    elif choice == "2":
        find_new_gyms_without_reviews()
    elif choice == "3":
        monitor_specific_city()
    else:
        print("Invalid choice")
