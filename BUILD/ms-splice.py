#!/usr/bin/env python3
"""Splice the rebuilt MS into a copy of the archived 9/MONSYS.

    ms-splice.py new old template out [loader]

new      - working copy of drums 21/22 made by COLLECT and COMTODRU (tape)
old      - archived 9/MONSYS (tape)
template - image to patch: a tape, or the disk file data/mons9.d9
out      - result: template with zones 0-77 replaced
loader   - tape made by mk-ld-img.sh: the dynamic loader, zone 0 (LOADER)
           and words 0-377 of zone 1 (REDUOL) go to the same places

The static part has the sections of the old catalog in its order, each
from the new image if COLLECT did relink it (now all of them: INPUTCAL,
FORTRAN with its phases, ASEMBLER, ALGOL with A/PRINTM, WRITLIB*), else
from the old one.  As COMTODRU does, it ends with zone 77 and the monitor
page is in the zone before it; the static catalog and word 1377 of zone 1
are made anew.  All the rest of zones 0-77 is new.
"""
import struct
import sys

ZONE = 8256             # 64 bytes of service words, 1024 words of data
NZ = 64                 # MS: drums 21 and 22
REC = 32                # words in a record
CAT = 0o1400            # static catalog in zone 1
MONPAGE = 0o1377        # zone 1: exchange word of the monitor page
W48 = (1 << 48) - 1     # a word; the tag of dubna lies above it


def load(path):
    d = open(path, 'rb').read()
    skip = len(d) % (ZONE * 32)         # a tape has 4 blocks before zone 0
    w = []
    for z in range(NZ):
        o = skip + z * ZONE + 64
        w += struct.unpack('<1024Q', d[o:o + 8192])
    return bytearray(d), skip, w


def pos(w):
    """Record number of a section, from drum 21 zone 0."""
    return ((w >> 30) & 0o77777) - (0o21 << 10)


def catalog(img):
    """Static catalog: [name, word], the root first."""
    c = []
    i = 1024 + CAT
    while img[i] & W48:
        c.append((img[i], img[i + 1]))
        i += 2
    return c, pos(img[i + 1])


def sections(img):
    """name -> (first record, number of records)."""
    c, end = catalog(img)
    starts = sorted(pos(w) for n, w in c[1:]) + [end]
    return {n: (pos(w), starts[starts.index(pos(w)) + 1] - pos(w))
            for n, w in c[1:]}


def decode(w):
    """A name in the TEXT code as a string."""
    return ''.join(chr(((w >> (42 - 6 * k)) & 0o77) + 0o40) for k in range(8)).strip()


def main():
    new_path, old_path, tmpl_path, out_path = sys.argv[1:5]
    _, _, new = load(new_path)
    _, _, old = load(old_path)
    out, skip, _ = load(tmpl_path)

    old_cat, _ = catalog(old)
    new_cat, _ = catalog(new)
    old_sec = sections(old)
    new_sec = sections(new)
    for name in new_sec:
        if name not in old_sec:
            sys.exit('ms-splice: %s is not in the old catalog' % decode(name))

    # Sections in the old order, each from the new image if COLLECT linked
    # it: (name, catalog word, image, first record, records).
    secs = []
    for name, _ in old_cat[1:]:
        src, cat, sec = (new, new_cat, new_sec) if name in new_sec else \
                        (old, old_cat, old_sec)
        secs.append((name, dict(cat)[name], src) + sec[name])

    # As COMTODRU: the static part ends with zone 77, the monitor page is
    # in the zone before it.
    start = NZ * 32 - sum(s[4] for s in secs)
    page = start // 32 - 1
    new_page = (new[1024 + MONPAGE] & 0o77) + \
        (((new[1024 + MONPAGE] >> 12) & 0o77) - 0o21) * 32

    # End of the dynamic part: word 0 of its catalog, zone 7.
    free = new[7 * 1024]
    dyn_end = ((free >> 10) & 0o37) * 1024 + (free & 0o1777)
    if dyn_end > page * 1024:
        sys.exit('ms-splice: the dynamic part is too long: %o words' % dyn_end)

    img = list(new)
    for i in range(dyn_end, NZ * 1024):
        img[i] = 0
    img[page * 1024:(page + 1) * 1024] = new[new_page * 1024:(new_page + 1) * 1024]

    # Zone 1: the catalog.  The root has the gap between the dynamic and
    # the static parts, a section its place, both in records; a zero name
    # and the place after zone 77 end it.
    place = ~(0o77777 << 30)
    i = 1024 + CAT
    gap = start - (dyn_end + REC - 1) // REC
    img[i] = old[i]
    img[i + 1] = (old[i + 1] & place) | (gap << 30)
    p = start
    for name, w, src, q, n in secs:
        img[p * REC:(p + n) * REC] = src[q * REC:(q + n) * REC]
        i += 2
        img[i] = name
        img[i + 1] = (w & place) | (((0o21 << 10) + p) << 30)
        p += n
    j = i + 2
    img[j] = old[j]
    img[j + 1] = (old[j + 1] & place) | (((0o21 << 10) + p) << 30)
    w = old[1024 + MONPAGE] & ~0o7777
    img[1024 + MONPAGE] = w | ((0o21 + page // 32) << 12) | (page % 32)

    if len(sys.argv) > 5:
        ld = open(sys.argv[5], 'rb').read()
        o = 4 * ZONE + 64               # dubna's tape: 4 blocks before zone 0
        ld = struct.unpack('<2048Q', ld[o:o + 8192] + ld[o + ZONE:o + ZONE + 8192])
        img[0:1024] = ld[0:1024]
        img[1024:1024 + 0o400] = ld[1024:1024 + 0o400]

    for z in range(NZ):
        o = skip + z * ZONE + 64
        out[o:o + 8192] = struct.pack('<1024Q', *img[z * 1024:(z + 1) * 1024])
    open(out_path, 'wb').write(out)


main()
