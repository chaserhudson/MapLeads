#!/usr/bin/env python3
"""
Launch script for MapLeads Web UI
Opens the web interface in your default browser
"""

import webbrowser
import time
import threading
from pathlib import Path
import sys

# Add project root to path so we can import our modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.web_server import start_web_server

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)  # Give server time to start
    webbrowser.open('http://localhost:5000')

def main():
    print("🗺️ MapLeads Web UI")
    print("==================")
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
    print("Starting web server...")
    
    # Start browser in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start web server (this blocks)
    try:
        print("🌐 Server will be available at: http://localhost:5000")
        start_web_server(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 MapLeads Web UI stopped.")
    except Exception as e:
        print(f"\n❌ Error starting web server: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check if port 5000 is already in use")
        print("3. Try running: python test_server.py")

if __name__ == '__main__':
    main()