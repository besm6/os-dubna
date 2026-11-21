#!/usr/bin/env python3
"""Compare the loader of tape 101 (mk-ld-img.sh) with the archived 9/MONSYS
(tape 9) and the rebuilt one (tape 203): zone 0 and words 0-377 of zone 1.

    ld-check.py tapes/101 tapes/9 tapes/203
"""
import struct
import sys

ZONE = 8256             # 64 bytes of service words, 1024 words of data
W48 = (1 << 48) - 1


def loader(path):
    d = open(path, 'rb').read()
    o = 4 * ZONE + 64               # 4 blocks before zone 0
    w = struct.unpack('<2048Q', d[o:o + 8192] + d[o + ZONE:o + ZONE + 8192])
    return [x & W48 for x in w[:1024 + 0o400]]


new = loader(sys.argv[1])
bad = 0
for path in sys.argv[2:]:
    diff = [i for i, (a, b) in enumerate(zip(new, loader(path))) if a != b]
    for i in diff[:10]:
        print('%s: zone %d word %04o differs' % (path, i // 1024, i % 1024))
    print('%s: loader %s' % (path, 'differs' if diff else 'equal'))
    bad |= bool(diff)
sys.exit(bad)
