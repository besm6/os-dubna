#!/usr/bin/env python3
"""findsame.py - find the same code in two images, at different addresses.

    findsame.py [-n MIN] A.bin BASE_A B.bin BASE_B...

Images are unpacked overlays (6-byte big-endian words, as ovl2bin writes
them; BASE: octal address of the first word). Prints the runs of at least
MIN words (default 8) of A that are equal to a run of B moved by a constant
shift: a word matches if it is equal, or if each half differs from the other
only by the shift in its address field (15 bits of a long instruction, 12
bits of a short one). So a module linked into both images at different
places shows up as one run: `A-from A-to len  B-from B-to  file`. A run
inside the 8-word headers is not reported.
"""
import sys

ADDR = ((1 << 19) & 0, 0)


def load(path):
    d = open(path, 'rb').read()
    return [int.from_bytes(d[i:i + 6], 'big') for i in range(0, len(d) - 5, 6)]


def half_ok(x, y, shift):
    if x == y:
        return True
    if (x ^ y) >> 15 == 0 and x >> 19 & 1:            # long: 15-bit address
        return (x - y) & 0o77777 == shift & 0o77777
    if (x ^ y) >> 12 == 0 and not x >> 19 & 1:         # short: 12-bit offset
        return (x - y) & 0o7777 == shift & 0o7777
    return False


def same(x, y, shift):
    return x == y or (half_ok(x >> 24, y >> 24, shift) and
                      half_ok(x & 0o77777777, y & 0o77777777, shift))


def main():
    args = sys.argv[1:]
    mn = 8
    if args[:1] == ['-n']:
        mn = int(args[1])
        args = args[2:]
    if len(args) < 4 or len(args) % 2:
        sys.exit(__doc__)
    a, base_a = load(args[0]), int(args[1], 8)
    for path, bb in zip(args[2::2], args[3::2]):
        b, base_b = load(path), int(bb, 8)
        where = {}
        for j, y in enumerate(b[8:], 8):
            if y:
                where.setdefault(y, []).append(j)
        done = set()
        runs = []
        for i, x in enumerate(a[8:], 8):
            for j in where.get(x, ())[:20]:
                shift = (base_a + i) - (base_b + j)
                if (i - j) in done and any(s <= i <= e and t == i - j
                                           for s, e, t in runs):
                    continue
                s, t = i, j
                while s > 8 and t > 8 and same(a[s - 1], b[t - 1], shift):
                    s, t = s - 1, t - 1
                e, f = i, j
                while e + 1 < len(a) and f + 1 < len(b) and \
                        same(a[e + 1], b[f + 1], shift):
                    e, f = e + 1, f + 1
                if e - s + 1 >= mn:
                    runs.append((s, e, i - j))
                    done.add(i - j)
        seen = set()
        for s, e, d in sorted(runs):
            if (s, e, d) in seen:
                continue
            seen.add((s, e, d))
            print('%05o-%05o %5o  %05o-%05o  %s' % (
                base_a + s, base_a + e, e - s + 1,
                base_b + s - d, base_b + e - d, path))


main()
