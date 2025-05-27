# MapLeads GUI Documentation

The MapLeads GUI provides a comprehensive graphical interface for all MapLeads functionality, making it easier to configure, monitor, and manage your lead generation operations.

## 🚀 Getting Started

Launch the GUI with:
```bash
python run_gui.py
```

## 📋 Interface Overview

The GUI is organized into four main tabs:

### 1. Configuration Tab
- **Search Configuration**: Set your search query and target locations
- **Advanced Settings**: Configure browser instances, delays, and result limits
- **Notification Settings**: Set up webhooks and alert preferences
- **Save/Load**: Persist your configuration settings

### 2. Database View Tab
- **Full Database Access**: View all discovered businesses in a sortable table
- **Real-time Filtering**: Search by any column (name, location, category, etc.)
- **Batch Operations**: Select and delete multiple records
- **Export Functions**: Direct CSV/JSON export from the interface
- **Status Bar**: Shows record counts and operation status

### 3. Operations Tab
- **Core Operations**: Setup, baseline creation, and monitoring
- **Process Management**: Start/stop operations with visual feedback
- **Progress Tracking**: Real-time progress bars and status updates
- **Database Management**: Clear database and test configuration

### 4. Logs Tab
- **Real-time Output**: See command output and system messages
- **Log Management**: Save logs to file or clear the display
- **Timestamps**: All messages include timing information

## 🎯 Key Features

### Database Management
- **Sortable Columns**: Click column headers to sort data
- **Advanced Filtering**: Filter by any field using the search box
- **Bulk Operations**: Select multiple rows for deletion
- **Export Options**: Save filtered results to CSV or JSON

### Process Control
- **Thread-safe Operations**: Long-running tasks don't freeze the interface
- **Real-time Updates**: Database refreshes automatically after operations
- **Process Termination**: Stop monitoring processes safely
- **Status Monitoring**: Visual indicators for all operations

### Configuration Management
- **Visual Editor**: No need to edit JSON files manually
- **Validation**: Built-in configuration testing
- **Persistence**: Settings automatically saved and loaded
- **Error Handling**: Clear error messages and recovery options

## 🔧 Troubleshooting

### Common Issues

**GUI won't start:**
- Ensure Python 3.8+ is installed
- Check that tkinter is available (included with most Python installations)
- Run `python run_gui.py` from the MapLeads directory

**Database not loading:**
- Verify the database file exists in the `data/` directory
- Check file permissions
- Run the setup process first if it's a new installation

**Configuration not saving:**
- Ensure write permissions to the `config/` directory
- Check for valid JSON in configuration fields
- Verify all required fields are filled

### Performance Tips

- Use fewer browser instances on slower machines
- Increase delays between searches if experiencing rate limiting
- Filter database results when viewing large datasets
- Clear logs periodically to improve performance

## 🆚 GUI vs CLI

| Feature | GUI | CLI |
|---------|-----|-----|
| Ease of Use | ✅ Visual interface | ⚡ Quick commands |
| Database Viewing | ✅ Full table view | ❌ Export only |
| Real-time Logs | ✅ Built-in viewer | ❌ File-based |
| Configuration | ✅ Visual editor | ⚡ Direct JSON |
| Automation | ❌ Manual operation | ✅ Scriptable |
| Resource Usage | 📊 Higher | ⚡ Lower |

## 🎨 Customization

The GUI is built with tkinter and can be customized:

- **Themes**: Modify the UI appearance in `ui/mapleads_gui.py`
- **Layout**: Adjust window sizes and component placement
- **Features**: Add new tabs or functionality as needed

## 📊 Data Export

The GUI provides multiple export options:

1. **CSV Export**: Structured data for spreadsheet analysis
2. **JSON Export**: Machine-readable format for further processing
3. **Filtered Exports**: Export only the currently filtered results
4. **Log Export**: Save operational logs for debugging

## 🔄 Workflow Integration

The GUI integrates seamlessly with the CLI workflow:

1. **Setup**: Use GUI for initial configuration
2. **Baseline**: Create baseline through GUI or CLI
3. **Monitoring**: Run monitoring via GUI or automate with CLI
4. **Analysis**: Use GUI database viewer for data analysis
5. **Export**: Export results through GUI for reporting

This hybrid approach gives you the best of both worlds - ease of use for interactive tasks and automation capabilities for production workflows.
