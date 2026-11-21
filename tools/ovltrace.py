#!/usr/bin/env python3
"""ovltrace.py - the code of an overlay that a dubna trace executed.

    ovltrace.py OV.gold.bin BASE trace... >> OV.sym

A trace of `dubna -d i --trace=FILE` holds every instruction of the job:
the monitor, other overlays loaded at the same address, the user program.
Only the lines `AAAAA L: ...` / `AAAAA R: ...` whose address lies in the
image (BASE octal: address of its first word) and whose instruction is the
half word of the image there count, so the rest cannot mark data of the
overlay as code. The words executed are written as symbol table lines of
disbesm6, `from-to C -`, one per run of consecutive words.
"""
import re
import sys

LINE = re.compile(r'^([0-7]{5}) ([LR]): ([0-7]{2}) ([0-7]{2,3}) ([0-7]{4,5})')


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    d = open(sys.argv[1], 'rb').read()
    base = int(sys.argv[2], 8)
    img = [int.from_bytes(d[i:i + 6], 'big') for i in range(0, len(d) - 5, 6)]
    seen = set()
    for path in sys.argv[3:]:
        for line in open(path, errors='replace'):
            m = LINE.match(line)
            if not m:
                continue
            a = int(m.group(1), 8)
            if not base <= a < base + len(img) or (a, m.group(2)) in seen:
                continue
            reg, op, addr = m.group(3), m.group(4), m.group(5)
            if len(op) == 2:            # format 2: 4+1+4 bits of M, opcode
                h = int(reg, 8) << 20 | int(op, 8) << 15 | int(addr, 8)
            else:
                h = int(reg, 8) << 20 | int(op, 8) << 12 | int(addr, 8)
            w = img[a - base]
            if h == (w >> 24 if m.group(2) == 'L' else w & 0o77777777):
                seen.add((a, m.group(2)))
    words = sorted({a for a, h in seen})
    i = 0
    while i < len(words):
        j = i
        while j + 1 < len(words) and words[j + 1] == words[j] + 1:
            j += 1
        print('%05o-%05o C -' % (words[i], words[j]))
        i = j + 1


main()
