#!/usr/bin/env python3
"""
Extract center 16x8 region from 40x8 bin file
Takes the center 16 columns (x: 12-27) from each frame
"""
import struct
import sys

def extract_center_16x8(input_path: str, output_path: str):
    """
    Extract center 16x8 from 40x8 bin file
    
    Args:
        input_path: Input bin file (40x8)
        output_path: Output bin file (16x8)
    """
    # Read input file
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Read header
    total_frames = struct.unpack('I', data[0:4])[0]
    height = struct.unpack('I', data[4:8])[0]
    width = struct.unpack('I', data[8:12])[0]
    fps = struct.unpack('I', data[12:16])[0]
    
    print(f"📖 Reading: {input_path}")
    print(f"   Input: {width}x{height}, {total_frames} frames, {fps} fps")
    
    if width != 40 or height != 8:
        print(f"❌ Error: Expected 40x8, got {width}x{height}")
        sys.exit(1)
    
    # Extract center 16 columns (x: 12-27, which is 16 columns)
    start_x = 12
    extract_width = 16
    new_width = extract_width
    new_height = height
    
    print(f"   Extracting columns {start_x} to {start_x + extract_width - 1}")
    print(f"   Output: {new_width}x{new_height}")
    
    # Process frames
    frame_size = width * height * 3  # RGB
    new_frames = []
    
    for frame_idx in range(total_frames):
        offset = 16 + (frame_idx * frame_size)
        frame_data = data[offset:offset + frame_size]
        
        # Extract center region
        new_frame = []
        for y in range(height):
            for x in range(start_x, start_x + extract_width):
                pixel_offset = (y * width + x) * 3
                r = frame_data[pixel_offset]
                g = frame_data[pixel_offset + 1]
                b = frame_data[pixel_offset + 2]
                new_frame.extend([r, g, b])
        
        new_frames.append(bytes(new_frame))
    
    # Write output file
    # Header: total_frames, height, width, fps
    output_data = struct.pack('<IIII', total_frames, new_height, new_width, fps)
    
    # Frames
    for frame in new_frames:
        output_data += frame
    
    # Trailer
    import time
    save_time = int(time.time())
    trailer = struct.pack('<IQI', total_frames, save_time, 0xDEADBEEF)
    output_data += trailer
    
    # Save
    with open(output_path, 'wb') as f:
        f.write(output_data)
    
    print(f"\n✅ Saved: {output_path}")
    print(f"   Size: {len(output_data):,} bytes")
    print(f"   Frames: {total_frames}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_center_16x8.py <input.bin> [output.bin]")
        print("\nExample:")
        print("  python extract_center_16x8.py ./output/smtm3_40x8_full.bin ./output/smtm3_16x8_full.bin")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        # Auto-generate output name
        output_path = input_path.replace("40x8", "16x8").replace("_full.bin", "_center16x8.bin")
        if output_path == input_path:
            output_path = input_path.replace(".bin", "_center16x8.bin")
    
    print("🎬 Extract Center 16x8 Region")
    print("=" * 50)
    
    extract_center_16x8(input_path, output_path)
    
    print("\n🎉 Extraction completed!")
