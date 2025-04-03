#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix PyInstaller build for WallStonks

This script creates a PyInstaller spec file with all necessary dependencies
and builds the executable with the console enabled for debugging.
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

def create_simple_spec():
    """Create a simple spec file with pandas dependencies."""
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

# Hidden imports for pandas
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
    'mplfinance',
    'PIL',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
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
    console=True,  # Enable console for debugging
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
    
    print("Created simplified spec file")

def main():
    """Main function."""
    print("WallStonks Build Fixer")
    print("=====================")
    
    # Clean build directories
    clean_build_dirs()
    
    # Create simplified spec file
    create_simple_spec()
    
    # Install required packages
    print("Making sure pandas is installed...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pandas", "numpy", "matplotlib", "mplfinance", "pillow", "pyside6", "pywin32", "requests"])
    
    # Build the executable
    print("Building executable with PyInstaller...")
    subprocess.run([sys.executable, "-m", "PyInstaller", "WallStonks.spec"])
    
    if os.path.exists(os.path.join("dist", "WallStonks.exe")):
        print("\nBuild successful!")
        print("Your executable is in the dist directory")
    else:
        print("\nBuild failed!")
    
if __name__ == "__main__":
    main() 