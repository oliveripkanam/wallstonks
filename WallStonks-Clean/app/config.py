#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Configuration manager for WallStonks application.
    Handles loading, saving, and accessing configuration settings.
    """
    
    def __init__(self, default_config=None):
        """
        Initialize the configuration manager.
        
        Args:
            default_config (dict, optional): Default configuration settings
        """
        self.default_config = default_config or {}
        self.config = self.default_config.copy()
        
        # Determine config file path
        self.config_dir = os.path.join(os.path.expanduser("~"), ".wallstonks")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
    
    def load(self):
        """
        Load configuration from file.
        If the file doesn't exist, create it with default settings.
        
        Returns:
            dict: The loaded configuration
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    
                # Merge with default config to ensure all required keys exist
                for key, value in self.default_config.items():
                    if key not in loaded_config:
                        loaded_config[key] = value
                
                self.config = loaded_config
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                # Create the config file with default settings
                self.save(self.default_config)
                logger.info(f"Created new configuration file at {self.config_file}")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # If loading fails, use default config
            self.config = self.default_config.copy()
            logger.info("Using default configuration")
            
        return self.config
    
    def save(self, config=None):
        """
        Save configuration to file.
        
        Args:
            config (dict, optional): Configuration to save. If None, saves the current config.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if config is not None:
            self.config = config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
                
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key, default=None):
        """
        Get a configuration value.
        
        Args:
            key (str): The configuration key
            default: The default value to return if the key doesn't exist
            
        Returns:
            The configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Set a configuration value.
        
        Args:
            key (str): The configuration key
            value: The value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.config[key] = value
        return self.save()
    
    def add_stock(self, symbol, name=""):
        """
        Add a stock to the tracked stocks list.
        
        Args:
            symbol (str): The stock symbol
            name (str, optional): The company name
            
        Returns:
            tuple: (success, message)
        """
        # Check if we already have 5 stocks
        current_stocks = self.config.get("stocks", [])
        if len(current_stocks) >= 5:
            return False, "Maximum of 5 stocks allowed"
            
        # Check if the stock is already in the list
        if symbol in current_stocks:
            return False, f"{symbol} is already being tracked"
            
        # Add the stock
        current_stocks.append(symbol)
        self.config["stocks"] = current_stocks
        
        # Save the config
        success = self.save()
        
        if success:
            return True, f"{symbol} added to tracked stocks"
        else:
            return False, "Error saving configuration"
    
    def remove_stock(self, symbol):
        """
        Remove a stock from the tracked stocks list.
        
        Args:
            symbol (str): The stock symbol
            
        Returns:
            tuple: (success, message)
        """
        current_stocks = self.config.get("stocks", [])
        
        if symbol not in current_stocks:
            return False, f"{symbol} is not in the tracked stocks list"
            
        # Remove the stock
        current_stocks.remove(symbol)
        self.config["stocks"] = current_stocks
        
        # Save the config
        success = self.save()
        
        if success:
            return True, f"{symbol} removed from tracked stocks"
        else:
            return False, "Error saving configuration"
            
    def delete(self):
        """
        Delete the configuration file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
                logger.info(f"Configuration file deleted: {self.config_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting configuration file: {e}")
            return False 