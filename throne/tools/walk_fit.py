"""walk_fit.py <level folder>:<lex name> ...: where each level's walk grid
lies on it, fitted: every collision outline (OCOL) line sloping as a wall
does (±0.5) is a wall's foot, open on the room's side (toward the middle
of all such lines' ends) and blocked on the other; the named spots
(.stripped.sp) open. Prints the grid's corner (x0, y0: walk_grid.mara).
Lines inside the room (screens, chests) count too, on whichever side the
room's middle falls, so the best score is well short of all; for the Mori
shrine it gives (1612, -215), the corner the overlay (walk.py) checks.
Where the corner comes from in the game's files isn't known yet."""
import sys, os, math, re
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
    """The outlines' lines sloping as walls do: (left x, right x, slope,
    where it meets x = 0, the open side: 1 down the screen, -1 up). An
    outline belongs to the record before it (lex.mara): a picture's or an
    animation's is a wall's foot (walls drawn are the far ones, the floor in
    front of them: open below); a plain ECOL's is a front edge (no wall
    drawn: open above); an event's area (ECOL TriggerEvent) is left out."""
    tags = sorted((m.start(), m.group()) for m in re.finditer(rb'EGRA|EANI|ECOL|OCOL', layout))
    owner = None
    lines = []
    for at, tag in tags:
        if tag in (b'EGRA', b'EANI'):
            owner = 'thing'
        elif tag == b'ECOL':
            owner = 'trigger' if b'TriggerEvent' in layout[at + 4:at + 36] else 'line'
        else:
            count = i32(layout, at + 4)
            if not 1 < count < 200 or owner not in ('thing', 'line'):
                continue
            points = [(i32(layout, at + 8 + 8 * k), i32(layout, at + 12 + 8 * k)) for k in range(count)]
            for (x1, y1), (x2, y2) in zip(points, points[1:]):
                if abs(x1 - x2) >= 48 and all(-1000 < v < 20000 for v in (x1, y1, x2, y2)):
                    slope = (y2 - y1) / (x2 - x1)
                    if abs(abs(slope) - 0.5) < 0.06:
                        lines.append((min(x1, x2), max(x1, x2), slope, y1 - slope * x1, 1 if owner == 'thing' else -1))
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
    for lo, hi, slope, c, inward in lines:
        for px in range(int(lo), int(hi) + 1, 16):
            samples.append((px, slope * px + c, inward))

    def blocked(px, py, x0, y0):
        u = (px - x0) / 16
        v = (py - y0) / 8
        gx = math.floor((u + v) / 2 + 0.5)
        up = math.floor((v - u) / 2 + 0.5)
        gy = height - 1 - up
        return not (0 <= gx < width and 0 <= gy < height) or rows[gy][gx] == 1

    def score(x0, y0):
        total = 0
        for px, py, inward in samples:
            total += 1 if not blocked(px, py + 10 * inward, x0, y0) else -1
            total += 1 if blocked(px, py - 10 * inward, x0, y0) else -1
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
