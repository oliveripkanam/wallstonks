#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WallStonks Runner

This script runs the WallStonks application directly without needing to build an executable.
It's a simpler approach that should work on all systems with Python.
"""

import sys
import os

# Ensure the app directory is in the path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

# Run the application
from app.main import main

if __name__ == "__main__":
    print("Starting WallStonks...")
    sys.exit(main()) 