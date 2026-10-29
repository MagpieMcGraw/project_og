"""lotget.py <archive.lot> <out folder> <pattern...>: unpacks files whose path matches any fnmatch pattern."""
import sys, os, fnmatch
sys.path.insert(0, os.path.dirname(__file__))
import lot

path, out_folder, patterns = sys.argv[1], sys.argv[2], sys.argv[3:]
limit = None
if patterns and patterns[0].startswith('--limit='):
    limit = int(patterns[0].split('=')[1])
    patterns = patterns[1:]
data = open(path, 'rb').read()
table, start = lot.directory(data)
taken = 0
for name, size, offset, kind, extra in lot.entries(table):
    if not any(fnmatch.fnmatch(name.lower(), p.lower()) for p in patterns):
        continue
    if kind == 1:
        body = data[offset:offset + size]
    else:
        body, end = lot.read_blocks(data, offset)
    if len(body) != size:
        print('size differs', name, len(body), size)
    target = os.path.join(out_folder, name)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, 'wb') as f:
        f.write(body)
    taken += 1
    if limit and taken >= limit:
        break
print('took', taken)
