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

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.web_server import start_web_server

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)  # Give server time to start
    webbrowser.open('http://localhost:5000')

def main():
    print("🗺️ MapLeads Web UI")
    print("==================")
    print("")
    print("Starting web server...")
    
    # Start browser in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start web server (this blocks)
    try:
        start_web_server(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 MapLeads Web UI stopped.")
    except Exception as e:
        print(f"\n❌ Error starting web server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check if port 5000 is already in use")
        print("3. Try running: python -m src.web_server")

if __name__ == '__main__':
    main()