"""
Main scraper module for MapLeads
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
            'existing_businesses': 0
        }
    
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
    
    def scan(self, monitoring_config: Dict, test_mode: bool = False) -> List[Dict]:
        """Run a complete scan based on configuration"""
        start_time = datetime.now()
        
        if not self.setup_driver():
            raise Exception("Failed to setup Chrome driver")
        
        try:
            # Generate URLs
            urls = self._generate_urls(monitoring_config, test_mode)
            if not urls:
                print("No URLs generated for scanning")
                return []
            
            print(f"Generated {len(urls)} URLs to scan")
            
            # Process URLs
            all_new_businesses = []
            
            for url in tqdm(urls, desc="Scanning locations"):
                businesses = self._scrape_url(url)
                
                # Check each business
                for business in businesses:
                    if not business.get('phone'):
                        continue
                    
                    if self.db.business_exists(business['phone']):
                        self.db.update_last_seen(business['phone'])
                        self.stats['existing_businesses'] += 1
                    else:
                        # New business found!
                        business_id = self.db.add_business(business)
                        business['id'] = business_id
                        all_new_businesses.append(business)
                        self.stats['new_businesses'] += 1
                
                # Small delay between requests
                time.sleep(random.uniform(1, 3))
            
            # Record scan in history
            duration = int((datetime.now() - start_time).total_seconds())
            self.db.add_scan_record(
                categories=monitoring_config['categories'],
                locations=monitoring_config['locations'],
                businesses_found=self.stats['businesses_found'],
                new_businesses=self.stats['new_businesses'],
                duration_seconds=duration
            )
            
            return all_new_businesses
            
        finally:
            self.cleanup()
    
    def _generate_urls(self, monitoring_config: Dict, test_mode: bool = False) -> List[str]:
        """Generate Google Maps URLs based on configuration"""
        categories = monitoring_config['categories']
        locations_config = monitoring_config['locations']
        max_urls = monitoring_config.get('max_urls', 100)
        
        if test_mode:
            max_urls = min(max_urls, 5)
        
        # Get locations from database
        locations = self.db.get_locations_for_filters(
            states=locations_config.get('states'),
            cities=locations_config.get('cities'),
            min_population=locations_config.get('min_population', 0)
        )
        
        urls = []
        for category in categories:
            category_formatted = category.replace(' ', '+')
            
            for location in locations:
                if len(urls) >= max_urls:
                    break
                    
                url = (
                    f"https://www.google.com/maps/search/{category_formatted}/@"
                    f"{location['lat']},{location['lng']},13z"
                )
                urls.append(url)
            
            if len(urls) >= max_urls:
                break
        
        # Randomize order
        random.shuffle(urls)
        
        return urls[:max_urls]
    
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
            
            # This is a simplified version - in production you'd want to
            # reverse geocode or match to nearest location in database
            return {
                'latitude': lat,
                'longitude': lng,
                'city': 'Unknown',
                'state': 'Unknown',
                'zip_code': 'Unknown'
            }
        
        return {
            'latitude': None,
            'longitude': None,
            'city': 'Unknown',
            'state': 'Unknown',
            'zip_code': 'Unknown'
        }
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
