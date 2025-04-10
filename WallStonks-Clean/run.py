#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WallStonks Runner

This script runs the WallStonks application directly.
"""

import sys
from app.main import main

if __name__ == "__main__":
    print("Starting WallStonks...")
    sys.exit(main())
