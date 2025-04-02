#!/bin/bash

echo "WallStonks Installation Script"
echo "============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create desktop entry
echo "Creating desktop entry..."
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/wallstonks.desktop << EOF
[Desktop Entry]
Name=WallStonks
Comment=Real-time stock wallpaper application
Exec=$(pwd)/venv/bin/python $(pwd)/run.py
Icon=$(pwd)/app/resources/icon.png
Terminal=false
Type=Application
Categories=Utility;Finance;
EOF

echo "Installation complete!"
echo "You can now run WallStonks from your applications menu or by running:"
echo "source $(pwd)/venv/bin/activate && python $(pwd)/run.py"

# Ask if user wants to run the application now
read -p "Would you like to run WallStonks now? (y/n): " choice
if [[ $choice == "y" || $choice == "Y" ]]; then
    echo "Starting WallStonks..."
    python run.py &
fi 