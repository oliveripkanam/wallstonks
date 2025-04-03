#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Rebuild for WallStonks
Fixes the SettingsDialog initialization in tray.py and main.py
"""

import os
import shutil

def fix_tray():
    """Fix the SettingsDialog initialization in tray.py."""
    tray_path = os.path.join("app", "ui", "tray.py")
    
    if not os.path.exists(tray_path):
        print(f"Warning: {tray_path} not found, cannot fix tray.py")
        return False
    
    print(f"Fixing tray.py...")
    
    # Read the file
    with open(tray_path, "r") as f:
        content = f.read()
    
    # Fix the specific line where SettingsDialog is called
    # Change from: dialog = SettingsDialog(self.config, None)
    # To: dialog = SettingsDialog(None, self.config)
    content = content.replace(
        "dialog = SettingsDialog(self.config, None)", 
        "dialog = SettingsDialog(None, self.config)"
    )
    
    # Write back the fixed content
    with open(tray_path, "w") as f:
        f.write(content)
    
    print(f"Fixed tray.py")
    
    # Also copy to dist if it exists
    dist_file = os.path.join("dist", "app", "ui", "tray.py")
    if os.path.exists(os.path.dirname(dist_file)):
        try:
            shutil.copy2(tray_path, dist_file)
            print(f"Copied fixed tray.py to {dist_file}")
        except Exception as e:
            print(f"Warning: Failed to copy tray.py to dist: {e}")
    
    return True

def fix_main():
    """Fix the SettingsDialog initialization in main.py."""
    main_path = os.path.join("app", "main.py")
    
    if not os.path.exists(main_path):
        print(f"Warning: {main_path} not found, cannot fix main.py")
        return False
    
    print(f"Fixing main.py...")
    
    # Read the file
    with open(main_path, "r") as f:
        content = f.read()
    
    # Fix the specific line where SettingsDialog is called
    # Change from: dialog = SettingsDialog(self.config)
    # To: dialog = SettingsDialog(None, self.config)
    content = content.replace(
        "dialog = SettingsDialog(self.config)", 
        "dialog = SettingsDialog(None, self.config)"
    )
    
    # Write back the fixed content
    with open(main_path, "w") as f:
        f.write(content)
    
    print(f"Fixed main.py")
    
    # Also copy to dist if it exists
    dist_file = os.path.join("dist", "app", "main.py")
    if os.path.exists(os.path.dirname(dist_file)):
        try:
            shutil.copy2(main_path, dist_file)
            print(f"Copied fixed main.py to {dist_file}")
        except Exception as e:
            print(f"Warning: Failed to copy main.py to dist: {e}")
    
    return True

def main():
    """Main function."""
    print("Quick Rebuild for WallStonks")
    print("==========================")
    
    # Fix tray.py
    fix_tray()
    
    # Fix main.py
    fix_main()
    
    print("\nFixes complete!")
    print("You can now run the application from dist/WallStonks.exe")

if __name__ == "__main__":
    main() 