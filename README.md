# MapLeads 🗺️

Automatically find new businesses as they appear on Google Maps. Perfect for contractors, service providers, and B2B sales teams looking for fresh leads in their target markets.

## 🎯 Key Features

- **New Business Detection**: Automatically finds businesses that just started listing on Google Maps
- **Multi-Category Monitoring**: Track gyms, restaurants, contractors, or any business type
- **Geographic Flexibility**: Monitor specific cities, states, or the entire country
- **Daily Monitoring**: Run continuously to catch new listings as they appear
- **SQLite Database**: Simple, no-setup-required data storage
- **Export Options**: CSV, JSON, and Excel export
- **Parallel Processing**: Use multiple browsers for faster data collection

## 🚀 Quick Start

### For Non-Technical Users (Easiest)

1. **Download MapLeads**:
   - Click the green "Code" button → "Download ZIP"
   - Extract the ZIP file to your Desktop
   - Open Terminal (Mac) or Command Prompt (Windows)
   - Navigate to the folder: `cd Desktop/MapLeads-main`

2. **One-Click Installation**:
   ```bash
   ./install.sh
   ```

3. **Set Up Your Preferences**:
   ```bash
   ./run.sh setup
   ```

4. **Start Finding Leads**:
   ```bash
   ./run.sh
   ```

### For Technical Users

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

## 🎮 Easy Commands (Non-Technical)

- `./run.sh setup` - Set up MapLeads for the first time
- `./run.sh` - Start finding new businesses
- `./run.sh status` - See what you've found so far
- `./run.sh export` - Save your leads to a CSV file
- `./run.sh test` - Quick test to make sure everything works
- `./run.sh category plumber` - Change what type of business to find
- `./run.sh instances 3` - Use 3 browsers for faster results
- `./run.sh categories` - See all available business types

## 🎮 Technical Commands

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

## 🆘 Common Issues & Solutions

### Installation Problems

**"Python 3 not found"**
- **Mac**: Install from [python.org](https://python.org) or use Homebrew: `brew install python3`
- **Windows**: Download from [python.org](https://python.org) and check "Add to PATH"
- **Linux**: `sudo apt install python3` (Ubuntu) or `sudo yum install python3` (CentOS)

**"Permission denied"**
```bash
chmod +x install.sh
chmod +x run.sh
```

**"Virtual environment creation failed"**
- Make sure you have enough disk space (at least 1GB free)
- Try: `python3 -m pip install --user virtualenv`

### Running Problems

**"No businesses found"**
- Try a different category: `./run.sh category electrician`
- Test with a more common category first: `./run.sh category restaurant`
- Check your internet connection

**"Chrome driver issues"**
- Make sure Google Chrome is installed
- Restart your computer and try again
- Close all Chrome windows before running MapLeads

**"Too slow"**
- Use more browser instances: `./run.sh instances 3`
- Make sure you have at least 4GB RAM for multiple instances

**"Memory issues"**
- Reduce browser instances: `./run.sh instances 1`
- Close other programs while running MapLeads

### Getting Help

1. Try running: `./run.sh test` to diagnose issues
2. Check the error message carefully
3. Restart your computer and try again
4. Create an issue on GitHub with the error message

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
