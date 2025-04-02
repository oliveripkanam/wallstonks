@echo off
echo WallStonks Build Script
echo ======================

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import PyInstaller" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
)

echo Building application...
python build_exe.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo Build completed successfully!
    echo The executable is located in the 'dist' folder.
    echo.
    echo Would you like to run the application now? (Y/N)
    set /p choice="> "
    if /i "%choice%"=="Y" (
        echo Starting WallStonks...
        start dist\WallStonks.exe
    )
) else (
    echo.
    echo Build failed. Check the error messages above.
)

pause 