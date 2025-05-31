#!/usr/bin/env python3

print("STARTING EMERGENCY TEST")
print("=" * 50)

# Test 1: Can we even run Python properly?
print("✅ Python is working")

# Test 2: Can we create a simple web server?
try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def test():
        return "<h1>WORKING!</h1><p>If you see this, the server works!</p>"
    
    print("✅ Flask imported successfully")
    print("")
    print("🌐 EMERGENCY SERVER STARTING...")
    print("🌐 Go to: http://localhost:5000")
    print("🌐 You should see 'WORKING!' in big letters")
    print("⏹️  Press Ctrl+C to stop")
    print("")
    
    app.run(host='localhost', port=5000, debug=True)
    
except ImportError:
    print("❌ FLASK NOT INSTALLED!")
    print("Run: pip install flask")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()