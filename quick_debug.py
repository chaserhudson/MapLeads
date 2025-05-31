#!/usr/bin/env python3
"""
Quick debug - check if main launch_ui.py has import issues
"""

import sys
from pathlib import Path

print("🔍 Quick Debug - Checking Import Issues")
print("======================================")
print("")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print(f"📁 Project root: {project_root}")
print(f"📁 Python path: {sys.path[0]}")
print("")

# Test 1: Basic imports
print("🧪 Test 1: Basic Python imports")
try:
    import webbrowser
    import time
    import threading
    print("✅ Basic imports: OK")
except Exception as e:
    print(f"❌ Basic imports failed: {e}")

# Test 2: Flask imports
print("\n🧪 Test 2: Flask imports")
try:
    from flask import Flask
    print("✅ Flask import: OK")
except Exception as e:
    print(f"❌ Flask import failed: {e}")
    print("Run: pip install flask")

# Test 3: Project imports
print("\n🧪 Test 3: Project imports")
try:
    from src.config_manager import ConfigManager
    print("✅ ConfigManager import: OK")
except Exception as e:
    print(f"❌ ConfigManager import failed: {e}")

try:
    from src.database import Database
    print("✅ Database import: OK")
except Exception as e:
    print(f"❌ Database import failed: {e}")

try:
    from src.web_server import start_web_server
    print("✅ Web server import: OK")
except Exception as e:
    print(f"❌ Web server import failed: {e}")

# Test 4: Check UI files
print("\n🧪 Test 4: UI files")
ui_dir = project_root / 'ui'
index_file = ui_dir / 'index.html'

print(f"📁 UI directory: {ui_dir}")
print(f"📄 UI directory exists: {ui_dir.exists()}")

if ui_dir.exists():
    html_files = list(ui_dir.glob('*.html'))
    print(f"📄 HTML files: {[f.name for f in html_files]}")
    
    if index_file.exists():
        size = index_file.stat().st_size
        print(f"📄 index.html size: {size} bytes")
        if size > 1000:
            print("✅ index.html looks good")
        else:
            print("⚠️ index.html might be empty or corrupted")
    else:
        print("❌ index.html not found")

print("\n" + "="*50)
print("🎯 Recommendations:")

# Check if Flask is the issue
try:
    from flask import Flask
    print("✅ Flask is installed - web UI should work")
    print("💡 Try: python simple_test.py")
except:
    print("❌ Flask missing - install it: pip install flask")

# Check if src imports are the issue  
try:
    from src.web_server import start_web_server
    print("✅ Web server module works")
    print("💡 The original ./run.sh ui should work")
except Exception as e:
    print(f"❌ Web server module broken: {e}")
    print("💡 Use simple_test.py instead")

print("")
print("Next steps:")
print("1. Run: python simple_test.py")
print("2. Test the /debug-vue link")
print("3. Check for Vue.js loading errors")