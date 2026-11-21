#!/usr/bin/env python3
"""Disassemble with DTRAN the modules of library 21, 22 or 23 that have no
source, into Madlen files ../besml2N/dtran/*.asm.

    dtran.py LIB [NAME...]      LIB is 21, 22 or 23; by default all the
                                modules without source

Each module is disassembled from a copy of the archived library (tape 9),
assembled again and checked: equal (the same words) or equivalent (DTRAN
of the new object gives the same text; compilers order the table of
designations in ways Madlen does not).  Text constants with characters the
editor loses, and words that differ, are given to DTRAN as OCT directives,
listed in NAME.dtr next to NAME.asm.  The listings go to dtran-LIB.list.
Run from BUILD/; needs dubna, besmtool and ../tools/cosy2txt.
"""
import difflib
import glob
import os
import re
import struct
import subprocess
import sys
import tempfile

import libcat

ZONE = 8256
LIBS = {'21': (0o240, 0o60, '../besml21/*.l21'),
        '22': (0o172, 0o46, '../besmtask/madlen.txt'),
        '23': (0o320, 0o60, '../besml23/*.l23')}
TAPES = os.environ.get('TAPES', os.path.abspath('tapes'))
COSY2TXT = os.path.abspath('../tools/cosy2txt')
PLAIN = 950             # + LIB % 10: plain copy of the library
TEXT, OBJ = 960, 961    # DTRAN text, perso of the assembled text
# modules with a source that does not compile (*FTN, *FOREX, *FORTRAN)
UNUSED = {'23': ['SERVER']}
LOOK = str.maketrans('АВЕКМНОРСТХУаеорсху', 'ABEKMHOPCTXYAEOPCXY')


def norm(s):
    return s.translate(LOOK).replace(' ', '').upper()


def sources(files):
    """Names of the modules defined in the source files."""
    out = set()
    for f in files:
        for line in open(f, encoding='utf-8', errors='replace'):
            if line[:1] in 'CcСс*':
                continue
            t = line.translate(LOOK)
            m = re.match(r'^\s*([^:,.]{1,12}?)\s*:\s*,\s*NAME\s*,', t, re.I)
            if m:
                out.add(norm(m.group(1)))
                continue
            m = re.match(r'^\s{6,}(?:[A-Z*0-9 ]*\s)?(SUBROUTINE|FUNCTION|PROGRAM|'
                         r'BLOCK ?DATA)\s*([^\s(]+)', t.upper())
            if m:
                out.add(norm(m.group(2)))
    return out


def fname(name):
    return name.lower().replace('*', '%').replace('/', '-')


def plain(lib):
    """Copy the library to a tape of its own, as a plain (unpacked) ОБСП:
    DTRAN reads only those."""
    base, n, _ = LIBS[lib]
    d = open(os.path.join(TAPES, '9'), 'rb').read()
    o = 4 * ZONE + base * ZONE
    w = bytearray(d[o:o + n * ZONE])
    w0 = struct.unpack('<Q', w[64:72])[0] & ~(0o17777 << 24)
    w[64:72] = struct.pack('<Q', w0)
    t = PLAIN + int(lib) % 10
    open(os.path.join(TAPES, str(t)), 'wb').write(d[:4 * ZONE] + w)
    return t


def run(job, files={}):
    with tempfile.TemporaryDirectory() as d:
        for k, v in files.items():
            open(os.path.join(d, k), 'w', encoding='utf-8').write(v)
        open(os.path.join(d, 'job.dub'), 'w', encoding='utf-8').write(job)
        r = subprocess.run(['dubna', 'job.dub'], cwd=d, capture_output=True,
                           text=True, env=dict(os.environ, BESM6_PATH=TAPES +
                                               ':/usr/local/share/besm6'))
        return r.stdout + r.stderr


def fresh(t):
    open(os.path.join(TAPES, str(t)), 'wb').close()


def ranges(a):
    out = []
    for x in sorted(set(a)):
        if out and out[-1][1] == x - 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def dtran(tape, name, octs, size=None):
    """DTRAN of the module on the tape (unit 32 from zone 0); size: memory
    length, commands and constants, to mend the BSS lines."""
    fresh(TEXT)
    d = ''
    if octs:
        d = 'OCT:%s\nEND:%s\n' % (','.join(
            '%o-%o' % (a, b) if a != b else '%o' % a for a, b in ranges(octs)), name)
    lst = run('*name dtran\n*tape:%d/dt,67,w\n*tape:%d/lib,32\n*library:23\n'
              '*call dtran:320000(%s)\n%s*edit\n*r:1\n*w:67\n*ee\n*end file\n'
              % (TEXT, tape, name, d))
    if 'IS ABSENT' in lst or 'HE ГAPAHTИPYET' in lst:
        return None
    dump = subprocess.run('besmtool dump %d --length=64 --to-file=/dev/stdout | %s'
                          % (TEXT, COSY2TXT), shell=True, capture_output=True,
                          env=dict(os.environ, BESM6_PATH=TAPES),
                          text=True).stdout
    lines = [l.rstrip() for l in dump.split('\n') if l.strip()]
    text = far('\n'.join(lines) + '\n')
    return bss(text, *size) if size else text


