#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, 
    QLineEdit, QComboBox, QPushButton, QGroupBox, QCheckBox,
    QListWidget, QListWidgetItem, QSpinBox, QGridLayout,
    QFormLayout, QFrame, QSizePolicy, QToolTip
)

from app.api.alphavantage import AlphaVantageClient
from app.ui.components.autocomplete import StockListWidget

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """
    Dialog for configuring application settings.
    """
    
    # Signals
    test_api_key_requested = Signal(str)
    
    def __init__(self, config):
        """
        Initialize the settings dialog.
        
        Args:
            config (dict): Current configuration settings
        """
        super().__init__()
        
        self.config = config.copy()
        self.setWindowTitle("WallStonks Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        
        # Create the layout
        self.create_layout()
        
        # Load current settings
        self.load_settings()
    
    def create_layout(self):
        """Create the dialog layout."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.tab_widget.addTab(self.create_general_tab(), "General")
        self.tab_widget.addTab(self.create_stocks_tab(), "Stocks")
        self.tab_widget.addTab(self.create_display_tab(), "Display")
        
        main_layout.addWidget(self.tab_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create the general settings tab."""
        # Create tab widget
        tab = QFrame()
        layout = QVBoxLayout(tab)
        
        # API key group
        api_group = QGroupBox("Alpha Vantage API Key")
        api_layout = QVBoxLayout(api_group)
        
        # Help text
        help_text = QLabel("You need an Alpha Vantage API key to fetch stock data.")
        help_text.setWordWrap(True)
        api_layout.addWidget(help_text)
        
        # Get key link
        api_link = QPushButton("Get a free API key")
        api_link.clicked.connect(self.open_api_website)
        api_layout.addWidget(api_link)
        
        # API key input
        key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Alpha Vantage API key")
        self.api_key_input.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        
        test_button = QPushButton("Test Key")
        test_button.clicked.connect(self.test_api_key)
        
        key_layout.addWidget(self.api_key_input)
        key_layout.addWidget(test_button)
        
        api_layout.addLayout(key_layout)
        layout.addWidget(api_group)
        
        # Update interval
        update_group = QGroupBox("Update Settings")
        update_layout = QFormLayout(update_group)
        
        # Update interval input
        self.update_interval_input = QSpinBox()
        self.update_interval_input.setMinimum(1)
        self.update_interval_input.setMaximum(60)
        self.update_interval_input.setSuffix(" minutes")
        update_layout.addRow("Update Interval:", self.update_interval_input)
        
        # Trading hours only checkbox
        self.trading_hours_only = QCheckBox("Only update during trading hours (9:30 AM - 4:00 PM ET, weekdays)")
        update_layout.addRow("", self.trading_hours_only)
        
        layout.addWidget(update_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
    
    def create_stocks_tab(self):
        """Create the stocks selection tab."""
        # Create tab widget
        tab = QFrame()
        layout = QVBoxLayout(tab)
        
        # Add explanatory text
        help_text = QLabel("Add up to 5 stocks to display on your wallpaper:")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        
        # Create stock list widget with search
        self.stock_list_widget = StockListWidget(self.config.get("stocks", []))
        layout.addWidget(self.stock_list_widget)
        
        return tab
    
    def create_display_tab(self):
        """Create the display settings tab."""
        # Create tab widget
        tab = QFrame()
        layout = QVBoxLayout(tab)
        
        # Chart type group
        chart_group = QGroupBox("Chart Type")
        chart_layout = QVBoxLayout(chart_group)
        
        # Chart type selection
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItem("Line Chart", "line")
        self.chart_type_combo.addItem("Candlestick Chart", "candlestick")
        chart_layout.addWidget(self.chart_type_combo)
        
        layout.addWidget(chart_group)
        
        # Time range group
        time_group = QGroupBox("Time Range")
        time_layout = QGridLayout(time_group)
        
        # Time range options
        self.time_range_combos = {}
        
        ranges = [
            ("1 Day", "1d"), 
            ("3 Days", "3d"), 
            ("1 Week", "1w"),
            ("1 Month", "1m"), 
            ("3 Months", "3m"), 
            ("6 Months", "6m"),
            ("1 Year", "1y"), 
            ("All Time", "all")
        ]
        
        row, col = 0, 0
        for label, value in ranges:
            radio = QCheckBox(label)
            radio.clicked.connect(lambda checked, v=value: self.set_time_range(v))
            self.time_range_combos[value] = radio
            time_layout.addWidget(radio, row, col)
            col += 1
            if col > 3:  # 4 columns
                col = 0
                row += 1
        
        layout.addWidget(time_group)
        
        # Visual options group
        visual_group = QGroupBox("Visual Options")
        visual_layout = QVBoxLayout(visual_group)
        
        # Theme selection
        self.dark_theme_checkbox = QCheckBox("Dark Theme")
        visual_layout.addWidget(self.dark_theme_checkbox)
        
        # Show grid
        self.show_grid_checkbox = QCheckBox("Show Grid")
        visual_layout.addWidget(self.show_grid_checkbox)
        
        # Show volume
        self.show_volume_checkbox = QCheckBox("Show Volume")
        visual_layout.addWidget(self.show_volume_checkbox)
        
        layout.addWidget(visual_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
    
    def set_time_range(self, value):
        """
        Set the time range by unchecking all other options.
        
        Args:
            value (str): The time range value to set
        """
        # Uncheck all other time range options
        for range_value, checkbox in self.time_range_combos.items():
            if range_value != value:
                checkbox.setChecked(False)
        
        # Ensure the selected option is checked
        self.time_range_combos[value].setChecked(True)
    
    def open_api_website(self):
        """Open the Alpha Vantage website to get an API key."""
        QDesktopServices.openUrl(QUrl("https://www.alphavantage.co/support/#api-key"))
    
    def test_api_key(self):
        """Test the current API key."""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QToolTip.showText(self.api_key_input.mapToGlobal(self.api_key_input.rect().bottomRight()), 
                             "Please enter an API key first")
            return
        
        # Emit signal to test the key
        self.test_api_key_requested.emit(api_key)
    
    def load_settings(self):
        """Load the current settings into the UI."""
        # API key
        self.api_key_input.setText(self.config.get("api_key", ""))
        
        # Update interval
        self.update_interval_input.setValue(self.config.get("update_interval", 15))
        
        # Trading hours only
        self.trading_hours_only.setChecked(self.config.get("trading_hours_only", True))
        
        # Chart type
        chart_type = self.config.get("chart_type", "line")
        index = self.chart_type_combo.findData(chart_type)
        if index >= 0:
            self.chart_type_combo.setCurrentIndex(index)
        
        # Time range
        time_range = self.config.get("time_range", "1d")
        if time_range in self.time_range_combos:
            self.time_range_combos[time_range].setChecked(True)
        
        # Visual options
        self.dark_theme_checkbox.setChecked(self.config.get("dark_theme", True))
        self.show_grid_checkbox.setChecked(self.config.get("show_grid", True))
        self.show_volume_checkbox.setChecked(self.config.get("show_volume", True))
    
    def get_config(self):
        """
        Get the updated configuration from the UI.
        
        Returns:
            dict: The updated configuration
        """
        # Start with the existing config
        updated_config = self.config.copy()
        
        # Update with new values
        updated_config["api_key"] = self.api_key_input.text().strip()
        updated_config["update_interval"] = self.update_interval_input.value()
        updated_config["trading_hours_only"] = self.trading_hours_only.isChecked()
        
        # Get selected stocks
        updated_config["stocks"] = self.stock_list_widget.get_selected_stocks()
        
        # Chart type
        updated_config["chart_type"] = self.chart_type_combo.currentData()
        
        # Time range
        for value, checkbox in self.time_range_combos.items():
            if checkbox.isChecked():
                updated_config["time_range"] = value
                break
        
        # Visual options
        updated_config["dark_theme"] = self.dark_theme_checkbox.isChecked()
        updated_config["show_grid"] = self.show_grid_checkbox.isChecked()
        updated_config["show_volume"] = self.show_volume_checkbox.isChecked()
        
        return updated_config 