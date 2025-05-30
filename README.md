# MapLeads 🗺️

Open-source B2B lead generation tool that monitors Google Maps for new business listings in your target market.

## 🎯 Key Features

- **New Business Detection**: Automatically finds businesses that just started listing on Google Maps
- **Multi-Category Monitoring**: Track gyms, restaurants, contractors, or any business type
- **Geographic Flexibility**: Monitor specific cities, states, or the entire country
- **Daily Monitoring**: Run continuously to catch new listings as they appear
- **SQLite Database**: Simple, no-setup-required data storage
- **Export Options**: CSV, JSON, and Excel export
- **Parallel Processing**: Use multiple browsers for faster data collection

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/chaserhudson/MapLeads.git
cd MapLeads

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run interactive setup
python mapleads.py setup

# Start monitoring
python mapleads.py run
```

## 📖 Use Cases

- **Service Providers**: Find new gyms to sell equipment or services
- **B2B Software**: Identify new service businesses for your software solutions
- **Contractors**: Discover new businesses that might need renovations
- **Marketing Agencies**: Track new businesses that need marketing services
- **Local Services**: Monitor competitors or potential partners in your area

## 📝 Category Notes

**Best Performance**: Home services (plumber, electrician, HVAC, contractor, etc.) work exceptionally well as phone numbers are readily visible in search results.

**Limited Support**: Restaurants, cafes, and food businesses may have incomplete phone number extraction since Google Maps often requires clicking individual business cards to access contact details.

## 🔧 Configuration

MapLeads uses a simple JSON configuration that you can set up interactively:

```json
{
  "monitoring": {
    "category": "plumber",
    "locations": {
      "states": ["CA", "TX"],
      "cities": ["Los Angeles", "Houston"],
      "min_population": 50000
    },
    "batch_size": 10,
    "browser_instances": 1
  }
}
```

## 🎯 Finding New Businesses

MapLeads excels at identifying newly established businesses by:

- **Daily Monitoring**: Catch businesses within days of their Google Maps listing
- **Historical Comparison**: Only shows you businesses not seen in previous scans
- **First-Mover Advantage**: Reach out to new businesses before your competitors

## 📊 How It Works

1. **Continuous Monitoring**: MapLeads regularly scans Google Maps based on your configuration
2. **Change Detection**: Compares results with previous scans to identify new listings
3. **Data Storage**: Keeps a local history for analysis and export

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
   
   # Create virtual environment (recommended)
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   pip install -r requirements.txt
   ```

2. **Run Interactive Setup**:
   ```bash
   python mapleads.py setup
   ```
   This will guide you through:
   - Selecting business categories to monitor
   - Choosing geographic areas
   - Configuring advanced settings

3. **Start Monitoring**:
   ```bash
   python mapleads.py run
   ```

## 🎮 Commands

- `python mapleads.py setup` - Interactive configuration wizard
- `python mapleads.py run` - Start monitoring with current config
- `python mapleads.py test` - Run a test scan
- `python mapleads.py status` - View monitoring statistics
- `python mapleads.py export` - Export data to CSV/JSON
- `python mapleads.py categories` - List available business categories


## 📈 Advanced Usage

### Custom Categories
```python
# Set custom search term in config.json
"category": "dog groomer"
```

### Parallel Processing
```bash
# Use 3 parallel browsers for faster scanning
python mapleads.py instances 3
python mapleads.py run
```

**Performance Impact**: 2-3 instances provide 2-3x faster scanning. Higher instances (4-5) offer greater speed but require more system resources (4GB+ RAM recommended).


### Scheduling
```bash
# Run with cron (Linux/Mac)
0 9 * * * cd /path/to/MapLeads && python mapleads.py run --headless

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
