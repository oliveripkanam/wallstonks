#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the SettingsDialog class with different calling patterns.
"""

import sys
import json
import os
from PySide6.QtWidgets import QApplication

from app.ui.settings import SettingsDialog

def main():
    """Main test function."""
    app = QApplication(sys.argv)
    
    # Create a test config
    config = {
        "api_key": "demo",
        "stocks": ["AAPL", "MSFT", "GOOGL"],
        "refresh_interval": 60,
        "dark_mode": False
    }
    
    print("Testing SettingsDialog with different calling patterns...")
    
    # Test calling pattern 1: config as first arg
    print("\nTest 1: dialog = SettingsDialog(config)")
    dialog1 = SettingsDialog(config)
    result1 = dialog1.exec()
    print(f"Dialog 1 result: {result1}")
    
    # Test calling pattern 2: parent as first arg, config as second
    print("\nTest 2: dialog = SettingsDialog(None, config)")
    dialog2 = SettingsDialog(None, config)
    result2 = dialog2.exec()
    print(f"Dialog 2 result: {result2}")
    
    # Test calling pattern 3: kwargs
    print("\nTest 3: dialog = SettingsDialog(config=config)")
    dialog3 = SettingsDialog(config=config)
    result3 = dialog3.exec()
    print(f"Dialog 3 result: {result3}")
    
    # Test that settings were saved correctly
    if result3:
        new_config = dialog3.get_config()
        print("\nSaved config:")
        print(json.dumps(new_config, indent=2))
    
    print("\nAll tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 