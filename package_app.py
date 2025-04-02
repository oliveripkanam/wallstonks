#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WallStonks - Packaging Script
=============================

This script automates the process of packaging the WallStonks application.
It handles the following tasks:
1. Building the application with PyInstaller
2. Creating an installer with Inno Setup (Windows only)
3. Creating a distributable DMG (macOS only)
4. Creating a .deb package (Linux only)

Usage:
    python package_app.py [options]

Options:
    --clean         Clean build directories before packaging
    --installer     Create an installer (Windows/macOS/Linux)
    --dmg           Create a DMG file (macOS only)
    --deb           Create a .deb package (Linux only)
    --all           Perform all packaging steps
"""

import os
import sys
import shutil
import argparse
import platform
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define constants
APP_NAME = "WallStonks"
APP_VERSION = "1.0.0"
SPEC_FILE = "WallStonks.spec"
INNO_SCRIPT = "installer_script.iss"

def clean_build_dir():
    """Clean build directories to ensure a fresh build."""
    logger.info("Cleaning build directories...")
    dirs_to_clean = ['build', 'dist']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            logger.info(f"Removing {dir_name} directory...")
            shutil.rmtree(dir_name)
    
    # Clean PyInstaller cache
    cache_dir = os.path.join(os.path.expanduser("~"), ".pyinstaller")
    if os.path.exists(cache_dir):
        logger.info(f"Removing PyInstaller cache at {cache_dir}...")
        shutil.rmtree(cache_dir)
    
    logger.info("Cleaning completed.")

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PyInstaller
        logger.info(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        logger.warning("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"], check=True)
    
    # Check platform-specific dependencies
    if platform.system() == "Windows":
        # Check for Inno Setup
        inno_found = False
        possible_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                inno_found = True
                break
        
        if not inno_found:
            logger.warning("WARNING: Inno Setup not found. Windows installer cannot be created.")
            logger.warning("         Please install Inno Setup from https://jrsoftware.org/isdl.php")
    
    elif platform.system() == "Linux":
        # Check for FPM
        try:
            subprocess.run(["fpm", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        except FileNotFoundError:
            logger.warning("WARNING: FPM not found. Linux packages cannot be created.")
            logger.warning("         Install FPM with: gem install fpm")

def build_executable():
    """Build the executable using PyInstaller."""
    logger.info("Building executable...")
    
    # Create PyInstaller spec file if it doesn't exist
    if not os.path.exists(SPEC_FILE):
        logger.info("Creating PyInstaller spec file...")
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--name=" + APP_NAME,
            "--onefile",
            "--windowed",
            "--add-data=app/assets:app/assets",
            "--icon=app/assets/icon.ico",
            "run.py"
        ], check=True)
    else:
        # Use existing spec file
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            SPEC_FILE
        ], check=True)
    
    logger.info("Executable build completed.")
    
    # Validate build
    if platform.system() == "Windows":
        expected_path = os.path.join("dist", "WallStonks.exe")
    elif platform.system() == "Darwin":
        expected_path = os.path.join("dist", "WallStonks.app")
    else:
        expected_path = os.path.join("dist", "WallStonks")
    
    if os.path.exists(expected_path):
        logger.info(f"Build successful: {expected_path}")
    else:
        logger.error(f"ERROR: Build failed, executable not found at {expected_path}")
        sys.exit(1)

def create_windows_installer():
    """Create a Windows installer using Inno Setup."""
    if platform.system() != "Windows":
        logger.warning("Windows installer can only be created on Windows.")
        return
    
    logger.info("Creating Windows installer...")
    
    # Check for Inno Setup
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe"
    ]
    
    iscc_path = None
    for path in iscc_paths:
        if os.path.exists(path):
            iscc_path = path
            break
    
    if not iscc_path:
        logger.error("ERROR: Inno Setup not found. Windows installer cannot be created.")
        logger.error("       Please install Inno Setup from https://jrsoftware.org/isdl.php")
        return
    
    # Run Inno Setup Compiler
    subprocess.run([iscc_path, INNO_SCRIPT], check=True)
    
    # Validate installer
    output_file = f"Output\\WallStonks_Setup.exe"
    if os.path.exists(output_file):
        logger.info(f"Windows installer created successfully: {output_file}")
    else:
        logger.error(f"ERROR: Installer creation failed, file not found at {output_file}")

def create_linux_package():
    """Create Linux packages (.deb, .rpm) using FPM."""
    if platform.system() != "Linux":
        logger.warning("Linux packages can only be created on Linux.")
        return
    
    logger.info("Creating Linux packages...")
    
    # Check for FPM
    try:
        subprocess.run(["fpm", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.error("ERROR: FPM not found. Linux packages cannot be created.")
        logger.error("       Install FPM with: gem install fpm")
        return
    
    # Create directory structure
    package_root = "packaging/linux"
    os.makedirs(f"{package_root}/usr/bin", exist_ok=True)
    os.makedirs(f"{package_root}/usr/share/applications", exist_ok=True)
    os.makedirs(f"{package_root}/usr/share/icons/hicolor/256x256/apps", exist_ok=True)
    os.makedirs(f"{package_root}/usr/share/wallstonks", exist_ok=True)
    
    # Copy executable
    shutil.copy("dist/WallStonks", f"{package_root}/usr/bin/wallstonks")
    
    # Create desktop file
    desktop_file = f"{package_root}/usr/share/applications/wallstonks.desktop"
    with open(desktop_file, "w") as f:
        f.write("""[Desktop Entry]
