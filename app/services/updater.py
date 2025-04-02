#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
import logging
from datetime import datetime, time as dt_time, timedelta
import pytz
from PySide6.QtCore import QObject, Signal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockUpdater(QObject):
    """
    Background service that periodically updates stock data and refreshes the wallpaper.
    Emits a signal when updates are ready so the main app can refresh the wallpaper.
    """
    
    # Define signals
    update_ready = Signal()
    status_changed = Signal(str)
    
    def __init__(self, config, client):
        """
        Initialize the updater service.
        
        Args:
            config (dict): App configuration
            client (AlphaVantageClient): Stock data client
        """
        super().__init__()
        self.config = config
        self.client = client
        self.running = False
        self.update_thread = None
        self.next_update_time = None
        self.market_closed = True
        self.is_market_day = False
        
        # Timezone for US markets (Eastern Time)
        self.market_tz = pytz.timezone('US/Eastern')
        
        # Market trading hours (9:30 AM - 4:00 PM Eastern Time)
        self.market_open_time = dt_time(9, 30)
        self.market_close_time = dt_time(16, 0)
    
    def start(self):
        """Start the update service."""
        if self.running:
            return
            
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        logger.info("Stock updater service started")
        self.status_changed.emit("Update service started")
    
    def stop(self):
        """Stop the update service."""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
            self.update_thread = None
            
        logger.info("Stock updater service stopped")
        self.status_changed.emit("Update service stopped")
    
    def _update_loop(self):
        """Main update loop that runs in a background thread."""
        while self.running:
            try:
                # Check if we need to update based on the configured interval
                self._check_and_update()
                
                # Sleep for a short period before checking again
                # Using short sleep intervals allows for more responsive stopping
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(60)  # Longer wait on error
    
    def _check_and_update(self):
        """Check if it's time to update and perform update if needed."""
        now = datetime.now()
        
        # Check market status
        self._update_market_status()
        
        # Determine if an update is needed
        if self._should_update(now):
            logger.info(f"Performing scheduled update at {now}")
            self.status_changed.emit("Updating stock data...")
            
            # Perform the update
            self._perform_update()
            
            # Calculate next update time
            self._calculate_next_update_time(now)
            
            logger.info(f"Next update scheduled for: {self.next_update_time}")
            status_msg = f"Updated. Next update: {self.next_update_time.strftime('%H:%M:%S')}"
            self.status_changed.emit(status_msg)
    
    def _should_update(self, now):
        """
        Determine if an update should be performed.
        
        Args:
            now (datetime): Current datetime
            
        Returns:
            bool: True if update is needed, False otherwise
        """
        # First run (no next update time set)
        if self.next_update_time is None:
            return True
            
        # If next update time has been reached
        if now >= self.next_update_time:
            return True
            
        # If trading_hours_only is enabled, check market status
        if self.config.get("trading_hours_only", True):
            # Only update during market hours
            return not self.market_closed and self.is_market_day
            
        # Otherwise update based on schedule
        return False
    
    def _update_market_status(self):
        """Update the market status (open/closed) and day type."""
        # Get current time in market timezone
        now_et = datetime.now(self.market_tz)
        
        # Check if it's a weekday (0 = Monday, 6 = Sunday)
        self.is_market_day = now_et.weekday() < 5
        
        # Market hours check (9:30 AM - 4:00 PM ET, weekdays only)
        current_time = now_et.time()
        
        if (self.is_market_day and 
            current_time >= self.market_open_time and 
            current_time < self.market_close_time):
            self.market_closed = False
        else:
            self.market_closed = True
            
        # If market status changed, emit signal
        if not self.market_closed:
            self.status_changed.emit("Market is open")
        else:
            if self.is_market_day:
                self.status_changed.emit("Market is closed")
            else:
                self.status_changed.emit("Market is closed (weekend)")
    
    def _calculate_next_update_time(self, now):
        """
        Calculate the next update time based on the current time and update interval.
        
        Args:
            now (datetime): Current datetime
        """
        # Get update interval in minutes
        interval_minutes = self.config.get("update_interval", 15)
        
        # Ensure interval is at least 1 minute to prevent excessive updates
        interval_minutes = max(1, interval_minutes)
        
        # Calculate next update time
        seconds_to_add = interval_minutes * 60
        self.next_update_time = now.fromtimestamp(now.timestamp() + seconds_to_add)
        
        # If trading hours only, adjust next update time if market is closed
        if self.config.get("trading_hours_only", True) and self.market_closed:
            # If weekend or after market close, set next update to market open on next trading day
            now_et = datetime.now(self.market_tz)
            
            # If it's a weekend (Saturday = 5, Sunday = 6)
            if now_et.weekday() >= 5:
                # Set next update to Monday morning
                days_to_add = 7 - now_et.weekday()
                next_date = now_et.date() + timedelta(days=days_to_add)
                next_date_time = datetime.combine(next_date, self.market_open_time)
                self.next_update_time = next_date_time.astimezone(pytz.utc).replace(tzinfo=None)
            
            # If it's after market close
            elif now_et.time() >= self.market_close_time:
                # Set next update to tomorrow morning if it's a weekday
                if now_et.weekday() < 4:  # Monday to Thursday
                    next_date = now_et.date() + timedelta(days=1)
                else:  # Friday
                    next_date = now_et.date() + timedelta(days=3)  # Skip to Monday
                
                next_date_time = datetime.combine(next_date, self.market_open_time)
                self.next_update_time = next_date_time.astimezone(pytz.utc).replace(tzinfo=None)
    
    def _perform_update(self):
        """Fetch updated stock data and signal that an update is ready."""
        # Emit update_ready signal so the main app can refresh the wallpaper
        self.update_ready.emit()
    
    def refresh_now(self):
        """Force an immediate refresh."""
        logger.info("Manual refresh requested")
        self.status_changed.emit("Manual refresh requested...")
        self._perform_update()
        
        # Reset next update time
        now = datetime.now()
        self._calculate_next_update_time(now)
        
        logger.info(f"Manual refresh completed. Next update at: {self.next_update_time}")
        status_msg = f"Refresh completed. Next update: {self.next_update_time.strftime('%H:%M:%S')}"
        self.status_changed.emit(status_msg) 