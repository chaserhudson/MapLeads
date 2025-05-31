#!/usr/bin/env python3
"""
Simple UI launcher for debugging
"""

import webbrowser
import time
import threading
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)  # Give server more time to start
    webbrowser.open('http://localhost:5000')

def main():
    print("🗺️ MapLeads Web UI (Simple Launcher)")
    print("====================================")
    print("")
    
    # Check if UI files exist
    ui_dir = project_root / 'ui'
    index_file = ui_dir / 'index.html'
    app_file = ui_dir / 'app.js'
    
    print(f"📁 Project root: {project_root}")
    print(f"📁 UI directory: {ui_dir}")
    
    if not ui_dir.exists():
        print(f"❌ UI directory not found: {ui_dir}")
        return
        
    if not index_file.exists():
        print(f"❌ index.html not found: {index_file}")
        return
        
    if not app_file.exists():
        print(f"❌ app.js not found: {app_file}")
        return
        
    print("✅ UI files found")
    
    try:
        # Import here to catch import errors
        from src.web_server import app
        print("✅ Web server imported successfully")
        
        print("Starting web server...")
        print("🌐 Server will be available at: http://localhost:5000")
        print("📱 Browser will open automatically")
        print("⏹️  Press Ctrl+C to stop")
        print("")
        
        # Start browser in background thread
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        # Start the Flask app directly
        app.run(host='localhost', port=5000, debug=False, threaded=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("")
        print("Possible solutions:")
        print("1. Make sure you're in the MapLeads directory")
        print("2. Activate virtual environment: source venv/bin/activate")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Check if Flask is installed: pip list | grep -i flask")
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()