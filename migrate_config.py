#!/usr/bin/env python3
"""
Migration script to update existing MapLeads configurations 
from scheduled mode to continuous processing mode
"""

import json
from pathlib import Path
import sys

def migrate_config(config_path):
    """Migrate config from scheduled to continuous processing"""
    
    # Read existing config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Backup original
    backup_path = config_path.with_suffix('.backup.json')
    with open(backup_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Backed up original config to: {backup_path}")
    
    # Update monitoring section
    if 'monitoring' in config:
        monitoring = config['monitoring']
        
        # Remove schedule field
        if 'schedule' in monitoring:
            del monitoring['schedule']
            print("✅ Removed 'schedule' field")
        
        # Convert max_urls to batch_size
        if 'max_urls' in monitoring:
            # Use 1/10 of max_urls as batch_size
            batch_size = max(10, monitoring['max_urls'] // 10)
            del monitoring['max_urls']
            monitoring['batch_size'] = batch_size
            print(f"✅ Converted max_urls to batch_size: {batch_size}")
        else:
            monitoring['batch_size'] = 10
            print("✅ Added default batch_size: 10")
        
        # Add batch_delay if not present
        if 'batch_delay' not in monitoring:
            monitoring['batch_delay'] = 60
            print("✅ Added batch_delay: 60 seconds")
        
        # Convert categories to single category
        if 'categories' in monitoring:
            if isinstance(monitoring['categories'], list) and monitoring['categories']:
                monitoring['category'] = monitoring['categories'][0]
                print(f"✅ Converted categories to single category: {monitoring['category']}")
            del monitoring['categories']
        elif 'category' not in monitoring:
            monitoring['category'] = 'restaurant'
            print("✅ Added default category: restaurant")
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration migrated successfully!")
    print("\nNew configuration uses continuous processing:")
    print(f"- Batch size: {config['monitoring']['batch_size']} locations")
    print(f"- Batch delay: {config['monitoring']['batch_delay']} seconds")
    print("\nMapLeads will now continuously cycle through all locations")

def main():
    # Find config file
    config_paths = [
        Path('config/config.json'),
        Path(__file__).parent / 'config' / 'config.json',
        Path.home() / '.mapleads' / 'config.json'
    ]
    
    config_path = None
    for path in config_paths:
        if path.exists():
            config_path = path
            break
    
    if not config_path:
        print("❌ No configuration file found!")
        print("Please run 'python mapleads.py setup' first")
        sys.exit(1)
    
    print(f"Found configuration at: {config_path}")
    
    # Check if already migrated
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    if 'monitoring' in config and 'batch_size' in config['monitoring'] and 'category' in config['monitoring']:
        print("✅ Configuration already migrated to continuous processing mode!")
        return
    
    # Migrate
    migrate_config(config_path)

if __name__ == "__main__":
    main()
