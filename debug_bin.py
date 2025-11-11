#!/usr/bin/env python3
"""
Debug script to check what colors are in the generated bin file
"""
import struct

bin_path = r".\output\smtm3_40x8_full.bin"

# Read bin file
with open(bin_path, 'rb') as f:
    data = f.read()

print(f"File size: {len(data)} bytes")
print(f"Expected format: 16-byte header + frames + trailer")

# Read header (4 unsigned ints: total_frames, height, width, fps)
total_frames = struct.unpack('I', data[0:4])[0]
height = struct.unpack('I', data[4:8])[0]
width = struct.unpack('I', data[8:12])[0]
fps = struct.unpack('I', data[12:16])[0]

print(f"Header:")
print(f"  Total frames: {total_frames}")
print(f"  Height: {height}")
print(f"  Width: {width}")
print(f"  FPS: {fps}")

# Calculate frame info
frame_size = width * height * 3  # width * height * 3 (RGB)
trailer_size = 16  # total_frames (4) + timestamp (8) + end_marker (4)
expected_data_size = 16 + (frame_size * total_frames) + trailer_size

print(f"Frame size: {frame_size} bytes")
print(f"Expected total size: {expected_data_size} bytes")
print(f"Actual size: {len(data)} bytes")
print()

# Analyze some key frames
# Based on mode3 timing: yellow should appear around frame 107-120
frames_to_check = [0, 70, 90, 100, 107, 110, 115, 120, 130, 150, 200, 250]

for frame_idx in frames_to_check:
    if frame_idx >= total_frames:
        continue
        
    offset = 16 + (frame_idx * frame_size)  # Skip 16-byte header
    frame_data = data[offset:offset + frame_size]
    
    # Count colors
    black_count = 0
    white_count = 0
    yellow_count = 0
    orange_count = 0
    red_count = 0
    other_count = 0
    
    for i in range(0, len(frame_data), 3):
        r = frame_data[i]
        g = frame_data[i+1]
        b = frame_data[i+2]
        
        if r == 0 and g == 0 and b == 0:
            black_count += 1
        elif r > 200 and g > 200 and b > 200:
            white_count += 1
        elif r > 150 and r < 200 and g > 150 and g < 200 and b < 50:  # Yellow (180, 180, 0)
            yellow_count += 1
        elif r > 200 and g > 100 and g < 160 and b < 50:  # Orange (255, 140, 0)
            orange_count += 1
        elif r > 200 and g < 100 and b < 50:  # Red
            red_count += 1
        else:
            other_count += 1
    
    total = black_count + white_count + yellow_count + orange_count + red_count + other_count
    
    print(f"Frame {frame_idx}:")
    print(f"  Black: {black_count}/{total} ({100*black_count/total:.1f}%)")
    print(f"  White: {white_count}/{total} ({100*white_count/total:.1f}%)")
    print(f"  Yellow: {yellow_count}/{total} ({100*yellow_count/total:.1f}%)")
    print(f"  Orange: {orange_count}/{total} ({100*orange_count/total:.1f}%)")
    print(f"  Red: {red_count}/{total} ({100*red_count/total:.1f}%)")
    print(f"  Other: {other_count}/{total} ({100*other_count/total:.1f}%)")
    
    # ALWAYS show sample colors to see what's actually in the file
    print(f"  Sample colors (first 10 unique non-black):")
    samples = []
    for i in range(0, len(frame_data), 3):
        r = frame_data[i]
        g = frame_data[i+1]
        b = frame_data[i+2]
        if (r, g, b) not in samples and not (r == 0 and g == 0 and b == 0):
            samples.append((r, g, b))
            if len(samples) >= 10:
                break
    for rgb in samples:
        print(f"    RGB({rgb[0]}, {rgb[1]}, {rgb[2]})")
    print()

print("\n📊 Analysis complete!")
