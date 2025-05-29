"""
Main scraper module for MapLeads - Continuous Processing Version
Handles Google Maps scraping with Selenium
"""

import re
import time
import random
import threading
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        self.drivers = []  # For multiple browser instances
        self.db_lock = threading.Lock()  # For thread-safe database access
        self.stats = {
            'urls_processed': 0,
            'businesses_found': 0,
            'new_businesses': 0,
            'existing_businesses': 0,
            'total_cycles': 0
        }
        self.stats_lock = threading.Lock()  # For thread-safe stats updates
        self.current_position = {'location_idx': 0}
        self.instance_stats = {}  # Progress tracking per instance
    
    def setup_driver(self, instance_id: int = 0) -> webdriver.Chrome:
        """Initialize Chrome driver for a specific instance"""
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
            
            # Unique user-data-dir for each instance to avoid conflicts
            options.add_argument(f"--user-data-dir=/tmp/chrome_instance_{instance_id}")
            
            # Use webdriver-manager
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            print(f"Failed to initialize Chrome driver for instance {instance_id}: {e}")
            return None

    def setup_multiple_drivers(self, num_instances: int) -> bool:
        """Initialize multiple Chrome drivers"""
        self.drivers = []
        for i in range(num_instances):
            driver = self.setup_driver(i)
            if driver:
                self.drivers.append(driver)
                self.instance_stats[i] = {
                    'urls_processed': 0,
                    'businesses_found': 0,
                    'new_businesses': 0,
                    'current_location': 'Ready'
                }
            else:
                # Clean up already created drivers on failure
                for d in self.drivers:
                    d.quit()
                return False
        
        print(f"✅ Initialized {len(self.drivers)} browser instances")
        return True
    
    def continuous_scan(self, monitoring_config: Dict) -> None:
        """Run continuous scanning through all locations with parallel processing"""
        num_instances = monitoring_config.get('browser_instances', 1)
        
        if not self.setup_multiple_drivers(num_instances):
            raise Exception("Failed to setup Chrome drivers")
        
        try:
            category = monitoring_config['category']
            locations_config = monitoring_config['locations']
            batch_size = monitoring_config.get('batch_size', 10)
            
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
            print(f"Browser instances: {num_instances}")
            print(f"Total locations to check: {len(all_locations)}")
            
            while True:  # Continuous loop
                cycle_start = datetime.now()
                
                print(f"\n📍 Processing category: {category}")
                category_formatted = category.replace(' ', '+')
                
                # Create progress display thread
                progress_thread = threading.Thread(target=self._display_progress, daemon=True)
                progress_thread.start()
                
                # Process all locations in parallel batches
                self._process_locations_parallel(all_locations, category_formatted, num_instances)
                
                # Completed full cycle
                self.stats['total_cycles'] += 1
                cycle_duration = (datetime.now() - cycle_start).total_seconds() / 60
                
                print(f"\n✅ Completed full cycle #{self.stats['total_cycles']}")
                print(f"   Duration: {cycle_duration:.1f} minutes")
                print(f"   Total new businesses found: {self.stats['new_businesses']}")
                print(f"   Starting next cycle...\n")
                
                # Record cycle completion
                with self.db_lock:
                    self.db.add_scan_record(
                        categories=[category],
                        locations=locations_config,
                        businesses_found=self.stats['businesses_found'],
                        new_businesses=self.stats['new_businesses'],
                        duration_seconds=int(cycle_duration * 60)
                    )
                
                # Pause between cycles
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopping continuous scan...")
            self._save_progress()
        finally:
            self.cleanup()

    def _process_locations_parallel(self, locations: List[Dict], category_formatted: str, num_instances: int):
        """Process locations using multiple browser instances"""
        # Split locations among instances
        chunks = [locations[i::num_instances] for i in range(num_instances)]
        
        with ThreadPoolExecutor(max_workers=num_instances) as executor:
            futures = []
            
            for instance_id, chunk in enumerate(chunks):
                if chunk:  # Only create thread if there are locations to process
                    future = executor.submit(
                        self._process_location_chunk, 
                        chunk, 
                        category_formatted, 
                        instance_id
                    )
                    futures.append(future)
            
            # Wait for all threads to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Thread error: {e}")

    def _process_location_chunk(self, locations: List[Dict], category_formatted: str, instance_id: int):
        """Process a chunk of locations with a specific browser instance"""
        driver = self.drivers[instance_id]
        
        for location in locations:
            try:
                # Update instance status
                self.instance_stats[instance_id]['current_location'] = f"{location['city']}, {location['state']}"
                
                url = (
                    f"https://www.google.com/maps/search/{category_formatted}/@"
                    f"{location['lat']},{location['lng']},13z"
                )
                
                businesses = self._scrape_url_with_driver(url, driver, instance_id)
                new_count = 0
                
                # Check if we got any businesses with phone numbers
                businesses_with_phones = [b for b in businesses if b.get('phone')]
                if not businesses_with_phones and businesses:
                    print(f"  ⚠️  [Instance {instance_id}] Found {len(businesses)} businesses in {location['city']}, {location['state']} but no phone numbers")
                    continue
                
                # Check each business (with database locking)
                with self.db_lock:
                    for business in businesses:
                        if not business.get('phone'):
                            continue
                        
                        # Add location info
                        business['city'] = location.get('city', 'Unknown')
                        business['state'] = location.get('state', 'Unknown')
                        business['zip_code'] = location.get('zip', 'Unknown')
                        
                        if self.db.business_exists(business['phone']):
                            self.db.update_last_seen(business['phone'])
                            with self.stats_lock:
                                self.stats['existing_businesses'] += 1
                        else:
                            # New business found!
                            business_id = self.db.add_business(business)
                            business['id'] = business_id
                            with self.stats_lock:
                                self.stats['new_businesses'] += 1
                            new_count += 1
                            
                            # Notify immediately if configured
                            if hasattr(self, 'notifier'):
                                self.notifier.send_notifications([business])
                
                if new_count > 0:
                    print(f"  ✨ [Instance {instance_id}] Found {new_count} new businesses in {location['city']}, {location['state']}")
                
                # Update instance stats
                self.instance_stats[instance_id]['new_businesses'] += new_count
                
            except Exception as e:
                print(f"  ❌ [Instance {instance_id}] Error processing {location['city']}: {e}")
        
        # Mark instance as completed
        self.instance_stats[instance_id]['current_location'] = 'Completed'

    def _display_progress(self):
        """Display real-time progress of all instances"""
        while True:
            time.sleep(5)  # Update every 5 seconds
            
            # Check if all instances are done
            all_done = all(
                stats['current_location'] == 'Completed' 
                for stats in self.instance_stats.values()
            )
            
            if all_done:
                break
            
            # Print progress
            print("\n📊 Instance Progress:")
            for instance_id, stats in self.instance_stats.items():
                location = stats['current_location']
                new_found = stats['new_businesses']
                print(f"   Instance {instance_id}: {location} (New: {new_found})")
            print()  # Add spacing
    
    def baseline_scan(self, monitoring_config: Dict) -> None:
        """Run a one-time baseline scan to populate database"""
        self.driver = self.setup_driver(0)
        if not self.driver:
            raise Exception("Failed to setup Chrome driver")
        
        try:
            category = monitoring_config['category']
            locations_config = monitoring_config['locations']
            
            # Get all locations
            all_locations = self.db.get_locations_for_filters(
                states=locations_config.get('states'),
                cities=locations_config.get('cities'),
                min_population=locations_config.get('min_population', 0)
            )
            
            if not all_locations:
                print("No locations found matching criteria")
                return
            
            total_locations = len(all_locations)
            
            # Calculate time estimation
            estimated_time = self._calculate_baseline_time(total_locations)
            
            print(f"🎯 Baseline Scan Configuration:")
            print(f"   Category: {category}")
            print(f"   Total locations: {total_locations}")
            print(f"   Estimated completion time: {estimated_time}")
            print()
            print("📊 This baseline scan will:")
            print("   • Find all existing businesses in your selected category/locations")
            print("   • Add them to the database for future comparison")
            print("   • NOT send any notifications (all businesses are 'new' since DB is empty)")
            print("   • Enable future scans to detect truly NEW businesses")
            print()
            
            # Confirm start
            try:
                from rich.prompt import Confirm
                if not Confirm.ask("Ready to start baseline scan?"):
                    print("Baseline scan cancelled.")
                    return
            except ImportError:
                input("Press Enter to continue or Ctrl+C to cancel...")
            
            baseline_start = datetime.now()
            category_formatted = category.replace(' ', '+')
            
            print(f"\n🚀 Starting baseline scan...")
            print(f"📍 Processing category: {category}")
            
            # Process all locations
            for idx, location in enumerate(all_locations, 1):
                url = (
                    f"https://www.google.com/maps/search/{category_formatted}/@"
                    f"{location['lat']},{location['lng']},13z"
                )
                
                # Progress indicator
                progress_pct = (idx / total_locations) * 100
                print(f"Progress: {progress_pct:.1f}% - Scanning {location['city']}, {location['state']} ({idx}/{total_locations})")
                
                try:
                    businesses = self._scrape_url(url)
                    found_count = 0
                    
                    # Process all businesses (no "new" vs "existing" in baseline mode)
                    for business in businesses:
                        if not business.get('phone'):
                            continue
                        
                        # Add location info
                        business['city'] = location.get('city', 'Unknown')
                        business['state'] = location.get('state', 'Unknown')
                        business['zip_code'] = location.get('zip', 'Unknown')
                        
                        # In baseline mode, add all businesses regardless of existence
                        if not self.db.business_exists(business['phone']):
                            self.db.add_business(business)
                            found_count += 1
                        else:
                            # Update last seen for existing businesses
                            self.db.update_last_seen(business['phone'])
                    
                    if found_count > 0:
                        print(f"   📋 Added {found_count} businesses from {location['city']}, {location['state']}")
                    
                except Exception as e:
                    print(f"   ❌ Error processing {location['city']}: {e}")
                
                # Delay between requests
                time.sleep(random.uniform(1, 3))
            
            # Baseline completed
            duration = datetime.now() - baseline_start
            duration_minutes = duration.total_seconds() / 60
            
            print(f"\n✅ Baseline scan completed!")
            print(f"   Duration: {duration_minutes:.1f} minutes")
            print(f"   Total businesses found: {self.stats['businesses_found']}")
            print(f"   Locations processed: {total_locations}")
            print()
            print("🎯 Your baseline is now established! Future scans will:")
            print("   • Only report businesses that are NEW since this baseline")
            print("   • Send notifications for genuinely new businesses")
            print("   • Track changes in business listings over time")
            print()
            print("To start monitoring for new businesses, run:")
            print("   python mapleads.py run")
            
            # Record baseline in scan history
            self.db.add_scan_record(
                categories=[category],
                locations=locations_config,
                businesses_found=self.stats['businesses_found'],
                new_businesses=0,  # In baseline mode, all are "baseline" not "new"
                duration_seconds=int(duration.total_seconds())
            )
            
        except KeyboardInterrupt:
            print("\n⏹️  Baseline scan stopped by user.")
        finally:
            self.cleanup()
    
    def _calculate_baseline_time(self, total_locations: int) -> str:
        """Calculate estimated time for baseline scan"""
        # Conservative estimates:
        # - Average 15 seconds per location (including delays)
        # - Add 20% buffer for unexpected delays
        
        avg_seconds_per_location = 15
        buffer_multiplier = 1.2
        
        total_seconds = total_locations * avg_seconds_per_location * buffer_multiplier
        
        if total_seconds < 60:
            return f"{int(total_seconds)} seconds"
        elif total_seconds < 3600:
            minutes = int(total_seconds / 60)
            return f"{minutes} minutes"
        else:
            hours = int(total_seconds / 3600)
            remaining_minutes = int((total_seconds % 3600) / 60)
            if remaining_minutes > 0:
                return f"{hours} hours, {remaining_minutes} minutes"
            else:
                return f"{hours} hours"
    
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
        """Scrape a single Google Maps URL (legacy single driver method)"""
        return self._scrape_url_with_driver(url, self.driver, 0)

    def _scrape_url_with_driver(self, url: str, driver: webdriver.Chrome, instance_id: int) -> List[Dict]:
        """Scrape a single Google Maps URL with a specific driver"""
        businesses = []
        
        try:
            driver.get(url)
            with self.stats_lock:
                self.stats['urls_processed'] += 1
            self.instance_stats[instance_id]['urls_processed'] += 1
            
            # Wait for initial load
            time.sleep(3)
            
            # Start auto-scrolling
            driver.execute_script(JS_SCROLL_SCRIPT)
            
            # Wait for results
            max_wait = 20
            for _ in range(max_wait):
                time.sleep(1)
                if "the end of the list" in driver.page_source.lower():
                    break
            
            # Extract business cards
            cards = driver.find_elements(
                By.XPATH, 
                '//div[contains(@jsaction, "mouseover")]'
            )
            
            for card in cards:
                try:
                    business = self._parse_business_card(card, url)
                    if business:
                        businesses.append(business)
                        with self.stats_lock:
                            self.stats['businesses_found'] += 1
                        self.instance_stats[instance_id]['businesses_found'] += 1
                except Exception:
                    continue
            
        except Exception as e:
            print(f"[Instance {instance_id}] Error scraping {url}: {e}")
        
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
        # Clean up single driver (for backward compatibility)
        if self.driver:
            self.driver.quit()
            self.driver = None
        
        # Clean up multiple drivers
        for driver in self.drivers:
            try:
                driver.quit()
            except Exception:
                pass
        self.drivers = []
