#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple WallStonks Builder

Creates a one-file executable.
"""

import os
import sys
import subprocess

def main():
    """Build the application."""
    print("Building WallStonks...")
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=WallStonks",
        "--onefile",
        "--windowed",
        "--clean",
        "app/main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild completed successfully!")
        print("Executable location: dist/WallStonks.exe")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
