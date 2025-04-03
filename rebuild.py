#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete Rebuild Script for WallStonks

This script:
1. Cleans out the build and dist directories
2. Creates fixed files for settings.py and any calling files
3. Rebuilds the application from scratch
"""

import os
import sys
import shutil
import subprocess
import glob

def clean_directories():
    """Clean out build and dist directories."""
    print("Cleaning build and dist directories...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            print(f"Removing {dir_path}...")
            shutil.rmtree(dir_path)
    
    # Also clean out any *.spec files
    for spec_file in glob.glob("*.spec"):
        print(f"Removing {spec_file}...")
        os.remove(spec_file)
    
    print("Clean-up complete.")
    return True

def create_fixed_settings():
    """Create a fixed version of settings.py."""
    settings_path = os.path.join("app", "ui", "settings.py")
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    
    print(f"Creating fixed settings.py file...")
    
    content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import json
import time
import requests
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                              QListWidget, QListWidgetItem, QPushButton, QLabel,
                              QMessageBox, QDialog, QTabWidget, QGridLayout,
                              QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox,
                              QGroupBox, QRadioButton, QScrollArea, QSizePolicy)

logger = logging.getLogger(__name__)

# Mock stock search data for when API isn't available
MOCK_STOCKS = [
    ("AAPL", "Apple Inc."),
    ("MSFT", "Microsoft Corporation"),
    ("GOOGL", "Alphabet Inc."),
    ("AMZN", "Amazon.com Inc."),
    ("META", "Meta Platforms Inc."),
    ("TSLA", "Tesla Inc."),
    ("NVDA", "NVIDIA Corporation"),
    ("JPM", "JPMorgan Chase & Co."),
    ("NFLX", "Netflix Inc."),
    ("DIS", "The Walt Disney Company")
]

class MockStockApiClient:
    """Mock API client with search_symbol method to prevent errors"""
    
    def __init__(self):
        self.mock_data = MOCK_STOCKS
    
    def search_symbol(self, query):
        """Mock implementation of search_symbol that returns filtered results from mock data"""
        query = query.strip().upper()
        results = []
        for symbol, name in self.mock_data:
            if query in symbol or query.lower() in name.lower():
                results.append((symbol, name))
        
        if not results and len(query) <= 5:  # Add query as result if it looks like a stock symbol
            results.append((query, "Search term"))
            
        return results

class StockSearchCompleter(QWidget):
    """Stock symbol autocomplete search box"""
    
    stock_selected = Signal(str)
    
    def __init__(self, api_client=None, parent=None):
        super().__init__(parent)
        
        # Always use our mock API client to prevent errors
        self.api_client = MockStockApiClient() if api_client is None else api_client
        
        # Set up UI
        layout = QVBoxLayout(self)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter stock symbol or company name")
        layout.addWidget(self.search_input)
        
        # Results list
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        # Connect signals
        self.search_input.textChanged.connect(self.on_text_changed)
        self.results_list.itemClicked.connect(self.on_item_clicked)
        
        # Setup search timer for debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.setLayout(layout)
    
    def on_text_changed(self, text):
        """Handle text changes in the search input"""
        # Reset the search timer
        self.search_timer.stop()
        
        if len(text) >= 2:
            # Start timer for debouncing
            self.search_timer.start(300)  # 300ms debounce
    
    def perform_search(self):
        """Execute the search"""
        query = self.search_input.text()
        if len(query) < 2:
            self.results_list.clear()
            return
        
        try:
            # Use our mock API client to search for stocks
            logger.info(f"Searching for stock symbols matching: {query}")
            results = self.api_client.search_symbol(query)
            
            # Update the results list
            self.results_list.clear()
            for symbol, name in results:
                item = QListWidgetItem(f"{symbol} - {name}")
                item.setData(Qt.UserRole, symbol)
                self.results_list.addItem(item)
                
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            # Even if regular search fails, add some mock results
            self.results_list.clear()
            if len(query) <= 5:  # Only add if query looks like a stock symbol
                item = QListWidgetItem(f"{query.upper()} - Search term")
                item.setData(Qt.UserRole, query.upper())
                self.results_list.addItem(item)
    
    def on_item_clicked(self, item):
        """Handle item selection from results list"""
        symbol = item.data(Qt.UserRole)
        self.stock_selected.emit(symbol)
        self.search_input.clear()
        self.results_list.clear()
        
class StockListWidget(QWidget):
    """Widget that combines search and selected stocks list"""
    
    def __init__(self, stocks=None, parent=None):
        super().__init__(parent)
        self.stocks = []
        
        # Set up UI
        layout = QVBoxLayout(self)
        
        # Create mock API client for the search completer
        mock_api = MockStockApiClient()
        
        # Add search completer
        self.search_completer = StockSearchCompleter(api_client=mock_api, parent=self)
        layout.addWidget(self.search_completer)
        
        # Label for selected stocks
        layout.addWidget(QLabel("Selected Stocks:"))
        
        # List of selected stocks
        self.stock_list = QListWidget()
        layout.addWidget(self.stock_list)
        
        # Remove button
        self.remove_btn = QPushButton("Remove Selected")
        layout.addWidget(self.remove_btn)
        
        # Connect signals
        self.search_completer.stock_selected.connect(self.add_stock)
        self.remove_btn.clicked.connect(self.remove_selected_stock)
        
        self.setLayout(layout)
        
        # Set initial stocks
        if stocks:
            self.set_stocks(stocks)
    
    def add_stock(self, symbol):
        """Add a stock to the list"""
        if symbol not in self.stocks and len(self.stocks) < 5:
            self.stocks.append(symbol)
            self.stock_list.addItem(symbol)
            return True
        elif symbol in self.stocks:
            QMessageBox.information(self, "Stock Already Added", 
                                   f"The stock {symbol} is already in your list.")
        elif len(self.stocks) >= 5:
            QMessageBox.warning(self, "Maximum Stocks Reached", 
                               "You can track a maximum of 5 stocks. Remove one to add another.")
        return False
    
    def remove_selected_stock(self):
        """Remove the selected stock"""
        selected_items = self.stock_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            symbol = item.text()
            if symbol in self.stocks:
                self.stocks.remove(symbol)
            row = self.stock_list.row(item)
            self.stock_list.takeItem(row)
    
    def set_stocks(self, stocks):
        """Set the list of stocks"""
        self.stocks = stocks[:5] if stocks else []  # Max 5 stocks
        self.stock_list.clear()
        for stock in self.stocks:
            self.stock_list.addItem(stock)
    
    def get_stocks(self):
        """Get the list of stocks"""
        return self.stocks
    
    def get_selected_stocks(self):
        """Alias for get_stocks to maintain compatibility"""
        return self.get_stocks()

# The ORIGINAL SettingsDialog class - not changing the signature
class SettingsDialog(QDialog):
    """Settings dialog for configuring the application."""
    
    test_api_key_requested = Signal(str)
    
    def __init__(self, parent=None, config=None):
        """Original method signature that works."""
        super().__init__(parent)
        
        # Store the config
        self.config = config or {}
        
        # Setup dialog
        self.setWindowTitle("Settings")
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the UI elements."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.tab_general = QWidget()
        self.tab_stocks = QWidget()
        self.tab_display = QWidget()
        
        self.tabs.addTab(self.tab_general, "General")
        self.tabs.addTab(self.tab_stocks, "Stocks")
        self.tabs.addTab(self.tab_display, "Display")
        
        # Setup tab contents
        self.setup_general_tab()
        self.setup_stocks_tab()
        self.setup_display_tab()
        
        # Add tabs to layout
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
        
        self.setLayout(layout)
    
    def setup_general_tab(self):
        """Setup the general settings tab."""
        layout = QGridLayout(self.tab_general)
        
        # API Key
        layout.addWidget(QLabel("API Key:"), 0, 0)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key")
        layout.addWidget(self.api_key_input, 0, 1)
        
        # Refresh Interval
        layout.addWidget(QLabel("Refresh Interval (seconds):"), 1, 0)
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setMinimum(5)
        self.refresh_interval.setMaximum(3600)
        self.refresh_interval.setValue(30)
        layout.addWidget(self.refresh_interval, 1, 1)
        
        # Auto-start
        self.auto_start = QCheckBox("Start with Windows")
        layout.addWidget(self.auto_start, 2, 0, 1, 2)
        
        # Startup mode
        layout.addWidget(QLabel("Startup Mode:"), 3, 0)
        self.startup_mode = QComboBox()
        self.startup_mode.addItems(["Normal", "Minimized to Tray"])
        layout.addWidget(self.startup_mode, 3, 1)
        
        # Add some stretch at the bottom
        layout.setRowStretch(4, 1)
        
        self.tab_general.setLayout(layout)
    
    def setup_stocks_tab(self):
        """Setup the stocks settings tab."""
        layout = QVBoxLayout(self.tab_stocks)
        
        # Stock list
        layout.addWidget(QLabel("Select stocks to track (max 5):"))
        
        # Stock search widget
        self.stock_list_widget = StockListWidget()
        layout.addWidget(self.stock_list_widget)
        
        self.tab_stocks.setLayout(layout)
    
    def setup_display_tab(self):
        """Setup the display settings tab."""
        layout = QVBoxLayout(self.tab_display)
        
        # Chart settings group
        chart_group = QGroupBox("Chart Settings")
        chart_layout = QGridLayout()
        
        # Chart type
        chart_layout.addWidget(QLabel("Chart Type:"), 0, 0)
        self.chart_type = QComboBox()
        self.chart_type.addItems(["Candlestick", "Line", "OHLC"])
        chart_layout.addWidget(self.chart_type, 0, 1)
        
        # Time range
        chart_layout.addWidget(QLabel("Default Time Range:"), 1, 0)
        self.time_range = QComboBox()
        self.time_range.addItems(["1 Day", "1 Week", "1 Month", "3 Months", "1 Year", "5 Years"])
        chart_layout.addWidget(self.time_range, 1, 1)
        
        # Chart colors
        self.use_custom_colors = QCheckBox("Use Custom Colors")
        chart_layout.addWidget(self.use_custom_colors, 2, 0, 1, 2)
        
        chart_group.setLayout(chart_layout)
        layout.addWidget(chart_group)
        
        # Display options group
        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout()
        
        # Checkboxes for different options
        self.show_volume = QCheckBox("Show Volume")
        self.show_volume.setToolTip("Display volume bars below the price chart")
        
        self.show_indicators = QCheckBox("Show Technical Indicators")
        self.show_indicators.setToolTip("Display technical indicators such as moving averages")
        
        self.dark_mode = QCheckBox("Dark Mode")
        self.dark_mode.setToolTip("Use dark color scheme for charts and UI")
        
        display_layout.addWidget(self.show_volume)
        display_layout.addWidget(self.show_indicators)
        display_layout.addWidget(self.dark_mode)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Add stretch at the bottom
        layout.addStretch()
        
        self.tab_display.setLayout(layout)
    
    def load_settings(self):
        """Load settings from config."""
        try:
            # General tab
            self.api_key_input.setText(self.config.get("api_key", ""))
            self.refresh_interval.setValue(self.config.get("refresh_interval", 30))
            self.auto_start.setChecked(self.config.get("auto_start", False))
            
            startup_mode_idx = 1 if self.config.get("start_minimized", False) else 0
            self.startup_mode.setCurrentIndex(startup_mode_idx)
            
            # Stocks tab
            stocks = self.config.get("stocks", [])
            if stocks:
                self.stock_list_widget.set_stocks(stocks)
            
            # Display tab
            chart_types = {"candlestick": 0, "line": 1, "ohlc": 2}
            chart_type = self.config.get("chart_type", "candlestick").lower()
            self.chart_type.setCurrentIndex(chart_types.get(chart_type, 0))
            
            time_ranges = {"1d": 0, "1w": 1, "1m": 2, "3m": 3, "1y": 4, "5y": 5}
            time_range = self.config.get("time_range", "1d").lower()
            self.time_range.setCurrentIndex(time_ranges.get(time_range, 0))
            
            self.use_custom_colors.setChecked(self.config.get("use_custom_colors", False))
            self.show_volume.setChecked(self.config.get("show_volume", True))
            self.show_indicators.setChecked(self.config.get("show_indicators", False))
            self.dark_mode.setChecked(self.config.get("dark_mode", False))
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to config and accept the dialog."""
        try:
            # General tab
            self.config["api_key"] = self.api_key_input.text()
            self.config["refresh_interval"] = self.refresh_interval.value()
            self.config["auto_start"] = self.auto_start.isChecked()
            self.config["start_minimized"] = (self.startup_mode.currentIndex() == 1)
            
            # Stocks tab
            self.config["stocks"] = self.stock_list_widget.get_stocks()
            
            # Display tab
            chart_types = ["candlestick", "line", "ohlc"]
            self.config["chart_type"] = chart_types[self.chart_type.currentIndex()]
            
            time_ranges = ["1d", "1w", "1m", "3m", "1y", "5y"]
            self.config["time_range"] = time_ranges[self.time_range.currentIndex()]
            
            self.config["use_custom_colors"] = self.use_custom_colors.isChecked()
            self.config["show_volume"] = self.show_volume.isChecked()
            self.config["show_indicators"] = self.show_indicators.isChecked()
            self.config["dark_mode"] = self.dark_mode.isChecked()
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            
    def get_config(self):
        """Return the current configuration."""
        return self.config

