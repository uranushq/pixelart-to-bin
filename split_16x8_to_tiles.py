#!/usr/bin/env python3
"""
Split 16x8 bin file into 4x4 tiles
"""
import struct
import sys
import os

def split_16x8_to_tiles(input_path: str, output_base: str):
    """
    Split 16x8 bin file into 4x4 tiles
    Layout: 4 horizontal x 2 vertical = 8 tiles total
    
    Tile layout:
    0  1  2  3
    4  5  6  7
    
    Args:
        input_path: Input bin file (16x8)
        output_base: Output base path (without extension)
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
    print(f"   Size: {width}x{height}")
    print(f"   Frames: {total_frames}")
    print(f"   FPS: {fps}")
    
    if width != 16 or height != 8:
        print(f"❌ Error: Expected 16x8, got {width}x{height}")
        sys.exit(1)
    
    # Tile configuration
    tile_width = 4
    tile_height = 4
    num_h = width // tile_width  # 4
    num_v = height // tile_height  # 2
    total_tiles = num_h * num_v  # 8
    
    print(f"   Tile layout: {num_h}x{num_v} = {total_tiles} tiles")
    
    # Initialize tile data
    tiles_by_number = [[] for _ in range(total_tiles)]
    
    # Process each frame
    frame_size = width * height * 3
    
    for frame_idx in range(total_frames):
        offset = 16 + (frame_idx * frame_size)
        frame_data = data[offset:offset + frame_size]
        
        # Extract tiles from this frame
        for tile_v in range(num_v):
            for tile_h in range(num_h):
                tile_idx = tile_v * num_h + tile_h
                tile_pixels = []
                
                # Extract 4x4 tile
                for y in range(tile_height):
                    for x in range(tile_width):
                        src_y = tile_v * tile_height + y
                        src_x = tile_h * tile_width + x
                        pixel_offset = (src_y * width + src_x) * 3
                        
                        r = frame_data[pixel_offset]
                        g = frame_data[pixel_offset + 1]
                        b = frame_data[pixel_offset + 2]
                        tile_pixels.extend([r, g, b])
                
                tiles_by_number[tile_idx].append(bytes(tile_pixels))
    
    # Save each tile
    print(f"\n💾 Saving {total_tiles} tile files...")
    
    for tile_idx in range(total_tiles):
        tile_path = f"{output_base}_tile_{tile_idx:02d}.bin"
        
        # Header for tile (4x4)
        tile_data = struct.pack('<IIII', total_frames, tile_height, tile_width, fps)
        
        # Frames
        for frame in tiles_by_number[tile_idx]:
            tile_data += frame
        
        # Trailer
        import time
        save_time = int(time.time())
        trailer = struct.pack('<IQI', total_frames, save_time, 0xDEADBEEF)
        tile_data += trailer
        
        # Save
        with open(tile_path, 'wb') as f:
            f.write(tile_data)
        
        print(f"   ✓ tile_{tile_idx:02d}.bin ({len(tile_data):,} bytes)")
    
    print(f"\n✅ All tiles saved!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_16x8_to_tiles.py <input.bin> [output_base]")
        print("\nExample:")
        print("  python split_16x8_to_tiles.py ./output/smtm3_16x8_full.bin ./output/smtm3_16x8")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_base = sys.argv[2]
    else:
        # Auto-generate output base
        output_base = input_path.replace("_full.bin", "").replace(".bin", "")
    
    print("🎬 Split 16x8 to 4x4 Tiles")
    print("=" * 50)
    
    split_16x8_to_tiles(input_path, output_base)
    
    print("\n🎉 Splitting completed!")
