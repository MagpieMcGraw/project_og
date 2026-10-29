"""walk_fit.py <level folder>:<lex name> ...: where each level's walk grid
lies on it, fitted: every two-point collision outline (OCOL) sloping as a
wall does (±0.5) is a wall's foot, open just below it and blocked just
above; the named spots (.stripped.sp) open. Prints the grid's corner (x0,
y0: walk_grid.mara). For the Mori shrine it gives (1536, -252), within a
cell of the hand fit (1552, -256); where the corner comes from in the
game's files isn't known yet."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lot, walk
data = open('D:/Games/Disciples 2/Throne of Darkness/LotFiles/World.lot', 'rb').read()
table, start = lot.directory(data)
files = {e[0].lower(): e for e in lot.entries(table)}


def read(path):
    body, end = lot.read_blocks(data, files[path][2])
    return body


def i32(d, at):
    return int.from_bytes(d[at:at + 4], 'little', signed=True)


def wall_lines(layout):
    lines = []
    at = layout.find(b'OCOL')
    while at >= 0:
        if i32(layout, at + 4) == 2:
            x1, y1, x2, y2 = (i32(layout, at + 8 + 4 * k) for k in range(4))
            if x1 != x2 and abs(x1 - x2) >= 48 and all(-1000 < v < 20000 for v in (x1, y1, x2, y2)):
                slope = (y2 - y1) / (x2 - x1)
                if abs(abs(slope) - 0.5) < 0.06:
                    lines.append((min(x1, x2), max(x1, x2), slope, y1 - slope * x1))
        at = layout.find(b'OCOL', at + 4)
    return lines


def spots_of(body):
    count = int.from_bytes(body[4:8], 'little')
    at = 8
    spots = []
    for k in range(count):
        length = body[at]
        spots.append((i32(body, at + 1 + length), i32(body, at + 5 + length)))
        at += 9 + length
    return spots


def fit(folder, name):
    folder = folder.lower().rstrip('/') + '/'
    lines = wall_lines(read(folder + name.lower() + '.lex'))
    spots_path = folder + name.lower() + '.stripped.sp'
    spots = spots_of(read(spots_path)) if spots_path in files else []
    width, height, rows = walk.walk_grid(read(folder + name.lower() + '.walk.sp'))
    samples = []
    for lo, hi, slope, c in lines:
        for px in range(int(lo), int(hi) + 1, 16):
            samples.append((px, slope * px + c))

    def blocked(px, py, x0, y0):
        u = (px - x0) / 16
        v = (py - y0) / 8
        gx = math.floor((u + v) / 2 + 0.5)
        up = math.floor((v - u) / 2 + 0.5)
        gy = height - 1 - up
        return not (0 <= gx < width and 0 <= gy < height) or rows[gy][gx] == 1

    def score(x0, y0):
        total = 0
        for px, py in samples:
            total += 1 if not blocked(px, py + 10, x0, y0) else -1
            total += 1 if blocked(px, py - 10, x0, y0) else -1
        for sx, sy in spots:
            total += 10 if not blocked(sx, sy, x0, y0) else -10
        return total

    best = None
    for x0 in range(-2000, 4001, 16):
        for y0 in range(-1500, 1501, 8):
            s = score(x0, y0)
            if best is None or s > best[0]:
                best = (s, x0, y0)
    s, bx, by = best
    for x0 in range(bx - 16, bx + 17, 2):
        for y0 in range(by - 8, by + 9, 1):
            s2 = score(x0, y0)
            if s2 > best[0]:
                best = (s2, x0, y0)
    s, x0, y0 = best
    print(f'{name:22s} grid {width}x{height} corner ({x0}, {y0}) score {s} of {2 * len(samples) + 10 * len(spots)} ({len(lines)} wall lines, {len(spots)} spots)', flush=True)


for arg in sys.argv[1:]:
    folder, name = arg.split(':')
    fit(folder, name)