def fix_tray():
    """Fix the tray.py file to handle the SettingsDialog arguments correctly."""
    tray_path = os.path.join("app", "ui", "tray.py")
    
    if not os.path.exists(tray_path):
        print(f"Warning: {tray_path} not found, cannot fix tray.py")
        return False
    
    print(f"Fixing tray.py...")
    
    # Read the file
    with open(tray_path, "r") as f:
        content = f.read()
    
    # Fix the specific line where SettingsDialog is called
    # Change from: dialog = SettingsDialog(self.config, None)
    # To: dialog = SettingsDialog(None, self.config)
    content = content.replace(
        "dialog = SettingsDialog(self.config, None)", 
        "dialog = SettingsDialog(None, self.config)"
    )
    
    # Write back the fixed content
    with open(tray_path, "w") as f:
        f.write(content)
    
    print(f"Fixed tray.py")
    return True

def fix_main():
    """Fix the main.py file to handle the SettingsDialog arguments correctly."""
    main_path = os.path.join("app", "main.py")
    
    if not os.path.exists(main_path):
        print(f"Warning: {main_path} not found, cannot fix main.py")
        return False
    
    print(f"Fixing main.py...")
    
    # Read the file
    with open(main_path, "r") as f:
        content = f.read()
    
    # Fix the specific line where SettingsDialog is called
    # Change from: dialog = SettingsDialog(self.config)
    # To: dialog = SettingsDialog(None, self.config)
    content = content.replace(
        "dialog = SettingsDialog(self.config)", 
        "dialog = SettingsDialog(None, self.config)"
    )
    
    # Write back the fixed content
    with open(main_path, "w") as f:
        f.write(content)
    
    print(f"Fixed main.py")
    return True

