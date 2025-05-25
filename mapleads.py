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
from src.scraper import MapLeadsScraper
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
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
@click.option('--parallel', default=1, help='Number of parallel browsers')
@click.option('--once', is_flag=True, help='Run once instead of continuous monitoring')
def run(headless, parallel, once):
    """Start monitoring for new businesses"""
    config_manager = ConfigManager()
    
    if not config_manager.config_exists():
        console.print("[red]No configuration found![/red]")
        console.print("Please run: [bold]python mapleads.py setup[/bold]")
        sys.exit(1)
    
    config = config_manager.load_config()
    console.print(f"\n[bold green]Starting MapLeads Monitor[/bold green]")
    console.print(f"Categories: {', '.join(config['monitoring']['categories'])}")
    console.print(f"Locations: {config['monitoring']['locations']}")
    
    db = Database()
    scraper = MapLeadsScraper(db, headless=headless)
    notifier = NotificationManager(config)
    
    try:
        if once:
            # Run single scan
            console.print("\n[yellow]Running single scan...[/yellow]")
            new_businesses = scraper.scan(config['monitoring'])
            
            if new_businesses:
                console.print(f"\n[green]Found {len(new_businesses)} new businesses![/green]")
                notifier.send_notifications(new_businesses)
                _display_new_businesses(new_businesses)
            else:
                console.print("\n[yellow]No new businesses found in this scan.[/yellow]")
        else:
            # Continuous monitoring
            console.print("\n[yellow]Starting continuous monitoring...[/yellow]")
            console.print("[dim]Press Ctrl+C to stop[/dim]\n")
            
            import schedule
            import time
            
            def run_scan():
                console.print(f"\n[blue]Running scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/blue]")
                new_businesses = scraper.scan(config['monitoring'])
                
                if new_businesses:
                    console.print(f"[green]Found {len(new_businesses)} new businesses![/green]")
                    notifier.send_notifications(new_businesses)
                    _display_new_businesses(new_businesses)
                else:
                    console.print("[dim]No new businesses found.[/dim]")
            
            # Schedule based on config
            schedule_config = config['monitoring'].get('schedule', 'daily')
            if schedule_config == 'hourly':
                schedule.every().hour.do(run_scan)
            elif schedule_config == 'daily':
                schedule.every().day.at("09:00").do(run_scan)
            else:
                schedule.every().day.do(run_scan)
            
            # Run immediately
            run_scan()
            
            # Keep running
            while True:
                schedule.run_pending()
                time.sleep(60)
                
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
            'categories': ['restaurant'],
            'locations': {
                'states': ['CA'],
                'min_population': 100000
            },
            'max_urls': 5
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