def sizes(lib, m):
    s = libcat.size(lib.body(m)[:3])
    return m[3], s[0], s[1]


def bss(text, length, ncmd, nconst):
    """DTRAN may put an unnamed BSS word into the count of the next label
    (*0132B:,BSS,2 then *0133B:): make the counts agree with the labels."""
    lines = text.split('\n')
    k = [i for i, l in enumerate(lines) if op(l) == 'BSS']
    if not k:
        n = length - ncmd - nconst
        if n > 0:
            i = next(i for i, l in enumerate(lines) if op(l) in ('DATA', 'END'))
            lines.insert(i, ' ,BSS,%d' % n)
        return '\n'.join(lines)
    labels = [re.match(r'^\s*\*([0-7]+)B:', lines[i]) for i in k]
    if not all(labels):
        return text
    at = [int(m.group(1), 8) for m in labels] + [length]
    if at[0] < ncmd + nconst:
        return text
    out, addr = [], ncmd + nconst
    for j, i in enumerate(k):
        if at[j] > addr:
            out.append((i, ' ,BSS,%d' % (at[j] - addr)))
        lines[i] = ' *%04oB:,BSS,%d' % (at[j], at[j + 1] - at[j])
        addr = at[j + 1]
    for i, l in reversed(out):
        lines.insert(i, l)
    return '\n'.join(lines)


DECL = ('NAME', 'SUBP', 'LC', 'EQU', 'ENTRY', 'BLOCK', 'CONT')
DATA = ('ISO', 'GOST', 'TEXT', 'OCT', 'LOG', 'INT', 'REAL')


def op(line):
    f = line.split(',')
    return f[1].strip() if len(f) > 2 else ''


def far(text):
    """DTRAN writes an address beyond the module as *NNNNN, which Madlen
    does not know: make it *0000B+NNNNNB, with the label at address 0."""
    if not re.search(r'\*\d{5,}(?![\dB])', text):
        return text
    text = re.sub(r'\*(\d{5,})(?![\dB])', r'*0000B+\1B', text)
    if re.search(r'^\s*\*0000B:', text, re.M):
        return text
    lines = text.split('\n')
    for i, l in enumerate(lines[1:], 1):
        if op(l) not in DECL:
            lines[i] = ' *0000B:' + l.lstrip().lstrip(':')
            break
    return '\n'.join(lines)


