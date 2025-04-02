#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime, timedelta
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockDataClient:
    """
    Client for fetching stock data from Alpha Vantage API.
    """
    
    def __init__(self, api_key=""):
        """Initialize the stock data client."""
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
        # Initialize Alpha Vantage client if API key is provided
        if api_key:
            self.client = TimeSeries(key=api_key, output_format='pandas')
        else:
            self.client = None
            logger.warning("No API key provided. Some features may not work.")
    
    def set_api_key(self, api_key):
        """Set the API key for Alpha Vantage."""
        self.api_key = api_key
        self.client = TimeSeries(key=api_key, output_format='pandas')
    
    def search_symbol(self, keywords):
        """Search for stock symbols based on keywords."""
        if not self.api_key:
            return [], "No API key provided"
        
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "bestMatches" in data:
                results = []
                for match in data["bestMatches"]:
                    results.append({
                        "symbol": match["1. symbol"],
                        "name": match["2. name"],
                        "type": match["3. type"],
                        "region": match["4. region"]
                    })
                return results, None
            else:
                return [], f"Error: {data.get('Note', 'Unknown error')}"
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for symbol: {e}")
            return [], f"Error: {str(e)}"
    
    def get_stock_data(self, symbol, time_range="1d", chart_type="line"):
        """
        Get stock data for a specific symbol and time range.
        
        Args:
            symbol (str): Stock symbol (e.g., AAPL, MSFT)
            time_range (str): Time range (1d, 3d, 1w, 1m, 3m, 6m, 1y, all)
            chart_type (str): Chart type (line or candlestick)
            
        Returns:
            tuple: (data, error) where data is a pandas DataFrame and error is an error message
        """
        if not self.api_key or not self.client:
            return None, "No API key provided"
        
        try:
            # Map time range to Alpha Vantage function and parameters
            if time_range in ["1d", "3d", "1w"]:
                data, meta_data = self.client.get_intraday(
                    symbol=symbol, 
                    interval='5min', 
                    outputsize='full'
                )
                
                # Filter data based on time range
                now = datetime.now()
                if time_range == "1d":
                    start_date = now - timedelta(days=1)
                elif time_range == "3d":
                    start_date = now - timedelta(days=3)
                else:  # 1w
                    start_date = now - timedelta(weeks=1)
                
                data = data[data.index >= start_date]
                
            elif time_range in ["1m", "3m", "6m"]:
                data, meta_data = self.client.get_daily(symbol=symbol, outputsize='full')
                
                # Filter data based on time range
                now = datetime.now()
                if time_range == "1m":
                    start_date = now - timedelta(days=30)
                elif time_range == "3m":
                    start_date = now - timedelta(days=90)
                else:  # 6m
                    start_date = now - timedelta(days=180)
                
                data = data[data.index >= start_date]
                
            elif time_range == "1y":
                data, meta_data = self.client.get_daily(symbol=symbol, outputsize='full')
                start_date = datetime.now() - timedelta(days=365)
                data = data[data.index >= start_date]
                
            else:  # all
                data, meta_data = self.client.get_daily(symbol=symbol, outputsize='full')
            
            return data, None
            
        except Exception as e:
            logger.error(f"Error fetching stock data: {e}")
            return None, f"Error: {str(e)}"
    
    def get_quote(self, symbol):
        """Get current quote for a stock symbol."""
        if not self.api_key:
            return None, "No API key provided"
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                result = {
                    "symbol": quote["01. symbol"],
                    "price": float(quote["05. price"]),
                    "change": float(quote["09. change"]),
                    "change_percent": quote["10. change percent"].rstrip("%"),
                    "volume": int(quote["06. volume"]),
                    "last_updated": quote["07. latest trading day"]
                }
                return result, None
            else:
                return None, f"Error: {data.get('Note', 'Unknown error')}"
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting quote: {e}")
            return None, f"Error: {str(e)}" 