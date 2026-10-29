import sys
d = open(sys.argv[1], 'rb').read()
assert d[:4] == b'IRES', d[:4]
count = int.from_bytes(d[4:8], 'little')
at = 8
total = 0
items = []
for k in range(count):
    kind = d[at:at+4].decode()
    length = d[at+4]
    name = d[at+5:at+5+length].decode('latin1')
    number = int.from_bytes(d[at+5+length:at+9+length], 'little')
    at += 9 + length
    items.append((kind, name, number))
    total += number
print('table ends at', at, 'file', len(d), 'sum of numbers', total, 'rest', len(d) - at)
for item in items[:12]:
    print('  ', item)
# what follows the table
print(d[at:at+48].hex(' '))
print(d[at:at+48])
