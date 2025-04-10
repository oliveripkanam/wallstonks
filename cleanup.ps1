# WallStonks Cleanup Script
Write-Host "Cleaning up WallStonks project..." -ForegroundColor Green

# Create clean directory
$cleanDir = "WallStonks-Clean"
if (Test-Path $cleanDir) {
    Remove-Item -Recurse -Force $cleanDir
}
New-Item -ItemType Directory -Path $cleanDir | Out-Null

# Create required directories
$dirs = @(
    "$cleanDir\app",
    "$cleanDir\app\ui",
    "$cleanDir\app\api",
    "$cleanDir\app\assets",
    "$cleanDir\app\resources",
    "$cleanDir\app\services"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir | Out-Null
    Write-Host "Created directory: $dir" -ForegroundColor Yellow
}

# Essential files to keep
$filesToKeep = @(
    @{Source="app\main.py"; Dest="$cleanDir\app\main.py"},
    @{Source="app\__init__.py"; Dest="$cleanDir\app\__init__.py"},
    @{Source="app\config.py"; Dest="$cleanDir\app\config.py"},
    @{Source="app\wallpaper.py"; Dest="$cleanDir\app\wallpaper.py"},
    @{Source="app\background.py"; Dest="$cleanDir\app\background.py"},
    @{Source="app\api_client.py"; Dest="$cleanDir\app\api_client.py"},
    @{Source="app\ui\settings.py"; Dest="$cleanDir\app\ui\settings.py"},
    @{Source="app\ui\tray.py"; Dest="$cleanDir\app\ui\tray.py"},
    @{Source="app\ui\__init__.py"; Dest="$cleanDir\app\ui\__init__.py"},
    @{Source="requirements.txt"; Dest="$cleanDir\requirements.txt"},
    @{Source="README.md"; Dest="$cleanDir\README.md"}
)

# Copy essential files
foreach ($file in $filesToKeep) {
    if (Test-Path $file.Source) {
        Copy-Item $file.Source $file.Dest
        Write-Host "Copied: $($file.Source) to $($file.Dest)" -ForegroundColor Cyan
    } else {
        Write-Host "Warning: File $($file.Source) not found!" -ForegroundColor Red
    }
}

# Create a simple run script
$runScript = @"
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WallStonks Runner

This script runs the WallStonks application directly.
"""

import sys
from app.main import main

if __name__ == "__main__":
    print("Starting WallStonks...")
    sys.exit(main())
"@

Set-Content "$cleanDir\run.py" $runScript
Write-Host "Created run script: $cleanDir\run.py" -ForegroundColor Green

# Create a simple build script
$buildScript = @"
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple WallStonks Builder

Creates a one-file executable.
"""

import os
import sys
import subprocess

def main():
    """Build the application."""
    print("Building WallStonks...")
    
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
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
"@

Set-Content "$cleanDir\build.py" $buildScript
Write-Host "Created build script: $cleanDir\build.py" -ForegroundColor Green

Write-Host "`nCleanup complete! The cleaned project is in the '$cleanDir' directory." -ForegroundColor Green
Write-Host "You can run the application with: python $cleanDir\run.py" -ForegroundColor Green
Write-Host "You can build an executable with: python $cleanDir\build.py" -ForegroundColor Green 