"""
Web server for MapLeads UI
Provides REST API endpoints for the Vue.js frontend
"""

import json
import threading
import time
import os
from pathlib import Path

try:
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Please install Flask dependencies:")
    print("pip install flask flask-cors")
    exit(1)

from .config_manager import ConfigManager
from .database import Database
from .scraper_continuous import MapLeadsScraper

# Get absolute path to UI directory
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
UI_DIR = PROJECT_ROOT / 'ui'

app = Flask(__name__, static_folder=str(UI_DIR), static_url_path='')
CORS(app)

# Global variables for scraper control
scraper_thread = None
scraper_instance = None
scraper_running = False

@app.route('/')
def index():
    """Serve the main UI"""
    try:
        # Check if index.html exists
        index_path = UI_DIR / 'index.html'
        if not index_path.exists():
            return f"Error: index.html not found at {index_path}", 404
        
        return send_from_directory(str(UI_DIR), 'index.html')
    except Exception as e:
        return f"Error serving UI: {e}", 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        config_manager = ConfigManager()
        if config_manager.config_exists():
            config = config_manager.load_config()
            return jsonify({'success': True, 'config': config})
        else:
            # Return default config if none exists
            config = config_manager.get_default_config()
            return jsonify({'success': True, 'config': config, 'is_default': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def save_config():
    """Save configuration"""
    try:
        config_data = request.json
        config_manager = ConfigManager()
        config_manager.save_config(config_data)
        return jsonify({'success': True, 'message': 'Configuration saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/businesses', methods=['GET'])
def get_businesses():
    """Get businesses from database"""
    try:
        db = Database()
        
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        days = request.args.get('days', None, type=int)
        
        print(f"📊 API request: limit={limit}, offset={offset}, days={days}")
        
        if days:
            businesses = db.get_businesses_since_days(days)
            print(f"📊 Found {len(businesses)} businesses in last {days} days")
        else:
            # Get recent businesses with pagination
            businesses = db.get_recent_businesses(limit, offset)
            print(f"📊 Found {len(businesses)} recent businesses (limit={limit}, offset={offset})")
        
        # Convert datetime objects to strings for JSON serialization
        for business in businesses:
            if 'first_seen' in business and business['first_seen']:
                business['first_seen'] = business['first_seen'].isoformat()
            if 'last_updated' in business and business['last_updated']:
                business['last_updated'] = business['last_updated'].isoformat()
        
        print(f"📊 Returning {len(businesses)} businesses to frontend")
        return jsonify({'success': True, 'businesses': businesses})
    except Exception as e:
        print(f"❌ API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get database statistics"""
    try:
        db = Database()
        stats = db.get_statistics()
        return jsonify({'success': True, 'statistics': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scraper/start', methods=['POST'])
def start_scraper():
    """Start the scraper in background thread"""
    global scraper_thread, scraper_instance, scraper_running
    
    try:
        if scraper_running:
            return jsonify({'success': False, 'error': 'Scraper is already running'})
        
        config_manager = ConfigManager()
        if not config_manager.config_exists():
            return jsonify({'success': False, 'error': 'No configuration found. Please set up configuration first.'})
        
        config = config_manager.load_config()
        
        def run_scraper():
            global scraper_instance, scraper_running
            try:
                scraper_running = True
                db = Database()
                scraper_instance = MapLeadsScraper(db, headless=True)
                scraper_instance.continuous_scan(config['monitoring'])
            except Exception as e:
                print(f"Scraper error: {e}")
            finally:
                scraper_running = False
                if scraper_instance:
                    scraper_instance.cleanup()
        
        scraper_thread = threading.Thread(target=run_scraper, daemon=True)
        scraper_thread.start()
        
        return jsonify({'success': True, 'message': 'Scraper started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scraper/stop', methods=['POST'])
def stop_scraper():
    """Stop the scraper"""
    global scraper_instance, scraper_running
    
    try:
        if not scraper_running:
            return jsonify({'success': False, 'error': 'Scraper is not running'})
        
        scraper_running = False
        if scraper_instance:
            scraper_instance.cleanup()
        
        return jsonify({'success': True, 'message': 'Scraper stopped successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scraper/status', methods=['GET'])
def get_scraper_status():
    """Get scraper status"""
    global scraper_running, scraper_instance
    
    status = {
        'running': scraper_running,
        'stats': {}
    }
    
    if scraper_instance and hasattr(scraper_instance, 'stats'):
        status['stats'] = scraper_instance.stats
    
    return jsonify({'success': True, 'status': status})

@app.route('/api/export', methods=['POST'])
def export_data():
    """Export businesses to file"""
    try:
        data = request.json
        format_type = data.get('format', 'csv')
        days = data.get('days', 30)
        
        db = Database()
        businesses = db.get_businesses_since_days(days)
        
        if not businesses:
            return jsonify({'success': False, 'error': f'No businesses found in the last {days} days'})
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mapleads_export_{timestamp}.{format_type}"
        
        from .exporter import export_businesses
        export_businesses(businesses, filename, format_type)
        
        return jsonify({
            'success': True, 
            'message': f'Exported {len(businesses)} businesses to {filename}',
            'filename': filename,
            'count': len(businesses)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get available business categories"""
    categories = {
        "Home Services": [
            "plumber", "electrician", "hvac", "contractor", "roofer",
            "landscaper", "painter", "flooring", "home cleaning",
            "handyman", "garage door", "fence installer", "tree service"
        ],
        "Health & Wellness": [
            "gym", "yoga studio", "dentist", "doctor", "chiropractor",
            "spa", "salon", "barber", "massage"
        ],
        "Automotive": [
            "auto repair", "car dealer", "tire shop", "auto parts",
            "car wash", "mechanic", "body shop"
        ],
        "Professional Services": [
            "lawyer", "accountant", "insurance agent", "real estate agent",
            "financial advisor", "marketing agency"
        ],
        "Food & Dining": [
            "restaurant", "cafe", "bakery", "bar", "food truck",
            "catering", "pizza", "coffee shop"
        ]
    }
    
    return jsonify({'success': True, 'categories': categories})

def start_web_server(host='localhost', port=8080, debug=False):
    """Start the web server"""
    print(f"🌐 Starting MapLeads Web UI at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    start_web_server(debug=True)