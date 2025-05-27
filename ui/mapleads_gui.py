import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sqlite3
import json
import threading
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the src directory to the path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from database import Database
from config_manager import ConfigManager
from exporter import export_businesses

class MapLeadsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MapLeads - Lead Generation Tool")
        self.root.geometry("1200x800")
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.db_manager = Database()
        
        # Process management
        self.process_running = False
        self.current_process = None
        
        # Create main interface
        self.create_widgets()
        self.load_config()
        self.refresh_database_view()
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_config_tab()
        self.create_database_tab()
        self.create_operations_tab()
        self.create_logs_tab()
        
    def create_config_tab(self):
        # Configuration Tab
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        
        # Main config frame with scrollbar
        canvas = tk.Canvas(config_frame)
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Search Configuration
        search_group = ttk.LabelFrame(scrollable_frame, text="Search Configuration", padding=10)
        search_group.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_group, text="Search Query:").grid(row=0, column=0, sticky='w', pady=2)
        self.search_query = tk.StringVar()
        ttk.Entry(search_group, textvariable=self.search_query, width=50).grid(row=0, column=1, sticky='ew', pady=2)
        
        ttk.Label(search_group, text="Location:").grid(row=1, column=0, sticky='w', pady=2)
        self.location = tk.StringVar()
        ttk.Entry(search_group, textvariable=self.location, width=50).grid(row=1, column=1, sticky='ew', pady=2)
        
        search_group.grid_columnconfigure(1, weight=1)
        
        # Advanced Settings
        advanced_group = ttk.LabelFrame(scrollable_frame, text="Advanced Settings", padding=10)
        advanced_group.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(advanced_group, text="Browser Instances:").grid(row=0, column=0, sticky='w', pady=2)
        self.browser_instances = tk.IntVar(value=1)
        ttk.Spinbox(advanced_group, from_=1, to=10, textvariable=self.browser_instances, width=10).grid(row=0, column=1, sticky='w', pady=2)
        
        ttk.Label(advanced_group, text="Delay Between Searches (seconds):").grid(row=1, column=0, sticky='w', pady=2)
        self.delay = tk.DoubleVar(value=2.0)
        ttk.Spinbox(advanced_group, from_=0.5, to=10.0, increment=0.5, textvariable=self.delay, width=10).grid(row=1, column=1, sticky='w', pady=2)
        
        ttk.Label(advanced_group, text="Max Results Per Search:").grid(row=2, column=0, sticky='w', pady=2)
        self.max_results = tk.IntVar(value=100)
        ttk.Spinbox(advanced_group, from_=10, to=1000, increment=10, textvariable=self.max_results, width=10).grid(row=2, column=1, sticky='w', pady=2)
        
        self.headless_mode = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_group, text="Headless Mode", variable=self.headless_mode).grid(row=3, column=0, columnspan=2, sticky='w', pady=2)
        
        # Notification Settings
        notify_group = ttk.LabelFrame(scrollable_frame, text="Notifications", padding=10)
        notify_group.pack(fill='x', padx=5, pady=5)
        
        self.enable_notifications = tk.BooleanVar()
        ttk.Checkbutton(notify_group, text="Enable Notifications", variable=self.enable_notifications).grid(row=0, column=0, columnspan=2, sticky='w', pady=2)
        
        ttk.Label(notify_group, text="Webhook URL:").grid(row=1, column=0, sticky='w', pady=2)
        self.webhook_url = tk.StringVar()
        ttk.Entry(notify_group, textvariable=self.webhook_url, width=50).grid(row=1, column=1, sticky='ew', pady=2)
        
        notify_group.grid_columnconfigure(1, weight=1)
        
        # Save Configuration Button
        ttk.Button(scrollable_frame, text="Save Configuration", command=self.save_config).pack(pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_database_tab(self):
        # Database Tab
        db_frame = ttk.Frame(self.notebook)
        self.notebook.add(db_frame, text="Database View")
        
        # Control frame
        control_frame = ttk.Frame(db_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Refresh", command=self.refresh_database_view).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Export CSV", command=self.export_csv).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Export JSON", command=self.export_json).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Delete Selected", command=self.delete_selected_rows).pack(side='left', padx=5)
        
        # Search frame
        search_frame = ttk.Frame(db_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Filter:").pack(side='left', padx=5)
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self.filter_database_view)
        ttk.Entry(search_frame, textvariable=self.filter_var, width=30).pack(side='left', padx=5)
        
        ttk.Label(search_frame, text="Column:").pack(side='left', padx=5)
        self.filter_column = ttk.Combobox(search_frame, width=15, state="readonly")
        self.filter_column.pack(side='left', padx=5)
        
        # Database view
        tree_frame = ttk.Frame(db_frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame, selectmode='extended')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and treeview
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(db_frame, textvariable=self.status_var, relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')
        
    def create_operations_tab(self):
        # Operations Tab
        ops_frame = ttk.Frame(self.notebook)
        self.notebook.add(ops_frame, text="Operations")
        
        # Operation buttons frame
        button_frame = ttk.LabelFrame(ops_frame, text="MapLeads Operations", padding=10)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        # First row of buttons
        row1 = ttk.Frame(button_frame)
        row1.pack(fill='x', pady=5)
        
        ttk.Button(row1, text="Setup MapLeads", command=self.run_setup, width=20).pack(side='left', padx=5)
        ttk.Button(row1, text="Create Baseline", command=self.run_baseline, width=20).pack(side='left', padx=5)
        ttk.Button(row1, text="Start Monitoring", command=self.start_monitoring, width=20).pack(side='left', padx=5)
        
        # Second row of buttons
        row2 = ttk.Frame(button_frame)
        row2.pack(fill='x', pady=5)
        
        ttk.Button(row2, text="Stop Monitoring", command=self.stop_monitoring, width=20).pack(side='left', padx=5)
        ttk.Button(row2, text="Test Configuration", command=self.test_config, width=20).pack(side='left', padx=5)
        ttk.Button(row2, text="Clear Database", command=self.clear_database, width=20).pack(side='left', padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(ops_frame, text="Operation Status", padding=10)
        status_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.operation_status = tk.StringVar()
        self.operation_status.set("Idle")
        ttk.Label(status_frame, textvariable=self.operation_status, font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)
        
    def create_logs_tab(self):
        # Logs Tab
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Log controls
        log_controls = ttk.Frame(logs_frame)
        log_controls.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(log_controls, text="Clear Logs", command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(log_controls, text="Save Logs", command=self.save_logs).pack(side='left', padx=5)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=20)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_manager.config_exists():
                config = self.config_manager.load_config()
            else:
                config = self.config_manager.get_default_config()
            
            # Load search configuration
            monitoring = config.get('monitoring', {})
            self.search_query.set(monitoring.get('category', ''))
            
            locations = monitoring.get('locations', {})
            # Combine states and cities for display
            location_parts = []
            if locations.get('states'):
                location_parts.extend(locations['states'])
            if locations.get('cities'):
                location_parts.extend(locations['cities'])
            self.location.set(', '.join(location_parts))
            
            # Load advanced settings - use defaults since they're not in current config
            self.browser_instances.set(1)
            self.delay.set(2.0)
            self.max_results.set(100)
            self.headless_mode.set(True)
            
            # Load notification settings
            notifications = config.get('notifications', {})
            webhook = notifications.get('webhook', {})
            self.enable_notifications.set(webhook.get('enabled', False))
            self.webhook_url.set(webhook.get('url', ''))
            
            self.log_message("Configuration loaded successfully")
            
        except Exception as e:
            self.log_message(f"Error loading configuration: {str(e)}")
            # Set defaults
            config = self.config_manager.get_default_config()
            self.search_query.set(config['monitoring']['category'])
            self.location.set(', '.join(config['monitoring']['locations']['states']))
            
    def save_config(self):
        """Save configuration to file"""
        try:
            # Parse location input
            location_input = self.location.get().strip()
            states = []
            cities = []
            
            if location_input:
                # Simple parsing - assume comma-separated values
                # For now, treat all as states (could be enhanced)
                locations = [loc.strip() for loc in location_input.split(',')]
                states = locations  # Simplified for now
            
            config = {
                'monitoring': {
                    'category': self.search_query.get(),
                    'locations': {
                        'states': states,
                        'cities': cities,
                        'min_population': 0
                    },
                    'batch_size': 10,
                    'batch_delay': 60
                },
                'notifications': {
                    'webhook': {
                        'enabled': self.enable_notifications.get(),
                        'url': self.webhook_url.get() if self.webhook_url.get() else None,
                        'headers': {}
                    },
                    'email': {
                        'enabled': False
                    },
                    'filters': {
                        'only_with_reviews': False,
                        'only_without_reviews': False,
                        'only_with_website': False
                    }
                }
            }
            
            self.config_manager.save_config(config)
            self.log_message("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            error_msg = f"Error saving configuration: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def refresh_database_view(self):
        """Refresh the database view"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Get data from database using the Database class
            businesses = self.db_manager.get_recent_businesses(limit=10000)
            
            if not businesses:
                self.status_var.set("No records found")
                return
            
            # Get column names from the first business record
            columns = list(businesses[0].keys())
            
            # Configure treeview columns
            self.tree['columns'] = columns
            self.tree['show'] = 'headings'
            
            # Configure column headings and widths
            for col in columns:
                self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
                self.tree.column(col, width=120, minwidth=80)
                
            # Update filter column combobox
            self.filter_column['values'] = columns
            if columns:
                self.filter_column.set(columns[0])
                
            # Insert data into treeview
            for business in businesses:
                # Convert datetime objects to strings for display
                row_values = []
                for col in columns:
                    value = business.get(col, '')
                    if hasattr(value, 'strftime'):  # datetime object
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    row_values.append(value)
                self.tree.insert('', 'end', values=row_values)
            
            # Update status
            self.status_var.set(f"Loaded {len(businesses)} records")
            self.log_message(f"Database view refreshed - {len(businesses)} records loaded")
            
        except Exception as e:
            error_msg = f"Error refreshing database view: {str(e)}"
            self.log_message(error_msg)
            self.status_var.set("Error loading data")
            
    def filter_database_view(self, *args):
        """Filter database view based on search criteria"""
        filter_text = self.filter_var.get().lower()
        filter_col = self.filter_column.get()
        
        if not filter_text:
            self.refresh_database_view()
            return
            
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Get column index
            columns = list(self.tree['columns'])
            if filter_col not in columns:
                return
                
            # Get filtered data
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            query = f"SELECT * FROM businesses WHERE LOWER({filter_col}) LIKE ? ORDER BY created_date DESC"
            cursor.execute(query, (f'%{filter_text}%',))
            rows = cursor.fetchall()
            
            # Insert filtered data
            for row in rows:
                self.tree.insert('', 'end', values=row)
                
            conn.close()
            self.status_var.set(f"Filtered: {len(rows)} records")
            
        except Exception as e:
            self.log_message(f"Error filtering data: {str(e)}")
            
    def sort_column(self, col):
        """Sort treeview by column"""
        try:
            data = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
            data.sort()
            
            for index, (val, item) in enumerate(data):
                self.tree.move(item, '', index)
                
        except Exception as e:
            self.log_message(f"Error sorting column: {str(e)}")
            
    def delete_selected_rows(self):
        """Delete selected rows from database"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No rows selected")
            return
            
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete {len(selected_items)} selected row(s)?")
        
        if result:
            try:
                conn = sqlite3.connect(self.db_manager.db_path)
                cursor = conn.cursor()
                
                # Assuming first column is ID
                columns = list(self.tree['columns'])
                id_col = columns[0] if columns else 'id'
                
                for item in selected_items:
                    values = self.tree.item(item)['values']
                    if values:
                        cursor.execute(f"DELETE FROM businesses WHERE {id_col} = ?", (values[0],))
                        
                conn.commit()
                conn.close()
                
                self.refresh_database_view()
                self.log_message(f"Deleted {len(selected_items)} records")
                
            except Exception as e:
                error_msg = f"Error deleting records: {str(e)}"
                self.log_message(error_msg)
                messagebox.showerror("Error", error_msg)
                
    def export_csv(self):
        """Export database to CSV"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if file_path:
                # Get all businesses from database (using high limit)
                businesses = self.db_manager.get_recent_businesses(limit=10000)
                export_businesses(businesses, file_path, 'csv')
                self.log_message(f"Data exported to CSV: {file_path}")
                messagebox.showinfo("Success", f"Data exported to {file_path}")
                
        except Exception as e:
            error_msg = f"Error exporting to CSV: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def export_json(self):
        """Export database to JSON"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                # Get all businesses from database (using high limit)
                businesses = self.db_manager.get_recent_businesses(limit=10000)
                export_businesses(businesses, file_path, 'json')
                self.log_message(f"Data exported to JSON: {file_path}")
                messagebox.showinfo("Success", f"Data exported to {file_path}")
                
        except Exception as e:
            error_msg = f"Error exporting to JSON: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def run_setup(self):
        """Run MapLeads setup"""
        self.run_command("setup", "Running MapLeads setup...")
        
    def run_baseline(self):
        """Run baseline creation"""
        self.run_command("baseline", "Creating baseline...")
        
    def start_monitoring(self):
        """Start monitoring for new leads"""
        if self.process_running:
            messagebox.showwarning("Warning", "A process is already running")
            return
            
        self.run_command("run", "Starting monitoring...")
        
    def stop_monitoring(self):
        """Stop current monitoring process"""
        if self.current_process and self.process_running:
            self.current_process.terminate()
            self.process_running = False
            self.progress.stop()
            self.operation_status.set("Stopped")
            self.log_message("Monitoring stopped by user")
        else:
            messagebox.showinfo("Info", "No process is currently running")
            
    def test_config(self):
        """Test current configuration"""
        self.log_message("Testing configuration...")
        try:
            if self.config_manager.config_exists():
                config = self.config_manager.load_config()
            else:
                self.log_message("❌ No configuration file found")
                messagebox.showwarning("Configuration Test", "No configuration found. Please save configuration first.")
                return
            
            # Basic validation
            monitoring = config.get('monitoring', {})
            if not monitoring.get('category'):
                self.log_message("❌ Search category is required")
                return
                
            locations = monitoring.get('locations', {})
            if not locations.get('states') and not locations.get('cities'):
                self.log_message("❌ At least one location (state or city) is required")
                return
                
            self.log_message("✅ Configuration appears valid")
            self.log_message(f"✅ Search Category: {monitoring.get('category')}")
            
            location_info = []
            if locations.get('states'):
                location_info.append(f"States: {', '.join(locations['states'])}")
            if locations.get('cities'):
                location_info.append(f"Cities: {', '.join(locations['cities'])}")
            self.log_message(f"✅ Locations: {' | '.join(location_info)}")
            
            notifications = config.get('notifications', {})
            webhook = notifications.get('webhook', {})
            if webhook.get('enabled'):
                self.log_message(f"✅ Webhook enabled: {webhook.get('url')}")
            else:
                self.log_message("ℹ️ Webhook notifications disabled")
            
            messagebox.showinfo("Configuration Test", "Configuration test completed - check logs for details")
            
        except Exception as e:
            error_msg = f"Configuration test failed: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Configuration Test", error_msg)
        
    def clear_database(self):
        """Clear all data from database"""
        result = messagebox.askyesno("Confirm Clear", 
                                   "Are you sure you want to clear ALL data from the database? This cannot be undone.")
        
        if result:
            try:
                conn = sqlite3.connect(self.db_manager.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM businesses")
                conn.commit()
                conn.close()
                
                self.refresh_database_view()
                self.log_message("Database cleared successfully")
                messagebox.showinfo("Success", "Database cleared successfully")
                
            except Exception as e:
                error_msg = f"Error clearing database: {str(e)}"
                self.log_message(error_msg)
                messagebox.showerror("Error", error_msg)
                
    def run_command(self, command, status_message):
        """Run a MapLeads command in a separate thread"""
        if self.process_running:
            messagebox.showwarning("Warning", "A process is already running")
            return
            
        def run_in_thread():
            try:
                self.process_running = True
                self.operation_status.set(status_message)
                self.progress.start()
                
                # Run the command
                cmd = [sys.executable, "mapleads.py", command]
                self.current_process = subprocess.Popen(
                    cmd,
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Read output in real-time
                for line in self.current_process.stdout:
                    self.root.after(0, lambda l=line.strip(): self.log_message(l))
                    
                self.current_process.wait()
                
                if self.current_process.returncode == 0:
                    self.root.after(0, lambda: self.operation_status.set("Completed successfully"))
                    self.root.after(0, lambda: self.log_message(f"Command '{command}' completed successfully"))
                else:
                    self.root.after(0, lambda: self.operation_status.set("Completed with errors"))
                    self.root.after(0, lambda: self.log_message(f"Command '{command}' completed with errors"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.operation_status.set("Error"))
                self.root.after(0, lambda: self.log_message(f"Error running command '{command}': {str(e)}"))
                
            finally:
                self.process_running = False
                self.root.after(0, lambda: self.progress.stop())
                self.current_process = None
                
                # Refresh database view if it was a data-changing operation
                if command in ['baseline', 'run']:
                    self.root.after(1000, self.refresh_database_view)
                    
        # Start thread
        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()
        
    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
    def clear_logs(self):
        """Clear log display"""
        self.log_text.delete(1.0, tk.END)
        
    def save_logs(self):
        """Save logs to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                    
                messagebox.showinfo("Success", f"Logs saved to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving logs: {str(e)}")

def main():
    root = tk.Tk()
    
    # Set window icon if available (optional)
    try:
        # You can add an icon file later
        pass
    except:
        pass
    
    app = MapLeadsGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
