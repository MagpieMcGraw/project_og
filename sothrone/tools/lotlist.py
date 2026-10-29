import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
import lot
path = sys.argv[1]
data = open(path, 'rb').read()
table, start = lot.directory(data)
found = lot.entries(table)
kinds = collections.Counter(e[3] for e in found)
extras = collections.Counter(e[4] for e in found)
exts = collections.Counter(os.path.splitext(e[0])[1].lower() for e in found)
print(os.path.basename(path), 'files', len(found), 'kinds', dict(kinds), 'extras', len(extras), extras.most_common(3))
print('  types', exts.most_common(30))
folders = collections.Counter(e[0].rsplit('/', 1)[0] if '/' in e[0] else '' for e in found)
print('  folders', len(folders), list(folders)[:12])
if len(sys.argv) > 2:
    for e in found[:int(sys.argv[2])]:
        print('   ', e)
