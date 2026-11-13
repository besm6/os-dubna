#!/usr/bin/env python3
"""Splice the rebuilt MS into a copy of the archived 9/MONSYS.

    ms-splice.py new old template out

new      - working copy of drums 21/22 made by COLLECT and COMTODRU (tape)
old      - archived 9/MONSYS (tape)
template - image to patch: a tape, or the disk file data/mons9.d9
out      - result: template with zones 0-77 replaced

The compilers exist only as linked static sections of the old image, so
COLLECT cannot rebuild them.  The result has the old static part at its
old place; sections that COLLECT did relink (INPUTCAL) replace the old
ones when they take the same room.  All the rest of zones 0-77 is new.
"""
import struct
import sys

ZONE = 8256             # 64 bytes of service words, 1024 words of data
NZ = 64                 # MS: drums 21 and 22
REC = 32                # words in a record
CAT = 0o1400            # static catalog in zone 1
MONPAGE = 0o1377        # zone 1: exchange word of the monitor page


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
    while img[i] & 0xFFFFFFFFFFFF:
        c.append((img[i], img[i + 1]))
        i += 2
    return c, pos(img[i + 1])


def sections(img):
    """name -> (first record, number of records)."""
    c, end = catalog(img)
    starts = sorted(pos(w) for n, w in c[1:]) + [end]
    return {n: (pos(w), starts[starts.index(pos(w)) + 1] - pos(w))
            for n, w in c[1:]}


def main():
    new_path, old_path, tmpl_path, out_path = sys.argv[1:]
    _, _, new = load(new_path)
    _, _, old = load(old_path)
    out, skip, _ = load(tmpl_path)

    old_cat, _ = catalog(old)
    old_sec = sections(old)
    new_sec = sections(new)
    start = min(p for p, n in old_sec.values())
    page = old[1024 + MONPAGE] & 0o77
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
    img[start * REC:] = old[start * REC:]
    for name, (p, n) in old_sec.items():
        if name in new_sec and new_sec[name][1] == n:
            q = new_sec[name][0]
            img[p * REC:(p + n) * REC] = new[q * REC:(q + n) * REC]

    # Zone 1: the old catalog and monitor page; the root keeps the gap
    # between the dynamic and the static parts, in records.
    i = 1024 + CAT
    j = i + 2 * len(old_cat) + 2
    img[i:j] = old[i:j]
    gap = start - (dyn_end + REC - 1) // REC
    img[i + 1] = (old[i + 1] & ~(0o77777 << 30)) | (gap << 30)
    img[1024 + MONPAGE] = old[1024 + MONPAGE]

    for z in range(NZ):
        o = skip + z * ZONE + 64
        out[o:o + 8192] = struct.pack('<1024Q', *img[z * 1024:(z + 1) * 1024])
    open(out_path, 'wb').write(out)


main()