def normal(text):
    """Lines of a DTRAN text with the equivalences put in and without
    comments, and the address of each line in the code."""
    t = subprocess.run([sys.executable, '../tools/degak.py', '-o'], input=text,
                       capture_output=True, text=True).stdout
    out, addr, h = [], [], 0
    for l in t.split('\n'):
        if l[:1] in 'CС':
            continue
        o = op(l)
        if o not in DATA:
            l = l.split('.')[0].rstrip() if o != 'NAME' else l
        out.append(canon(l, o))
        a = None
        if o in DECL or h is None:
            pass
        elif o == 'BSS':
            h = None
        elif o in DATA:
            h += h % 2
            a = h // 2
            m = re.match(r'(\d+)H', l.split(',', 2)[2])
            n = int(m.group(1)) if m and o in ('ISO', 'GOST', 'TEXT') else 1
            h += 2 * (-(-n // (8 if o == 'TEXT' else 6)) if m else 1)
        elif o or l.strip():
            if ':' in l.split(',')[0]:
                h += h % 2
            a = h // 2
            h += 1
        addr.append(a)
    # names DTRAN makes up (GAK/5), numbered in order of appearance
    seen = {}
    out = [re.sub(r'(?<![\w*/])GA[A-Z]/\d+(?![\w*/])',
                  lambda m: seen.setdefault(m.group(0), 'G#%d' % len(seen)), l)
           for l in out]
    # join consecutive strings of one code, padded to their length
    i = 0
    while i + 1 < len(out):
        m1 = re.match(r' ,(ISO|GOST|TEXT),(\d+)H(.*)$', out[i])
        m2 = re.match(r' ,(ISO|GOST|TEXT),(\d+)H(.*)$', out[i + 1])
        if m1 and m2 and m1.group(1) == m2.group(1):
            a = m1.group(3).ljust(int(m1.group(2)))
            b = m2.group(3).ljust(int(m2.group(2)))
            out[i] = ' ,%s,%dH%s' % (m1.group(1), len(a + b), (a + b).rstrip())
            del out[i + 1], addr[i + 1]
        else:
            i += 1
    for i, l in enumerate(out):
        m1 = re.match(r' ,(ISO|GOST|TEXT),(\d+)H(.*)$', l)
        if m1:
            out[i] = ' ,%s,%sH%s' % (m1.group(1), m1.group(2), m1.group(3).rstrip())
    # merge runs of BSS
    i = 0
    while i + 1 < len(out):
        m1, m2 = re.match(r' ,BSS,(\d*)$', out[i]), re.match(r' ,BSS,(\d*)$', out[i + 1])
        if m1 and m2:
            out[i] = ' ,BSS,%d' % (int(m1.group(1) or 1) + int(m2.group(1) or 1))
            del out[i + 1], addr[i + 1]
        else:
            i += 1
    return out, addr


SHORT = ['ATX', 'STX', 'MOD', 'XTS', 'A+X', 'A-X', 'X-A', 'AMX', 'XTA', 'AAX',
         'AEX', 'ARX', 'AVX', 'AOX', 'A/X', 'A*X', 'APX', 'AUX', 'ACX', 'ANX',
         'E+X', 'E-X', 'ASX', 'XTR', 'RTE', 'YTA', '032', '033', 'E+N', 'E-N',
         'ASN', 'NTR', 'ATI', 'STI', 'ITA', 'ITS', 'MTJ', 'J+M']


def canon(l, o):
    """A line in the form that does not depend on how it was written:
    no labels *NNNNB:, *NNNNB+d computed, a short command with a number
    as its code and a 15-bit address (1xx is xx from address 70000B)."""
    l = re.sub(r'^(\s*)(?:[*/][0-7]{4}B)?:', r'\1', l)
    l = re.sub(r'/([0-7]{4}B)', r'*\1', l)
    l = re.sub(r'\+0(?![\dB])', '', l)
    l = re.sub(r'\*([0-7]{4})B([+-]\d+)(?![\dB])',
               lambda m: '*%04oB' % (int(m.group(1), 8) + int(m.group(2))), l)
    f = l.split(',')
    if len(f) != 3:
        return l
    if o in SHORT:
        c = SHORT.index(o)
    elif re.fullmatch(r'\*[5-7][0-7]', o):
        c = int(o[1:], 8)
    elif re.fullmatch(r'[01][0-7][0-7]', o):
        c = int(o, 8)
    else:
        return l
    a = f[2].strip()
    if re.fullmatch(r'[0-7]+B', a):
        v = int(a[:-1], 8)
    elif re.fullmatch(r'-?\d+', a):
        v = int(a)
    elif not a:
        v = 0
    else:
        return l
    if c >= 0o100:
        c, v = c - 0o100, v + 0o70000
    return '%s,%03o,%oB' % (f[0], c, v & 0o77777)


CONST = re.compile(r'^\s*(?:\*([0-7]+)B)?:?,(ISO|GOST|TEXT|OCT|LOG|INT|REAL|BSS),(.*)$')


def strings(text, ncmd, nconst):
    """Addresses to give as OCT: text constants that lost characters on the
    way through the editor (control characters), and words of the code or
    constants that DTRAN took for BSS."""
    out, addr = [], None
    for line in text.split('\n')[1:]:
        b = re.match(r'^\s*\*([0-7]+)B:,BSS,(\d*)', line)
        if b and int(b.group(1), 8) < ncmd + nconst:
            a = int(b.group(1), 8)
            out += range(a, min(a + int(b.group(2) or 1), ncmd + nconst))
        m = CONST.match(line)
        if not m:
            addr = None
            continue
        if m.group(1):
            addr = int(m.group(1), 8)
        elif addr is None:
            addr = ncmd                 # the constants follow the commands
        op, arg = m.group(2), m.group(3)
        if op == 'BSS':
            break
        n = 1
        h = re.match(r'(\d+)H(.*)$', arg)
        if op in ('ISO', 'GOST', 'TEXT') and h:
            k = int(h.group(1))
            n = -(-k // (8 if op == 'TEXT' else 6))
            if len(h.group(2)) != k:
                out += range(addr, addr + n)
        addr += n
    return out


def assemble(texts):
    """Assemble the texts, return the library of perso and the listing."""
    fresh(OBJ)
    lst = run('*name dtasm\n*disc:1/local\n*file:src,50\n*tape:%d/obj,66,w\n'
              '*edit\n*r:50000\n*w:66100\n*ee\n*madlen\n*read:66100\n'
              '*to perso:66000,77\n*end file\n' % OBJ, {'src.txt': ''.join(texts)})
    return libcat.Library(os.path.join(TAPES, str(OBJ)), 0), lst


def own(m):
    """Entries of a module that Madlen can make: not beyond its end (the
    library tools put others into a catalog, as PAIB of LIBSUB)."""
    return [e for e in m[4] if e[1] < m[3]]


def compare(x, y):
    """equal, or the addresses of differing constant words (all words of
    code and constants if the tables of designations agree)."""
    if x == y:
        return 'equal'
    if len(x) < 3 or len(y) < 3:
        return []
    sx, sy = libcat.size(x[:3]), libcat.size(y[:3])
    lo = 0 if sx[5:] == sy[5:] else sx[0]
    hi = sx[0] + sx[1]
    return [i - 3 for i in range(3 + lo, 3 + hi) if i < len(y) and x[i] != y[i]]


def main(lib, names):
    base, _, src = LIBS[lib]
    arch = libcat.Library(os.path.join(TAPES, '9'), base)
    if not names:
        have = sources(glob.glob(src))
        names = [m[0] for m in arch.modules
                 if norm(m[0]) not in have or m[0] in UNUSED.get(lib, [])]
    if len({fname(n) for n in names}) != len(names):
        sys.exit('file names collide')
    out = '../besml%s/dtran' % lib
    os.makedirs(out, exist_ok=True)
    tape = plain(lib)
    octs = {}
    todo, res, logs = list(names), {}, []
    for rnd in range(4):
        texts = {}
        for n in todo:
            t = dtran(tape, n, octs.get(n), sizes(arch, arch.get(n)))
            if t is None:
                res[n] = 'DTRAN failed'
                continue
            s = strings(t, *libcat.size(arch.body(arch.get(n))[:3])[:2])
            if not set(s) <= set(octs.get(n, [])):
                octs[n] = sorted(set(octs.get(n, [])) | set(s))
                t = dtran(tape, n, octs[n], sizes(arch, arch.get(n)))
            texts[n] = t
        again = []
        part = [n for n in todo if n in texts]
        for k in range(0, len(part), 40):
            new, lst = assemble(texts[n] for n in part[k:k + 40])
            logs.append(lst)
            for n in part[k:k + 40]:
                m, a = new.get(n), arch.get(n)
                if not m:
                    res[n] = 'not assembled'
                    continue
                if m[3] != a[3] or sorted(m[4]) != sorted(own(a)):
                    res[n] = 'length or entries differ'
                    continue
                r = compare(arch.body(a), new.body(m))
                if r == 'equal':
                    res[n] = r
                    continue
                x, ax = normal(texts[n])
                y, _ = normal(dtran(OBJ, n, octs.get(n), sizes(new, m)) or '')
                if x == y:
                    res[n] = 'equivalent'
                    continue
                for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
                        None, x, y, autojunk=False).get_opcodes():
                    if tag != 'equal':
                        r += [a for a in ax[i1:max(i2, i1 + 1)] if a is not None]
                if r and not set(r) <= set(octs.get(n, [])):
                    octs[n] = sorted(set(octs.get(n, [])) | set(r))
                    again.append(n)
                    res[n] = 'differ'
                else:
                    res[n] = 'differ'
        for n in texts:
            open(os.path.join(out, fname(n) + '.asm'), 'w',
                 encoding='utf-8').write(texts[n])
            f = os.path.join(out, fname(n) + '.dtr')
            if octs.get(n):
                open(f, 'w').write(' '.join('%o' % a for a in octs[n]) + '\n')
            elif os.path.exists(f):
                os.remove(f)
        print('round %d: %d modules, %d to redo' % (rnd, len(todo), len(again)))
        todo = again
        if not todo:
            break
    open('dtran-%s.list' % lib, 'w').write(''.join(logs))
    count = {}
    for n in names:
        count[res[n]] = count.get(res[n], 0) + 1
        if res[n] not in ('equal', 'equivalent'):
            print('%-8s %s' % (n, res[n]))
    print(', '.join('%d %s' % (v, k) for k, v in sorted(count.items())))
    return 0 if set(count) <= {'equal', 'equivalent'} else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2:]))
