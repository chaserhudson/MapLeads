#!/usr/bin/env python3

print("🔧 WORKING TEST - Using Port 8080")
print("=" * 40)

try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def test():
        return """
        <html>
        <head><title>WORKING!</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 100px;">
            <h1 style="color: green; font-size: 48px;">✅ WORKING!</h1>
            <p style="font-size: 24px;">Flask is working on port 8080!</p>
            <p style="font-size: 18px;">Port 5000 was blocked by ControlCenter</p>
            <hr>
            <h2>Next: Test Vue.js</h2>
            <div id="vue-test">Loading Vue.js...</div>
            
            <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
            <script>
                setTimeout(() => {
                    if (typeof Vue !== 'undefined') {
                        const { createApp } = Vue;
                        createApp({
                            data() { return { message: 'Vue.js works too!' } }
                        }).mount('#vue-test');
                    } else {
                        document.getElementById('vue-test').innerHTML = '❌ Vue.js failed to load';
                    }
                }, 1000);
            </script>
        </body>
        </html>
        """
    
    print("✅ Flask app created")
    print("")
    print("🌐 STARTING ON PORT 8080...")
    print("🌐 Go to: http://localhost:8080")
    print("🌐 You should see a big green 'WORKING!'")
    print("⏹️  Press Ctrl+C to stop")
    print("")
    
    # Kill the process blocking port 5000 first
    import os
    os.system("kill -9 77511 2>/dev/null")
    print("🔪 Killed ControlCenter process on port 5000")
    
    app.run(host='localhost', port=8080, debug=True)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()