#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PySide6.QtWidgets import QApplication
from app.ui.settings import SettingsDialog
import json
import os

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Default config
    config = {
        "api_key": "",
        "stocks": ["AAPL", "MSFT", "GOOGL"],
        "refresh_interval": 60,
        "dark_mode": False
    }
    
    # Config file path
    config_dir = os.path.expanduser("~/.wallstonks")
    config_file = os.path.join(config_dir, "config.json")
    
    # Try to load existing config
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config.update(json.load(f))
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Create settings dialog
    dialog = SettingsDialog(None, config)
    
    # Show the dialog
    if dialog.exec():
        # Save the config
        config = dialog.get_config()
        
        # Create config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Save config to file
        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    # Exit application
    return 0

if __name__ == "__main__":
    sys.exit(main())
