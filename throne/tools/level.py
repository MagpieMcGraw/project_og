"""level.py <World.lot> <level folder> <lex name> <out.png> [order]

Draws a level from the game's files: its .lex's placed pictures (EGRA) and
animations (EANI, their first frame), each the resource its index names in
the .lex's table, found by name in the level's .rex bundles, drawn with the
palette its record names (EGRA) or its own (EANI); (x, y) the top left of
the sprite's canvas. order: "file" (as the .lex has them) or "y" (by the
bottom of their box, after the first group, the ground).
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lot, spr8, lex


def u32(d, at):
    return int.from_bytes(d[at:at + 4], 'little')


def i32(d, at):
    return int.from_bytes(d[at:at + 4], 'little', signed=True)


def rex_resources(d):
    """A .rex's resources by name (upper case): (kind, bytes)."""
    assert d[:4] == b'IRES'
    count = u32(d, 4)
    at = 8
    found = {}
    for k in range(count):
        kind = d[at:at + 4].decode()
        length = d[at + 4]
        name = d[at + 5:at + 5 + length].decode('latin1').upper()
        place = u32(d, at + 5 + length)
        at += 9 + length
        if d[place:place + 4].decode('latin1') != kind:
            continue
        size = u32(d, place + 4)
        found[name] = (kind, d[place + 8:place + 8 + size])
    return found


def raw_palette(b):
    """A bundle's RPLT: 256 colours, RGB565, and nothing else."""
    colours = []
    for k in range(256):
        c = int.from_bytes(b[k * 2:k * 2 + 2], 'little')
        r, g, bl = (c >> 11) & 31, (c >> 5) & 63, c & 31
        colours.append(((r << 3) | (r >> 2), (g << 2) | (g >> 4), (bl << 3) | (bl >> 2)))
    return colours


def placed(d, entries, start):
    """The .lex's placed pictures and animations, found by their tags:
    (tag, x, y, resource, palette or None, offset)."""
    things = []
    at = start
    count = len(entries)
    while True:
        at_graphic = d.find(b'EGRA', at)
        at_animation = d.find(b'EANI', at)
        candidates = [p for p in (at_graphic, at_animation) if p >= 0]
        if not candidates:
            return things
        at = min(candidates)
        if d[at:at + 4] == b'EGRA':
            x, y, a, b, index, palette = (i32(d, at + 4 + 4 * k) for k in range(6))
            if 0 <= index < count and entries[index][0] == 'RGRA' and 0 <= palette < count and entries[palette][0] == 'RPLT':
                things.append(('EGRA', x, y, index, palette, at))
        else:
            x, y = i32(d, at + 4), i32(d, at + 8)
            length = d[at + 12]
            name = d[at + 13:at + 13 + length]
            if 0 < length < 40 and all(32 <= c < 127 for c in name):
                index = i32(d, at + 13 + length + 7)
                if 0 <= index < count and entries[index][0] == 'RANI':
                    things.append(('EANI', x, y, index, None, at))
        at += 4


if __name__ == '__main__':
    world_lot, folder, lex_name, out = sys.argv[1:5]
    order = sys.argv[5] if len(sys.argv) > 5 else 'file'
    data = open(world_lot, 'rb').read()
    table, start = lot.directory(data)
    files = {e[0].lower(): e for e in lot.entries(table)}
    folder = folder.lower().replace('\\', '/').rstrip('/') + '/'

    def read(path):
        e = files[path.lower()]
        body, end = lot.read_blocks(data, e[2])
        return body

    lex_bytes = read(folder + lex_name + '.lex')
    table_at = lex_bytes.find(b'IRES')
    entries, end = lex.read_table(lex_bytes, table_at)
    resources = {}
    for path in files:
        if path.startswith(folder) and path.endswith('.rex'):
            resources.update(rex_resources(read(path)))
    things = placed(lex_bytes, entries, end)
    missing = [entries[t[3]][1] for t in things if entries[t[3]][1].upper() not in resources]
    print(len(things), 'placed;', len(resources), 'resources in the bundles;', len(set(missing)), 'not found', sorted(set(missing))[:5])
    # The level's size: the boxes of what's placed.
    drawn = []
    for tag, x, y, index, palette, at in things:
        name = entries[index][1].upper()
        if name not in resources:
            continue
        sprite = resources[name][1]
        colours = raw_palette(resources[entries[palette][1].upper()][1]) if palette is not None else spr8.palette_of(sprite)
        offsets = spr8.frames_of(sprite)
        head, w, h, pixels = spr8.decode(sprite, offsets[0], offsets[1], colours)
        drawn.append((x + head[4], y + head[2], w, h, pixels, tag, at))
    left = min(t[0] for t in drawn)
    top = min(t[1] for t in drawn)
    right = max(t[0] + t[2] for t in drawn)
    bottom = max(t[1] + t[3] for t in drawn)
    print('level box', left, top, right, bottom)
    # (Where the picture starts on the level, for walk.py to lay the grid on it.)
    open(out + '.box', 'w').write(f'{left} {top}')
    if order == 'y':
        ground = [t for t in drawn if t[6] < things[0][5] + 1] if False else []
        drawn.sort(key=lambda t: t[1] + t[3])
    width, height = right - left, bottom - top
    image = bytearray(bytes((20, 20, 24, 255)) * (width * height))
    for x0, y0, w, h, pixels, tag, at in drawn:
        for y in range(h):
            for x in range(w):
                p = (y * w + x) * 4
                alpha = pixels[p + 3]
                if not alpha:
                    continue
                q = ((y0 - top + y) * width + x0 - left + x) * 4
                for c in range(3):
                    image[q + c] = (pixels[p + c] * alpha + image[q + c] * (255 - alpha)) // 255
    spr8.write_png(out, width, height, image)
    print('written', out, width, height)
