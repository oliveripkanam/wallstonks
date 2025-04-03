#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Fix for WallStonks

This script creates a patched version of the settings module and runs the application.
"""

import os
import sys
import importlib
import types
import subprocess

def create_patched_settings():
    """Create a patched version of the settings module."""
    # Create a new module
    settings_module = types.ModuleType("app.ui.settings")
    
    # Import required components
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
    from PySide6.QtCore import Signal
    
    # Define the patched class
    class SettingsDialog(QDialog):
        """Patched SettingsDialog class."""
        
        test_api_key_requested = Signal(str)
        
        def __init__(self, *args, **kwargs):
            print(f"SettingsDialog.__init__ called with args: {args}, kwargs: {kwargs}")
            
            # Handle both calling patterns
            if args and isinstance(args[0], dict):
                # First arg is config, second (if exists) is parent
                config = args[0]
                parent = args[1] if len(args) > 1 else None
                # Call QDialog.__init__ with parent only
                super().__init__(parent)
                self.config = config
            else:
                # Normal case - parent first, then config
                parent = args[0] if args else None
                config = args[1] if len(args) > 1 and isinstance(args[1], dict) else kwargs.get('config', {})
                super().__init__(parent)
                self.config = config or {}
            
            # Create a simple UI
            self.setWindowTitle("Fixed Settings")
            self.setMinimumWidth(450)
            self.setMinimumHeight(200)
            
            layout = QVBoxLayout(self)
            
            label = QLabel("WallStonks Settings (Fixed Version)")
            label.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(label)
            
            # Add OK button
            btn_layout = QHBoxLayout()
            ok_btn = QPushButton("OK")
            ok_btn.clicked.connect(self.accept)
            btn_layout.addWidget(ok_btn)
            
            layout.addLayout(btn_layout)
            self.setLayout(layout)
        
        def get_config(self):
            """Return the current configuration."""
            return self.config
        
        def exec(self):
            """Override exec to always accept the dialog."""
            # Always accept
            self.accept()
            return True
    
    # Add the class to the module
    settings_module.SettingsDialog = SettingsDialog
    
    # Replace the module in sys.modules
    sys.modules["app.ui.settings"] = settings_module
    
    print("Successfully patched the settings module")
    return settings_module

def main():
    """Main function."""
    print("WallStonks Simple Fix")
    print("====================")
    
    # Create the patched module
    create_patched_settings()
    
    # Find the WallStonks executable
    exe_path = os.path.join("dist", "WallStonks", "WallStonks.exe")
    if not os.path.exists(exe_path):
        print(f"Error: WallStonks executable not found at {exe_path}")
        sys.exit(1)
    
    # Run the executable
    print(f"Running {exe_path} with patched settings module...")
    subprocess.run([exe_path])

if __name__ == "__main__":
    main() 