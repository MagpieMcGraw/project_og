"""atlas_check.py <archive.lot> <sprite path in it> <atlas.png from `throne sprite`>

Builds the atlas `throne sprite` writes (art.mara's layout: a row per
direction, a column per frame, cells the box round all frames) with the
Python decoder, and compares it with the PNG pixel by pixel.
"""
import sys, os, zlib, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lot, spr8


def read_png(path):
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    at = 8
    idat = b''
    while at < len(data):
        length, kind = struct.unpack('>I4s', data[at:at + 8])
        body = data[at + 8:at + 8 + length]
        if kind == b'IHDR':
            width, height, depth, colour = struct.unpack('>IIBB', body[:10])
            assert depth == 8 and colour == 6, (depth, colour)
        elif kind == b'IDAT':
            idat += body
        at += 12 + length
    raw = zlib.decompress(idat)
    row_size = width * 4
    pixels = bytearray()
    previous = bytearray(row_size)
    for y in range(height):
        kind = raw[y * (row_size + 1)]
        row = bytearray(raw[y * (row_size + 1) + 1:(y + 1) * (row_size + 1)])
        for x in range(row_size):
            left = row[x - 4] if x >= 4 else 0
            up = previous[x]
            corner = previous[x - 4] if x >= 4 else 0
            if kind == 1:
                row[x] = (row[x] + left) & 255
            elif kind == 2:
                row[x] = (row[x] + up) & 255
            elif kind == 3:
                row[x] = (row[x] + (left + up) // 2) & 255
            elif kind == 4:
                guess = left + up - corner
                pa, pb, pc = abs(guess - left), abs(guess - up), abs(guess - corner)
                pick = left if pa <= pb and pa <= pc else (up if pb <= pc else corner)
                row[x] = (row[x] + pick) & 255
        pixels += row
        previous = row
    return width, height, pixels


archive, sprite_path, png_path = sys.argv[1:4]
data = open(archive, 'rb').read()
table, start = lot.directory(data)
entries = {e[0].lower(): e for e in lot.entries(table)}
entry = entries[sprite_path.lower().replace('\\', '/')]
body, end = lot.read_blocks(data, entry[2])
colours = spr8.palette_of(body)
offsets = spr8.frames_of(body)
decoded = [spr8.decode(body, offsets[k], offsets[k + 1], colours) for k in range(len(offsets) - 1)]
frames = len(decoded)
rows = 8 if frames % 8 == 0 else 1
columns = frames // rows
left = min(f[0][4] for f in decoded)
top = min(f[0][2] for f in decoded)
cell_w = max(f[0][5] for f in decoded) - left
cell_h = max(f[0][3] for f in decoded) - top
width, height = cell_w * columns, cell_h * rows
atlas = bytearray(width * height * 4)
for k, (head, w, h, pixels) in enumerate(decoded):
    ox = (k % columns) * cell_w + head[4] - left
    oy = (k // columns) * cell_h + head[2] - top
    for y in range(h):
        for x in range(w):
            at = (y * w + x) * 4
            if pixels[at + 3]:
                to = ((oy + y) * width + ox + x) * 4
                atlas[to:to + 4] = pixels[at:at + 4]
png_width, png_height, png_pixels = read_png(png_path)
print(f'python atlas {width}x{height}, png {png_width}x{png_height}')
if (width, height) != (png_width, png_height):
    sys.exit('sizes differ')
differ = sum(1 for k in range(0, len(atlas), 4) if atlas[k:k + 4] != png_pixels[k:k + 4])
solid = sum(1 for k in range(3, len(atlas), 4) if atlas[k])
print(f'{differ} of {width * height} pixels differ ({solid} drawn)')
