#!/usr/bin/env python3
"""
Simple test to check if the web server works
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.web_server import app
    print("✅ Web server module imported successfully")
    
    # Test if UI files exist and are readable
    ui_dir = project_root / 'ui'
    index_file = ui_dir / 'index.html'
    app_file = ui_dir / 'app.js'
    
    if index_file.exists():
        print(f"✅ index.html found: {index_file}")
        print(f"   Size: {index_file.stat().st_size} bytes")
    else:
        print(f"❌ index.html not found at: {index_file}")
    
    if app_file.exists():
        print(f"✅ app.js found: {app_file}")
        print(f"   Size: {app_file.stat().st_size} bytes")
    else:
        print(f"❌ app.js not found at: {app_file}")
    
    # Test Flask app configuration
    print(f"✅ Flask static folder: {app.static_folder}")
    print(f"✅ Flask static URL path: {app.static_url_path}")
    
    # Test if we can start the server
    print("\n🧪 Testing server startup...")
    print("Starting server on http://localhost:5001 (test port)")
    print("Open your browser manually to: http://localhost:5001")
    print("Press Ctrl+C to stop")
    
    app.run(host='localhost', port=5001, debug=True)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the MapLeads directory")
    print("and that you've activated the virtual environment")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()