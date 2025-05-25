"""
Interactive setup wizard for MapLeads
Guides users through initial configuration
"""

from typing import List, Dict, Optional
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.panel import Panel
import json

from .config_manager import ConfigManager

console = Console()

class InteractiveSetup:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_default_config()
    
    def run(self) -> Path:
        """Run the interactive setup wizard"""
        console.print(Panel.fit(
            "[bold]This wizard will help you configure MapLeads for your needs.[/bold]\n\n"
            "You'll be asked to:\n"
            "1. Choose business categories to monitor\n"
            "2. Select geographic areas\n"
            "3. Configure notifications (optional)\n"
            "4. Set monitoring schedule",
            title="Setup Wizard"
        ))
        
        # Step 1: Categories
        self._setup_categories()
        
        # Step 2: Locations
        self._setup_locations()
        
        # Step 3: Schedule
        self._setup_schedule()
        
        # Step 4: Notifications
        self._setup_notifications()
        
        # Step 5: Advanced settings
        self._setup_advanced()
        
        # Show summary
        self._show_summary()
        
        # Save configuration
        if Confirm.ask("\nSave this configuration?", default=True):
            self.config_manager.save_config(self.config)
            console.print("[green]✅ Configuration saved![/green]")
            
            # Create example config too
            example_path = self.config_manager.create_example_config()
            console.print(f"[dim]Example config created at: {example_path}[/dim]")
            
            return self.config_manager.config_path
        else:
            console.print("[yellow]Configuration not saved. Exiting.[/yellow]")
            exit(0)
    
    def _setup_categories(self):
        """Setup business categories to monitor"""
        console.print("\n[bold cyan]Step 1: Business Categories[/bold cyan]")
        console.print("What types of businesses do you want to monitor?")
        
        # Show popular categories
        categories = {
            "1": ["restaurant", "cafe", "bar", "bakery"],
            "2": ["gym", "yoga studio", "fitness center"],
            "3": ["plumber", "electrician", "hvac", "contractor"],
            "4": ["dentist", "doctor", "chiropractor"],
            "5": ["auto repair", "mechanic", "car dealer"],
            "6": "Custom categories"
        }
        
        console.print("\nPopular category sets:")
        for key, value in categories.items():
            if key != "6":
                console.print(f"  {key}. {', '.join(value)}")
            else:
                console.print(f"  {key}. {value}")
        
        choice = Prompt.ask("\nSelect option (1-6) or enter custom categories", default="6")
        
        if choice in ["1", "2", "3", "4", "5"]:
            self.config['monitoring']['categories'] = categories[choice]
        else:
            # Custom categories
            custom = Prompt.ask("Enter categories separated by commas")
            self.config['monitoring']['categories'] = [
                cat.strip() for cat in custom.split(',') if cat.strip()
            ]
        
        console.print(f"[green]Selected categories: {', '.join(self.config['monitoring']['categories'])}[/green]")
    
    def _setup_locations(self):
        """Setup geographic locations to monitor"""
        console.print("\n[bold cyan]Step 2: Geographic Areas[/bold cyan]")
        
        # Choose scope
        scope = Prompt.ask(
            "Monitor scope",
            choices=["nationwide", "states", "cities"],
            default="states"
        )
        
        if scope == "nationwide":
            self.config['monitoring']['locations']['states'] = None
            self.config['monitoring']['locations']['cities'] = None
            console.print("[green]Monitoring: All US locations[/green]")
        
        elif scope == "states":
            states_input = Prompt.ask(
                "Enter state codes separated by commas (e.g., CA,TX,FL)",
                default="CA,TX"
            )
            states = [s.strip().upper() for s in states_input.split(',') if s.strip()]
            self.config['monitoring']['locations']['states'] = states
            self.config['monitoring']['locations']['cities'] = None
            console.print(f"[green]Monitoring states: {', '.join(states)}[/green]")
        
        else:  # cities
            cities_input = Prompt.ask(
                "Enter city names separated by commas",
                default="Los Angeles,Houston"
            )
            cities = [c.strip() for c in cities_input.split(',') if c.strip()]
            self.config['monitoring']['locations']['cities'] = cities
            self.config['monitoring']['locations']['states'] = None
            console.print(f"[green]Monitoring cities: {', '.join(cities)}[/green]")
        
        # Minimum population
        min_pop = IntPrompt.ask(
            "\nMinimum city population (0 for all sizes)",
            default=50000
        )
        self.config['monitoring']['locations']['min_population'] = min_pop
    
    def _setup_schedule(self):
        """Setup monitoring schedule"""
        console.print("\n[bold cyan]Step 3: Monitoring Schedule[/bold cyan]")
        
        schedule = Prompt.ask(
            "How often should MapLeads check for new businesses?",
            choices=["hourly", "daily", "weekly"],
            default="daily"
        )
        
        self.config['monitoring']['schedule'] = schedule
        console.print(f"[green]Schedule: {schedule} monitoring[/green]")
    
    def _setup_notifications(self):
        """Setup notification preferences"""
        console.print("\n[bold cyan]Step 4: Notifications (Optional)[/bold cyan]")
        
        if Confirm.ask("Do you want to set up notifications?", default=False):
            # Email notifications
            if Confirm.ask("\nSet up email notifications?", default=False):
                self.config['notifications']['email']['enabled'] = True
                self.config['notifications']['email']['email'] = Prompt.ask("Your email address")
                
                # For Gmail, provide app password instructions
                if "gmail" in self.config['notifications']['email']['email']:
                    console.print("[yellow]Note: For Gmail, use an App Password instead of your regular password[/yellow]")
                    console.print("[dim]See: https://support.google.com/accounts/answer/185833[/dim]")
                
                self.config['notifications']['email']['password'] = Prompt.ask("Email password", password=True)
                
                recipients = Prompt.ask("Recipient emails (comma-separated)", default=self.config['notifications']['email']['email'])
                self.config['notifications']['email']['recipients'] = [
                    r.strip() for r in recipients.split(',') if r.strip()
                ]
            
            # Webhook notifications
            if Confirm.ask("\nSet up webhook notifications?", default=False):
                self.config['notifications']['webhook']['enabled'] = True
                self.config['notifications']['webhook']['url'] = Prompt.ask("Webhook URL")
                
                if Confirm.ask("Add authorization header?", default=False):
                    auth = Prompt.ask("Authorization header value")
                    self.config['notifications']['webhook']['headers'] = {
                        "Authorization": auth
                    }
            
            # Filters
            console.print("\n[bold]Notification Filters[/bold]")
            self.config['notifications']['filters']['only_with_website'] = Confirm.ask(
                "Only notify for businesses with websites?", default=False
            )
            self.config['notifications']['filters']['only_with_reviews'] = Confirm.ask(
                "Only notify for businesses with reviews?", default=False
            )
            self.config['notifications']['filters']['only_without_reviews'] = Confirm.ask(
                "Only notify for businesses WITHOUT reviews (newer businesses)?", default=False
            )
            
            if Confirm.ask("Set minimum rating filter?", default=False):
                min_rating = Prompt.ask("Minimum rating (1-5)", default="4.0")
                self.config['notifications']['filters']['min_rating'] = float(min_rating)
    
    def _setup_advanced(self):
        """Setup advanced settings"""
        console.print("\n[bold cyan]Step 5: Advanced Settings[/bold cyan]")
        
        # Max URLs per scan
        max_urls = IntPrompt.ask(
            "Maximum locations to check per scan (higher = more thorough but slower)",
            default=100
        )
        self.config['monitoring']['max_urls'] = max_urls
    
    def _show_summary(self):
        """Show configuration summary"""
        console.print("\n[bold]Configuration Summary[/bold]\n")
        
        # Monitoring settings
        table = Table(title="Monitoring Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Categories", ", ".join(self.config['monitoring']['categories']))
        
        locations = self.config['monitoring']['locations']
        if locations['states']:
            location_str = f"States: {', '.join(locations['states'])}"
        elif locations['cities']:
            location_str = f"Cities: {', '.join(locations['cities'])}"
        else:
            location_str = "Nationwide"
        
        table.add_row("Locations", location_str)
        table.add_row("Min Population", str(locations['min_population']))
        table.add_row("Schedule", self.config['monitoring']['schedule'])
        table.add_row("Max URLs", str(self.config['monitoring']['max_urls']))
        
        console.print(table)
        
        # Notification settings
        if self.config['notifications']['email']['enabled'] or self.config['notifications']['webhook']['enabled']:
            console.print("\n[bold]Notification Settings[/bold]")
            
            if self.config['notifications']['email']['enabled']:
                console.print(f"  📧 Email: Enabled → {', '.join(self.config['notifications']['email']['recipients'])}")
            
            if self.config['notifications']['webhook']['enabled']:
                console.print(f"  🔗 Webhook: Enabled → {self.config['notifications']['webhook']['url']}")
            
            filters = self.config['notifications']['filters']
            if any([filters['only_with_website'], filters['only_with_reviews'], filters['min_rating']]):
                console.print("\n  Filters:")
                if filters['only_with_website']:
                    console.print("    • Only with websites")
                if filters['only_with_reviews']:
                    console.print("    • Only with reviews")
                if filters['min_rating']:
                    console.print(f"    • Minimum rating: {filters['min_rating']}")
