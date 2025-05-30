#!/usr/bin/env python3
"""
MapLeads - Open-source B2B lead generation tool
Monitor Google Maps for new business listings in your target market
"""

import click
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import track

from src.config_manager import ConfigManager
from src.scraper_continuous import MapLeadsScraper
from src.database import Database
from src.notifier import NotificationManager
from src.interactive_setup import InteractiveSetup

console = Console()

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """MapLeads - Find new businesses as they appear on Google Maps"""
    pass

@cli.command()
def setup():
    """Interactive setup wizard to configure MapLeads"""
    console.print("\n[bold blue]Welcome to MapLeads Setup Wizard! 🗺️[/bold blue]\n")
    
    setup_wizard = InteractiveSetup()
    config_path = setup_wizard.run()
    
    console.print(f"\n[green]✅ Configuration saved to: {config_path}[/green]")
    console.print("\n[yellow]To start monitoring, run:[/yellow] [bold]python mapleads.py run[/bold]\n")

@cli.command()
@click.argument('new_category', required=False)
def category(new_category):
    """Change the monitoring category (e.g., 'restaurant', 'gym', 'plumber')"""
    config_manager = ConfigManager()
    
    if not config_manager.config_exists():
        console.print("[red]No configuration found. Run 'python mapleads.py setup' first.[/red]")
        return
    
    config = config_manager.load_config()
    
    if new_category:
        # Category provided as argument
        old_category = config['monitoring']['category']
        config['monitoring']['category'] = new_category
        config_manager.save_config(config)
        console.print(f"[green]✅ Category changed from '{old_category}' to '{new_category}'[/green]")
    else:
        # Interactive category selection
        console.print(f"\n[cyan]Current category: {config['monitoring']['category']}[/cyan]")
        console.print("\nPopular categories:")
        
        popular_categories = [
            "restaurant", "gym", "plumber", "dentist", "auto repair",
            "yoga studio", "coffee shop", "electrician", "contractor", 
            "salon", "bakery", "lawyer", "accountant"
        ]
        
        for i, cat in enumerate(popular_categories, 1):
            console.print(f"  {i}. {cat}")
        console.print(f"  {len(popular_categories)+1}. Custom category")
        
        from rich.prompt import Prompt
        choice = Prompt.ask(f"\nSelect option (1-{len(popular_categories)+1}) or enter custom category")
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(popular_categories):
                new_category = popular_categories[choice_idx]
            else:
                new_category = Prompt.ask("Enter your custom business category").strip()
        except ValueError:
            new_category = choice.strip()
        
        old_category = config['monitoring']['category']
        config['monitoring']['category'] = new_category
        config_manager.save_config(config)
        console.print(f"[green]✅ Category changed from '{old_category}' to '{new_category}'[/green]")

@cli.command()
@click.argument('num_instances', type=int, required=False)
def instances(num_instances):
    """Change the number of browser instances (1-5) for parallel processing"""
    config_manager = ConfigManager()
    
    if not config_manager.config_exists():
        console.print("[red]No configuration found. Run 'python mapleads.py setup' first.[/red]")
        return
    
    config = config_manager.load_config()
    
    if num_instances:
        # Validate range
        if num_instances < 1 or num_instances > 5:
            console.print("[red]Number of instances must be between 1 and 5[/red]")
            return
        
        old_instances = config['monitoring'].get('browser_instances', 1)
        config['monitoring']['browser_instances'] = num_instances
        config_manager.save_config(config)
        console.print(f"[green]✅ Browser instances changed from {old_instances} to {num_instances}[/green]")
        
        # Show performance impact
        if num_instances > old_instances:
            console.print(f"[yellow]⚡ Faster processing: {num_instances}x parallel scraping[/yellow]")
            console.print(f"[yellow]📋 Resource usage will increase[/yellow]")
        elif num_instances < old_instances:
            console.print(f"[yellow]🐌 Slower processing but lower resource usage[/yellow]")
    else:
        # Interactive selection
        current_instances = config['monitoring'].get('browser_instances', 1)
        console.print(f"\n[cyan]Current browser instances: {current_instances}[/cyan]")
        console.print("\nChoose number of browser instances:")
        console.print("  1. Single instance (safest, slowest)")
        console.print("  2. Two instances (balanced)")
        console.print("  3. Three instances (faster)")
        console.print("  4. Four instances (much faster)")
        console.print("  5. Five instances (fastest, highest resource usage)")
        
        from rich.prompt import IntPrompt
        choice = IntPrompt.ask("\nSelect instances (1-5)", default=current_instances, choices=["1", "2", "3", "4", "5"])
        
        config['monitoring']['browser_instances'] = choice
        config_manager.save_config(config)
        console.print(f"[green]✅ Browser instances changed from {current_instances} to {choice}[/green]")

