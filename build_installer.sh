#!/bin/bash
# WallStonks Linux installer builder

set -e  # Exit on error

echo "=== WallStonks Linux Package Builder ==="
echo

# Check Python installation
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Found Python $PYTHON_VERSION"

# Check for pip
echo "Step 2: Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 not found. Please install pip for Python 3."
    exit 1
fi

# Check for PyInstaller
echo "Step 3: Checking PyInstaller installation..."
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller>=6.0.0
fi

# Check for FPM (for .deb packaging)
echo "Step 4: Checking FPM installation..."
if ! command -v fpm &> /dev/null; then
    echo "WARNING: FPM not found. Will skip creating .deb package."
    echo "         Install FPM with: gem install fpm"
    SKIP_DEB=1
else
    SKIP_DEB=0
fi

# Install dependencies
echo "Step 5: Installing dependencies..."
pip3 install -r requirements.txt

# Clean build directories
echo "Step 6: Cleaning build directories..."
rm -rf build dist

# Build executable
echo "Step 7: Building executable with PyInstaller..."
python3 -m PyInstaller WallStonks.spec

# Check if build succeeded
if [ ! -f "dist/WallStonks" ]; then
    echo "ERROR: Build failed, executable not found."
    exit 1
fi

echo "Executable built successfully: dist/WallStonks"

# Create .deb package if FPM is available
if [ $SKIP_DEB -eq 0 ]; then
    echo "Step 8: Creating Debian package..."
    
    # Create directory structure
    PACKAGE_ROOT="packaging/linux"
    mkdir -p "${PACKAGE_ROOT}/usr/bin"
    mkdir -p "${PACKAGE_ROOT}/usr/share/applications"
    mkdir -p "${PACKAGE_ROOT}/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "${PACKAGE_ROOT}/usr/share/wallstonks"
    
    # Copy executable
    cp "dist/WallStonks" "${PACKAGE_ROOT}/usr/bin/wallstonks"
    chmod +x "${PACKAGE_ROOT}/usr/bin/wallstonks"
    
    # Create desktop file
    cat > "${PACKAGE_ROOT}/usr/share/applications/wallstonks.desktop" << EOL
[Desktop Entry]
Name=WallStonks
Comment=Real-time stock wallpaper application
Exec=wallstonks
Icon=wallstonks
Terminal=false
Type=Application
Categories=Office;Finance;
StartupNotify=true
EOL
    
    # Copy icon
    if [ -f "app/assets/icon.png" ]; then
        cp "app/assets/icon.png" "${PACKAGE_ROOT}/usr/share/icons/hicolor/256x256/apps/wallstonks.png"
    else
        echo "WARNING: Icon file not found at app/assets/icon.png"
    fi
    
    # Create package
    VERSION="1.0.0"
    fpm -s dir -t deb \
        -n "wallstonks" \
        -v "$VERSION" \
        --vendor "WallStonks Team" \
        --description "Real-time stock wallpaper application" \
        --url "https://github.com/yourusername/wallstonks" \
        --license "MIT" \
        -C "$PACKAGE_ROOT" \
        --depends "python3" \
        --category "finance"
    
    # Clean up
    rm -rf "$PACKAGE_ROOT"
    
    # Check if package was created
    if [ -f "wallstonks_${VERSION}_amd64.deb" ]; then
        echo "Debian package created successfully: wallstonks_${VERSION}_amd64.deb"
    else
        echo "ERROR: Debian package creation failed."
    fi
else
    echo "Skipping Debian package creation (FPM not installed)."
fi

echo
echo "=== Build process completed! ==="
echo
echo "Executable: dist/WallStonks"
if [ $SKIP_DEB -eq 0 ] && [ -f "wallstonks_${VERSION}_amd64.deb" ]; then
    echo "Debian package: wallstonks_${VERSION}_amd64.deb"
fi
echo

exit 0 