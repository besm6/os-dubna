#!/usr/bin/env python3
"""codesym.py - guess the code that a disassembly still shows as data.

    codesym.py [-t] OV.gold.bin BASE OV.gold.dis [OV.sym] >> OV.sym

disbesm6 follows the flow from the entry and the code marks of the symbol
table; code reached only through a stored return address or a table stays
`конд`. A run of such words that follows code (or a `пам`) and decodes as
instructions up to an unconditional jump (`пб`, `пб (Мr)`) is printed as a
line `from-to C -`; with -t only if its first word is the target of a jump
or call or the operand of `уиа` (a return address). The lines `from-to D -`
of OV.sym (data that looks like code: tables) are left alone. Run it again with a fresh listing until it prints
nothing, then read the result: a table of jumps or of instructions (code
templates) is data that only looks like code.

A word is an instruction if both halves are: no privileged or illegal
opcode (Format 1: 002 032 033 046 047; Format 2: 032 033), and a jump or
call (Format 2: 26 27 30 31 34 35 37) with no index register goes to
code, into the run itself or out of the image (the monitor): a template
of object code that a compiler keeps (`сч 4444; пв 4114(М15)`) calls
places in its tables, which hold no code. The address 4444 is taken as the
mark of such a template (the placeholder of ALGOL-ГДР) and is data too.
"""
import re
import sys

BAD1 = {0o002, 0o032, 0o033, 0o046, 0o047}


def halfok(h):
    if h >> 19 & 1:                     # format 2
        op = h >> 15 & 0o37
        return op != 0o32 and op != 0o33 and h & 0o77777 != 0o4444
    op = (h >> 12 & 0o77) | (h >> 18 & 1) << 6
    return (op & 0o77) not in BAD1 and h & 0o7777 != 0o4444


JUMPS = {0o26, 0o27, 0o30, 0o31, 0o34, 0o35, 0o37}


def target_ok(h, kind, base, n, run):
    """a jump with no index register must go to code (or out of the image)"""
    if not h >> 19 & 1 or h >> 15 & 0o37 not in JUMPS:
        return True
    op, reg, t = h >> 15 & 0o37, h >> 20, h & 0o77777
    if reg and op in (0o26, 0o27, 0o30):    # U-relative: target unknown
        return True
    if not base + 8 <= t < base + n:
        return True
    return kind.get(t) == 'c' or t in run


def jump(h):
    """unconditional jump: пб (Format 2, opcode 30)"""
    return h >> 19 & 1 and h >> 15 & 0o37 == 0o30


def main():
    args = sys.argv[1:]
    strict = args[:1] == ['-t']
    if strict:
        args = args[1:]
    if len(args) not in (3, 4):
        sys.exit(__doc__)
    d = open(args[0], 'rb').read()
    base = int(args[1], 8)
    data = set()
    for l in open(args[3]) if len(args) == 4 else ():
        x = re.match(r'([0-7]+)(?:-([0-7]+))? D\b', l)
        if x:
            data.update(range(int(x.group(1), 8), int(x.group(2) or x.group(1), 8) + 1))
    w = [int.from_bytes(d[i:i + 6], 'big') for i in range(0, len(d) - 5, 6)]
    kind, targets = {}, set()
    for l in open(args[2], encoding='utf-8', errors='replace'):
        x = re.search(r'\t(пб|пвл?|по|пе|пино|пио|цикл|уиа)\t[GD]([0-7]{5})(?:\+(\d+))?', l)
        if x:
            targets.add(int(x.group(2), 8) + int(x.group(3) or 0))
        m = re.match(r'^ ?([0-7]{4,5})[ :]', l)
        if not m:
            continue
        a = int(m.group(1), 8)
        if 'конд' in l or 'конк' in l:
            kind[a] = 'd'
        elif '\tпам\t' in l:
            n = int(l.split('пам')[1].split()[0])
            for k in range(n):
                kind[a + k] = '0'
        else:
            kind[a] = 'c'
    a = base + 8
    while a < base + len(w):
        if kind.get(a) == 'd' and kind.get(a - 1) in ('c', '0') and \
                (a in targets or not strict) and a not in data:
            b = a
            run = set()
            while kind.get(b) == 'd':
                run.add(b)
                b += 1
            b = a
            while kind.get(b) == 'd' and b not in data:
                x = w[b - base]
                if not (halfok(x >> 24) and halfok(x & 0o77777777)) or x == 0 or \
                        not all(target_ok(h, kind, base, len(w), run)
                                for h in (x >> 24, x & 0o77777777)):
                    break
                if jump(x >> 24) or jump(x & 0o77777777):
                    print('%05o-%05o C -' % (a, b))
                    break
                b += 1
            a = b + 1
        else:
            a += 1


main()