Name=WallStonks
Comment=Real-time stock wallpaper application
Exec=wallstonks
Icon=wallstonks
Terminal=false
Type=Application
Categories=Office;Finance;
StartupNotify=true
""")
    
    # Copy icon
    shutil.copy("app/assets/icon.png", 
                f"{package_root}/usr/share/icons/hicolor/256x256/apps/wallstonks.png")
    
    # Create packages
    subprocess.run([
        "fpm", 
        "-s", "dir", 
        "-t", "deb",
        "-n", "wallstonks",
        "-v", APP_VERSION,
        "--vendor", "WallStonks Team",
        "--description", "Real-time stock wallpaper application",
        "--url", "https://github.com/yourusername/wallstonks",
        "--license", "MIT",
        "-C", package_root,
        "--depends", "python3",
        "--category", "finance"
    ], check=True)
    
    # Clean up
    shutil.rmtree(package_root)
    
    # Validate package
    deb_file = f"wallstonks_{APP_VERSION}_amd64.deb"
    if os.path.exists(deb_file):
        logger.info(f"Linux package created successfully: {deb_file}")
    else:
        logger.error(f"ERROR: Package creation failed, file not found at {deb_file}")

def create_macos_dmg():
    """Create a macOS DMG file."""
    if platform.system() != "Darwin":
        logger.warning("macOS DMG can only be created on macOS.")
        return
    
    logger.info("Creating macOS DMG...")
    
    # Install required tools
    try:
        subprocess.run(["create-dmg", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.warning("Installing create-dmg...")
        subprocess.run(["brew", "install", "create-dmg"], check=True)
    
    # Create DMG
    subprocess.run([
        "create-dmg",
        "--volname", "WallStonks Installer",
        "--volicon", "app/assets/icon.icns",
        "--background", "app/assets/dmg-background.png",
        "--window-pos", "200", "120",
        "--window-size", "800", "400",
        "--icon-size", "100",
        "--icon", "WallStonks.app", "200", "190",
        "--hide-extension", "WallStonks.app",
        "--app-drop-link", "600", "190",
        "dist/WallStonks-Installer.dmg",
        "dist/WallStonks.app"
    ], check=True)
    
    # Validate DMG
    dmg_file = "dist/WallStonks-Installer.dmg"
    if os.path.exists(dmg_file):
        logger.info(f"macOS DMG created successfully: {dmg_file}")
    else:
        logger.error(f"ERROR: DMG creation failed, file not found at {dmg_file}")

def main():
    """Main entry point for the packaging script."""
    parser = argparse.ArgumentParser(description='Package WallStonks application')
    parser.add_argument('--clean', action='store_true', help='Clean build directories')
    parser.add_argument('--build', action='store_true', help='Build executable')
    parser.add_argument('--installer', action='store_true', help='Create Windows installer')
    parser.add_argument('--deb', action='store_true', help='Create Debian package')
    parser.add_argument('--dmg', action='store_true', help='Create macOS DMG')
    parser.add_argument('--all', action='store_true', help='Perform all packaging steps')
    
    args = parser.parse_args()
    
    # If no arguments are provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Check for required dependencies
    check_dependencies()
    
    # Process commands
    if args.clean or args.all:
        clean_build_dir()
    
    if args.build or args.all:
        build_executable()
    
    if args.installer or args.all:
        create_windows_installer()
    
    if args.deb or args.all:
        create_linux_package()
    
    if args.dmg or args.all:
        create_macos_dmg()
    
    logger.info("Packaging completed!")

if __name__ == "__main__":
    main() 