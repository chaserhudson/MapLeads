#!/usr/bin/env python3
"""
Simple standalone test - just serve the HTML files directly
"""

import webbrowser
import time
import threading
from pathlib import Path
import sys

# Check if we can import Flask
try:
    from flask import Flask, send_from_directory
    print("✅ Flask is available")
except ImportError:
    print("❌ Flask not installed. Run: pip install flask")
    sys.exit(1)

# Get paths
project_root = Path(__file__).parent
ui_dir = project_root / 'ui'

# Create simple Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Serve debug page"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MapLeads Simple Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .box {{ border: 1px solid #ccc; padding: 20px; margin: 20px 0; }}
            .success {{ background: #d4edda; border-color: #c3e6cb; }}
            .error {{ background: #f8d7da; border-color: #f5c6cb; }}
        </style>
    </head>
    <body>
        <h1>🗺️ MapLeads Simple Test</h1>
        
        <div class="box success">
            <h3>✅ Flask Server is Working!</h3>
            <p>This confirms the basic web server setup is functional.</p>
        </div>
        
        <div class="box">
            <h3>Test Links:</h3>
            <p><a href="/debug-vue">🧪 Test Vue.js Loading</a></p>
            <p><a href="/main-ui">📱 Test Main UI (original)</a></p>
            <p><a href="/minimal">⚡ Test Minimal UI</a></p>
        </div>
        
        <div class="box">
            <h3>File Check:</h3>
            <p>UI Directory: {ui_dir}</p>
            <p>UI Directory Exists: {ui_dir.exists()}</p>
            <p>Files: {list(ui_dir.glob('*.html')) if ui_dir.exists() else 'None'}</p>
        </div>
    </body>
    </html>
    """

@app.route('/debug-vue')
def debug_vue():
    """Test Vue.js with detailed logging"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vue.js Debug Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .log { background: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #007bff; }
            .error { border-left-color: #dc3545; background: #f8d7da; }
            .success { border-left-color: #28a745; background: #d4edda; }
        </style>
    </head>
    <body>
        <h1>🧪 Vue.js Debug Test</h1>
        <div id="logs"></div>
        <div id="vue-test">Loading Vue.js...</div>
        
        <script>
            const logs = document.getElementById('logs');
            
            function log(message, type = 'info') {
                console.log(message);
                const div = document.createElement('div');
                div.className = 'log ' + (type === 'error' ? 'error' : type === 'success' ? 'success' : '');
                div.textContent = new Date().toLocaleTimeString() + ': ' + message;
                logs.appendChild(div);
            }
            
            log('Starting Vue.js test...');
            
            // Try to load Vue.js
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/vue@3/dist/vue.global.js';
            
            script.onload = function() {
                log('Vue.js script loaded successfully', 'success');
                
                if (typeof Vue !== 'undefined') {
                    log('Vue.js is available, version: ' + Vue.version, 'success');
                    
                    try {
                        const { createApp } = Vue;
                        const app = createApp({
                            data() {
                                return { message: 'Vue.js is working!' }
                            },
                            mounted() {
                                log('Vue app mounted successfully!', 'success');
                            }
                        });
                        app.mount('#vue-test');
                        log('Vue app created and mounted', 'success');
                    } catch (error) {
                        log('Vue app creation failed: ' + error.message, 'error');
                    }
                } else {
                    log('Vue.js script loaded but Vue is not available', 'error');
                }
            };
            
            script.onerror = function() {
                log('Failed to load Vue.js from CDN', 'error');
                log('This could be a network issue or CDN problem', 'error');
            };
            
            document.head.appendChild(script);
            log('Vue.js script tag added to page');
        </script>
    </body>
    </html>
    """

@app.route('/main-ui')
def main_ui():
    """Serve the original main UI"""
    try:
        return send_from_directory(str(ui_dir), 'index.html')
    except Exception as e:
        return f"❌ Error serving main UI: {e}"

@app.route('/minimal')
def minimal():
    """Serve minimal test"""
    try:
        return send_from_directory(str(ui_dir), 'minimal.html')
    except Exception as e:
        return f"❌ Error serving minimal.html: {e}"

def open_browser():
    """Open browser after delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

def main():
    print("🗺️ MapLeads Simple Test Server")
    print("==============================")
    print("")
    print(f"📁 UI Directory: {ui_dir}")
    print(f"📁 UI Exists: {ui_dir.exists()}")
    
    if ui_dir.exists():
        html_files = list(ui_dir.glob('*.html'))
        print(f"📄 HTML Files: {[f.name for f in html_files]}")
    
    print("")
    print("🌐 Starting server at http://localhost:5000")
    print("📱 Browser will open automatically")
    print("⏹️  Press Ctrl+C to stop")
    print("")
    
    # Start browser
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start server
    try:
        app.run(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == '__main__':
    main()