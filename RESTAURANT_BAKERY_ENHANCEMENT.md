# Restaurant and Bakery Enhancement Plan

## Problem
The current scraper works well for most business categories (gyms, plumbers, dentists, etc.) but fails to extract phone numbers for restaurants and bakeries. This is because Google Maps displays these business types differently in search results.

## Root Cause
- **Regular businesses**: Phone numbers are visible directly in the search result cards
- **Restaurants/Bakeries**: Phone numbers are NOT shown in search result cards
- **Solution**: Phone numbers are only available when you click each individual business card to open the detailed view

## Technical Implementation Required

### 1. Enhanced Scraping Method
For categories like "restaurant", "bakery", "cafe", etc., implement a two-step process:

#### Step 1: Click Business Cards
```python
# For each business card in search results
business_cards = driver.find_elements(By.XPATH, "//div[contains(@jsaction, 'mouseover')]")
for card in business_cards:
    card.click()  # Opens detailed view
    time.sleep(2)  # Wait for detail panel to load
```

#### Step 2: Extract from Detail Panel
```python
# Extract phone number from expanded detail view
phone_selectors = [
    "button[data-item-id^='phone:tel:']",
    "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc",  # Phone number container
    "a[href^='tel:']"
]

# Extract other enhanced details available in detail view
address_selector = "button[data-item-id='address'] .Io6YTe"
hours_selector = ".OMl5r .ZDu9vd"
website_selector = "a[data-item-id='authority']"
```

### 2. Category Detection
Add logic to detect categories that require enhanced scraping:

```python
ENHANCED_CATEGORIES = [
    'restaurant', 'bakery', 'cafe', 'coffee shop', 
    'bar', 'pub', 'diner', 'pizzeria', 'bistro'
]

def requires_enhanced_scraping(category):
    return any(cat in category.lower() for cat in ENHANCED_CATEGORIES)
```

### 3. Modified Scraping Flow
```python
def scrape_location(self, url, category):
    businesses = []
    
    if requires_enhanced_scraping(category):
        # Enhanced method: click each card
        businesses = self._enhanced_scrape_method(url)
    else:
        # Current method: extract from search results
        businesses = self._current_scrape_method(url)
    
    return businesses
```

### 4. Performance Considerations
- **Slower processing**: Each business requires individual click + wait
- **Rate limiting**: Need longer delays between requests
- **Batch size**: Reduce batch_size for enhanced categories
- **Timeout handling**: Longer timeouts for detail panel loading

### 5. Error Handling
- Handle cases where detail panel fails to load
- Skip businesses where phone extraction fails
- Implement retry logic for click failures
- Graceful fallback to basic info extraction

## Files to Modify

### 1. `src/scraper_continuous.py`
- Add category detection logic
- Implement enhanced scraping method
- Modify main scraping loop to choose method based on category

### 2. `src/config_manager.py`
- Add configuration for enhanced categories
- Add settings for enhanced scraping timeouts/delays

### 3. `mapleads.py`
- Update category command to warn about enhanced categories
- Display appropriate messages for unsupported categories

## Implementation Priority

### Phase 1: Detection and Messaging ✅ (Current)
- Detect when no phone numbers found
- Display user-friendly message about unsupported categories

### Phase 2: Enhanced Scraping
- Implement click-based extraction for restaurants/bakeries
- Add configuration options for enhanced categories

### Phase 3: Optimization
- Optimize performance and error handling
- Add progress indicators for slower enhanced scraping

## User Experience Impact

### Current Behavior
- User selects "restaurant" category
- Scraper finds 0 businesses with phone numbers
- User gets confused about why nothing was found

### Enhanced Behavior
- User selects "restaurant" category  
- System detects enhanced category requirement
- Either:
  - Runs enhanced scraping (slower but comprehensive)
  - OR displays clear message about current limitations

## Example Enhanced Extraction

```python
def _extract_phone_from_detail_panel(self, driver):
    phone_selectors = [
        "button[data-item-id^='phone:tel:'] .Io6YTe",
        "a[href^='tel:']",
    ]
    
    for selector in phone_selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            phone_text = element.text.strip()
            if re.match(r'\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}', phone_text):
                return phone_text
        except:
            continue
    
    return None
```

This enhancement would make MapLeads comprehensive for ALL business categories, not just service-based businesses.