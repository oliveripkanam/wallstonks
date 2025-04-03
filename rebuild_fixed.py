#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Focused Rebuild for WallStonks

This script:
1. Uses the existing code structure
2. Creates minimal PyInstaller spec file
3. Builds the application with minimal changes
"""

import os
import sys
import shutil
import subprocess

def clean_dist():
    """Clean only the dist directory to avoid conflicts."""
    print("Cleaning dist directory...")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    print("Clean-up complete.")
    return True

def create_spec_file():
    """Create a minimal PyInstaller spec file."""
    spec_path = "WallStonks.spec"
    print(f"Creating spec file at {spec_path}...")
    
    content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['matplotlib'],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
    
    with open(spec_path, "w") as f:
        f.write(content)
    
    print(f"Spec file created at {spec_path}")
    return True

def ensure_init_files():
    """Ensure all necessary __init__.py files exist."""
    print("Ensuring __init__.py files exist in all directories...")
    
    # List of directories to check
    dirs = []
    
    # Find all app directories recursively
    for root, dirs_list, files in os.walk("app"):
        for directory in dirs_list:
            dirs.append(os.path.join(root, directory))
    
    # Add __init__.py to any directories that don't have one
    for dir_path in dirs:
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            print(f"Creating {init_file}")
            with open(init_file, "w") as f:
                f.write("# Auto-generated __init__.py\n")
    
    print("Finished ensuring __init__.py files exist.")
    return True

def build_application():
    """Build the application with PyInstaller."""
    print("Building application with PyInstaller...")
    
    # Run PyInstaller
    try:
        result = subprocess.run(
            ["pyinstaller", "WallStonks.spec", "--clean"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("Application built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building application: {e}")
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)
        return False

def main():
    """Main function."""
    print("WallStonks Focused Rebuild")
    print("==========================")
    
    # Clean dist directory
    clean_dist()
    
    # Create spec file
    create_spec_file()
    
    # Ensure __init__.py files exist
    ensure_init_files()
    
    # Build the application
    success = build_application()
    
    if success:
        print("\nRebuild complete!")
        print("You can run the application from dist/WallStonks.exe")
    else:
        print("\nRebuild failed. Please check the error messages above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 