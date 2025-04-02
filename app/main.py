#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import logging
import threading
from pathlib import Path
import json
import traceback
import pandas as pd

from PySide6.QtCore import QCoreApplication, QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox

from app.config import ConfigManager
from app.api.alphavantage import AlphaVantageClient
from app.wallpaper import WallpaperManager
from app.ui.settings import SettingsDialog
from app.services.updater import StockUpdater

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global constants
APP_NAME = "WallStonks"
APP_VERSION = "1.0.0"
DEFAULT_CONFIG = {
    "api_key": "",
    "stocks": [],
    "chart_type": "line",
    "time_range": "1d",
    "update_interval": 15,  # minutes
    "trading_hours_only": True,
    "dark_theme": True,
    "show_grid": True,
    "show_volume": True
}

class WallStonksApp:
    """
    Main application class for WallStonks.
    Handles the system tray icon, settings dialog, and background services.
    """
    
    def __init__(self):
        """Initialize the application."""
        # Create the application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)
        
        # Set up the icon
        self.setup_icon()
        
        # Load configuration
        self.config_manager = ConfigManager(DEFAULT_CONFIG)
        self.config = self.config_manager.load()
        
        # Initialize stock API client
        self.api_client = AlphaVantageClient(self.config.get("api_key", ""))
        
        # Initialize wallpaper manager
        self.wallpaper_manager = WallpaperManager(self.config)
        
        # Initialize updater service
        self.updater = StockUpdater(self.config, self.api_client)
        self.updater.update_ready.connect(self.refresh_wallpaper)
        self.updater.status_changed.connect(self.update_status)
        
        # Create system tray icon
        self.setup_tray()
        
        # Status variable
        self.status_message = "Ready"
        
        # Stock data cache
        self.stock_data = {}
        self.quotes = {}
        
        # Flag to track initial setup
        self.initial_setup_done = False
        
        # Check if this is first run or API key is missing
        if not self.config.get("api_key") or not self.config.get("stocks"):
            # Show settings dialog on first run
            self.show_settings()
            self.show_info("Welcome to WallStonks!", 
                           "Please configure your API key and add stocks to track.")
            self.initial_setup_done = True
        else:
            # Start in background
            QTimer.singleShot(1000, self.start_background_services)
    
    def setup_icon(self):
        """Set up the application icon."""
        # Use default icons if custom icon is not available
        icon_path = None
        
        # Check for application icon
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                icon_path = path
                break
        
        if icon_path:
            self.icon = QIcon(icon_path)
        else:
            # Use a system icon as fallback
            self.icon = QIcon.fromTheme("utilities-system-monitor")
    
    def setup_tray(self):
        """Set up the system tray icon and menu."""
        # Create the tray icon
        self.tray = QSystemTrayIcon(self.icon)
        self.tray.setToolTip(f"{APP_NAME} v{APP_VERSION}")
        
        # Create the tray menu
        self.tray_menu = QMenu()
        
        # Add menu items
        self.refresh_action = self.tray_menu.addAction("Refresh Now")
        self.refresh_action.triggered.connect(self.manual_refresh)
        
        self.settings_action = self.tray_menu.addAction("Settings")
        self.settings_action.triggered.connect(self.show_settings)
        
        self.tray_menu.addSeparator()
        
        self.about_action = self.tray_menu.addAction("About")
        self.about_action.triggered.connect(self.show_about)
        
        self.exit_action = self.tray_menu.addAction("Exit")
        self.exit_action.triggered.connect(self.quit)
        
        # Set the menu and show the tray icon
        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()
        
        # Connect signals
        self.tray.activated.connect(self.tray_activated)
    
    def start_background_services(self):
        """Start background services."""
        logger.info("Starting background services")
        try:
            # Check if API key is configured
            if not self.config.get("api_key"):
                self.show_error("API Key Missing", 
                               "Please configure your Alpha Vantage API key in the settings.")
                self.show_settings()
                return
            
            # Check if stocks are configured
            if not self.config.get("stocks"):
                self.show_error("No Stocks Selected", 
                               "Please add at least one stock to track in the settings.")
                self.show_settings()
                return
            
            # Start updater service
            self.updater.start()
            
            # Initial wallpaper update
            QTimer.singleShot(1000, self.refresh_wallpaper)
            
        except Exception as e:
            logger.error(f"Error starting background services: {e}")
            self.show_error("Error", f"Failed to start background services: {str(e)}")
    
    def tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - show basic info
            self.show_status()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - show settings
            self.show_settings()
    
    def show_settings(self):
        """Show the settings dialog."""
        try:
            logger.info("Opening settings dialog")
            dialog = SettingsDialog(self.config)
            
            # Connect the API key test signal
            dialog.test_api_key_requested.connect(self.test_api_key)
            
            # Show dialog
            if dialog.exec():
                # Save the new configuration
                new_config = dialog.get_config()
                
                # Check if API key changed
                api_key_changed = new_config.get("api_key") != self.config.get("api_key")
                
                # Update the config
                self.config = new_config
                self.config_manager.save(self.config)
                
                # Update client API key if changed
                if api_key_changed:
                    self.api_client.set_api_key(self.config.get("api_key", ""))
                
                # Restart services if they're running
                if self.updater.running:
                    self.updater.stop()
                    self.start_background_services()
                elif not self.initial_setup_done:
                    # First-time setup
                    self.start_background_services()
                    self.initial_setup_done = True
                else:
                    # Manual refresh with new settings
                    self.refresh_wallpaper()
                
                logger.info("Settings updated")
            else:
                logger.info("Settings dialog canceled")
                
        except Exception as e:
            logger.error(f"Error in settings dialog: {e}")
            self.show_error("Error", f"Failed to open settings: {str(e)}")
    
    def test_api_key(self, api_key):
        """
        Test the provided Alpha Vantage API key.
        
        Args:
            api_key (str): The API key to test
        """
        logger.info("Testing API key")
        try:
            # Create a temporary client with the new key
            test_client = AlphaVantageClient(api_key)
            
            # Test by getting a simple quote
            result = test_client.get_global_quote("AAPL")
            
            if result and 'Global Quote' in result:
                self.show_info("API Key Test", "The API key is valid.")
                return True
            else:
                self.show_error("API Key Test", "The API key appears to be invalid or rate limited.")
                return False
                
        except Exception as e:
            logger.error(f"API key test failed: {e}")
            self.show_error("API Key Test", f"Error testing API key: {str(e)}")
            return False
    
    def manual_refresh(self):
        """Manually refresh the wallpaper."""
        logger.info("Manual refresh requested")
        try:
            # Check if updater is running, start it if not
            if not self.updater.running:
                self.start_background_services()
            else:
                # Request immediate refresh
                self.updater.refresh_now()
                
        except Exception as e:
            logger.error(f"Error during manual refresh: {e}")
            self.show_error("Error", f"Failed to refresh: {str(e)}")
    
    def refresh_wallpaper(self):
        """Refresh the wallpaper with current stock data."""
        logger.info("Refreshing wallpaper with latest stock data")
        try:
            # Update status
            self.update_status("Fetching stock data...")
            self.tray.setToolTip(f"{APP_NAME} - Updating...")
            
            # Fetch data for all configured stocks
            symbols = self.config.get("stocks", [])
            time_range = self.config.get("time_range", "1d")
            
            if not symbols:
                logger.warning("No stocks configured")
                self.update_status("No stocks configured")
                return
                
            # Fetch stock data for all symbols
            self.stock_data = {}
            self.quotes = {}
            
            for symbol in symbols:
                try:
                    # Get quote data
                    quote_data = self.api_client.get_global_quote(symbol)
                    if quote_data and 'Global Quote' in quote_data:
                        quote = quote_data['Global Quote']
                        self.quotes[symbol] = {
                            'price': float(quote.get('05. price', 0)),
                            'change': float(quote.get('09. change', 0)),
                            'change_percent': quote.get('10. change percent', '0%').strip('%')
                        }
                    
                    # Get time series data
                    df = None
                    if time_range == '1d':
                        df = self.api_client.get_intraday(symbol, interval='5min')
                    elif time_range in ['3d', '1w']:
                        df = self.api_client.get_intraday(symbol, interval='15min', outputsize='full')
                        # Filter to last N days
                        if df is not None:
                            days = 3 if time_range == '3d' else 7
                            cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
                            df = df[df.index > cutoff]
                    elif time_range == '1m':
                        df = self.api_client.get_daily(symbol, outputsize='compact')
                        # Filter to last 30 days
                        if df is not None:
                            cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
                            df = df[df.index > cutoff]
                    elif time_range in ['3m', '6m', '1y']:
                        df = self.api_client.get_daily(symbol, outputsize='full')
                        # Filter based on time range
                        if df is not None:
                            months = 3 if time_range == '3m' else 6 if time_range == '6m' else 12
                            cutoff = pd.Timestamp.now() - pd.Timedelta(days=30*months)
                            df = df[df.index > cutoff]
                    elif time_range == 'all':
                        # Get all available data
                        df = self.api_client.get_daily(symbol, outputsize='full')
                    
                    if df is not None:
                        self.stock_data[symbol] = df
                        logger.info(f"Fetched data for {symbol}: {len(df)} data points")
                    else:
                        logger.warning(f"No data returned for {symbol}")
                
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
                    continue
            
            if not self.stock_data:
                self.update_status("Failed to fetch any stock data")
                return
            
            # Create and set wallpaper
            self.update_status("Creating wallpaper...")
            wallpaper_path = self.wallpaper_manager.create_chart_wallpaper(
                self.stock_data, self.quotes)
            
            if wallpaper_path:
                success = self.wallpaper_manager.set_wallpaper(wallpaper_path)
                if success:
                    self.update_status("Wallpaper updated successfully")
                    
                    # Update tooltip with latest stock info
                    tooltip = f"{APP_NAME} - "
                    for symbol, quote in self.quotes.items():
                        price = quote['price']
                        change = quote['change']
                        tooltip += f"{symbol}: ${price:.2f} "
                        if change >= 0:
                            tooltip += f"▲{abs(change):.2f} "
                        else:
                            tooltip += f"▼{abs(change):.2f} "
                    
                    self.tray.setToolTip(tooltip)
                else:
                    self.update_status("Failed to set wallpaper")
            else:
                self.update_status("Failed to create wallpaper")
        
        except Exception as e:
            logger.error(f"Error refreshing wallpaper: {e}")
            self.update_status(f"Error: {str(e)}")
    
    def update_status(self, message=None):
        """
        Update the status message.
        
        Args:
            message (str, optional): The new status message
        """
        if message:
            self.status_message = message
            logger.info(f"Status: {message}")
    
    def show_status(self):
        """Show the current status message."""
        stocks_info = ""
        for symbol, quote in self.quotes.items():
            price = quote['price']
            change = quote['change']
            change_percent = quote['change_percent']
            stocks_info += f"{symbol}: ${price:.2f} "
            if float(change) >= 0:
                stocks_info += f"▲{abs(float(change)):.2f} ({change_percent}%)\n"
            else:
                stocks_info += f"▼{abs(float(change)):.2f} ({change_percent}%)\n"
        
        title = f"{APP_NAME} Status"
        message = f"Status: {self.status_message}\n\n"
        
        if stocks_info:
            message += f"Current Quotes:\n{stocks_info}\n"
        
        message += f"Update Interval: {self.config.get('update_interval', 15)} minutes\n"
        message += f"Chart Type: {self.config.get('chart_type', 'line')}\n"
        message += f"Time Range: {self.config.get('time_range', '1d')}"
        
        self.show_info(title, message)
    
    def show_about(self):
        """Show the about dialog."""
        title = f"About {APP_NAME}"
        message = f"{APP_NAME} v{APP_VERSION}\n\n"
        message += "A desktop application that sets your wallpaper to stock charts.\n\n"
        message += "Data provided by Alpha Vantage\n"
        message += "https://www.alphavantage.co/"
        
        self.show_info(title, message)
    
    def show_info(self, title, message):
        """Show an information message box."""
        QMessageBox.information(None, title, message)
    
    def show_error(self, title, message):
        """Show an error message box."""
        QMessageBox.critical(None, title, message)
    
    def quit(self):
        """Quit the application."""
        logger.info("Exiting application")
        # Stop background services
        if hasattr(self, 'updater'):
            self.updater.stop()
        
        # Quit the application
        QCoreApplication.quit()
    
    def run(self):
        """Run the application main loop."""
        return self.app.exec()

def main():
    """Main entry point for the application."""
    try:
        # Set application attributes for high DPI
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create and run the application
        app = WallStonksApp()
        return app.run()
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        logger.critical(traceback.format_exc())
        
        # Show error message if possible
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Fatal Error", 
                               f"A fatal error occurred:\n\n{str(e)}\n\nSee log for details.")
        except:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main()) 