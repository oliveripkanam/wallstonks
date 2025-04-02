#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate a simple icon for WallStonks application.
"""

import os
from PIL import Image, ImageDraw

def create_icon():
    """Create a simple icon for the application."""
    size = 256
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a background circle
    circle_color = (0, 120, 212)  # Blue color
    draw.ellipse((10, 10, size-10, size-10), fill=circle_color)
    
    # Draw a simple chart line
    chart_color = (255, 255, 255)  # White
    points = [
        (50, 150),
        (90, 120),
        (130, 180),
        (170, 80),
        (210, 100)
    ]
    draw.line(points, fill=chart_color, width=10)
    
    # Draw a W in the center (without font)
    draw.text((size//2-30, size//2-40), "W", fill=(255, 255, 255))
    
    # Save the icon
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
    img.save(icon_path)
    
    print(f"Icon created at {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_icon() 