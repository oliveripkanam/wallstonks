#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import threading
import time
from datetime import datetime, timedelta
from app.api_client import StockDataClient
from app.wallpaper import WallpaperManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackgroundService:
    """
    Background service for WallStonks application.
    Manages periodic updates and data fetching in the background.
    """
    
    def __init__(self, config):
        """Initialize the background service."""
        self.config = config
        self.stock_client = StockDataClient(config.get("api_key", ""))
        self.wallpaper_manager = WallpaperManager(config)
        
        self.stock_data = {}  # Historical data by symbol
        self.quotes = {}      # Current quotes by symbol
        
        self.running = False
        self.thread = None
        self.last_update = None
        
        # Lock for thread safety
        self.lock = threading.Lock()
    
    def start(self):
        """Start the background service."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._background_task, daemon=True)
        self.thread.start()
        logger.info("Background service started")
    
    def stop(self):
        """Stop the background service."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        logger.info("Background service stopped")
    
    def _background_task(self):
        """Background task that runs periodically."""
        while self.running:
            try:
                # Refresh interval in seconds
                interval = self.config.get("refresh_interval", 60)
                
                # Check if we should update
                current_time = datetime.now()
                if (self.last_update is None or 
                    (current_time - self.last_update).total_seconds() >= interval):
                    
                    # Check if we're in trading hours (if trading_hours_only is enabled)
                    if self.config.get("trading_hours_only", True) and not self._is_trading_hours():
                        logger.info("Outside trading hours, skipping update")
                    else:
                        # Update data
                        self._update_data()
                        self.last_update = current_time
                
                # Sleep for a short time before checking again
                time.sleep(5)
            
            except Exception as e:
                logger.error(f"Error in background task: {e}")
                time.sleep(30)  # Longer sleep on error
    
    def _is_trading_hours(self):
        """
        Check if current time is within trading hours.
        Trading hours are considered to be 9:30 AM to 4:00 PM Eastern Time, Monday to Friday.
        This is a simplified check and doesn't account for holidays.
        """
        # In a real implementation, you would need to convert to Eastern Time
        # For now, we'll use a simplified approach
        now = datetime.now()
        
        # Check if it's a weekday (0 = Monday, 6 = Sunday)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check if it's between 9:30 AM and 4:00 PM (simplified)
        # In a real implementation, you'd convert to Eastern Time
        if now.hour < 9 or now.hour > 16:
            return False
        if now.hour == 9 and now.minute < 30:
            return False
        
        return True
    
    def _update_data(self):
        """Update stock data and wallpaper."""
        # Skip if no API key or no stocks configured
        if not self.config.get("api_key") or not self.config.get("stocks"):
            logger.warning("No API key or stocks configured, skipping update")
            return
        
        # Get settings
        stocks = self.config.get("stocks", [])
        time_range = self.config.get("time_range", "1d")
        chart_type = self.config.get("chart_type", "line")
        
        with self.lock:
            # Fetch data for each stock
            for symbol in stocks:
                try:
                    # Get historical data
                    data, error = self.stock_client.get_stock_data(
                        symbol, 
                        time_range=time_range, 
                        chart_type=chart_type
                    )
                    
                    if data is not None:
                        self.stock_data[symbol] = data
                    elif error:
                        logger.error(f"Error fetching data for {symbol}: {error}")
                    
                    # Get current quote
                    quote, error = self.stock_client.get_quote(symbol)
                    if quote is not None:
                        self.quotes[symbol] = quote
                    elif error:
                        logger.error(f"Error fetching quote for {symbol}: {error}")
                
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
            
            # Update wallpaper with new data
            if self.stock_data and self.quotes:
                try:
                    wallpaper_path = self.wallpaper_manager.create_chart_wallpaper(
                        self.stock_data, 
                        self.quotes
                    )
                    
                    if wallpaper_path:
                        self.wallpaper_manager.set_wallpaper(wallpaper_path)
                        logger.info("Wallpaper updated with latest stock data")
                except Exception as e:
                    logger.error(f"Error updating wallpaper: {e}")
            else:
                logger.warning("No data available to update wallpaper")
    
    def get_data(self):
        """Get the current stock data and quotes (thread-safe)."""
        with self.lock:
            return self.stock_data.copy(), self.quotes.copy()
    
    def force_update(self):
        """Force an immediate data update."""
        threading.Thread(target=self._update_data, daemon=True).start() 