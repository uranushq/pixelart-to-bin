"""
Create test images for scattering animation
"""
from PIL import Image
import os

# Create test directory
test_dir = "./data/test_scattering"
os.makedirs(test_dir, exist_ok=True)

# Create 3 simple test images (8x8 pixels)
# Image 1: Red
img1 = Image.new('RGB', (8, 8), color=(255, 0, 0))
img1.save(os.path.join(test_dir, "test_1.png"))

# Image 2: Green
img2 = Image.new('RGB', (8, 8), color=(0, 255, 0))
img2.save(os.path.join(test_dir, "test_2.png"))

# Image 3: Blue
img3 = Image.new('RGB', (8, 8), color=(0, 0, 255))
img3.save(os.path.join(test_dir, "test_3.png"))

# Create config.json
import json
config = {
    "loop": 1,
    "loopDelay": 0,
    "countDown": False
}

with open(os.path.join(test_dir, "config.json"), 'w') as f:
    json.dump(config, f, indent=4)

print(f"Created test images in {test_dir}")
print("  - test_1.png (Red 8x8)")
print("  - test_2.png (Green 8x8)")
print("  - test_3.png (Blue 8x8)")
print("  - config.json")
