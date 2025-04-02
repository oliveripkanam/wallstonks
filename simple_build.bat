@echo off
echo WallStonks Simple Build Script
echo ============================

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Install required packages if needed
echo Checking required packages...
python -m pip install -r requirements.txt

REM Run the simple build script
echo Running build script...
python simple_build.py

REM Check if build was successful and the executable exists
if exist "dist\WallStonks.exe" (
    echo.
    echo Build successful! The executable is in the 'dist' folder.
    echo.
    echo Would you like to run the application now? (Y/N)
    set /p choice="> "
    if /i "%choice%"=="Y" (
        echo Starting WallStonks...
        start dist\WallStonks.exe
    )
) else (
    echo.
    echo Build process completed, but executable was not found.
    echo Check for errors in the output above.
)

pause 