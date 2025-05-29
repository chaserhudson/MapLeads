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
        
        # Step 1: Category
        self._setup_category()
        
        # Step 2: Locations
        self._setup_locations()
        
        # Step 3: Notifications
        self._setup_notifications()
        
        # Step 4: Advanced settings
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
    
    def _setup_category(self):
        """Setup business category to monitor"""
        console.print("\n[bold cyan]Step 1: Business Category[/bold cyan]")
        console.print("What type of business do you want to monitor?")
        
        # Show popular categories
        categories = {
            "1": ["restaurant", "cafe", "bar", "bakery"],
            "2": ["gym", "yoga studio", "fitness center"],
            "3": ["plumber", "electrician", "hvac", "contractor"],
            "4": ["dentist", "doctor", "chiropractor"],
            "5": ["auto repair", "mechanic", "car dealer"],
            "6": "Custom categories"
        }
        
        console.print("\nPopular categories:")
        popular_categories = [
            "restaurant", "gym", "plumber", "dentist", "auto repair",
            "yoga studio", "coffee shop", "electrician", "contractor",
            "salon", "bakery", "lawyer", "accountant"
        ]
        
        for i, cat in enumerate(popular_categories, 1):
            console.print(f"  {i}. {cat}")
        console.print(f"  {len(popular_categories)+1}. Custom category")
        
        choice = Prompt.ask(f"\nSelect option (1-{len(popular_categories)+1}) or enter custom category", default=str(len(popular_categories)+1))
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(popular_categories):
                category = popular_categories[choice_idx]
            else:
                category = Prompt.ask("Enter your custom business category (e.g., 'deck builder')").strip()
        except ValueError:
            category = choice.strip()
        
        self.config['monitoring']['category'] = category
        console.print(f"[green]Selected category: {category}[/green]")
    
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
    
    # Schedule setup removed - continuous processing mode enabled
    
    def _setup_notifications(self):
        """Setup notification preferences"""
        console.print("\n[bold cyan]Step 3: Notifications (Optional)[/bold cyan]")
        
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
        console.print("\n[bold cyan]Step 4: Advanced Settings[/bold cyan]")
        
        # Batch size for continuous processing
        batch_size = IntPrompt.ask(
            "Number of locations to process in each batch",
            default=10
        )
        self.config['monitoring']['batch_size'] = batch_size
        
        # Delay between batches
        delay = IntPrompt.ask(
            "Delay between batches in seconds (to avoid rate limiting)",
            default=60
        )
        self.config['monitoring']['batch_delay'] = delay
        
        # Number of browser instances
        browser_instances = IntPrompt.ask(
            "Number of parallel browser instances (1-5, more = faster but uses more resources)",
            default=1,
            choices=["1", "2", "3", "4", "5"]
        )
        self.config['monitoring']['browser_instances'] = browser_instances
    
    def _show_summary(self):
        """Show configuration summary"""
        console.print("\n[bold]Configuration Summary[/bold]\n")
        
        # Monitoring settings
        table = Table(title="Monitoring Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Category", self.config['monitoring']['category'])
        
        locations = self.config['monitoring']['locations']
        if locations['states']:
            location_str = f"States: {', '.join(locations['states'])}"
        elif locations['cities']:
            location_str = f"Cities: {', '.join(locations['cities'])}"
        else:
            location_str = "Nationwide"
        
        table.add_row("Locations", location_str)
        table.add_row("Min Population", str(locations['min_population']))
        table.add_row("Processing Mode", "Continuous")
        table.add_row("Batch Size", str(self.config['monitoring'].get('batch_size', 10)))
        table.add_row("Batch Delay", f"{self.config['monitoring'].get('batch_delay', 60)} seconds")
        table.add_row("Browser Instances", str(self.config['monitoring'].get('browser_instances', 1)))
        
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
