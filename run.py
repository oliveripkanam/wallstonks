#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WallStonks - Real-time Stock Wallpaper Application
Launch script for the application.
"""

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

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
from app.main import main

if __name__ == "__main__":
    main() 