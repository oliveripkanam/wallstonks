#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QSystemTrayIcon, QMenu, QDialog, 
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QApplication
)
from PySide6.QtGui import QIcon, QAction, QPixmap, QColor, QPainter
from PySide6.QtCore import Qt, QTimer, QSize
import os

from app.ui.settings import SettingsDialog
from app.api_client import StockDataClient
from app.wallpaper import WallpaperManager

class SystemTrayIcon(QSystemTrayIcon):
    """
    System tray icon for WallStonks application.
    Provides menu options for configuration and app control.
    """
    
    def __init__(self, config):
        """Initialize the system tray icon."""
        super().__init__()
        self.config = config
        self.setToolTip("WallStonks")
        
        # Create a blank icon (Qt requires an icon even if we don't want one visible)
        self.create_blank_icon()
        
        # Initialize components
        self.stock_client = StockDataClient(config.get("api_key", ""))
        self.wallpaper_manager = WallpaperManager(config)
        
        # Data storage
        self.stock_data = {}  # Will store stock data indexed by symbol
        self.quotes = {}      # Will store current quotes indexed by symbol
        
        # Create the tray menu
        self.setup_menu()
        
        # Connect signals
        self.activated.connect(self.on_tray_activated)
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.start_refresh_timer()
        
        # Initial data refresh
        self.refresh_data()
    
    def create_blank_icon(self):
        """Create a minimal blank/transparent icon."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        # Add a tiny dot so it's minimally visible
        painter = QPainter(pixmap)
        painter.setPen(QColor(200, 200, 200, 50))  # Very light gray, mostly transparent
        painter.drawPoint(8, 8)
        painter.end()
        
        icon = QIcon(pixmap)
        self.setIcon(icon)
    
    def setup_menu(self):
        """Set up the system tray menu."""
        menu = QMenu()
        
        # Main actions
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.open_settings)
        
        self.refresh_action = QAction("Refresh Now", self)
        self.refresh_action.triggered.connect(self.refresh_data)
        
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about)
        
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.quit_application)
        
        # Add actions to menu
        menu.addAction(self.settings_action)
        menu.addAction(self.refresh_action)
        menu.addSeparator()
        menu.addAction(self.about_action)
        menu.addSeparator()
        menu.addAction(self.quit_action)
        
        # Set the menu
        self.setContextMenu(menu)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - show a quick view of stock performance
            self.show_quick_view()
    
    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self.config)
        dialog.settingsChanged.connect(self.on_settings_changed)
        dialog.exec()
    
    def on_settings_changed(self):
        """Handle settings changes."""
        # Update API client if key changed
        self.stock_client.set_api_key(self.config.get("api_key", ""))
        
        # Update refresh timer if interval changed
        self.start_refresh_timer()
        
        # Refresh data with new settings
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh stock data and update wallpaper."""
        # Skip if no API key or no stocks configured
        if not self.config.get("api_key") or not self.config.get("stocks"):
            self.showMessage("WallStonks", "Please add an API key and at least one stock in settings.")
            return
        
        # Get stock data for each configured stock
        stocks = self.config.get("stocks", [])
        time_range = self.config.get("time_range", "1d")
        chart_type = self.config.get("chart_type", "line")
        
        # Fetch data for each stock
        for symbol in stocks:
            # Get historical data
            data, error = self.stock_client.get_stock_data(
                symbol, 
                time_range=time_range, 
                chart_type=chart_type
            )
            
            if data is not None:
                self.stock_data[symbol] = data
            
            # Get current quote
            quote, error = self.stock_client.get_quote(symbol)
            if quote is not None:
                self.quotes[symbol] = quote
        
        # Update wallpaper with new data
        if self.stock_data and self.quotes:
            wallpaper_path = self.wallpaper_manager.create_chart_wallpaper(
                self.stock_data, 
                self.quotes
            )
            
            if wallpaper_path:
                self.wallpaper_manager.set_wallpaper(wallpaper_path)
                self.showMessage("WallStonks", "Wallpaper updated with latest stock data.")
    
    def show_about(self):
        """Show the about dialog."""
        about_dialog = QDialog()
        about_dialog.setWindowTitle("About WallStonks")
        
        layout = QVBoxLayout()
        
        title_label = QLabel("WallStonks")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        version_label = QLabel("Version 0.1.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc_label = QLabel(
            "A real-time stock wallpaper application that lets you monitor "
            "your stock performance directly on your desktop background."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        button = QPushButton("Close")
        button.clicked.connect(about_dialog.accept)
        
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addSpacing(10)
        layout.addWidget(desc_label)
        layout.addSpacing(10)
        layout.addWidget(button)
        
        about_dialog.setLayout(layout)
        about_dialog.exec()
    
    def show_quick_view(self):
        """Show a quick view of current stock performance."""
        if not self.quotes:
            self.showMessage("WallStonks", "No stock data available. Check your settings.")
            return
        
        # Create a simple message showing current stock performance
        message = "Current Stock Performance:\n\n"
        
        for symbol, quote in self.quotes.items():
            change = quote['change']
            change_pct = quote['change_percent']
            arrow = "▲" if float(change) >= 0 else "▼"
            
            message += f"{symbol}: ${quote['price']} {arrow} {abs(float(change)):.2f} ({change_pct}%)\n"
        
        self.showMessage("WallStonks", message)
    
    def start_refresh_timer(self):
        """Start the refresh timer based on configuration."""
        interval = self.config.get("refresh_interval", 60) * 1000  # Convert to milliseconds
        self.refresh_timer.start(interval)
    
    def quit_application(self):
        """Quit the application."""
        self.refresh_timer.stop()
        self.hide()
        QApplication.quit() 