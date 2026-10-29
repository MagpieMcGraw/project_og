"""Throne of Darkness .lot archives: files as runs of LZO1X blocks, a packed directory at the end."""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from lzo import decompress


def read_blocks(data, at):
    """Unpacks the blocks of one file starting at `at`; returns (bytes, end)."""
    out = bytearray()
    while True:
        kind = data[at]
        if kind == 0:
            return bytes(out), at + 1
        if kind & 0x80:
            # small block: one-byte sizes
            size = data[at+1] + 1
            packed = data[at+2] + 1
            head = 3
        else:
            size = int.from_bytes(data[at+1:at+3], 'little') + 1
            packed = int.from_bytes(data[at+3:at+5], 'little') + 1
            head = 5
        method = kind & 0x7f
        if method == 4:
            piece, used = decompress(data, at + head)
            assert len(piece) == size and used == packed, (at, len(piece), size, used, packed)
        elif method == 1:
            assert size == packed, (at, size, packed)
            piece = data[at + head:at + head + size]
        else:
            raise ValueError(f"block kind {kind} at {at:x}: {data[at:at+16].hex(' ')}")
        out += piece
        at += head + packed


def directory(data):
    size = int.from_bytes(data[-4:], 'little')
    start = len(data) - 4 - size
    table, end = read_blocks(data, start)
    assert end == len(data) - 4, (end, len(data))
    return table, start


if __name__ == '__main__':
    data = open(sys.argv[1], 'rb').read()
    table, start = directory(data)
    print('directory at', hex(start), 'unpacked', len(table))
    sys.stdout.flush()
    sys.stdout.buffer.write(table[:int(sys.argv[2]) if len(sys.argv) > 2 else 512])


def entries(table):
    """Yields (path, size, offset, kind, extra) for every file in an unpacked directory."""
    assert table[:4] == b'\xce\xfa\xef\xbe', table[:8].hex(' ')
    at = 4
    found = []

    def u32():
        nonlocal at
        value = int.from_bytes(table[at:at+4], 'little')
        at += 4
        return value

    def name():
        nonlocal at
        length = table[at]
        text = table[at+1:at+1+length].decode('latin1')
        at += 1 + length
        return text

    def folder(path):
        for k in range(u32()):
            file_name = name()
            size, offset, kind, extra = u32(), u32(), u32(), u32()
            found.append((path + file_name, size, offset, kind, extra))
        for k in range(u32()):
            folder(path + name() + '/')

    folder('')
    assert at == len(table), (at, len(table))
    return found
