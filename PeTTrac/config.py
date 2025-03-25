#!/usr/bin/env python3
# PeTTraC Configuration Module

import os
import json
import logging

# Default configuration
DEFAULT_CONFIG = {
    # Display settings
    "display": {
        "rotation": 0,  # 0, 90, 180, 270 degrees
        "brightness": 50,  # 0-100%
        "theme": "default",  # default, dark, light
        "update_interval": 1.0,  # seconds
    },
    
    # Battery settings
    "battery": {
        "low_warning": 20,  # percentage
        "critical_warning": 10,  # percentage
        "auto_shutdown": 5,  # percentage
        "show_percentage": True,
        "show_voltage": True,
    },
    
    # System settings
    "system": {
        "debug_mode": False,
        "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        "auto_start": True,
    },
    
    # Button mappings (customizable)
    "buttons": {
        "key1": "toggle_menu",
        "key2": "toggle_brightness",
        "key3": "toggle_theme",
    }
}

class Configuration:
    """Configuration manager for PeTTraC"""
    
    def __init__(self, config_file=None):
        """Initialize configuration with optional config file path"""
        if config_file is None:
            # Default config path is in the same directory as this file
            self.config_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "config.json"
            )
        else:
            self.config_file = config_file
            
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default if not exists"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                
                # Merge user config with defaults (to ensure new options are included)
                config = DEFAULT_CONFIG.copy()
                self._update_dict_recursively(config, user_config)
                logging.info(f"Configuration loaded from {self.config_file}")
                return config
            else:
                # Create default config file
                self._save_config(DEFAULT_CONFIG)
                logging.info(f"Created default configuration at {self.config_file}")
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            logging.info("Using default configuration")
            return DEFAULT_CONFIG.copy()
    
    def _update_dict_recursively(self, target, source):
        """Update target dict with source dict recursively"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict_recursively(target[key], value)
            else:
                target[key] = value
    
    def _save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            logging.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, section, key=None):
        """Get configuration value(s)"""
        if section not in self.config:
            return None
        
        if key is None:
            return self.config[section]
        
        if key not in self.config[section]:
            return None
            
        return self.config[section][key]
    
    def set(self, section, key, value):
        """Set configuration value and save to file"""
        if section not in self.config:
            self.config[section] = {}
            
        self.config[section][key] = value
        return self._save_config()
    
    def save(self):
        """Save current configuration to file"""
        return self._save_config()


# Create a singleton configuration instance
config = Configuration()

# Function to get configuration instance
def get_config():
    """Get the configuration instance"""
    return config 