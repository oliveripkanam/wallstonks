#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import json
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                              QListWidget, QListWidgetItem, QPushButton, QLabel,
                              QMessageBox, QDialog, QTabWidget, QGridLayout,
                              QCheckBox, QComboBox, QSpinBox)

logger = logging.getLogger(__name__)

# Mock stock data
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
    """Mock API client for stocks"""
    
    def __init__(self):
        self.mock_data = MOCK_STOCKS
    
    def search_symbol(self, query):
        """Search for stock symbols"""
        query = query.strip().upper()
        results = []
        for symbol, name in self.mock_data:
            if query in symbol or query.lower() in name.lower():
                results.append((symbol, name))
        
        if not results and len(query) <= 5:
            results.append((query, "Search term"))
            
        return results

class StockSearchCompleter(QWidget):
    """Stock symbol search widget"""
    
    stock_selected = Signal(str)
    
    def __init__(self, api_client=None, parent=None):
        super().__init__(parent)
        
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
        self.search_input.textChanged.connect(self.perform_search)
        self.results_list.itemClicked.connect(self.on_item_clicked)
        
        self.setLayout(layout)
    
    def perform_search(self, text):
        """Execute the search"""
        query = text
        if len(query) < 2:
            self.results_list.clear()
            return
        
        try:
            results = self.api_client.search_symbol(query)
            
            # Update the results list
            self.results_list.clear()
            for symbol, name in results:
                item = QListWidgetItem(f"{symbol} - {name}")
                item.setData(Qt.UserRole, symbol)
                self.results_list.addItem(item)
                
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            self.results_list.clear()
            if len(query) <= 5:
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
    """Widget that shows the selected stocks"""
    
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

# Key fix: SettingsDialog that can handle config-first initialization
class SettingsDialog(QDialog):
    """Settings dialog for configuring the application."""
    
    test_api_key_requested = Signal(str)
    
    def __init__(self, *args, **kwargs):
        """Initialize with flexible argument handling."""
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
            config = args[1] if len(args) > 1 else kwargs.get('config', {})
            super().__init__(parent)
            self.config = config or {}
        
        # Setup dialog
        self.setWindowTitle("Settings")
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the UI."""
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
        
        # Chart settings
        layout.addWidget(QLabel("Chart Type:"))
        self.chart_type = QComboBox()
        self.chart_type.addItems(["Candlestick", "Line", "OHLC"])
        layout.addWidget(self.chart_type)
        
        # Display options
        self.show_volume = QCheckBox("Show Volume")
        self.dark_mode = QCheckBox("Dark Mode")
        
        layout.addWidget(self.show_volume)
        layout.addWidget(self.dark_mode)
        
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
            
            # Stocks tab
            stocks = self.config.get("stocks", [])
            if stocks:
                self.stock_list_widget.set_stocks(stocks)
            
            # Display tab
            self.show_volume.setChecked(self.config.get("show_volume", True))
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
            
            # Stocks tab
            self.config["stocks"] = self.stock_list_widget.get_stocks()
            
            # Display tab
            self.config["show_volume"] = self.show_volume.isChecked()
            self.config["dark_mode"] = self.dark_mode.isChecked()
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            
    def get_config(self):
        """Return the current configuration."""
        return self.config
