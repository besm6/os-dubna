#!/usr/bin/env python3
"""Put the rebuilt libraries 21, 22, 23 (tapes 251-253, mk-libs.sh) into
an image of 9/MONSYS at their old zones, the zones that the library table
of the monitor (zone 6) gives.

    lib-splice.py image...      tapes/203, data/mons9.bin

A tape has 4 blocks before zone 0, the disk file none.  Each library must
fit its area; the rest of the area keeps what it had.
"""
import os
import sys

ZONE = 8256
TAPES = os.environ.get('TAPES', 'tapes')
AREA = {'251': (0o240, 0o60), '252': (0o172, 0o46), '253': (0o320, 0o60)}

for path in sys.argv[1:]:
    d = bytearray(open(path, 'rb').read())
    skip = len(d) % (ZONE * 32)
    for t, (base, room) in AREA.items():
        lib = open(os.path.join(TAPES, t), 'rb').read()[4 * ZONE:]
        n = len(lib) // ZONE
        if n > room:
            sys.exit('%s: library of tape %s takes %o zones, room for %o'
                     % (path, t, n, room))
        o = skip + base * ZONE
        d[o:o + n * ZONE] = lib[:n * ZONE]
    open(path, 'wb').write(d)
