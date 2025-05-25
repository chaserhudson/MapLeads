"""
Configuration management for MapLeads
Handles loading, saving, and validating configuration
"""

import json
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, validator
from typing import List

class LocationConfig(BaseModel):
    states: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    min_population: int = 0

class MonitoringConfig(BaseModel):
    categories: List[str]
    locations: LocationConfig
    schedule: str = "daily"
    max_urls: Optional[int] = 100

class EmailConfig(BaseModel):
    enabled: bool = False
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = 587
    email: Optional[str] = None
    password: Optional[str] = None
    recipients: List[str] = []

class WebhookConfig(BaseModel):
    enabled: bool = False
    url: Optional[str] = None
    headers: Dict[str, str] = {}

class NotificationFilters(BaseModel):
    only_with_reviews: bool = False
    only_without_reviews: bool = False  # Find newer businesses
    only_with_website: bool = False
    min_rating: Optional[float] = None

class NotificationConfig(BaseModel):
    email: Optional[EmailConfig] = EmailConfig()
    webhook: Optional[WebhookConfig] = WebhookConfig()
    filters: NotificationFilters = NotificationFilters()

class MapLeadsConfig(BaseModel):
    monitoring: MonitoringConfig
    notifications: NotificationConfig = NotificationConfig()
    
    @validator('monitoring')
    def validate_monitoring(cls, v):
        if not v.categories:
            raise ValueError("At least one category must be specified")
        return v


class ConfigManager:
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager"""
        if config_path is None:
            self.config_dir = Path(__file__).parent.parent / 'config'
            self.config_path = self.config_dir / 'config.json'
        else:
            self.config_path = config_path
            self.config_dir = config_path.parent
        
        self.config_dir.mkdir(exist_ok=True)
    
    def config_exists(self) -> bool:
        """Check if configuration file exists"""
        return self.config_path.exists()
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        if not self.config_exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)
        
        # Validate using Pydantic
        config = MapLeadsConfig(**config_data)
        return config.dict()
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        # Validate first
        validated_config = MapLeadsConfig(**config)
        
        # Save to file with pretty formatting
        with open(self.config_path, 'w') as f:
            json.dump(validated_config.dict(), f, indent=2)
    
    def get_default_config(self) -> Dict:
        """Get default configuration template"""
        return {
            "monitoring": {
                "categories": ["restaurant", "gym"],
                "locations": {
                    "states": ["CA", "TX"],
                    "cities": [],
                    "min_population": 50000
                },
                "schedule": "daily",
                "max_urls": 100
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "email": "",
                    "password": "",
                    "recipients": []
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "headers": {}
                },
                "filters": {
                    "only_with_reviews": False,
                    "only_with_website": False,
                    "min_rating": None
                }
            }
        }
    
    def create_example_config(self):
        """Create an example configuration file"""
        example_path = self.config_dir / 'config.example.json'
        
        example_config = {
            "monitoring": {
                "categories": [
                    "restaurant",
                    "gym", 
                    "dentist"
                ],
                "locations": {
                    "states": ["CA", "TX", "FL"],
                    "cities": [],
                    "min_population": 50000
                },
                "schedule": "daily",
                "max_urls": 200
            },
            "notifications": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "email": "your-email@gmail.com",
                    "password": "your-app-password",
                    "recipients": ["recipient@example.com"]
                },
                "webhook": {
                    "enabled": True,
                    "url": "https://hooks.zapier.com/hooks/catch/123456/abcdef/",
                    "headers": {
                        "Authorization": "Bearer YOUR_TOKEN"
                    }
                },
                "filters": {
                    "only_with_reviews": False,
                    "only_with_website": True,
                    "min_rating": 4.0
                }
            }
        }
        
        with open(example_path, 'w') as f:
            json.dump(example_config, f, indent=2)
        
        return example_path
