#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Build script for WallStonks application using PyInstaller's Python API directly.
"""

import os
import sys
import PyInstaller.__main__
from pathlib import Path

def build_executable():
    """Build the WallStonks executable using PyInstaller's Python API."""
    print("Building WallStonks application...")
    
    # Create resources directory if it doesn't exist
    resources_dir = Path("app/resources")
    resources_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate icon if it doesn't exist
    icon_path = resources_dir / "icon.png"
    if not icon_path.exists():
        print("Generating application icon...")
        try:
            from app.resources.generate_icon import create_icon
            create_icon()
        except Exception as e:
            print(f"Error generating icon: {e}")
            print("Continuing without custom icon...")
    
    # Set PyInstaller arguments
    args = [
        "run.py",
        "--name=WallStonks",
        "--onefile",
        "--windowed",
        "--clean",
    ]
    
    # Add icon if it exists
    if icon_path.exists():
        args.append(f"--icon={icon_path}")
    
    # Add data files
    args.append("--add-data=app/resources;app/resources")
    
    # Add hidden imports
    args.extend([
        "--hidden-import=matplotlib",
        "--hidden-import=matplotlib.backends.backend_qt5agg",
        "--hidden-import=numpy",
        "--hidden-import=alpha_vantage",
        "--hidden-import=alpha_vantage.timeseries",
        "--hidden-import=PySide6",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=sqlite3",
        "--hidden-import=ctypes",
    ])
    
    print("Running PyInstaller with the following arguments:")
    print(" ".join(args))
    
    # Run PyInstaller using its Python API
    try:
        PyInstaller.__main__.run(args)
        
        # Check if build was successful
        dist_path = Path("dist/WallStonks.exe")
        if dist_path.exists():
            print(f"\nBuild successful! Executable created at: {dist_path.absolute()}")
            print("\nYou can now distribute this file to users.")
        else:
            print("\nBuild process completed, but executable not found. Check for errors above.")
    
    except Exception as e:
        print(f"Error building executable: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable() 