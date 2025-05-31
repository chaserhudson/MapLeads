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

3. **Launch Web Interface** (Easiest):
   ```bash
   ./run.sh ui
   ```
   This opens a user-friendly web interface at http://localhost:8080 where you can:
   - Configure settings with a simple form
   - View your leads in a sortable table
   - Start/stop monitoring with buttons
   - Export data with one click

   **OR use command line**:
   ```bash
   ./run.sh setup  # Set up preferences
   ./run.sh        # Start finding leads
   ```

### ⚠️ **Important First-Time Setup Notes**

**Your first run establishes a baseline** - this means MapLeads will scan your chosen areas and save all existing businesses to its database. **You won't see "new" businesses on the first run** because everything is new to the empty database.

**On your second and subsequent runs**, MapLeads will compare against this baseline and only show you truly NEW businesses that weren't there before.

**⏱️ Expected Initial Scan Times:**
- **Single State (e.g., California)**: 30-60 minutes
- **Multiple States (e.g., CA, TX, FL)**: 2-4 hours  
- **Nationwide + High Population (50k+)**: 4-8 hours
- **Nationwide + No Population Limit**: 8-24 hours (40,000+ zip codes!)

💡 **Tip**: Start with a single state and higher population limit (100k+) for your first test run.

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

## 👀 Viewing Your Data While Monitoring

**While MapLeads is running**, you can view your data in a second terminal window:

1. **Open a new Terminal/Command Prompt window**
2. **Navigate to your MapLeads folder**: `cd Desktop/MapLeads-main`
3. **Check your statistics**: `./run.sh status`
4. **Export your data**: `./run.sh export`
5. **View recent discoveries**: Look for the CSV file in your folder

**Don't stop the monitoring window** - let it keep running to find new businesses!

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

## 🔄 Understanding How MapLeads Works

### First Run (Baseline Establishment)
- **What happens**: MapLeads scans all locations and saves every business it finds
- **What you'll see**: Hundreds or thousands of businesses added to your database
- **Important**: These are NOT "new" businesses - they're just new to your database
- **Time required**: See timing estimates above

### Second Run Onwards (True New Business Detection)
- **What happens**: MapLeads compares current scan against your baseline
- **What you'll see**: Only businesses that weren't there before (truly NEW businesses)
- **Typical results**: 0-50 new businesses per run (depending on your area/category)
- **Time required**: Much faster since it's just checking for changes

### What Makes a Business "New"?
- Business just created their Google Maps listing
- Business just started appearing in search results for your category
- Business recently opened and is now discoverable online

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

### Web Interface (Recommended for Beginners)
- `./run.sh ui` - **Launch web interface** (easiest way to use MapLeads!)

### Command Line Options  
- `./run.sh setup` - Set up MapLeads for the first time
- `./run.sh` - Start finding new businesses
- `./run.sh status` - See what you've found so far
- `./run.sh export` - Save your leads to a CSV file
- `./run.sh test` - Quick test to make sure everything works
- `./run.sh category plumber` - Change what type of business to find
- `./run.sh instances 3` - Use 3 browsers for faster results
- `./run.sh categories` - See all available business types
- `./run.sh help` - Show all available commands

## 📋 Best Practices for New Users

### Start Small
1. **Choose 1-2 states** instead of nationwide for your first run
2. **Set minimum population to 100,000+** to reduce scan time
3. **Use 2-3 browser instances** for faster results (if you have 4GB+ RAM)

### Monitor Progress
- Watch the terminal for progress updates
- Each location shows how many businesses were found
- New businesses are marked with ✨ when discovered

### Check Your Results
- Run `./run.sh status` to see total businesses found
- Run `./run.sh export` to save your leads to CSV
- Open the CSV file in Excel or Google Sheets to view/sort your leads

### Optimize Performance
- **Faster**: Increase browser instances (`./run.sh instances 3`)
- **Slower but safer**: Use 1 browser instance if you have memory issues
- **Target better**: Increase minimum population or focus on specific states

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

## 🌐 Web Interface Guide

### 🚀 Getting Started with the Web UI

1. **Launch the Interface**:
   ```bash
   ./run.sh ui
   ```
   This will:
   - Start a local web server
   - Automatically open your browser to http://localhost:5000
   - Show the MapLeads dashboard

2. **First-Time Setup**:
   - Click "Configuration" in the sidebar
   - Choose your business category (e.g., "plumber", "electrician")
   - Select monitoring scope (Nationwide, specific states, or cities)
   - Set minimum population and browser instances
   - Click "Save Configuration"

3. **Start Monitoring**:
   - Go back to "Dashboard"
   - Click the green "Start" button in the sidebar
   - Watch the real-time progress and statistics

### 📋 Web Interface Features

**Dashboard**:
- Overview statistics (total businesses, new this week/month)
- Current configuration summary
- Real-time monitoring status
- Recent business discoveries

**Businesses View**:
- Sortable table of all discovered businesses
- Filter by date range (last 7/30/90 days, all time)
- Shows name, phone, category, location, reviews, and discovery date

**Configuration**:
- Easy form-based setup (no JSON editing needed)
- Business category dropdown with popular options
- Location scope selection with helpful guidance
- Performance settings (browser instances, batch size)

**Export Data**:
- Choose format: CSV, JSON, or Excel
- Select time period for export
- One-click download of your leads

### 💻 Web UI vs Command Line

| Feature | Web UI | Command Line |
|---------|--------|--------------|
| **Ease of Use** | 🟢 Very Easy | 🟡 Technical |
| **Setup** | 🟢 Point & Click | 🟡 Text Commands |
| **View Data** | 🟢 Visual Table | 🟡 Text Output |
| **Real-time Stats** | 🟢 Live Dashboard | 🟡 Manual Check |
| **Export** | 🟢 One Click | 🟡 Commands |
| **Start/Stop** | 🟢 Buttons | 🟡 Terminal Control |

💡 **Recommendation**: Use the Web UI if you're new to MapLeads or prefer visual interfaces!

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
