#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple build script for WallStonks application.
"""

import os
import sys
import subprocess
from pathlib import Path

def build_with_spec():
    """Build the executable using the spec file directly."""
    print("Building WallStonks with PyInstaller spec file...")
    
    # Make sure the icon exists
    icon_path = Path("app/resources/icon.png")
    if not icon_path.exists():
        print("Generating application icon...")
        try:
            from app.resources.generate_icon import create_icon
            create_icon()
        except Exception as e:
            print(f"Error generating icon: {e}")
    
    # Find PyInstaller executable
    pyinstaller_cmd = "pyinstaller"
    
    # Check if we're running in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment, use the venv's Scripts directory
        scripts_dir = os.path.join(sys.prefix, 'Scripts')
        pyinstaller_path = os.path.join(scripts_dir, 'pyinstaller.exe')
        if os.path.exists(pyinstaller_path):
            pyinstaller_cmd = pyinstaller_path
    
    # Try to find PyInstaller in PATH
    try:
        # First, directly use the spec file
        print("Running PyInstaller with spec file...")
        cmd = [pyinstaller_cmd, "WallStonks.spec"]
        print(f"Command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # Check if the build was successful
        dist_path = Path("dist/WallStonks.exe")
        if dist_path.exists():
            print(f"\nBuild successful! Executable created at: {dist_path.absolute()}")
            print("\nYou can now run this executable directly.")
        else:
            print("\nFallback to direct PyInstaller arguments...")
            # Fallback to direct arguments
            cmd = [
                pyinstaller_cmd,
                "--name=WallStonks",
                "--onefile",
                "--windowed",
                "run.py"
            ]
            print(f"Command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
            if dist_path.exists():
                print(f"\nFallback build successful! Executable created at: {dist_path.absolute()}")
            else:
                print("\nBuild failed. No executable was created.")
                
    except subprocess.CalledProcessError as e:
        print(f"Error running PyInstaller: {e}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Trying to install it...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("PyInstaller installed. Please run this script again.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install PyInstaller: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = build_with_spec()
    if success:
        print("\nBuild completed. Check the 'dist' folder for the executable.")
    else:
        print("\nBuild failed. Please check the errors above.")
        
    input("Press Enter to exit...") 