@cli.command()
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
def run(headless):
    """Start monitoring for new businesses"""
    config_manager = ConfigManager()
    
    if not config_manager.config_exists():
        console.print("[red]No configuration found![/red]")
        console.print("Please run: [bold]python mapleads.py setup[/bold]")
        sys.exit(1)
    
    config = config_manager.load_config()
    console.print(f"\n[bold green]Starting MapLeads Monitor[/bold green]")
    console.print(f"Category: {config['monitoring']['category']}")
    console.print(f"Locations: {config['monitoring']['locations']}")
    
    db = Database()
    scraper = MapLeadsScraper(db, headless=headless)
    notifier = NotificationManager(config)
    
    try:
        # Continuous monitoring mode
        console.print("\n[yellow]Starting continuous monitoring...[/yellow]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        # Set up notifier on scraper for real-time notifications
        scraper.notifier = notifier
        
        # Start continuous scanning
        scraper.continuous_scan(config['monitoring'])
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)
    finally:
        scraper.cleanup()


@cli.command()
def status():
    """View monitoring statistics and recent discoveries"""
    db = Database()
    stats = db.get_statistics()
    
    console.print("\n[bold]MapLeads Statistics[/bold]\n")
    
    # Overall stats
    table = Table(title="Overview")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Businesses", str(stats['total_businesses']))
    table.add_row("New This Week", str(stats['new_this_week']))
    table.add_row("New This Month", str(stats['new_this_month']))
    table.add_row("Categories Tracked", str(stats['categories_count']))
    
    console.print(table)
    
    # Recent discoveries
    recent = db.get_recent_businesses(10)
    if recent:
        console.print("\n[bold]Recent Discoveries[/bold]\n")
        recent_table = Table()
        recent_table.add_column("Date", style="dim")
        recent_table.add_column("Name", style="cyan")
        recent_table.add_column("Category", style="yellow")
        recent_table.add_column("Location", style="green")
        
        for biz in recent:
            recent_table.add_row(
                biz['first_seen'].strftime('%Y-%m-%d'),
                biz['name'],
                biz['category'],
                f"{biz['city']}, {biz['state']}"
            )
        
        console.print(recent_table)

@cli.command()
@click.option('--format', type=click.Choice(['csv', 'json', 'xlsx']), default='csv')
@click.option('--days', default=30, help='Export businesses from last N days')
@click.option('--output', help='Output filename')
def export(format, days, output):
    """Export discovered businesses to file"""
    db = Database()
    businesses = db.get_businesses_since_days(days)
    
    if not businesses:
        console.print(f"[yellow]No businesses found in the last {days} days.[/yellow]")
        return
    
    if not output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = f"mapleads_export_{timestamp}.{format}"
    
    try:
        from src.exporter import export_businesses
        export_businesses(businesses, output, format)
        console.print(f"[green]✅ Exported {len(businesses)} businesses to {output}[/green]")
    except Exception as e:
        console.print(f"[red]Export failed: {e}[/red]")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Validate the file without importing')
