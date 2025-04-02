#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Build script for WallStonks application.
Creates a standalone executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build a standalone executable using PyInstaller."""
    print("Building WallStonks executable...")
    
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
    
    # PyInstaller command
    pyinstaller_args = [
        "pyinstaller",
        "--name=WallStonks",
        "--onefile",
        "--windowed",
        "--clean",
        f"--icon={icon_path}" if icon_path.exists() else "",
        "--add-data=app/resources;app/resources",
        "--hidden-import=matplotlib",
        "--hidden-import=numpy",
        "--hidden-import=alpha_vantage",
        "--hidden-import=PySide6",
        "run.py"
    ]
    
    # Remove empty arguments
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    print("Running PyInstaller with the following arguments:")
    print(" ".join(pyinstaller_args))
    
    # Run PyInstaller
    try:
        subprocess.run(pyinstaller_args, check=True)
        
        # Check if build was successful
        dist_path = Path("dist/WallStonks.exe")
        if dist_path.exists():
            print(f"\nBuild successful! Executable created at: {dist_path.absolute()}")
            print("\nYou can now distribute this file to users.")
        else:
            print("\nBuild process completed, but executable not found. Check for errors above.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        sys.exit(1)

def create_installer():
    """Create a Windows installer using Inno Setup."""
    print("Creating Windows installer...")
    
    # Check if Inno Setup is installed
    inno_setup_path = "C:/Program Files (x86)/Inno Setup 6/ISCC.exe"
    if not os.path.exists(inno_setup_path):
        print("Inno Setup not found. Skipping installer creation.")
        print("To create an installer, please install Inno Setup from: https://jrsoftware.org/isinfo.php")
        return
    
    # Create Inno Setup script
    iss_script = """
[Setup]
AppName=WallStonks
AppVersion=0.1.0
DefaultDirName={pf}\\WallStonks
DefaultGroupName=WallStonks
UninstallDisplayIcon={app}\\WallStonks.exe
Compression=lzma2
SolidCompression=yes
OutputDir=installer
OutputBaseFilename=WallStonks_Setup

[Files]
Source="dist\\WallStonks.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\\WallStonks"; Filename: "{app}\\WallStonks.exe"
Name: "{commondesktop}\\WallStonks"; Filename: "{app}\\WallStonks.exe"

[Registry]
Root: HKCU; Subkey: "Software\\Microsoft\\Windows\\CurrentVersion\\Run"; ValueType: string; ValueName: "WallStonks"; ValueData: "{app}\\WallStonks.exe"; Flags: uninsdeletevalue
    """
    
    # Create installer directory
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    
    # Write Inno Setup script
    iss_path = Path("installer/WallStonks.iss")
    with open(iss_path, "w") as f:
        f.write(iss_script)
    
    # Run Inno Setup
    try:
        subprocess.run([inno_setup_path, str(iss_path)], check=True)
        print("\nInstaller created successfully in the 'installer' directory.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating installer: {e}")

if __name__ == "__main__":
    build_executable()
    create_installer() 