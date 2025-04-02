# WallStonks

A desktop application that displays real-time stock charts as your wallpaper.

## Features

- Track up to 5 stocks simultaneously
- Choose between line charts and candlestick charts
- Support for different time ranges (1 day to all time)
- Auto-update during market hours
- Dark and light themes
- System tray integration for easy access
- Configure charts to your preference

## Installation

### Windows

#### Option 1: Install from Pre-built Installer

1. Download the latest WallStonks_Setup.exe from the [Releases](https://github.com/yourusername/wallstonks/releases) page
2. Run the installer and follow the instructions
3. The application will start automatically after installation

#### Option 2: Build from Source

You can build the application from source using one of the following methods:
```
.\build_installer.bat
```

**Method 2: Using Python**
```
python -m PyInstaller WallStonks.spec
```

**Method 3: Using the packaging script**
```
python package_app.py --all
```

### Linux

#### Option 1: Install from .deb Package

For Ubuntu/Debian-based systems:
```
sudo dpkg -i wallstonks_1.0.0_amd64.deb
```

#### Option 2: Build from Source

1. Install dependencies:
```
pip3 install -r requirements.txt
```

2. Run the build script:
```
chmod +x build_installer.sh
./build_installer.sh
```

Or use the packaging script:
```
python3 package_app.py --all
```

### macOS

#### Option 1: Install from DMG

1. Download the latest WallStonks.dmg from the [Releases](https://github.com/yourusername/wallstonks/releases) page
2. Open the DMG file and drag WallStonks to your Applications folder

#### Option 2: Build from Source

```
python3 -m PyInstaller WallStonks.spec
```

Or use the packaging script:
```
python3 package_app.py --all
```

## Getting an API Key

WallStonks uses the Alpha Vantage API to fetch stock data. You will need to obtain a free API key:

1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Register for a free API key
3. Enter the API key in the WallStonks settings dialog

## Usage

1. Launch WallStonks from the Start Menu (Windows), Applications folder (macOS), or Application Menu (Linux)
2. The application will appear in your system tray
3. Right-click the tray icon to access the menu:
   - **Settings**: Configure stocks, chart types, update intervals, and more
   - **Refresh Now**: Manually update the wallpaper
   - **About**: View application information
   - **Exit**: Close the application

### First-Time Setup

On first launch, you'll need to:
1. Enter your Alpha Vantage API key
2. Add stocks to track (up to 5)
3. Configure your preferred chart settings
4. Save the settings

The application will then update your wallpaper with stock charts based on your settings.

## Auto-starting with Windows

You can configure WallStonks to start automatically when Windows starts:

1. Run the auto-start configuration tool:
```
python autostart.py
```

2. Choose whether to enable or disable auto-start

Or use command line arguments:
```
python autostart.py --enable   # Enable auto-start
python autostart.py --disable  # Disable auto-start
python autostart.py --status   # Check auto-start status
```

## Packaging

For detailed packaging instructions, see the [PACKAGING.md](PACKAGING.md) file.

### Quick Packaging Guide

#### Windows Installer

To create a Windows installer:

```
python package_app.py --installer
```

Or use the batch script:

```
.\build_installer.bat
```

#### Linux .deb Package

To create a Debian/Ubuntu package:

```
python package_app.py --deb
```

Or use the shell script:

```
chmod +x build_installer.sh
./build_installer.sh
```

#### macOS DMG

To create a macOS disk image:

```
python package_app.py --dmg
```

### All-in-one Packaging

To build for all supported platforms (will skip platform-specific steps that can't be run):

```
python package_app.py --all
```

### Custom Packaging Options

The packaging script supports several options:

```
python package_app.py --help
```

## Troubleshooting

### Build Issues

- **Missing Dependencies**: Ensure all required libraries are installed with `pip install -r requirements.txt`
- **PyInstaller Error**: If PyInstaller fails, try installing it directly with `pip install pyinstaller`
- **Inno Setup Not Found**: Ensure Inno Setup is installed and in the PATH (Windows only)

### Runtime Issues

- **API Key Invalid**: Double-check your Alpha Vantage API key in the settings
- **No Data Shown**: Ensure your internet connection is working and API key is valid
- **Application Not Starting**: Check logs in `%APPDATA%\WallStonks` (Windows), `~/.wallstonks` (Linux/macOS)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Stock data provided by [Alpha Vantage](https://www.alphavantage.co/)
- Built with [PySide6](https://doc.qt.io/qtforpython/) and [Matplotlib](https://matplotlib.org/) 