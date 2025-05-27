# MapLeads 🗺️

Open-source B2B lead generation tool that monitors Google Maps for new business listings. Get notified when new businesses in your target market appear online.

## 🎯 Key Features

- **New Business Detection**: Automatically finds businesses that just started listing on Google Maps
- **Multi-Category Monitoring**: Track gyms, restaurants, contractors, or any business type
- **Geographic Flexibility**: Monitor specific cities, states, or the entire country
- **Daily Monitoring**: Run continuously to catch new listings as they appear
- **Smart Notifications**: Get alerted only for new businesses matching your criteria
- **SQLite Database**: Simple, no-setup-required data storage
- **Export Options**: CSV, JSON, and webhook integrations
- **Parallel Processing**: Use multiple browsers for faster data collection

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/chaserhudson/MapLeads.git
cd MapLeads

# Install dependencies
pip install -r requirements.txt

# Run interactive setup
python mapleads.py setup

# Establish baseline (first-time users)
python mapleads.py baseline

# Start monitoring
python mapleads.py run
```

## 🖥️ Graphical User Interface

MapLeads now includes a comprehensive GUI for easier management:

```bash
# Launch the GUI
python run_gui.py
```

### GUI Features

- **Configuration Tab**: Visual configuration editor with all CLI options
- **Database View**: Browse, filter, sort, and export all database records
- **Operations Tab**: Run all MapLeads operations (setup, baseline, monitoring) with progress tracking
- **Logs Tab**: Real-time command output and logging

### GUI Benefits

- **Visual Database Management**: View all discovered businesses in a sortable table
- **Real-time Filtering**: Search and filter businesses by any column
- **Export Integration**: Direct CSV/JSON export from the interface
- **Process Management**: Start/stop monitoring with visual feedback
- **Configuration Management**: Easy setup without command-line knowledge

## 📖 Use Cases

- **Service Providers**: Find new gyms to sell equipment or services
- **B2B Software**: Identify new restaurants for your POS system
- **Contractors**: Discover new businesses that might need renovations
- **Marketing Agencies**: Track new businesses that need marketing services
- **Local Services**: Monitor competitors or potential partners in your area

## 🔧 Configuration

MapLeads uses a simple JSON configuration that you can set up interactively:

```json
{
  "monitoring": {
    "categories": ["restaurant", "gym", "dentist"],
    "locations": {
      "states": ["CA", "TX"],
      "cities": ["Los Angeles", "Houston"],
      "min_population": 50000
    },
    "schedule": "daily"
  },
  "notifications": {
    "email": "your@email.com",
    "webhook": "https://your-webhook-url.com",
    "filters": {
      "only_with_reviews": false,
      "only_without_reviews": false,
      "only_with_website": true
    }
  }
}
```

## 🎯 Finding New Businesses

MapLeads excels at identifying newly established businesses by:

- **No Reviews Filter**: Use `only_without_reviews: true` to find businesses with no reviews yet - a strong indicator they're new
- **Daily Monitoring**: Catch businesses within days of their Google Maps listing
- **Historical Comparison**: Only alerts you about businesses not seen in previous scans
- **First-Mover Advantage**: Reach out to new businesses before your competitors

## 📊 How It Works

1. **Continuous Monitoring**: MapLeads regularly scans Google Maps based on your configuration
2. **Change Detection**: Compares results with previous scans to identify new listings
3. **Smart Filtering**: Applies your criteria to reduce noise
4. **Instant Alerts**: Notifies you through your preferred channel
5. **Data Storage**: Keeps a local history for analysis and export

## 🛠️ Installation

### Requirements
- Python 3.8+
- Chrome browser
- 2GB RAM minimum (4GB recommended for parallel mode)

### Detailed Setup

1. **Install MapLeads**:
   ```bash
   git clone https://github.com/chaserhudson/MapLeads.git
   cd MapLeads
   pip install -r requirements.txt
   ```

2. **Run Interactive Setup**:
   ```bash
   python mapleads.py setup
   ```
   This will guide you through:
   - Selecting business categories to monitor
   - Choosing geographic areas
   - Setting up notifications
   - Configuring scan frequency

3. **Establish Baseline** (First-time users):
   ```bash
   python mapleads.py baseline
   ```
   This populates your database with existing businesses so future scans can detect truly NEW businesses.

4. **Start Monitoring**:
   ```bash
   python mapleads.py run
   ```

## 🎮 Commands

- `python mapleads.py setup` - Interactive configuration wizard
- `python mapleads.py baseline` - Establish baseline (first-time users)
- `python mapleads.py run` - Start monitoring with current config
- `python mapleads.py test` - Run a test scan (10 searches)
- `python mapleads.py status` - View monitoring statistics
- `python mapleads.py export` - Export data to CSV/JSON
- `python mapleads.py categories` - List available business categories

### First-Time Setup

When running MapLeads for the first time, establish a baseline to avoid false positives:

```bash
# 1. Configure your preferences
python mapleads.py setup

# 2. Establish baseline (IMPORTANT for first-time users)
python mapleads.py baseline

# 3. Start monitoring for NEW businesses
python mapleads.py run
```

**Why baseline mode?** Without a baseline, every business will appear "new" since your database is empty. The baseline scan populates your database with existing businesses, so future scans can accurately detect genuinely new businesses that appear after your baseline.

## 📈 Advanced Usage

### Custom Categories
```python
# Add custom search terms to config.json
"categories": ["dog groomer", "pet store", "veterinarian"]
```

### Parallel Processing
```bash
# Use 3 parallel browsers for faster scanning
python mapleads.py run --parallel 3
```

### Webhook Integration
```python
# Configure webhook in config.json
"webhook": {
  "url": "https://your-app.com/new-leads",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN"
  }
}
```

### Scheduling
```bash
# Run with cron (Linux/Mac)
0 9 * * * cd /path/to/MapLeads && python mapleads.py run --headless

# Or use the built-in scheduler
python mapleads.py daemon
```

## 📊 Data Schema

Each business record includes:
- Business name
- Phone number
- Address
- Category
- Reviews count & rating
- Website (if available)
- First seen date
- Last updated date
- Geographic coordinates

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for legitimate business development purposes only. Users are responsible for complying with Google's Terms of Service and applicable laws. Be respectful of rate limits and use responsibly.

## 🙋 Support

- **Issues**: [GitHub Issues](https://github.com/chaserhudson/MapLeads/issues)
- **Discussions**: [GitHub Discussions](https://github.com/chaserhudson/MapLeads/discussions)
- **Wiki**: [Documentation Wiki](https://github.com/chaserhudson/MapLeads/wiki)

---

**Built with ❤️ for the B2B community**
