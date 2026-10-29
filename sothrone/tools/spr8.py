"""Throne of Darkness SPR8 sprites: decode frames to RGBA, write PNG contact sheets.

spr8.py <sprite.s8> <out.png> [palette.s8] [columns]
"""
import sys, struct, zlib


def u16(d, at):
    return int.from_bytes(d[at:at + 2], 'little')


def u32(d, at):
    return int.from_bytes(d[at:at + 4], 'little')


def palette_of(d):
    at = u32(d, 0x20) + 4
    colors = []
    for k in range(256):
        c = u16(d, at + 2 * k)
        r, g, b = (c >> 11) & 31, (c >> 5) & 63, c & 31
        colors.append(((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)))
    return colors


def frames_of(d):
    count = u16(d, 0x16)
    table = u32(d, 0x24)
    return [u32(d, table + 4 * k) for k in range(count)] + [len(d)]


def decode(d, start, end, colors):
    """Returns (head, width, height, rgba rows) for one frame."""
    head = [u16(d, start + 2 * j) for j in range(8)]
    canvas_w, canvas_h, top, bottom, left, right = head[:6]
    width, height = right - left, bottom - top
    pixels = bytearray(width * height * 4)
    x = y = 0
    k = start + 16

    def put(color, alpha):
        if 0 <= x < width and 0 <= y < height:
            r, g, b = colors[color]
            at = (y * width + x) * 4
            pixels[at:at + 4] = bytes((r, g, b, alpha))

    while k < end:
        b = d[k]
        k += 1
        op, count = b & 3, b >> 2
        if op == 0:
            x += count
        elif op == 1:
            put(d[k], min(255, count * 4 + count // 16))
            k += 1
            x += 1
        elif op == 2:
            y += 1
            x = count
        else:
            for j in range(count + 1):
                put(d[k + j], 255)
                x += 1
            k += count + 1
    return head, width, height, pixels


def write_png(path, width, height, rgba):
    rows = b''.join(b'\x00' + bytes(rgba[y * width * 4:(y + 1) * width * 4]) for y in range(height))

    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))

    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)))
        f.write(chunk(b'IDAT', zlib.compress(rows, 6)))
        f.write(chunk(b'IEND', b''))


if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    colors = palette_of(open(sys.argv[3], 'rb').read() if len(sys.argv) > 3 and sys.argv[3] != '-' else d)
    columns = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    offsets = frames_of(d)
    decoded = [decode(d, offsets[k], offsets[k + 1], colors) for k in range(len(offsets) - 1)]
    # place frames on their shared canvas, cropped to the union box, on a grey background
    top = min(f[0][2] for f in decoded)
    bottom = max(f[0][3] for f in decoded)
    left = min(f[0][4] for f in decoded)
    right = max(f[0][5] for f in decoded)
    cell_w, cell_h = right - left + 2, bottom - top + 2
    rows = (len(decoded) + columns - 1) // columns
    sheet_w, sheet_h = cell_w * columns, cell_h * rows
    sheet = bytearray(bytes((96, 96, 96, 255)) * (sheet_w * sheet_h))
    for n, (head, width, height, pixels) in enumerate(decoded):
        ox = (n % columns) * cell_w + head[4] - left
        oy = (n // columns) * cell_h + head[2] - top
        for y in range(height):
            for x in range(width):
                at = (y * width + x) * 4
                alpha = pixels[at + 3]
                if alpha:
                    to = ((oy + y) * sheet_w + ox + x) * 4
                    for c in range(3):
                        sheet[to + c] = (pixels[at + c] * alpha + sheet[to + c] * (255 - alpha)) // 255
    write_png(sys.argv[2], sheet_w, sheet_h, sheet)
    print(len(decoded), 'frames, box', (left, top, right, bottom), 'sheet', sheet_w, sheet_h)
