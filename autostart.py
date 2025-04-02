#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WallStonks - Auto-start configuration script
===========================================

This script configures WallStonks to start automatically when Windows starts.
It can be run manually or by the installer.

Usage:
    python autostart.py [--enable|--disable]
"""

import os
import sys
import ctypes
import platform
import winreg
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Application constants
APP_NAME = "WallStonks"
APP_EXE = "WallStonks.exe"

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def get_startup_path():
    """Get the path to the startup folder."""
    try:
        # Use the Windows Registry to get the startup folder path
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        startup_path = winreg.QueryValueEx(key, "Startup")[0]
        winreg.CloseKey(key)
        
        # Expand environment variables if needed
        startup_path = os.path.expandvars(startup_path)
        return startup_path
    except Exception as e:
        logger.error(f"Error getting startup path: {e}")
        return None

def get_install_path():
    """Get the installation path of the application."""
    try:
        # Try to get installation path from Registry
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           rf"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}_is1")
        install_path = winreg.QueryValueEx(key, "InstallLocation")[0]
        winreg.CloseKey(key)
        return install_path
    except:
        # If registry key not found, try common installation locations
        pass
    
    # Try common installation locations
    common_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), APP_NAME),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), APP_NAME),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Local', APP_NAME),
    ]
    
    # Check if script is in the application directory (for portable installations)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    common_paths.append(script_dir)
    
    for path in common_paths:
        exe_path = os.path.join(path, APP_EXE)
        if os.path.exists(exe_path):
            return path
    
    return None

def enable_autostart():
    """Enable auto-start for the application."""
    # Get paths
    startup_path = get_startup_path()
    install_path = get_install_path()
    
    if not startup_path:
        logger.error("Failed to determine startup folder path")
        return False
    
    if not install_path:
        logger.error(f"Could not find {APP_NAME} installation")
        return False
    
    # Check if executable exists
    exe_path = os.path.join(install_path, APP_EXE)
    if not os.path.exists(exe_path):
        logger.error(f"Executable not found: {exe_path}")
        return False
    
    try:
        # Create shortcut (.lnk) file in startup folder
        shortcut_path = os.path.join(startup_path, f"{APP_NAME}.lnk")
        
        # Use Windows Script Host to create shortcut
        with open(f"{shortcut_path}.vbs", "w") as f:
            f.write(f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{exe_path}"
oLink.WorkingDirectory = "{install_path}"
oLink.Description = "{APP_NAME}"
oLink.Save
''')
        
        # Execute the VBS script
        os.system(f'cscript //nologo "{shortcut_path}.vbs"')
        os.remove(f"{shortcut_path}.vbs")
        
        if os.path.exists(shortcut_path):
            logger.info(f"Auto-start enabled: {shortcut_path}")
            return True
        else:
            logger.error("Failed to create shortcut")
            return False
            
    except Exception as e:
        logger.error(f"Error enabling auto-start: {e}")
        return False

def disable_autostart():
    """Disable auto-start for the application."""
    startup_path = get_startup_path()
    
    if not startup_path:
        logger.error("Failed to determine startup folder path")
        return False
    
    try:
        shortcut_path = os.path.join(startup_path, f"{APP_NAME}.lnk")
        
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            logger.info(f"Auto-start disabled: {shortcut_path} removed")
            return True
        else:
            logger.info("Auto-start is already disabled")
            return True
            
    except Exception as e:
        logger.error(f"Error disabling auto-start: {e}")
        return False

def check_autostart():
    """Check if auto-start is enabled."""
    startup_path = get_startup_path()
    
    if not startup_path:
        logger.error("Failed to determine startup folder path")
        return False
    
    shortcut_path = os.path.join(startup_path, f"{APP_NAME}.lnk")
    return os.path.exists(shortcut_path)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=f"Configure auto-start for {APP_NAME}")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--enable", action="store_true", help="Enable auto-start")
    group.add_argument("--disable", action="store_true", help="Disable auto-start")
    group.add_argument("--status", action="store_true", help="Check auto-start status")
    
    args = parser.parse_args()
    
    # Ensure we're running on Windows
    if platform.system() != "Windows":
        logger.error("This script is for Windows only")
        return 1
    
    # If no arguments provided, show status and menu
    if not (args.enable or args.disable or args.status):
        if check_autostart():
            print(f"{APP_NAME} is configured to start automatically with Windows.")
            choice = input("Would you like to disable auto-start? (y/n): ")
            if choice.lower() == 'y':
                disable_autostart()
        else:
            print(f"{APP_NAME} is not configured to start automatically with Windows.")
            choice = input("Would you like to enable auto-start? (y/n): ")
            if choice.lower() == 'y':
                enable_autostart()
    else:
        # Process command-line arguments
        if args.status:
            if check_autostart():
                print(f"{APP_NAME} auto-start is enabled")
            else:
                print(f"{APP_NAME} auto-start is disabled")
            
        elif args.enable:
            if enable_autostart():
                print(f"{APP_NAME} will now start automatically with Windows")
            else:
                print("Failed to enable auto-start")
                return 1
                
        elif args.disable:
            if disable_autostart():
                print(f"{APP_NAME} will no longer start automatically with Windows")
            else:
                print("Failed to disable auto-start")
                return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 