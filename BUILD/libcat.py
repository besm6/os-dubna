#!/usr/bin/env python3
"""Read a library (ОБСП, plain or packed by CRELIB) on a tape image.

    libcat.py TAPE ZONE                list modules and entries
    libcat.py -n TAPE ZONE             module names only, one per line
    libcat.py -x TAPE ZONE NAME        module words in octal
    libcat.py -e TAPE ZONE NAME ENTRY ADDR
                                       add an entry (ADDR octal) to module
                                       NAME of a plain library (perso)
    libcat.py cmp TAPE ZONE TAPE ZONE [NAME...]
                                       compare two libraries: names, entries,
                                       lengths; the NAMEs may differ

ZONE is octal (9/MONSYS: 172 library 22, 240 library 21, 320 library 23).
Catalog: word 0 characteristic, word 1 zero, then pairs name (TEXT) and
location: record in bits 46-42, zone in bits 41-31 (drum 21 from zone 0,
so 01040 is the first zone of the library), length in bits 30-16; an entry
has bits 48-16 zero and its address in bits 15-1.
"""
import struct
import sys

ZONE = 8256
W48 = (1 << 48) - 1
TEXT = " .БЦДФГИ()*ЙЛЯЖ/0123456789Ь,П-+ЫЗABCDEFGHIJKLMNOPQRSTUVWXYZШЭЩЧЮ"


def text(w):
    return ''.join(TEXT[(w >> (42 - 6 * k)) & 0o77] for k in range(8)).rstrip()


class Library:
    def __init__(self, path, zone):
        self.data = open(path, 'rb').read()
        self.skip = 4 * ZONE                # 4 blocks before zone 0
        self.base = zone
        self.modules = []           # [name, zone, record, length, [(entry, addr)]]
        w = self.words(zone, 8 * 1024)
        self.head = w[0]
        i = 2
        while w[i] and w[i] != W48:
            name, loc = text(w[i]), w[i + 1]
            if loc >> 15:
                self.modules.append([name, ((loc >> 30) & 0o3777) - 0o1040,
                                     (loc >> 41) & 0o37, (loc >> 15) & 0o77777, []])
            else:
                self.modules[-1][4].append((name, loc & 0o77777))
            i += 2

    def words(self, zone, n):
        w = []
        z = zone
        while len(w) < n:
            o = self.skip + z * ZONE + 64
            if o + 8192 > len(self.data):
                break
            w += [x & W48 for x in struct.unpack('<1024Q', self.data[o:o + 8192])]
            z += 1
        return w[:n]

    def body(self, m):
        """The standard array: 3 words of structure, commands, constants,
        data, its scatter list, header, designations, long names, debug."""
        _, z, r, n, _ = m
        w = self.words(self.base + z, r * 32 + 3)[r * 32:]
        n = 3 + sum(size(w))
        return self.words(self.base + z, r * 32 + n)[r * 32:]

    def get(self, name):
        for m in self.modules:
            if m[0] == name:
                return m
        return None


def size(s):
    """Parts of a standard array from its 3 structure words:
    commands, constants, data, scatter, header, designations, long, debug."""
    return [s[2] & 0o77777, s[2] >> 30, (s[1] >> 15) & 0o77777, s[1] & 0o77777,
            s[0] & 0o7777, (s[0] >> 12) & 0o7777, s[1] >> 30, s[0] >> 36]


def listing(lib):
    print('word 0 %016o, %d modules, %d entries' % (
        lib.head, len(lib.modules), sum(len(m[4]) for m in lib.modules)))
    for name, z, r, n, ent in lib.modules:
        print('%-8s zone %03o rec %02o len %05o' % (name, lib.base + z, r, n))
        for e, a in ent:
            print('  (%s) %05o' % (e, a))


def entry(path, zone, name, ent, addr):
    """Insert the catalog pair of an entry after the entries of a module."""
    d = bytearray(open(path, 'rb').read())
    o = 4 * ZONE + zone * ZONE
    pos = lambda i: o + (i // 1024) * ZONE + 64 + (i % 1024) * 8
    get = lambda i: struct.unpack('<Q', d[pos(i):pos(i) + 8])[0]
    w = [get(i) for i in range(8 * 1024)]
    i, at = 2, None
    while w[i] & W48 and w[i] & W48 != W48:
        if at is None and text(w[i]) == name:
            at = i + 2
            while w[at + 1] & W48 and not (w[at + 1] & W48) >> 15:
                at += 2
        i += 2
    end = i + 2                         # the end mark is two words
    if at is None or end + 2 > 8 * 1024:
        sys.exit('no module %s or no room' % name)
    t = w[at] & ~W48                    # tag of dubna
    v = 0
    for k, c in enumerate(ent.ljust(8)):
        v |= TEXT.index(c) << (42 - 6 * k)
    w[at:at] = [t | v, t | int(addr, 8)]
    for i in range(at, end + 2):
        d[pos(i):pos(i) + 8] = struct.pack('<Q', w[i])
    open(path, 'wb').write(d)


def compare(a, b, allow=()):
    """Every module of a must be in b with the same length (in memory) and
    entries; modules named in allow may differ.  Words may differ: modules
    rebuilt from disassembly are equivalent, not equal."""
    bad, same = 0, 0
    names = {m[0] for m in a.modules}
    for m in a.modules:
        n = b.get(m[0])
        what = None
        if not n:
            what = 'missing'
        elif sorted(m[4]) != sorted(n[4]):
            what = 'entries %s / %s' % (sorted(m[4]), sorted(n[4]))
        elif m[3] != n[3]:
            what = 'length %05o / %05o' % (m[3], n[3])
        elif a.body(m) == b.body(n):
            same += 1
        if what:
            print('%-8s %s%s' % (m[0], what, ' (allowed)' if m[0] in allow else ''))
            bad |= m[0] not in allow
    for m in b.modules:
        if m[0] not in names:
            print('%-8s extra' % m[0])
            bad = 1
    print('%d modules, %d of the same words, %s' % (
        len(a.modules), same, 'BAD' if bad else 'GOOD'))
    return bad


def main(a):
    if a[0] == 'cmp':
        sys.exit(compare(Library(a[1], int(a[2], 8)), Library(a[3], int(a[4], 8)),
                         a[5:]))
    if a[0] == '-n':
        for m in Library(a[1], int(a[2], 8)).modules:
            print(m[0])
    elif a[0] == '-e':
        entry(a[1], int(a[2], 8), *a[3:6])
    elif a[0] == '-x':
        lib = Library(a[1], int(a[2], 8))
        for i, w in enumerate(lib.body(lib.get(a[3]))):
            print('%05o %016o' % (i, w))
    else:
        listing(Library(a[0], int(a[1], 8)))


if __name__ == '__main__':
    main(sys.argv[1:])