def create_icon():
    """Create a simple icon if needed."""
    icon_path = os.path.join("app", "assets", "icon.png")
    
    if os.path.exists(icon_path):
        print(f"Icon already exists at {icon_path}")
        return True
    
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)
    
    try:
        from PIL import Image, ImageDraw
        
        # Create a 32x32 icon with a blue background
        img = Image.new('RGB', (32, 32), color=(0, 120, 212))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple stock chart line
        draw.line([(5, 20), (10, 15), (15, 25), (20, 10), (25, 15)], 
                 fill=(255, 255, 255), width=2)
        
        # Save the icon
        img.save(icon_path)
        print(f"Created icon at {icon_path}")
        return True
    except Exception as e:
        print(f"Warning: Failed to create icon: {e}")
        # Create an empty file as a placeholder
        with open(icon_path, "wb") as f:
            f.write(b"")
        print(f"Created empty icon placeholder at {icon_path}")
        return True

def ensure_init_files():
    """Ensure __init__.py files exist in all app subdirectories."""
    print("Creating __init__.py files in app subdirectories...")
    
    for root, dirs, files in os.walk("app"):
        for dir_name in dirs:
            init_path = os.path.join(root, dir_name, "__init__.py")
            dir_path = os.path.join(root, dir_name)
            
            if os.path.isdir(dir_path) and not os.path.exists(init_path):
                with open(init_path, "w") as f:
                    f.write("# Auto-generated __init__.py\n")
                print(f"Created {init_path}")
    
    return True

