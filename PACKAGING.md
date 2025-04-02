# WallStonks Packaging Guide

This document provides detailed instructions for packaging the WallStonks application for distribution on various platforms.

## Prerequisites

### Common Requirements

- Python 3.8 or higher
- PyInstaller 6.0.0 or higher
- All dependencies listed in `requirements.txt`

### Platform-Specific Requirements

#### Windows
- Inno Setup 6.x (for creating installer)
- Windows SDK (recommended for proper icon handling)

#### Linux
- FPM (Effing Package Management) for creating .deb packages
- Ruby and Ruby development packages

#### macOS
- macOS Developer Tools

## Building the Application

### Using the Packaging Script

The easiest way to build the application is using the `package_app.py` script, which handles all platform-specific details:

```bash
# For all packaging steps
python package_app.py --all

# For cleaning and building only
python package_app.py --clean

# For creating the installer only
python package_app.py --installer

# For creating a macOS DMG file
python package_app.py --dmg

# For creating a Linux .deb package
python package_app.py --deb
```

### Manual Building

#### 1. Using PyInstaller Directly

```bash
# Windows
python -m PyInstaller WallStonks.spec

# macOS/Linux
python3 -m PyInstaller WallStonks.spec
```

#### 2. Using Platform-Specific Scripts

**Windows**:
```
.\build_installer.bat
```

**Linux**:
```
chmod +x build_installer.sh
./build_installer.sh
```

## Packaging Details

### PyInstaller Spec File

The `WallStonks.spec` file contains all configurations for building the application with PyInstaller. Key configurations include:

- Hidden imports for dependencies
- Inclusion of necessary data files
- Icon settings
- Single-executable vs. directory options
- macOS bundle settings

### Windows Installer (Inno Setup)

The `installer_script.iss` file defines the Windows installer configuration, including:

- Application metadata (name, version, publisher)
- Installation directory settings
- Start menu and desktop shortcuts
- Auto-start settings
- Registry entries
- Uninstallation behavior

### Linux Packaging

The Linux packaging process creates a .deb package using FPM with:

- Correct directory structure following Filesystem Hierarchy Standard
- Desktop file integration
- Icon integration
- Dependencies specification
- Application metadata

### macOS DMG

The macOS packaging creates a DMG file that:

- Contains the macOS application bundle (.app)
- Has proper icon and metadata
- Supports drag-and-drop installation

## Auto-Start Configuration

### Windows Auto-Start

The `autostart.py` script manages auto-start configuration for Windows:

```
# Enable auto-start
python autostart.py --enable

# Disable auto-start
python autostart.py --disable

# Check auto-start status
python autostart.py --status
```

This script creates/removes shortcuts in the user's startup folder.

### Linux Auto-Start

For Linux, auto-start is configured through desktop entries:

```
mkdir -p ~/.config/autostart
cp /usr/share/applications/wallstonks.desktop ~/.config/autostart/
```

### macOS Auto-Start

For macOS, auto-start is handled through Login Items:

```
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/WallStonks.app", hidden:false}'
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure all dependencies are installed with:
   ```
   pip install -r requirements.txt
   ```

2. **PyInstaller Not Finding Modules**: Add missing modules to the `hidden_imports` list in the spec file.

3. **Icon Issues**: Ensure icons are in the correct format for each platform (.ico for Windows, .icns for macOS, .png for Linux).

4. **Permissions Issues**: When packaging on Linux/macOS, ensure scripts have execute permissions:
   ```
   chmod +x build_installer.sh
   ```

### Platform-Specific Issues

#### Windows
- Ensure Inno Setup is installed and available in PATH
- Run cmd/PowerShell as administrator for certain operations

#### Linux
- Ensure FPM is installed correctly
- For .deb packages, ensure proper dependencies are specified

#### macOS
- Ensure developer tools are installed
- For code signing, a valid Apple Developer certificate is required

## Distribution Channels

After packaging, consider these distribution channels:

1. **GitHub Releases**: Upload installers/packages to GitHub releases
2. **Website Downloads**: Host installers on your website
3. **Package Managers**:
   - Windows: Microsoft Store
   - Linux: PPA for Ubuntu, AUR for Arch
   - macOS: Homebrew Cask

## Version Management

When updating the application:

1. Update version in all relevant files:
   - `package_app.py`
   - `installer_script.iss`
   - `app/main.py`
   - `README.md`

2. Update changelog in `CHANGELOG.md`

3. Tag the repository with the new version:
   ```
   git tag v1.0.0
   git push origin v1.0.0
   ```

## Continuous Integration

For automated builds, consider setting up GitHub Actions:

1. Create `.github/workflows/build.yml` with build configurations
2. Configure automated releases on tags
3. Set up matrix builds for multiple platforms 