@echo off
echo === WallStonks Windows Installer Builder ===
echo.

echo Step 1: Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

echo Step 2: Checking PyInstaller installation...
python -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller>=6.0.0
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install PyInstaller.
        exit /b 1
    )
)

echo Step 3: Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies.
    exit /b 1
)

echo Step 4: Cleaning build directories...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo Step 5: Building executable with PyInstaller...
python -m PyInstaller WallStonks.spec
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyInstaller build failed.
    exit /b 1
)

echo Step 6: Checking for Inno Setup...
for %%I in (ISCC.exe) do set INNO_PATH=%%~$PATH:I
if defined INNO_PATH (
    echo Inno Setup found: %INNO_PATH%
) else (
    for %%P in (
        "C:\Program Files\Inno Setup 6\ISCC.exe"
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    ) do (
        if exist "%%~P" set INNO_PATH=%%~P
    )
)

if not defined INNO_PATH (
    echo WARNING: Inno Setup not found. Skipping installer creation.
    echo          Please install Inno Setup from https://jrsoftware.org/isdl.php
    echo          and add it to your PATH or run the ISCC.exe manually:
    echo.
    echo          ISCC.exe installer_script.iss
    echo.
    echo Build completed successfully. Executable is in the dist directory.
    exit /b 0
)

echo Step 7: Creating installer with Inno Setup...
"%INNO_PATH%" installer_script.iss
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Inno Setup failed to create installer.
    exit /b 1
)

echo.
echo === Build completed successfully! ===
echo.
echo Executable: dist\WallStonks.exe
echo Installer: Output\WallStonks_Setup.exe
echo.

exit /b 0 