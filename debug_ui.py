#!/usr/bin/env python3
"""
Debug UI server - minimal Flask app to test file serving
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from flask import Flask, send_from_directory
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    exit(1)

# Get absolute paths
UI_DIR = project_root / 'ui'
print(f"📁 UI Directory: {UI_DIR}")
print(f"📁 UI Directory exists: {UI_DIR.exists()}")

if UI_DIR.exists():
    files = list(UI_DIR.glob('*'))
    print(f"📄 Files in UI directory: {files}")

app = Flask(__name__)

@app.route('/')
def index():
    """Serve a simple test page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MapLeads Debug Test</title>
    </head>
    <body>
        <h1>🗺️ MapLeads Debug Test</h1>
        <p>If you can see this, the Flask server is working!</p>
        <p>Testing file paths:</p>
        <ul>
            <li>UI Directory: """ + str(UI_DIR) + """</li>
            <li>UI Directory exists: """ + str(UI_DIR.exists()) + """</li>
        </ul>
        <p><a href="/static-test">Test Static File Serving</a></p>
        <p><a href="/ui-test">Test UI File Serving</a></p>
        <p><a href="/simple">Test Simple HTML</a></p>
        <p><a href="/test">Test Vue.js</a></p>
    </body>
    </html>
    """

@app.route('/static-test')
def static_test():
    """Test if we can serve static files"""
    try:
        # Try to serve index.html directly
        index_path = UI_DIR / 'index.html'
        if index_path.exists():
            with open(index_path, 'r') as f:
                content = f.read()
            return f"<pre>File exists and readable. Size: {len(content)} characters\n\nFirst 500 chars:\n{content[:500]}</pre>"
        else:
            return f"❌ index.html not found at: {index_path}"
    except Exception as e:
        return f"❌ Error reading file: {e}"

@app.route('/ui-test')
def ui_test():
    """Test sending file through Flask"""
    try:
        return send_from_directory(str(UI_DIR), 'index.html')
    except Exception as e:
        return f"❌ Error serving file through Flask: {e}"

@app.route('/simple')
def simple_test():
    """Test simple HTML page"""
    try:
        return send_from_directory(str(UI_DIR), 'simple.html')
    except Exception as e:
        return f"❌ Error serving simple.html: {e}"

@app.route('/test')
def vue_test():
    """Test Vue.js page"""
    try:
        return send_from_directory(str(UI_DIR), 'test.html')
    except Exception as e:
        return f"❌ Error serving test.html: {e}"

if __name__ == '__main__':
    print("\n🧪 Starting Debug Server")
    print("Open your browser to: http://localhost:5001")
    print("This will help diagnose the issue")
    print("Press Ctrl+C to stop\n")
    
    app.run(host='localhost', port=5001, debug=True)