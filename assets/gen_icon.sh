#!/bin/bash
set -e

ICONSET="text2prompt.iconset"
mkdir -p "$ICONSET"

# Generate icon PNGs at required sizes using macOS sips
# Base: 1024x1024 solid color with text overlay using python
python3 -c "
import struct, zlib

def create_png(width, height, color, output_path):
    '''Create a minimal PNG with a gradient circle'''
    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    raw = b''
    for y in range(height):
        raw += b'\x00'  # filter byte
        for x in range(width):
            cx, cy = width/2, height/2
            dist = ((x-cx)**2 + (y-cy)**2)**0.5
            max_dist = width/2
            if dist < max_dist:
                t = dist / max_dist
                r = int(color[0] * (1-t) + 255 * t)
                g = int(color[1] * (1-t) + 255 * t)
                b = int(color[2] * (1-t) + 255 * t)
                raw += bytes([r, g, b, 255])
            else:
                raw += bytes([0, 0, 0, 0])

    with open(output_path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)))
        f.write(chunk(b'IDAT', zlib.compress(raw)))
        f.write(chunk(b'IEND', b''))

# Generate all sizes
sizes = [16, 32, 64, 128, 256, 512, 1024]
for s in sizes:
    create_png(s, s, (100, 120, 200), f'$ICONSET/icon_{s}x{s}.png')
    if s <= 512:
        create_png(s*2, s*2, (100, 120, 200), f'$ICONSET/icon_{s}x{s}@2x.png')
    else:
        create_png(s, s, (100, 120, 200), f'$ICONSET/icon_{s}x{s}@2x.png')
"

# Convert to .icns using macOS iconutil
iconutil -c icns "$ICONSET" -o text2prompt.icns
rm -rf "$ICONSET"

echo "Icon generated: text2prompt.icns"