def import_data(file_path, dry_run):
    """Import businesses from CSV, JSON, or Excel file"""
    try:
        from src.exporter import import_businesses
        
        console.print(f"[yellow]Importing businesses from: {file_path}[/yellow]")
        
        # Import and validate
        businesses, errors = import_businesses(file_path)
        
        if errors:
            console.print(f"\n[red]Validation errors found:[/red]")
            for error in errors[:10]:  # Show first 10 errors
                console.print(f"  • {error}")
            if len(errors) > 10:
                console.print(f"  ... and {len(errors) - 10} more errors")
            
            if not businesses:
                console.print(f"\n[red]No valid businesses found in import file.[/red]")
                return
        
        console.print(f"\n[green]Found {len(businesses)} valid businesses to import[/green]")
        
        if dry_run:
            console.print("[yellow]Dry run complete - no data was imported[/yellow]")
            return
        
        # Confirm import
        from rich.prompt import Confirm
        if not Confirm.ask(f"\nImport {len(businesses)} businesses to database?"):
            console.print("[yellow]Import cancelled[/yellow]")
            return
        
        # Import to database
        db = Database()
        imported_count = 0
        duplicate_count = 0
        
        for business in businesses:
            if db.business_exists(business['phone']):
                duplicate_count += 1
                # Update last seen for existing businesses
                db.update_last_seen(business['phone'])
            else:
                db.add_business(business)
                imported_count += 1
        
        console.print(f"\n[green]✅ Import completed![/green]")
        console.print(f"   New businesses imported: {imported_count}")
        console.print(f"   Duplicates skipped: {duplicate_count}")
        
        if errors:
            console.print(f"   Rows with errors: {len(errors)}")
        
    except Exception as e:
        console.print(f"[red]Import failed: {e}[/red]")

@cli.command()
def categories():
    """List popular business categories for monitoring"""
    categories = {
        "Home Services": [
            "plumber", "electrician", "hvac", "roofer", "painter",
            "contractor", "handyman", "landscaper", "pest control"
        ],
        "Food & Dining": [
            "restaurant", "cafe", "bakery", "bar", "food truck",
            "catering", "pizza", "coffee shop"
        ],
        "Health & Wellness": [
            "gym", "yoga studio", "dentist", "doctor", "chiropractor",
            "spa", "salon", "barber", "massage"
        ],
        "Automotive": [
            "auto repair", "car dealer", "tire shop", "auto parts",
            "car wash", "mechanic", "body shop"
        ],
        "Professional Services": [
            "lawyer", "accountant", "insurance agent", "real estate agent",
            "financial advisor", "marketing agency"
        ],
        "Retail": [
            "clothing store", "gift shop", "bookstore", "pet store",
            "jewelry store", "furniture store"
        ]
    }
    
    console.print("\n[bold]Popular Business Categories[/bold]\n")
    
    for category_type, items in categories.items():
        console.print(f"[bold cyan]{category_type}:[/bold cyan]")
        for item in items:
            console.print(f"  • {item}")
        console.print()

@cli.command()
def test():
    """Run a test scan with minimal searches"""
    console.print("\n[bold yellow]Running test scan...[/bold yellow]\n")
    
    # Create minimal test config
    test_config = {
        'monitoring': {
            'category': 'restaurant',
            'locations': {
                'states': ['CA'],
                'min_population': 100000
            },
            'batch_size': 5
        }
    }
    
    db = Database()
    scraper = MapLeadsScraper(db, headless=False)
    
    try:
        results = scraper.scan(test_config['monitoring'], test_mode=True)
        console.print(f"\n[green]Test completed! Found {len(results)} businesses.[/green]")
        
        if results:
            _display_new_businesses(results[:5])  # Show max 5 results
            
    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")
    finally:
        scraper.cleanup()

def _display_new_businesses(businesses):
    """Display new businesses in a nice table"""
    table = Table(title="New Businesses")
    table.add_column("Name", style="cyan")
    table.add_column("Phone", style="yellow")
    table.add_column("Category", style="green")
    table.add_column("Location", style="blue")
    table.add_column("Reviews", style="magenta")
    
    for biz in businesses[:10]:  # Show max 10
        table.add_row(
            biz.get('name', 'N/A'),
            biz.get('phone', 'N/A'),
            biz.get('category', 'N/A'),
            f"{biz.get('city', 'N/A')}, {biz.get('state', 'N/A')}",
            biz.get('reviews', 'N/A')
        )
    
    console.print(table)
    
    if len(businesses) > 10:
        console.print(f"\n[dim]... and {len(businesses) - 10} more[/dim]")

if __name__ == '__main__':
    cli()
