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
    category: str  # Single category instead of list
    locations: LocationConfig
    batch_size: int = 10
    browser_instances: int = 1  # Number of parallel browser instances (1-5)

class MapLeadsConfig(BaseModel):
    monitoring: MonitoringConfig
    
    @validator('monitoring')
    def validate_monitoring(cls, v):
        if not v.category:
            raise ValueError("A category must be specified")
        if v.browser_instances < 1 or v.browser_instances > 5:
            raise ValueError("Browser instances must be between 1 and 5")
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
                "category": "plumber",
                "locations": {
                    "states": None,
                    "cities": None,
                    "min_population": 50000
                },
                "batch_size": 10,
                "browser_instances": 1
            },
        }
    
    def create_example_config(self):
        """Create an example configuration file"""
        example_path = self.config_dir / 'config.example.json'
        
        example_config = {
            "monitoring": {
                "category": "plumber",
                "locations": {
                    "states": ["CA", "TX", "FL"],
                    "cities": [],
                    "min_population": 50000
                },
                "batch_size": 20,
                "browser_instances": 2
            },
        }
        
        with open(example_path, 'w') as f:
            json.dump(example_config, f, indent=2)
        
        return example_path
