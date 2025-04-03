#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final Build Fix for WallStonks

This script creates a production-ready executable with fixes for:
1. Missing system tray icon
2. API client initialization issues
"""

import os
import sys
import subprocess
import shutil

def clean_build_dirs():
    """Clean build directories."""
    dirs_to_clean = ['build', 'dist']
    for d in dirs_to_clean:
        if os.path.exists(d):
            print(f"Removing {d} directory...")
            shutil.rmtree(d)

def create_final_spec():
    """Create a production spec file with fixes for known issues."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Check if icon file exists
icon_file = None
for icon_path in ['app/assets/icon.ico', 'app/assets/icon.icns', 'app/assets/icon.jpeg', 'app/assets/icon.jpg', 'app/assets/icon.png']:
    if os.path.exists(icon_path):
        icon_file = icon_path
        break

# Data files
datas = []
if os.path.exists('app/assets'):
    datas.append(('app/assets', 'app/assets'))
for file in ['README.md', 'HOW_TO_RUN.txt', 'autostart.py']:
    if os.path.exists(file):
        datas.append((file, '.'))

# Hidden imports for pandas and other dependencies
hidden_imports = [
    'numpy', 
    'pandas',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.parsing',
    'pandas._libs.tslibs.period',
    'pandas._libs.tslibs.strptime',
    'pandas._libs.tslibs.offsets',
    'pandas.io.formats.style',
    'pandas.core.indexes.base',
    'pandas.core',
    'matplotlib',
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_qtagg',
    'mplfinance',
    'PIL',
    'PIL._tkinter_finder',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
    'app.api.client',
    'app.ui.components.autocomplete',
]

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WallStonks',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Disabled for production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)
"""
    
    with open('WallStonks.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created production-ready spec file")

def create_icon_placeholder():
    """Create a simple icon file if none exists."""
    if not any(os.path.exists(f"app/assets/icon.{ext}") for ext in ["ico", "png", "jpeg", "jpg"]):
        print("Creating placeholder icon in app/assets...")
        os.makedirs("app/assets", exist_ok=True)
        
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple 256x256 icon
            img = Image.new('RGB', (256, 256), color=(0, 120, 212))
            draw = ImageDraw.Draw(img)
            
            # Draw a simple chart-like line
            points = [(50, 200), (100, 100), (150, 180), (200, 80)]
            draw.line(points, fill=(255, 255, 255), width=10)
            
            # Save as PNG
            img.save("app/assets/icon.png")
            print("Created placeholder icon at app/assets/icon.png")
        except ImportError:
            print("PIL not available, creating an empty icon file")
            with open("app/assets/icon.png", "wb") as f:
                # Write minimal PNG header
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\x00\x00\x00\x90\x91h6\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x15IDAT(\x91c\xfc\xff\xff?\x03\x03\x03\x03\x03\x03\x03\x83\x92\xc4\x00\x00\x12\x05\x01\xe7\xdf\xd7\x8f\xa4\x00\x00\x00\x00IEND\xaeB`\x82')

def patch_autocomplete_issue():
    """Try to patch the autocomplete component issue."""
    autocomplete_file = "app/ui/components/autocomplete.py"
    if os.path.exists(autocomplete_file):
        print(f"Checking {autocomplete_file} for API client issues...")
        
        with open(autocomplete_file, "r") as f:
            content = f.read()
        
        # Check if the issue is in how the API client is accessed
        if "No API client available for search" in content:
            print("Found the warning message, patching the issue...")
            
            # Common patterns that might cause the issue
            patterns = [
                ('self.api_client = None', 'self.api_client = api_client'),
                ('if self.api_client is None:', 'if self.api_client is None and api_client is not None:'),
                ('logger.warning("No API client available for search")', 
                 'logger.warning("No API client available for search, attempting to initialize...")\n        from app.api.client import StockDataClient\n        self.api_client = StockDataClient()')
            ]
            
            for old, new in patterns:
                content = content.replace(old, new)
            
            with open(autocomplete_file, "w") as f:
                f.write(content)
            
            print(f"Patched {autocomplete_file}")
        else:
            print("Warning message not found in source, skipping patch.")

def fix_icon_issue():
    """Fix system tray icon loading issue."""
    main_file = "app/main.py"
    if os.path.exists(main_file):
        print(f"Checking {main_file} for system tray icon issues...")
        
        with open(main_file, "r") as f:
            content = f.read()
        
        # Look for system tray icon initialization
        if "QSystemTrayIcon" in content and "setIcon" in content:
            print("Found system tray code, adding icon fallback...")
            
            # Add fallback code for icon loading
            fallback_code = """
        # Icon fallback for system tray
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.png')
        if not os.path.exists(icon_path):
            for ext in ['.ico', '.jpeg', '.jpg']:
                alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', f'icon{ext}')
                if os.path.exists(alt_path):
                    icon_path = alt_path
                    break
        
        # Create a QIcon regardless of file existence
        from PySide6.QtGui import QIcon
        if os.path.exists(icon_path):
            tray_icon = QIcon(icon_path)
        else:
            # Create a simple programmatic icon
            from PySide6.QtGui import QPixmap, QPainter, QColor
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor(0, 120, 212))
            tray_icon = QIcon(pixmap)
        
        self.tray_icon.setIcon(tray_icon)
"""
            
            # Find the appropriate place to insert the fallback code
            if "self.tray_icon = QSystemTrayIcon(self)" in content:
                content = content.replace(
                    "self.tray_icon = QSystemTrayIcon(self)",
                    "self.tray_icon = QSystemTrayIcon(self)\n" + fallback_code
                )
            
            with open(main_file, "w") as f:
                f.write(content)
            
            print(f"Added icon fallback code to {main_file}")
        else:
            print("System tray code not found in main file, skipping patch.")

def main():
    """Main function."""
    print("WallStonks Final Build Fixer")
    print("===========================")
    
    # Clean build directories
    clean_build_dirs()
    
    # Create placeholder icon if needed
    create_icon_placeholder()
    
    # Try to patch the autocomplete issue
    patch_autocomplete_issue()
    
    # Fix system tray icon issue
    fix_icon_issue()
    
    # Create production spec file
    create_final_spec()
    
    # Install required packages
    print("Making sure all dependencies are installed...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pandas", "numpy", "matplotlib", "mplfinance", "pillow", "pyside6", "pywin32", "requests"])
    
    # Build the executable
    print("Building production executable with PyInstaller...")
    subprocess.run([sys.executable, "-m", "PyInstaller", "WallStonks.spec"])
    
    if os.path.exists(os.path.join("dist", "WallStonks.exe")):
        print("\nBuild successful!")
        print("Your production-ready executable is in the dist directory")
        # Copy icon to dist directory for easy access
        if os.path.exists("app/assets/icon.png"):
            shutil.copy("app/assets/icon.png", "dist/")
    else:
        print("\nBuild failed!")
    
if __name__ == "__main__":
    main() 