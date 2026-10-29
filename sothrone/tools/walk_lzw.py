import sys

def lzw_bits(data, bit_start, width0, first_code, max_width=12, early=0, clear=True):
    out = bytearray()
    pos = bit_start
    width = width0
    table_len = first_code
    table = {}
    prev = None
    total = len(data) * 8
    while pos + width <= total:
        code = 0
        for k in range(width):
            code |= ((data[(pos + k) >> 3] >> ((pos + k) & 7)) & 1) << k
        pos += width
        if clear and first_code >= 258 and code == 256:
            table = {}; table_len = first_code; width = width0; prev = None
            continue
        if clear and first_code >= 258 and code == 257:
            return out, f'end at bit {pos} of {total}'
        if code < 256:
            entry = bytes([code])
        elif code in table:
            entry = table[code]
        elif code == table_len and prev is not None:
            entry = prev + prev[:1]
        else:
            return out, f'bad code {code} (table {table_len}) at bit {pos}'
        out += entry
        if prev is not None:
            table[table_len] = prev + entry[:1]
            table_len += 1
        prev = entry
        if table_len + early >= (1 << width) and width < max_width:
            width += 1
    return out, 'ran out'

d = open(sys.argv[1], 'rb').read()
results = []
for byte_start in range(8, 18):
    for shift in range(8):
        for width0 in (9,):
            for first in (256, 258):
                for early in (0, 1):
                    out, why = lzw_bits(d[byte_start:], shift, width0, first, early=early)
                    results.append((len(out), byte_start, shift, first, early, why, out[:16].hex(' ')))
results.sort(reverse=True)
for r in results[:8]:
    print(r)
