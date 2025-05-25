#!/usr/bin/env python3
"""
Quick start script for MapLeads
Handles initial setup and data preparation
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("🚀 MapLeads Quick Start\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed\n")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("Try running: pip install -r requirements.txt")
        sys.exit(1)
    
    # Prepare data
    print("📍 Preparing location data...")
    try:
        subprocess.check_call([sys.executable, "prepare_data.py"])
        print("✅ Location data ready\n")
    except subprocess.CalledProcessError:
        print("⚠️  Location data preparation failed")
        print("You can continue but geographic filtering may be limited\n")
    
    # Run setup
    print("🔧 Starting interactive setup...")
    print("-" * 50)
    
    try:
        subprocess.check_call([sys.executable, "mapleads.py", "setup"])
    except subprocess.CalledProcessError:
        print("\n❌ Setup failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ MapLeads is ready to use!")
    print("\nNext steps:")
    print("1. Run a test scan: python mapleads.py test")
    print("2. Start monitoring: python mapleads.py run")
    print("3. View examples: python examples.py")
    print("\nHappy lead hunting! 🎯")

if __name__ == "__main__":
    main()
