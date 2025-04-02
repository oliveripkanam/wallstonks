#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WallStonks Icon Generator

This script creates icons for different platforms from a source image.
It requires Pillow (PIL) to be installed.
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install it with: pip install pillow")
    sys.exit(1)

# Icon sizes for different platforms
ICON_SIZES = {
    'windows': [16, 24, 32, 48, 64, 128, 256],  # .ico file
    'macos': [16, 32, 64, 128, 256, 512, 1024],  # .icns file needs these sizes
    'linux': [16, 24, 32, 48, 64, 128, 256, 512]  # Various .png files
}

def create_windows_icon(source_image, output_path):
    """Create a Windows .ico file with multiple sizes."""
    try:
        img = Image.open(source_image)
        sizes = ICON_SIZES['windows']
        resized_images = [img.resize((size, size), Image.LANCZOS) for size in sizes]
        
        # Save as .ico with multiple sizes
        resized_images[0].save(
            output_path, 
            format='ICO', 
            sizes=[(size, size) for size in sizes],
            append_images=resized_images[1:]
        )
        print(f"Windows icon created at: {output_path}")
        return True
    except Exception as e:
        print(f"Error creating Windows icon: {e}")
        return False

def create_macos_iconset(source_image, output_dir):
    """Create macOS .iconset directory with required sizes."""
    try:
        img = Image.open(source_image)
        iconset_dir = output_dir.with_suffix('.iconset')
        os.makedirs(iconset_dir, exist_ok=True)
        
        for size in ICON_SIZES['macos']:
            resized_img = img.resize((size, size), Image.LANCZOS)
            resized_img.save(iconset_dir / f"icon_{size}x{size}.png")
            
            # macOS also needs 2x versions
            if size * 2 <= 1024:  # Don't exceed 1024
                resized_img_2x = img.resize((size * 2, size * 2), Image.LANCZOS)
                resized_img_2x.save(iconset_dir / f"icon_{size}x{size}@2x.png")
        
        print(f"macOS iconset created at: {iconset_dir}")
        
        # Convert to .icns if on macOS
        if sys.platform == 'darwin':
            import subprocess
            icns_path = output_dir.with_suffix('.icns')
            subprocess.run(['iconutil', '-c', 'icns', str(iconset_dir)])
            print(f"macOS .icns file created at: {icns_path}")
        else:
            print("Note: You need to run this on macOS with iconutil to create .icns file")
        
        return True
    except Exception as e:
        print(f"Error creating macOS iconset: {e}")
        return False

def create_linux_icons(source_image, output_dir):
    """Create various sized PNG files for Linux."""
    try:
        img = Image.open(source_image)
        os.makedirs(output_dir, exist_ok=True)
        
        for size in ICON_SIZES['linux']:
            resized_img = img.resize((size, size), Image.LANCZOS)
            output_path = output_dir / f"icon_{size}x{size}.png"
            resized_img.save(output_path)
            
            # Also save the 256x256 version as the main icon
            if size == 256:
                resized_img.save(output_dir / "icon.png")
        
        print(f"Linux icons created in directory: {output_dir}")
        return True
    except Exception as e:
        print(f"Error creating Linux icons: {e}")
        return False

def main():
    """Main function to create icons for all platforms."""
    if len(sys.argv) < 2:
        print("Usage: python create_icon.py [source_image.png]")
        print("The source image should be at least 1024x1024 pixels")
        sys.exit(1)
    
    source_image = Path(sys.argv[1])
    if not source_image.exists():
        print(f"Error: Source image '{source_image}' not found")
        sys.exit(1)
    
    # Create output directory
    assets_dir = Path(__file__).parent
    
    # Create icons for each platform
    windows_icon = assets_dir / "icon.ico"
    create_windows_icon(source_image, windows_icon)
    
    macos_icon_base = assets_dir / "icon"
    create_macos_iconset(source_image, macos_icon_base)
    
    linux_icons_dir = assets_dir
    create_linux_icons(source_image, linux_icons_dir)
    
    print("\nIcon generation completed!")
    print("Make sure to check the output files and directories.")

if __name__ == "__main__":
    main() 