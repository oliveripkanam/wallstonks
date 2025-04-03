#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Settings Fix for WallStonks

This script copies the fixed settings.py file to the correct location in the build directory.
"""

import os
import sys
import shutil
import subprocess

def copy_fixed_settings():
    """Copy the fixed settings.py file to the build directory."""
    source_file = os.path.join("app", "ui", "settings.py")
    
    # Make sure the source file exists
    if not os.path.exists(source_file):
        print(f"Error: settings.py not found at {source_file}")
        return False
    
    print(f"Copying fixed settings.py file...")
    
    # Define possible target locations
    target_dirs = [
        os.path.join("dist", "app", "ui"),
        os.path.join("build", "WallStonks", "app", "ui"),
        os.path.join("build", "WallStonks", "localpycs", "app", "ui"),
    ]
    
    success = False
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        
        target_file = os.path.join(target_dir, "settings.py")
        try:
            shutil.copy2(source_file, target_file)
            print(f"Successfully copied settings.py to {target_file}")
            success = True
        except Exception as e:
            print(f"Warning: Failed to copy to {target_file}: {e}")
    
    return success

def run_pyinstaller():
    """Run PyInstaller to rebuild the executable."""
    try:
        print("Running PyInstaller to update the executable...")
        result = subprocess.run(
            ["pyinstaller", "WallStonks.spec", "--noconfirm"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running PyInstaller: {e}")
        return False

def main():
    """Main function."""
    print("WallStonks Settings Fix")
    print("======================")
    
    # Copy the fixed settings.py
    if not copy_fixed_settings():
        print("Failed to copy fixed settings.py file")
        return
    
    # Run PyInstaller to rebuild
    if not run_pyinstaller():
        print("Failed to rebuild the executable")
        return
    
    print("\nSettings fix complete!")
    print("You can now run the executable in the dist directory")
    
if __name__ == "__main__":
    main() 