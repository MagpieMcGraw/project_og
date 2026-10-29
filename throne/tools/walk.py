"""walk.py: a level's walk grid (.walk.sp / .walk.mp), where one can walk.

The file: u32 0, u32 width, u32 height (in cells), then blocks (a byte,
the block's size less 1, then its bytes) to the end. The blocks' bytes
joined are LZW from their bit 3: 9-bit codes and wider as the table grows
(to 12), lowest bit first, the table's new entries from 256, no clear or
end codes; at 4096 entries the table starts over. Unpacked, a bit per
cell, row by row, the high bit first: 1 blocked, 0 open; exactly width x
height bits (all 110 of the game's). The rows run from the level's far end.

walk.py <World.lot> <level folder> <lex name> <out.png> [cell_w cell_h x0 y0]
draws the level (level.py) with the blocked cells shaded over it, the
grid laid on the level as an isometric one: cell (gx, gy)'s middle at
x0 + (gx - gy) * cell_w / 2, y0 + (gx + gy) * cell_h / 2.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def lzw(data, bit):
    out = bytearray()
    width = 9
    table = {}
    table_len = 256
    prev = None
    total = len(data) * 8
    while bit + width <= total:
        code = 0
        for k in range(width):
            code |= ((data[(bit + k) >> 3] >> ((bit + k) & 7)) & 1) << k
        bit += width
        if code < 256:
            entry = bytes([code])
        elif code in table:
            entry = table[code]
        elif code == table_len and prev is not None:
            entry = prev + prev[:1]
        else:
            raise ValueError(f'bad code {code} at bit {bit}')
        out += entry
        if prev is not None:
            table[table_len] = prev + entry[:1]
            table_len += 1
        prev = entry
        if table_len >= (1 << width) and width < 12:
            width += 1
        elif table_len >= 4096:
            table = {}
            table_len = 256
            width = 9
            prev = None
    return bytes(out)


def walk_grid(body):
    """(width, height, rows of 0 open / 1 blocked)."""
    width = int.from_bytes(body[4:8], 'little')
    height = int.from_bytes(body[8:12], 'little')
    stream = bytearray()
    at = 12
    while at < len(body):
        count = body[at] + 1
        stream += body[at + 1:at + 1 + count]
        at += 1 + count
    bits = lzw(bytes(stream), 3)
    size = (width * height + 7) // 8
    bits = bits[:size] + b'\xff' * (size - min(size, len(bits)))
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            k = y * width + x
            row.append((bits[k >> 3] >> (7 - (k & 7))) & 1)
        rows.append(row)
    return width, height, rows


if __name__ == '__main__':
    import lot, lex, spr8, level
    world_lot, folder, lex_name, out = sys.argv[1:5]
    cell_w, cell_h, x0, y0 = (float(v) for v in sys.argv[5:9]) if len(sys.argv) > 8 else (32, 16, 1552, -256)
    data = open(world_lot, 'rb').read()
    table, start = lot.directory(data)
    files = {e[0].lower(): e for e in lot.entries(table)}
    folder = folder.lower().replace('\\', '/').rstrip('/') + '/'
    body, end = lot.read_blocks(data, files[folder + lex_name.lower() + '.walk.sp'][2])
    width, height, rows = walk_grid(body)
    open_cells = [(x, y) for y in range(height) for x in range(width) if not rows[y][x]]
    xs = [c[0] for c in open_cells]
    ys = [c[1] for c in open_cells]
    print(f'{width}x{height}, {len(open_cells)} open, x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)}')
    # The level picture, then the blocked cells near the open ones shaded red.
    os.system(f'python -I "{os.path.join(os.path.dirname(os.path.abspath(__file__)), "level.py")}" "{world_lot}" "{folder}" {lex_name} "{out}" file > nul')
    import zlib, struct
    png = open(out, 'rb').read()
    # read back the PNG level.py wrote (filter 0 rows, RGBA)
    at = 8
    idat = b''
    while at < len(png):
        length, kind = struct.unpack('>I4s', png[at:at + 8])
        chunk = png[at + 8:at + 8 + length]
        if kind == b'IHDR':
            image_w, image_h = struct.unpack('>II', chunk[:8])
        elif kind == b'IDAT':
            idat += chunk
        at += 12 + length
    raw = zlib.decompress(idat)
    image = bytearray()
    for y in range(image_h):
        image += raw[y * (image_w * 4 + 1) + 1:(y + 1) * (image_w * 4 + 1)]
    # level.py's picture starts at the level's box; its top left:
    box_left, box_top = (int(v) for v in open(out + '.box').read().split()) if os.path.exists(out + '.box') else (0, 0)
    for gy in range(height):
        for gx in range(width):
            # (The rows are stored from the level's far end: row 0 is gy = height - 1.)
            up = height - 1 - gy
            middle_x = x0 + (gx - up) * cell_w / 2 - box_left
            middle_y = y0 + (gx + up) * cell_h / 2 - box_top
            if not (-cell_w < middle_x < image_w + cell_w and -cell_h < middle_y < image_h + cell_h):
                continue
            blocked = rows[gy][gx]
            # the cell's diamond, filled by a few points
            for dy in range(-int(cell_h // 2) + 1, int(cell_h // 2)):
                span = int((cell_w / 2) * (1 - abs(dy) / (cell_h / 2)))
                py = int(middle_y + dy)
                if not 0 <= py < image_h:
                    continue
                for dx in range(-span, span + 1):
                    px = int(middle_x + dx)
                    if 0 <= px < image_w:
                        p = (py * image_w + px) * 4
                        if blocked:
                            image[p] = min(255, image[p] // 2 + 120)
                            image[p + 1] = image[p + 1] // 2
                            image[p + 2] = image[p + 2] // 2
                        else:
                            image[p + 1] = min(255, image[p + 1] // 2 + 60)
    spr8.write_png(out, image_w, image_h, image)
    print('written', out)
