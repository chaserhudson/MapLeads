# MapLeads v2.0 - Parallel Processing Update

## 🚀 What's New

This major update introduces **parallel processing** capabilities to MapLeads, allowing you to run multiple browser instances simultaneously for significantly faster scraping performance.

### Key Features Added

1. **Multi-Browser Processing (1-5 instances)**
   - Configure 1-5 parallel browser instances
   - Dramatically reduces scanning time
   - Smart load distribution across instances

2. **Real-Time Progress Tracking**
   - Live progress display for each browser instance
   - See which locations each instance is processing
   - Track new businesses found per instance

3. **Thread-Safe Database Operations**
   - Concurrent database access with proper locking
   - No data conflicts between browser instances
   - Maintains data integrity during parallel operations

4. **Data Import/Export Enhancements**
   - Import existing business data from CSV, JSON, or Excel
   - Data validation during import
   - Duplicate detection and handling

5. **Dynamic Configuration**
   - Change browser instances on-the-fly with CLI commands
   - No need to restart monitoring when adjusting performance

## 🔄 Upgrading from Previous Version

### Option 1: Fresh Installation (Recommended)
1. **Export your existing data** (if you have any):
   ```bash
   python mapleads.py export --format csv --output my_backup.csv
   ```

2. **Update MapLeads**:
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

3. **Run new setup** (will create updated config):
   ```bash
   python mapleads.py setup
   ```

4. **Import your old data** (if you exported it):
   ```bash
   python mapleads.py import-data my_backup.csv
   ```

### Option 2: Manual Config Update
If you want to keep your existing configuration, add this to your `config/config.json`:

```json
{
  "monitoring": {
    "category": "your_category",
    "locations": { ... },
    "batch_size": 10,
    "batch_delay": 60,
    "browser_instances": 2
  }
}
```

## 📊 Performance Impact

| Browser Instances | Speed Increase | Resource Usage | Recommended For |
|------------------|----------------|----------------|-----------------|
| 1 | Baseline | Low | Small datasets, limited resources |
| 2 | ~2x faster | Medium | Balanced performance |
| 3 | ~3x faster | Medium-High | Most users |
| 4 | ~4x faster | High | Large datasets |
| 5 | ~5x faster | Very High | Maximum performance |

## 🛠️ New Commands

### Change Browser Instances
```bash
# Set specific number of instances
python mapleads.py instances 3

# Interactive selection
python mapleads.py instances
```

### Import Data
```bash
# Import from file
python mapleads.py import-data businesses.csv

# Validate without importing
python mapleads.py import-data --dry-run businesses.csv
```

### Export Data (Enhanced)
```bash
# Export last 30 days to CSV
python mapleads.py export --format csv --days 30

# Export to Excel
python mapleads.py export --format xlsx --output my_businesses.xlsx
```

## 🔧 Configuration Options

### Browser Instances
- **Range**: 1-5 instances
- **Default**: 1 instance
- **Recommendation**: Start with 2-3 instances
- **Memory Usage**: ~200-400MB per instance

### Setup Wizard Updates
The setup wizard now asks for:
- Number of browser instances (1-5)
- Performance vs resource usage preference

## 🚨 Important Notes

### System Requirements
- **RAM**: Minimum 2GB, recommended 4GB+ for multiple instances
- **CPU**: Multi-core recommended for parallel processing
- **Disk Space**: Temporary chrome profiles (~50MB per instance)

### Rate Limiting
- Delays between requests are maintained to avoid detection
- Each instance operates independently with built-in delays
- Total request rate is distributed across instances

### Database Compatibility
- Existing databases are fully compatible
- No data migration required
- Thread-safe operations ensure data integrity

## 🐛 Troubleshooting

### High Memory Usage
If you experience high memory usage:
```bash
# Reduce browser instances
python mapleads.py instances 1
```

### Chrome Driver Issues
If chrome drivers fail to start:
1. Close all Chrome instances
2. Clear temporary directories:
   ```bash
   rm -rf /tmp/chrome_instance_*
   ```
3. Restart MapLeads

### Performance Issues
For better performance:
1. Use headless mode (default)
2. Start with 2 instances and increase gradually
3. Monitor system resources during operation

## 📱 Data Migration Guide

### Exporting from Old Version
```bash
# Export all data
python mapleads.py export --format csv --days 9999

# Export specific timeframe
python mapleads.py export --format json --days 90
```

### Importing to New Version
```bash
# Validate first
python mapleads.py import-data --dry-run exported_data.csv

# Import if validation passes
python mapleads.py import-data exported_data.csv
```

### Required Import Fields
- `name` (business name)
- `phone` (phone number)
- `category` (business category)

### Optional Import Fields
- `reviews`, `rating`, `website`
- `city`, `state`, `zip_code`
- `latitude`, `longitude`

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** for error messages
2. **Try reducing browser instances** to 1
3. **Verify system resources** (RAM, CPU)
4. **Report issues** with detailed error messages

## 🎯 Best Practices

### For Maximum Performance
- Use 3-4 browser instances on powerful machines
- Monitor system resources during operation
- Use SSD storage for better performance

### For Stability
- Start with 1-2 instances
- Monitor for Chrome crashes or memory issues
- Use headless mode to reduce resource usage

### For Data Integrity
- Always export data before major updates
- Use dry-run flag when importing data
- Monitor database size and performance

---

**Happy lead generation with parallel processing! 🚀**

For questions or issues, please check the main README or create an issue on GitHub.