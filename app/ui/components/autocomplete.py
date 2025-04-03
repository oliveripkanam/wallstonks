#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import threading
import time
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QListWidget, QListWidgetItem, QPushButton, QLabel,
    QCompleter, QMessageBox
)

from app.api.alphavantage import AlphaVantageClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockSearchCompleter(QWidget):
    """
    A search box with autocomplete for stock symbols.
    Uses the Alpha Vantage API to search for symbols as the user types.
    """
    
    # Signals
    stock_selected = Signal(str, str)  # symbol, name
    
    def __init__(self, api_key=None):
        """
        Initialize the stock search completer.
        
        Args:
            api_key (str, optional): Alpha Vantage API key
        """
        super().__init__()
        
        # Initialize API client
        self.client = AlphaVantageClient(api_key) if api_key else None
        
        # Store search results
        self.search_results = {}  # Map symbols to names
        
        # Flag to track if a search is in progress
        self.search_in_progress = False
        
        # Create UI components
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search for a stock symbol or company name...")
        self.search_box.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.search_box)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setMaximumHeight(200)
        self.results_list.itemClicked.connect(self._on_item_selected)
        self.results_list.setVisible(False)  # Hide until needed
        layout.addWidget(self.results_list)
        
        # Set up a timer for delayed search (to avoid too many API calls)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
    
    def set_api_key(self, api_key):
        """
        Set or update the API key.
        
        Args:
            api_key (str): The Alpha Vantage API key
        """
        if not api_key:
            self.client = None
            return
            
        if self.client:
            self.client.set_api_key(api_key)
        else:
            self.client = AlphaVantageClient(api_key)
    
    def _on_text_changed(self, text):
        """
        Handle text changes in the search box.
        
        Args:
            text (str): The current text in the search box
        """
        # Reset the search timer to avoid too many API calls
        self.search_timer.stop()
        
        # Clear results if text is empty
        if not text:
            self.results_list.clear()
            self.results_list.setVisible(False)
            return
        
        # Start the search timer (will trigger after delay)
        self.search_timer.start(500)  # 500ms delay
    
    def _perform_search(self):
        """Perform the actual search using the API."""
        query = self.search_box.text().strip()
        
        if not query or len(query) < 1:
            self.results_list.clear()
            self.results_list.setVisible(False)
            return
        
        if not self.client:
            logger.warning("No API client available for search, attempting to initialize...")
        from app.api.client import StockDataClient
        self.api_client = StockDataClient()
            return
        
        # Don't start a new search if one is already in progress
        if self.search_in_progress:
            return
            
        # Flag to indicate search is in progress
        self.search_in_progress = True
        
        # Start search in a separate thread to keep UI responsive
        threading.Thread(target=self._search_thread, args=(query,), daemon=True).start()
    
    def _search_thread(self, query):
        """
        Search thread to keep UI responsive.
        
        Args:
            query (str): The search query
        """
        try:
            # Clear previous results
            self.search_results = {}
            
            # Perform the search
            results = self.client.search_symbol(query)
            
            # Store and process results
            if results and 'bestMatches' in results:
                for match in results['bestMatches']:
                    symbol = match.get('1. symbol', '')
                    name = match.get('2. name', '')
                    if symbol and name:
                        self.search_results[symbol] = name
            
            # Update UI in the main thread
            self._update_results_list()
            
        except Exception as e:
            logger.error(f"Error searching for stocks: {e}")
        finally:
            # Clear the search in progress flag
            self.search_in_progress = False
    
    def _update_results_list(self):
        """Update the results list with search results (called from main thread)."""
        # Clear the current list
        self.results_list.clear()
        
        # Add each result to the list
        for symbol, name in self.search_results.items():
            item = QListWidgetItem(f"{symbol} - {name}")
            item.setData(Qt.UserRole, (symbol, name))
            self.results_list.addItem(item)
        
        # Show the results list if we have results
        has_results = len(self.search_results) > 0
        self.results_list.setVisible(has_results)
        
        if has_results:
            # Resize to fit content
            total_height = min(200, (self.results_list.count() * 30) + 10)
            self.results_list.setFixedHeight(total_height)
    
    def _on_item_selected(self, item):
        """
        Handle item selection from the results list.
        
        Args:
            item (QListWidgetItem): The selected item
        """
        # Get the symbol and name from the item data
        data = item.data(Qt.UserRole)
        if data:
            symbol, name = data
            
            # Clear the search box
            self.search_box.clear()
            
            # Hide the results list
            self.results_list.clear()
            self.results_list.setVisible(False)
            
            # Emit the selected stock
            self.stock_selected.emit(symbol, name)


class StockListWidget(QWidget):
    """
    A widget that combines a stock search box with a list of selected stocks.
    """
    
    def __init__(self, selected_stocks=None):
        """
        Initialize the stock list widget.
        
        Args:
            selected_stocks (list, optional): List of initially selected stock symbols
        """
        super().__init__()
        
        # Store selected stocks
        self.selected_stocks = [] if selected_stocks is None else list(selected_stocks)
        
        # Initialize UI
        self.setup_ui()
        
        # Update the stock list
        self.update_stock_list()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Search completer
        self.search_widget = StockSearchCompleter()
        self.search_widget.stock_selected.connect(self.add_stock)
        layout.addWidget(self.search_widget)
        
        # Selected stocks label
        layout.addWidget(QLabel("Selected Stocks:"))
        
        # List of selected stocks
        self.stock_list = QListWidget()
        self.stock_list.setMaximumHeight(150)
        layout.addWidget(self.stock_list)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Add remove button
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_stock)
        button_layout.addWidget(self.remove_button)
        
        layout.addLayout(button_layout)
    
    def set_api_key(self, api_key):
        """
        Set or update the API key for the search completer.
        
        Args:
            api_key (str): The Alpha Vantage API key
        """
        self.search_widget.set_api_key(api_key)
    
    def update_stock_list(self):
        """Update the list of selected stocks."""
        # Clear the current list
        self.stock_list.clear()
        
        # Add each selected stock
        for symbol in self.selected_stocks:
            item = QListWidgetItem(symbol)
            self.stock_list.addItem(item)
    
    def add_stock(self, symbol, name):
        """
        Add a stock to the list.
        
        Args:
            symbol (str): The stock symbol
            name (str): The company name
        """
        # Check if we already have this stock
        if symbol in self.selected_stocks:
            # Already in the list
            QMessageBox.information(self, "Duplicate Stock", 
                                   f"{symbol} is already in your list.")
            return
            
        # Check maximum limit (5 stocks)
        if len(self.selected_stocks) >= 5:
            QMessageBox.warning(self, "Maximum Reached", 
                               "You can track up to 5 stocks. Please remove a stock before adding another.")
            return
            
        # Add the stock
        self.selected_stocks.append(symbol)
        
        # Update the list
        self.update_stock_list()
    
    def remove_selected_stock(self):
        """Remove the selected stock from the list."""
        # Get the selected items
        selected_items = self.stock_list.selectedItems()
        
        if not selected_items:
            QMessageBox.information(self, "No Selection", 
                                   "Please select a stock to remove.")
            return
            
        # Remove the selected stocks
        for item in selected_items:
            symbol = item.text()
            if symbol in self.selected_stocks:
                self.selected_stocks.remove(symbol)
        
        # Update the list
        self.update_stock_list()
    
    def get_selected_stocks(self):
        """
        Get the list of selected stock symbols.
        
        Returns:
            list: The selected stock symbols
        """
        return list(self.selected_stocks) 