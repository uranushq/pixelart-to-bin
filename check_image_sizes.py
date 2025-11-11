#!/usr/bin/env python3
"""
Check image sizes in data folders
"""
from PIL import Image
import os

folders = [
    "./data/s+m+t+m+12",
    "./data/smtm+12",
    "./data/smtm12"
]

for folder in folders:
    if not os.path.exists(folder):
        print(f"❌ {folder} not found")
        continue
    
    print(f"\n📁 {folder}")
    for filename in os.listdir(folder):
        if filename.endswith('.png'):
            path = os.path.join(folder, filename)
            img = Image.open(path)
            print(f"   {filename}: {img.size[0]}x{img.size[1]}")
