#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import ctypes
import tempfile
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter
from datetime import datetime
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WallpaperManager:
    """
    Manager for creating and setting stock chart wallpapers.
    """
    
    def __init__(self, config):
        """Initialize the wallpaper manager."""
        self.config = config
        self.wallpaper_path = None
    
    def create_chart_wallpaper(self, stock_data_dict, quotes_dict):
        """
        Create a wallpaper with stock charts.
        
        Args:
            stock_data_dict (dict): Dictionary of stock data frames indexed by stock symbol
            quotes_dict (dict): Dictionary of current quotes indexed by stock symbol
            
        Returns:
            str: Path to the created wallpaper image
        """
        # Get screen dimensions (approximation)
        width_inches = 19.2  # For 1920px at 100 DPI
        height_inches = 10.8  # For 1080px at 100 DPI
        dpi = 100
        
        # Create figure with appropriate size
        plt.figure(figsize=(width_inches, height_inches), dpi=dpi)
        
        # Set theme
        if self.config.get("dark_theme", True):
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
        
        # Number of stocks
        num_stocks = len(stock_data_dict)
        if num_stocks == 0:
            return None
        
        # Add title
        time_range_labels = {
            "1d": "1 Day", "3d": "3 Days", "1w": "1 Week",
            "1m": "1 Month", "3m": "3 Months", "6m": "6 Months",
            "1y": "1 Year", "all": "All Time"
        }
        time_range = self.config.get("time_range", "1d")
        title = f"WallStonks Portfolio - {time_range_labels.get(time_range, time_range)} View"
        plt.suptitle(title, fontsize=24, fontweight='bold', y=0.98)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plt.figtext(0.98, 0.02, f"Updated: {timestamp}", ha='right', fontsize=8)
        
        # Create subplots for each stock
        for i, (symbol, data) in enumerate(stock_data_dict.items(), 1):
            if data is None or data.empty:
                continue
                
            # Create subplot with appropriate size
            ax = plt.subplot(num_stocks, 1, i)
            
            # Get current quote data
            quote = quotes_dict.get(symbol)
            
            # Plot stock data
            chart_type = self.config.get("chart_type", "line")
            
            if chart_type == "line":
                # Line chart
                self._plot_line_chart(ax, data, symbol, quote)
            else:
                # Candlestick chart
                self._plot_candlestick_chart(ax, data, symbol, quote)
            
            # Format the chart
            self._format_chart(ax, data, symbol, quote, i == num_stocks)
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # Save the chart as an image file
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.wallpaper_path = os.path.join(temp_dir, f"wallstonks_{timestamp}.png")
        
        plt.savefig(self.wallpaper_path, dpi=dpi, bbox_inches='tight')
        plt.close()
        
        return self.wallpaper_path
    
    def _plot_line_chart(self, ax, data, symbol, quote):
        """Plot line chart for stock data."""
        # Get close prices
        close_prices = data['4. close']
        
        # Calculate colors based on performance
        if len(close_prices) > 0:
            start_price = close_prices.iloc[0]
            end_price = close_prices.iloc[-1]
            color = 'green' if end_price >= start_price else 'red'
        else:
            color = 'white'
        
        # Plot the line with gradient color
        ax.plot(data.index, close_prices, linewidth=2, color=color)
        
        # Add fill under the curve
        alpha = 0.2  # Transparency
        ax.fill_between(data.index, close_prices, alpha=alpha, color=color)
        
        # Highlight current price
        if quote:
            current_price = quote['price']
            latest_date = data.index[-1]
            ax.scatter([latest_date], [current_price], s=50, color=color, edgecolors='white', zorder=5)
    
    def _plot_candlestick_chart(self, ax, data, symbol, quote):
        """Plot candlestick chart for stock data."""
        # Prepare the data
        width = 0.6  # Width of candlesticks
        
        # Split into up and down candles
        up = data[data['4. close'] >= data['1. open']]
        down = data[data['4. close'] < data['1. open']]
        
        # Up candles (green)
        if not up.empty:
            # Bodies
            ax.bar(up.index, up['4. close'] - up['1. open'], width=width, 
                   bottom=up['1. open'], color='green', alpha=0.8)
            # Wicks
            ax.bar(up.index, up['2. high'] - up['4. close'], width=0.1, 
                   bottom=up['4. close'], color='green', alpha=0.8)
            ax.bar(up.index, up['1. open'] - up['3. low'], width=0.1, 
                   bottom=up['3. low'], color='green', alpha=0.8)
        
        # Down candles (red)
        if not down.empty:
            # Bodies
            ax.bar(down.index, down['1. open'] - down['4. close'], width=width, 
                   bottom=down['4. close'], color='red', alpha=0.8)
            # Wicks
            ax.bar(down.index, down['2. high'] - down['1. open'], width=0.1, 
                   bottom=down['1. open'], color='red', alpha=0.8)
            ax.bar(down.index, down['4. close'] - down['3. low'], width=0.1, 
                   bottom=down['3. low'], color='red', alpha=0.8)
        
        # Highlight latest price
        if quote and not data.empty:
            current_price = quote['price']
            latest_date = data.index[-1]
            ax.scatter([latest_date], [current_price], s=50, color='yellow', edgecolors='white', zorder=5)
    
    def _format_chart(self, ax, data, symbol, quote, is_last_subplot):
        """Format the chart with labels and styling."""
        # Format the title with quote information if available
        if quote:
            price = quote['price']
            change = quote['change']
            change_pct = quote['change_percent']
            arrow = "▲" if float(change) >= 0 else "▼"
            color = "green" if float(change) >= 0 else "red"
            
            title = f"{symbol} - ${price:.2f} {arrow} {abs(float(change)):.2f} ({change_pct}%)"
            ax.set_title(title, color=color, fontweight='bold', fontsize=14)
        else:
            ax.set_title(symbol, fontsize=14)
        
        # Format x-axis to show dates nicely
        # Choose the right date format based on time range
        time_range = self.config.get("time_range", "1d")
        
        if time_range in ["1d", "3d"]:
            # For short time ranges, show hour:minute
            date_format = '%H:%M'
            ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        elif time_range in ["1w", "1m"]:
            # For medium time ranges, show month/day
            date_format = '%m/%d'
            ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        else:
            # For long time ranges, show month/year
            date_format = '%m/%y'
            ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        
        # Only show x-tick labels for the bottom subplot
        if not is_last_subplot:
            plt.setp(ax.get_xticklabels(), visible=False)
        else:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Format y-axis with dollar signs
        ax.yaxis.set_major_formatter(FormatStrFormatter('$%.2f'))
        
        # Add grid if enabled
        if self.config.get("show_grid", True):
            ax.grid(True, alpha=0.3, linestyle='--')
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add volume bars at the bottom (if available)
        if '5. volume' in data.columns and len(data) > 0:
            # Create a twin axis for volume
            volume_ax = ax.twinx()
            volume_ax.set_ylim(0, data['5. volume'].max() * 3)
            volume_ax.bar(data.index, data['5. volume'], width=0.6, alpha=0.3, color='blue')
            volume_ax.set_ylabel('Volume', color='blue', alpha=0.5)
            volume_ax.tick_params(axis='y', colors='blue', alpha=0.5)
            volume_ax.spines['top'].set_visible(False)
            volume_ax.spines['right'].set_visible(False)
            volume_ax.set_zorder(0)
            ax.set_zorder(1)
            ax.patch.set_visible(False)
    
    def set_wallpaper(self, image_path=None):
        """
        Set the desktop wallpaper.
        
        Args:
            image_path (str, optional): Path to the image file. If not provided,
                uses the last created wallpaper.
                
        Returns:
            bool: True if successful, False otherwise
        """
        if image_path is None:
            image_path = self.wallpaper_path
            
        if not image_path or not os.path.exists(image_path):
            logger.error(f"Wallpaper image not found: {image_path}")
            return False
        
        try:
            # Windows
            if os.name == 'nt':
                ctypes.windll.user32.SystemParametersInfoW(20, 0, str(Path(image_path)), 3)
                return True
            
            # macOS
            elif sys.platform == 'darwin':
                script = f'''
                tell application "Finder"
                set desktop picture to POSIX file "{image_path}"
                end tell
                '''
                os.system(f"osascript -e '{script}'")
                return True
            
            # Linux (assuming GNOME)
            elif sys.platform.startswith('linux'):
                os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{image_path}")
                return True
            
            else:
                logger.error(f"Unsupported platform: {sys.platform}")
                return False
        
        except Exception as e:
            logger.error(f"Error setting wallpaper: {e}")
            return False 