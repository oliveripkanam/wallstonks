#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple WallStonks Builder

Creates a one-file executable that's easier to locate and use.
"""

import os
import sys
import subprocess
import shutil

def clean():
    """Clean build artifacts."""
    print("Cleaning build directories...")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    for file in os.listdir("."):
        if file.endswith(".spec"):
            os.remove(file)
    print("Cleanup complete.")

def build():
    """Build the application."""
    print("Building WallStonks...")
    
    # Build command: create a one-file executable for simplicity
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
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        return False

def main():
    """Main function."""
    print("=== Simple WallStonks Builder ===")
    
    # Clean previous builds
    clean()
    
    # Build the application
    success = build()
    
    if success:
        # Verify the executable exists
        exe_path = os.path.join("dist", "WallStonks.exe")
        if os.path.exists(exe_path):
            print(f"\nExecutable created successfully at: {os.path.abspath(exe_path)}")
            # Could add auto-run option here
        else:
            print("\nError: Executable not found after build!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 