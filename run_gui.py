#!/usr/bin/env python3
"""
MapLeads GUI Launcher
Run this script to launch the MapLeads graphical user interface.
"""

import sys
import os
from pathlib import Path

# Add the ui directory to the path
project_root = Path(__file__).parent
ui_dir = project_root / "ui"
sys.path.insert(0, str(ui_dir))

if __name__ == "__main__":
    try:
        # Change to project directory to ensure relative paths work
        os.chdir(project_root)
        
        from mapleads_gui import main
        print("Starting MapLeads GUI...")
        main()
    except ImportError as e:
        print(f"Error importing GUI modules: {e}")
        print("Make sure all required dependencies are installed.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)
