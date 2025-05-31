#!/usr/bin/env python3
"""
Test the complete user flow to identify the exact issue
"""

import sys
from pathlib import Path
import webbrowser
import time
import threading

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def open_browser_to_debug():
    """Open browser to debug page"""
    time.sleep(2)
    print("🌐 Opening debug page...")
    webbrowser.open('http://localhost:5001/debug')

def main():
    print("🧪 MapLeads Flow Test")
    print("====================")
    print("")
    print("This will:")
    print("1. Start debug server")
    print("2. Open debug page to capture errors")
    print("3. Help identify the exact issue")
    print("")
    
    try:
        from src.web_server import app
        print("✅ Web server imported successfully")
        
        # Start browser to debug page
        browser_thread = threading.Thread(target=open_browser_to_debug, daemon=True)
        browser_thread.start()
        
        print("🌐 Debug server starting at http://localhost:5001")
        print("📋 Debug page will open automatically")
        print("⏹️  Press Ctrl+C to stop")
        print("")
        print("👀 Look for:")
        print("  - Console errors in red")
        print("  - Failed tests")
        print("  - API response issues")
        print("")
        
        # Start the Flask app
        app.run(host='localhost', port=5001, debug=False, threaded=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("")
        print("Solutions:")
        print("1. Activate virtual environment: source venv/bin/activate")
        print("2. Install dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()