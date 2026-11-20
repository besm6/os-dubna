#!/usr/bin/env python3
"""Splice the rebuilt MS into a copy of the archived 9/MONSYS.

    ms-splice.py new old template out [NAME=image.bin ...]

new      - working copy of drums 21/22 made by COLLECT and COMTODRU (tape)
old      - archived 9/MONSYS (tape)
template - image to patch: a tape, or the disk file data/mons9.d9
out      - result: template with zones 0-77 replaced
NAME=image.bin - a static section rebuilt elsewhere (../fortran, ../asembler:
           FORTRAN=../fortran/fortran.silver.bin): its image as loaded, 6-byte
           big-endian words, header included

The compilers have no perso, so COLLECT cannot link them.  The result has
the old static part at its old place; sections that COLLECT did relink
(INPUTCAL) replace the old ones when they take the same room.  A section
given as NAME=image.bin replaces the old one too: it keeps the old header
(8 words: places on the drums, right for the old place) and the old piece
of TRP, and must have the old length and fit into the old records (the
catalog stays the old one).  An image equal to the old keeps the old bytes;
another one is packed anew.  All the rest of zones 0-77 is new.
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


def text(name):
    """A name in the TEXT code: 8 characters of 6 bits, ASCII - 040."""
    w = 0
    for k, c in enumerate(name.ljust(8)[:8]):
        w |= (ord(c) - 0o40) << (42 - 6 * k)
    return w


def unpack(img, i, length):
    """The packed section at word i: (image, words of the packed groups)."""
    out, j = [], i
    while True:
        h = img[j] & W48
        j += 1
        m, n = (h >> 15) & 0o77777, h & 0o77777
        if m == 0 and n == 0:
            break
        rep = 0
        if h >> 47 and m:
            rep = img[j] & W48
            j += 1
        out += [x & W48 for x in img[j:j + n]]
        j += n
        out += [rep] * m
    if len(out) != length:
        sys.exit('ms-splice: a packed section of %o words, not %o' % (len(out), length))
    return out, j - i


def pack(words):
    """Groups of literal words, each followed by a run of one repeated word:
    of 2 zeros or more, of 3 other words or more (as the original packer)."""
    def run(j):
        return j + 1 < n and words[j] == words[j + 1] and \
            (not words[j] or j + 2 < n and words[j] == words[j + 2])
    out, i, n = [], 0, len(words)
    while i < n:
        j = i                            # literals up to the next run
        while j < n and not run(j):
            j += 1
        k = j
        while k < n and words[k] == words[j]:
            k += 1
        lit, m = words[i:j], k - j
        while len(lit) > 0o77777:
            out += [0o77777] + lit[:0o77777]
            lit = lit[0o77777:]
        rep = words[j] if m else 0
        while m > 0o77777:
            out += ([1 << 47 | 0o77777 << 15, rep] if rep else [0o77777 << 15])
            m -= 0o77777
        out += [(1 << 47 if rep and m else 0) | m << 15 | len(lit)]
        if rep and m:
            out.append(rep)
        out += lit
        i = k
    return out + [0]


def rebuilt(old, cat, name, path):
    """The section NAME packed from the image in path, at its old place."""
    word = next((w for n, w in cat if n & W48 == text(name)), None)
    if word is None:
        sys.exit('ms-splice: no section %s' % name)
    p, length = pos(word), (word >> 15) & 0o77777
    secs = sections(old)
    n = secs[next(k for k in secs if k & W48 == text(name))][1]
    image, used = unpack(old, p * REC, length)
    d = open(path, 'rb').read()
    new = [int.from_bytes(d[i:i + 6], 'big') for i in range(0, len(d) - 5, 6)]
    if len(new) != length:
        sys.exit('ms-splice: %s is %o words, the catalog says %o' % (path, len(new), length))
    new[:8] = image[:8]
    if new == image:
        return p, old[p * REC:(p + n) * REC]
    trp = old[p * REC + used:(p + n) * REC]         # the piece of TRP, if any
    while trp and not trp[-1] & W48:
        trp.pop()
    words = pack(new) + trp + ([0] if trp else [])  # it ends with a zero word
    if len(words) > n * REC:
        sys.exit('ms-splice: %s does not fit into its %d records' % (name, n))
    return p, words + [0] * (n * REC - len(words))


def main():
    new_path, old_path, tmpl_path, out_path = sys.argv[1:5]
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
    for arg in sys.argv[5:]:
        name, path = arg.split('=', 1)
        p, words = rebuilt(old, old_cat, name, path)
        img[p * REC:p * REC + len(words)] = words

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
