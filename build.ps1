# WallStonks PowerShell Build Script

Write-Host "WallStonks PowerShell Build Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://www.python.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if PyInstaller is installed, install if needed
Write-Host "Checking for required packages..." -ForegroundColor Yellow
try {
    python -c "import PyInstaller" 2>$null
    Write-Host "PyInstaller is installed." -ForegroundColor Green
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
}

# Use PyInstaller to build the executable directly
Write-Host "Building executable..." -ForegroundColor Yellow

# Get the Python Scripts directory path
$pythonPath = (python -c "import sys; print(sys.executable)") | Out-String
$pythonPath = $pythonPath.Trim()
$pythonDir = Split-Path -Path $pythonPath -Parent
$scriptsDir = Join-Path -Path $pythonDir -ChildPath "Scripts"
$pyInstallerPath = Join-Path -Path $scriptsDir -ChildPath "pyinstaller.exe"

if (Test-Path $pyInstallerPath) {
    Write-Host "Found PyInstaller at: $pyInstallerPath" -ForegroundColor Green
    
    # Use the direct path to PyInstaller
    Write-Host "Running PyInstaller..." -ForegroundColor Yellow
    & $pyInstallerPath --name=WallStonks --onefile --windowed --clean run.py
} else {
    # Try using the module approach
    Write-Host "Using Python module to run PyInstaller..." -ForegroundColor Yellow
    python -m PyInstaller --name=WallStonks --onefile --windowed --clean run.py
}

# Check if the build was successful
$exePath = ".\dist\WallStonks.exe"
if (Test-Path $exePath) {
    Write-Host "`nBuild successful!" -ForegroundColor Green
    Write-Host "Executable created at: $(Resolve-Path $exePath)" -ForegroundColor Green
    
    $choice = Read-Host "Would you like to run the application now? (Y/N)"
    if ($choice -eq "Y" -or $choice -eq "y") {
        Write-Host "Starting WallStonks..." -ForegroundColor Cyan
        Start-Process $exePath
    }
} else {
    Write-Host "`nBuild process completed, but executable was not found." -ForegroundColor Red
    Write-Host "Check for errors in the output above." -ForegroundColor Red
}

Write-Host "`nPress Enter to exit..." -ForegroundColor Cyan
Read-Host 