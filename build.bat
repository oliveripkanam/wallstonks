@echo off
echo Starting WallStonks build...

rem Clean dist directory
echo Cleaning dist directory...
if exist dist rmdir /s /q dist

rem Create the PyInstaller command
echo Running PyInstaller...
python -m PyInstaller --name=WallStonks --windowed --clean app/main.py

echo Build complete. Check for errors above.
echo You can run the application from dist\WallStonks\WallStonks.exe 