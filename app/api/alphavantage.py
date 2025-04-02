#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlphaVantageClient:
    """
    Client for the Alpha Vantage API.
    
    Alpha Vantage provides financial data including stock prices, forex, and crypto.
    This client provides methods to fetch data from the API.
    
    API documentation: https://www.alphavantage.co/documentation/
    """
    
    def __init__(self, api_key):
        """
        Initialize the Alpha Vantage client.
        
        Args:
            api_key (str): Alpha Vantage API key
        """
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def set_api_key(self, api_key):
        """
        Set or update the API key.
        
        Args:
            api_key (str): Alpha Vantage API key
        """
        self.api_key = api_key
    
    def search_symbol(self, keywords):
        """
        Search for stocks by keywords (symbol or name).
        
        Args:
            keywords (str): Search keywords
            
        Returns:
            dict: Search results or None if error occurred
        """
        try:
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": keywords,
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            
            data = response.json()
            
            # Check for API error messages
            if "Error Message" in data:
                logger.error(f"API error: {data['Error Message']}")
                return None
                
            # Check if we have results
            if "bestMatches" not in data:
                logger.warning("No search results found")
                return None
                
            return data
            
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return None
    
    def get_intraday(self, symbol, interval="5min", outputsize="compact"):
        """
        Get intraday time series data.
        
        Args:
            symbol (str): Stock symbol
            interval (str): Time interval between data points (1min, 5min, 15min, 30min, 60min)
            outputsize (str): 'compact' returns the latest 100 data points, 'full' returns all data points
            
        Returns:
            DataFrame: Pandas DataFrame with the time series data or None if error occurred
        """
        try:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API error messages
            if "Error Message" in data:
                logger.error(f"API error for {symbol}: {data['Error Message']}")
                return None
            
            # Extract time series data
            time_series_key = f"Time Series ({interval})"
            if time_series_key not in data:
                logger.warning(f"No time series data found for {symbol}")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            
            # Convert columns to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
                
            # Sort by date (ascending)
            df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return None
    
    def get_daily(self, symbol, outputsize="compact"):
        """
        Get daily time series data.
        
        Args:
            symbol (str): Stock symbol
            outputsize (str): 'compact' returns the latest 100 data points, 'full' returns up to 20 years of data
            
        Returns:
            DataFrame: Pandas DataFrame with the time series data or None if error occurred
        """
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": outputsize,
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API error messages
            if "Error Message" in data:
                logger.error(f"API error for {symbol}: {data['Error Message']}")
                return None
            
            # Extract time series data
            if "Time Series (Daily)" not in data:
                logger.warning(f"No daily data found for {symbol}")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            
            # Convert columns to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
                
            # Sort by date (ascending)
            df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching daily data for {symbol}: {e}")
            return None
    
    def get_weekly(self, symbol):
        """
        Get weekly time series data.
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            DataFrame: Pandas DataFrame with the time series data or None if error occurred
        """
        try:
            params = {
                "function": "TIME_SERIES_WEEKLY",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API error messages
            if "Error Message" in data:
                logger.error(f"API error for {symbol}: {data['Error Message']}")
                return None
            
            # Extract time series data
            if "Weekly Time Series" not in data:
                logger.warning(f"No weekly data found for {symbol}")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data["Weekly Time Series"], orient="index")
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            
            # Convert columns to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
                
            # Sort by date (ascending)
            df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching weekly data for {symbol}: {e}")
            return None
    
    def get_monthly(self, symbol):
        """
        Get monthly time series data.
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            DataFrame: Pandas DataFrame with the time series data or None if error occurred
        """
        try:
            params = {
                "function": "TIME_SERIES_MONTHLY",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API error messages
            if "Error Message" in data:
                logger.error(f"API error for {symbol}: {data['Error Message']}")
                return None
            
            # Extract time series data
            if "Monthly Time Series" not in data:
                logger.warning(f"No monthly data found for {symbol}")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data["Monthly Time Series"], orient="index")
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index)
            
            # Convert columns to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
                
            # Sort by date (ascending)
            df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching monthly data for {symbol}: {e}")
            return None
    
    def get_global_quote(self, symbol):
        """
        Get current quote for a symbol.
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Quote data or None if error occurred
        """
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API error messages
            if "Error Message" in data:
                logger.error(f"API error for {symbol}: {data['Error Message']}")
                return None
                
            # Check if we have data
            if "Global Quote" not in data or not data["Global Quote"]:
                logger.warning(f"No quote data found for {symbol}")
                return None
                
            return data
            
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None 