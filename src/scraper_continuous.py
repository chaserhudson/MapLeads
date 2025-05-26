"""
Main scraper module for MapLeads - Continuous Processing Version
Handles Google Maps scraping with Selenium
"""

import re
import time
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

from .database import Database

# Phone number cleaning
PHONE_TRANSLATION_TABLE = str.maketrans({"(": None, ")": None, " ": None, "-": None})

# JavaScript for auto-scrolling
JS_SCROLL_SCRIPT = """
function scroll() {
    const elements = document.querySelectorAll("*");
    for (let i = 0; i < elements.length; i++) {
        if (elements[i].scrollHeight > elements[i].offsetHeight) {
            elements[i].scrollTop = elements[i].scrollHeight;
        }
    }
    
    const targetPhrase = "You've reached the end of the list.";
    if (document.documentElement.innerHTML.includes(targetPhrase)) {
        clearInterval(intervalId);
    }
}

const intervalId = setInterval(scroll, 500);
"""

class MapLeadsScraper:
    def __init__(self, database: Database, headless: bool = True):
        """Initialize the scraper"""
        self.db = database
        self.headless = headless
        self.driver = None
        self.stats = {
            'urls_processed': 0,
            'businesses_found': 0,
            'new_businesses': 0,
            'existing_businesses': 0,
            'total_cycles': 0
        }
        self.current_position = {'location_idx': 0}
    
    def setup_driver(self) -> bool:
        """Initialize Chrome driver"""
        try:
            options = ChromeOptions()
            
            # Performance optimizations
            options.add_argument("--disable-images")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            
            if self.headless:
                options.add_argument("--headless")
            
            # Anti-detection
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            return False
    
    def continuous_scan(self, monitoring_config: Dict) -> None:
        """Run continuous scanning through all locations"""
        if not self.setup_driver():
            raise Exception("Failed to setup Chrome driver")
        
        try:
            category = monitoring_config['category']  # Single category
            locations_config = monitoring_config['locations']
            batch_size = monitoring_config.get('batch_size', 10)  # Process 10 locations at a time
            
            # Get all locations once
            all_locations = self.db.get_locations_for_filters(
                states=locations_config.get('states'),
                cities=locations_config.get('cities'),
                min_population=locations_config.get('min_population', 0)
            )
            
            if not all_locations:
                print("No locations found matching criteria")
                return
            
            print(f"Found {len(all_locations)} locations to monitor")
            print(f"Monitoring category: {category}")
            print(f"Total locations to check: {len(all_locations)}")
            
            while True:  # Continuous loop
                cycle_start = datetime.now()
                
                print(f"\n📍 Processing category: {category}")
                category_formatted = category.replace(' ', '+')
                
                # Process all locations for this category
                for loc_idx in range(0, len(all_locations), batch_size):
                    batch_locations = all_locations[loc_idx:loc_idx + batch_size]
                    
                    # Show progress
                    progress = (loc_idx / len(all_locations)) * 100
                    print(f"Progress: {progress:.1f}% - Processing {len(batch_locations)} locations "
                          f"({loc_idx + 1}-{min(loc_idx + batch_size, len(all_locations))} "
                          f"of {len(all_locations)})")
                    
                    # Process batch
                    for location in batch_locations:
                        url = (
                            f"https://www.google.com/maps/search/{category_formatted}/@"
                            f"{location['lat']},{location['lng']},13z"
                        )
                        
                        try:
                            businesses = self._scrape_url(url)
                            new_count = 0
                            
                            # Check each business
                            for business in businesses:
                                if not business.get('phone'):
                                    continue
                                
                                # Add location info
                                business['city'] = location.get('city', 'Unknown')
                                business['state'] = location.get('state', 'Unknown')
                                business['zip_code'] = location.get('zip', 'Unknown')
                                
                                if self.db.business_exists(business['phone']):
                                    self.db.update_last_seen(business['phone'])
                                    self.stats['existing_businesses'] += 1
                                else:
                                    # New business found!
                                    business_id = self.db.add_business(business)
                                    business['id'] = business_id
                                    self.stats['new_businesses'] += 1
                                    new_count += 1
                                    
                                    # Notify immediately if configured
                                    if hasattr(self, 'notifier'):
                                        self.notifier.send_notifications([business])
                            
                            if new_count > 0:
                                print(f"  ✨ Found {new_count} new businesses in {location['city']}, {location['state']}")
                            
                        except Exception as e:
                            print(f"  ❌ Error processing {location['city']}: {e}")
                        
                        # Small delay between requests
                        time.sleep(random.uniform(1, 3))
                        
                    # Save position after each batch
                    self.current_position = {'location_idx': loc_idx}
                    self._save_progress()
                
                # Completed full cycle
                self.stats['total_cycles'] += 1
                cycle_duration = (datetime.now() - cycle_start).total_seconds() / 60
                
                print(f"\n✅ Completed full cycle #{self.stats['total_cycles']}")
                print(f"   Duration: {cycle_duration:.1f} minutes")
                print(f"   Total new businesses found: {self.stats['new_businesses']}")
                print(f"   Starting next cycle...\n")
                
                # Record cycle completion
                self.db.add_scan_record(
                    categories=[category],  # Convert to list for compatibility
                    locations=locations_config,
                    businesses_found=self.stats['businesses_found'],
                    new_businesses=self.stats['new_businesses'],
                    duration_seconds=int(cycle_duration * 60)
                )
                
                # Optional: Add a delay between cycles
                time.sleep(60)  # 1 minute pause between cycles
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopping continuous scan...")
            self._save_progress()
        finally:
            self.cleanup()
    
    def _save_progress(self):
        """Save current progress to resume later"""
        progress_data = {
            'position': self.current_position,
            'stats': self.stats,
            'timestamp': datetime.now().isoformat()
        }
        # Could save to file or database
        # For now, just log it
        print(f"Progress saved at location {self.current_position['location_idx']}")
    
    def _scrape_url(self, url: str) -> List[Dict]:
        """Scrape a single Google Maps URL"""
        businesses = []
        
        try:
            self.driver.get(url)
            self.stats['urls_processed'] += 1
            
            # Wait for initial load
            time.sleep(3)
            
            # Start auto-scrolling
            self.driver.execute_script(JS_SCROLL_SCRIPT)
            
            # Wait for results
            max_wait = 20
            for _ in range(max_wait):
                time.sleep(1)
                if "the end of the list" in self.driver.page_source.lower():
                    break
            
            # Extract business cards
            cards = self.driver.find_elements(
                By.XPATH, 
                '//div[contains(@jsaction, "mouseover")]'
            )
            
            for card in cards:
                try:
                    business = self._parse_business_card(card, url)
                    if business:
                        businesses.append(business)
                        self.stats['businesses_found'] += 1
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        
        return businesses
    
    def _parse_business_card(self, card, source_url: str) -> Optional[Dict]:
        """Parse a business card element"""
        try:
            card_text = card.text
            
            # Extract phone number
            phone_match = re.search(r'\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}', card_text)
            if not phone_match:
                return None
            
            phone = phone_match.group().translate(PHONE_TRANSLATION_TABLE)
            
            # Split into lines
            lines = card_text.split('\n')
            if len(lines) < 3:
                return None
            
            name = lines[0].strip()
            reviews = lines[1].strip()
            category = lines[2].strip()
            
            # Clean category
            if '·' in category:
                category = category.split('·')[0].strip()
            
            # Extract rating
            rating = None
            rating_match = re.match(r'^(\d\.\d)', reviews)
            if rating_match:
                rating = float(rating_match.group(1))
            
            # Try to get website
            website = None
            try:
                website_div = card.find_element(By.XPATH, ".//div[contains(text(), 'Website')]")
                parent_div = website_div.find_element(By.XPATH, '..')
                website = parent_div.get_attribute('href')
            except NoSuchElementException:
                pass
            
            # Extract location from URL
            location_data = self._extract_location_from_url(source_url)
            
            return {
                'name': name,
                'phone': phone,
                'category': category,
                'reviews': reviews,
                'rating': rating,
                'website': website,
                'source_url': source_url,
                **location_data,
                'metadata': {
                    'scraped_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return None
    
    def _extract_location_from_url(self, url: str) -> Dict:
        """Extract location info from Google Maps URL"""
        # Extract coordinates from URL
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            
            return {
                'latitude': lat,
                'longitude': lng
            }
        
        return {
            'latitude': None,
            'longitude': None
        }
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
