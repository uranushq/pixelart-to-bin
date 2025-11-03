"""
Test error handling for invalid dimensions
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.utils.tile_splitter import validate_dimensions, split_into_4x4_tiles

# Test with invalid dimensions
print("Testing dimension validation:")
print()

# Test 1: 15x16 (height not multiple of 4)
test_matrix_1 = [
    [[0, 0, 0] for _ in range(16)]
    for _ in range(15)
]
print("Test 1: 15x16 matrix")
try:
    validate_dimensions(test_matrix_1)
    print("  ✗ Should have raised error")
except ValueError as e:
    print(f"  ✓ Error caught: {e}")

print()

# Test 2: 16x15 (width not multiple of 4)
test_matrix_2 = [
    [[0, 0, 0] for _ in range(15)]
    for _ in range(16)
]
print("Test 2: 16x15 matrix")
try:
    validate_dimensions(test_matrix_2)
    print("  ✗ Should have raised error")
except ValueError as e:
    print(f"  ✓ Error caught: {e}")

print()

# Test 3: 13x13 (both not multiples of 4)
test_matrix_3 = [
    [[0, 0, 0] for _ in range(13)]
    for _ in range(13)
]
print("Test 3: 13x13 matrix")
try:
    validate_dimensions(test_matrix_3)
    print("  ✗ Should have raised error")
except ValueError as e:
    print(f"  ✓ Error caught: {e}")

print()

# Test 4: 16x16 (valid)
test_matrix_4 = [
    [[0, 0, 0] for _ in range(16)]
    for _ in range(16)
]
print("Test 4: 16x16 matrix")
try:
    h, w = validate_dimensions(test_matrix_4)
    print(f"  ✓ Valid dimensions: {h}x{w}")
    tiles = split_into_4x4_tiles(test_matrix_4)
    print(f"  ✓ Successfully split into {len(tiles)} tiles")
except ValueError as e:
    print(f"  ✗ Unexpected error: {e}")
