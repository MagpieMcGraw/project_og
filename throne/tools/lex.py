"""lex.py <file.lex>: a level layout's header, resource table and placed things.

A .lex: a header (u32 at 0x4E and 0x52, 0x5E ...), then "IRES" and a
table like a .rex's — but where a .rex gives each resource's offset, a
.lex gives its size (RGRA: width, height; RANI: width, height, frames) —
then records, each a 4-letter tag and its fields.
"""
import sys, collections

TAG_LETTERS = set(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')


def u32(d, at):
    return int.from_bytes(d[at:at + 4], 'little')


def i32(d, at):
    return int.from_bytes(d[at:at + 4], 'little', signed=True)


def is_tag(d, at):
    return at + 4 <= len(d) and all(c in TAG_LETTERS for c in d[at:at + 4])


def read_table(d, at):
    """The resource table at at ("IRES"): its entries and where it ends."""
    assert d[at:at + 4] == b'IRES'
    count = u32(d, at + 4)
    at += 8
    entries = []
    for k in range(count):
        kind = d[at:at + 4].decode()
        length = d[at + 4]
        name = d[at + 5:at + 5 + length].decode('latin1')
        at += 5 + length
        numbers = []
        while not is_tag(d, at) and len(numbers) < 8 and at + 4 <= len(d):
            numbers.append(u32(d, at))
            at += 4
        entries.append((kind, name, numbers))
    return entries, at


def read_records(d, at):
    records = []
    while at < len(d):
        if not is_tag(d, at):
            records.append(('????', [d[at:at + 16].hex(' ')]))
            break
        tag = d[at:at + 4].decode()
        at += 4
        fields = []
        while at + 4 <= len(d) and not is_tag(d, at):
            fields.append(i32(d, at))
            at += 4
        records.append((tag, fields))
    return records


if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    table_at = d.find(b'IRES')
    print('header', [u32(d, a) for a in range(0, table_at, 4) if u32(d, a)][:20], 'table at', table_at)
    entries, end = read_table(d, table_at)
    for k, e in enumerate(entries):
        print(f'  {k:3d} {e[0]} {e[2]} {e[1]}')
    records = read_records(d, end)
    print('records', collections.Counter(r[0] for r in records))
    shapes = collections.Counter((r[0], len(r[1])) for r in records)
    print('shapes', shapes)
    for r in records[:int(sys.argv[2]) if len(sys.argv) > 2 else 40]:
        print('  ', r)