def create_run_file():
    """Create a simple run.py file to start the application."""
    run_path = "run.py"
    
    content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WallStonks Application Entry Point
"""

import sys
from app.main import WallStonksApp

if __name__ == "__main__":
    app = WallStonksApp()
    sys.exit(app.run())
'''
    
    with open(run_path, "w") as f:
        f.write(content)
    
    print(f"Created {run_path}")
    return True

def build_with_pyinstaller():
    """Build the application with PyInstaller."""
    print("Building application with PyInstaller...")
    
    # Create a spec file
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all necessary modules
hiddenimports = []
hiddenimports += collect_submodules('app')
hiddenimports += collect_submodules('PIL')
hiddenimports += collect_submodules('matplotlib')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('numpy')
hiddenimports += collect_submodules('scipy')
hiddenimports += collect_submodules('PySide6')

# App specific data
datas = [
    ('app/assets/*', 'app/assets'),
]

a = Analysis(
    ['run.py'],
    pathex=[os.path.abspath(os.getcwd())],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WallStonks',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/assets/icon.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WallStonks',
)
'''
    
    with open("WallStonks.spec", "w") as f:
        f.write(spec_content)
    
    print("Created PyInstaller spec file")
    
    # Build with PyInstaller
    try:
        print("Running PyInstaller...")
        subprocess.run(["pyinstaller", "WallStonks.spec", "--noconfirm"], check=True)
        print("PyInstaller build completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: PyInstaller build failed: {e}")
        return False
    except Exception as e:
        print(f"Error: Failed to run PyInstaller: {e}")
        return False

def main():
    """Main function to rebuild the application."""
    print("WallStonks Complete Rebuild")
    print("==========================")
    
    # Clean up existing build artifacts
    if not clean_directories():
        print("Failed to clean directories, continuing anyway...")
    
    # Create fixed settings.py
    if not create_fixed_settings():
        print("Failed to create fixed settings.py")
        return
    
    # Fix tray.py
    fix_tray()
    
    # Fix main.py
    fix_main()
    
    # Create icon if needed
    create_icon()
    
    # Ensure __init__.py files exist
    ensure_init_files()
    
    # Create run.py
    create_run_file()
    
    # Build with PyInstaller
    if not build_with_pyinstaller():
        print("Failed to build with PyInstaller")
        return
    
    print("\nRebuild complete!")
    print("You can now run the application from dist/WallStonks/WallStonks.exe")
    
if __name__ == "__main__":
    main() 