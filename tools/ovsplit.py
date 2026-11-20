#!/usr/bin/env python3
"""
ovsplit.py - cut a static overlay into modules and common blocks.

Run in the directory of the overlay OV, which holds OV.layout.py, OV.gold.bin
and OV.gold.dis (several overlays of one program share a directory):

    ovsplit.py OV be           write NAME.be (BEMSH) for every module piece
    ovsplit.py OV asm NAME     filter: DTRAN output of NAME (stdin) -> final
                               Madlen text (stdout)
    ovsplit.py OV cmp [-v] [build.lst]
                               after a build: check every module and common
                               block of OV.silver.bin against OV.gold.bin at
                               its intended address, using the load map in the
                               overlay.pl listing (one wrong length does not
                               hide everything after it); -v lists the words
    ovsplit.py OV check        byte comparison of OV.silver.bin with
                               OV.gold.bin (-> OV.cmp.out); prints GOOD when
                               only the 8-word header differs
    ovsplit.py OV map          print the layout table
    ovsplit.py OV modules      file names (without suffix) of the module pieces
    ovsplit.py OV shared       the Madlen files of the S modules

OV.layout.py defines
    BASE, END   address of the overlay header, address after the last word
    LAYOUT      [(address, kind, name)] in address order, covering everything
                after the header:
                  M  a module cut from the disassembly at a call boundary
                  L  a module taken from the permanent library
                  C  a common block (`name:,LC,len`)
                  S  a module that another overlay has too, linked from its
                     file there (SHARE, SAME), or from a copy of that file
                     here or in SPATH (no SHARE: its names, entries and
                     VECTORS/OFFSETS are given here, RENAME and ALIASES)
    LIB         {address: (module name, {offset: entry name})} for L items
    RENAME      {name in the .be: real name}: BEMSH labels are at most 6
                characters without `*`, real names appear only in Madlen
    LOW         load table of the resident monitor (lowmap.txt: name, E for an
                entry, C for a common block, address); numeric addresses of
                its routines and common blocks become names (aliases Raaaaa
                and Kaaaaa in the .be). An operand with an index register, or
                one that follows `мода X`/`мод X`, is an offset and is left
                alone; so is the operand of `уиа`, unless `счи`/`счим` of
                the same register follows within two instructions (an
                address passed to a procedure). An address inside a routine
                past its last name is the routine plus an offset
                (MONITOR*+2). LOW = 'dubna': the resident of the Dubna
                monitor system, from `dubna --help-resident`, up to the BASE
                of the root overlay. LOWSKIP: names to leave
    ERRCALLS    addresses of the error routines: the number that `уиа` loads
                shortly before a call of one of them is an
                error number, not an address, and stays a number
    NUMBERS     addresses of words whose `уиа` loads a number although it
                looks like an address (what the rule above cannot see);
                (address, 'Мr') for the one `уиа` of that register there
    ERRMSG      file of error messages (`code text`, see ftnerr.py): the error
                numbers found by the ERRCALLS and NUMBERS rules get a comment
                with the text in the .asm (the low 12 bits are the code)
    OWNER       {common address: module address}: the module whose `,DATA,`
                section sets the block, when it is not the one before it
    VECTORS     {module address: n} for a module that begins with a vector of
                n one-word jumps: other modules refer to them as `MODULE+k`
                instead of entry names (BEMSH/DTRAN lose entries beyond 19)
    OFFSETS     [module address]: other modules refer to words inside it as
                `MODULE+k`, not by entry names (a module that would have more
                than 19 entries)
    BASES       {module address: register} for a module that keeps its own
                address in a base register: operands indexed by it are
                offsets from the module start and stay numbers; with
                `base:R,X` in NAME.dtr (X: octal offset of the address the
                register holds) DTRAN turns them into local labels, and
                `R,BASE,` is written. An offset that falls outside the module
                stays a number. Pieces that use the base of an earlier piece
                (or hold the data it reaches) are one module (PUTLABEL,
                FUNCREF); a common block it reaches that another module also
                uses becomes data of the module with an entry (D41115)
    SHARE       'dir/OV': the overlay whose Madlen files the S modules are
    SAME        {address here: address there} of the S modules, and of the
                modules and common blocks that correspond to those of SHARE:
                a reference here into an S module gets the name it has
                there (its entry, MODULE+k of VECTORS/OFFSETS), and an
                address that an S module refers to by name becomes an entry
                of that name in the module here; an item may stand for a
                single word there (a variable that lies elsewhere here)
    ALIASES     {address: name}: an entry of that name that S modules use,
                where SAME cannot tell it (a module here of another edition)
    REBASE      {address: new base}: from the instruction at that address
                on (it loads the base register of BASES with the new base) the
                operands indexed by the register are fields of the new base,
                written by name (D37315+k), and the loading becomes
                `R,BASE,name` in the .asm (GLINK: M8 holds GLINK+2, then the
                fields of the statement record D37315)
    ROOT        (sub-overlay only) OV name of the root overlay; addresses in
                the root that the listing shows as numbers become the names of
                its modules, entries and common blocks

Data that more than one module refers to is not left inside a module: it is a
common block, and its non-zero words are set by a `,DATA,` section
(`n,SET,label` / `1,,block+off`) in the module that precedes it (the one the
data belonged to).

The loader places modules and commons in the order of the external table of
the first module, so that module declares every item of LAYOUT in address
order; that pins the layout.

Why .be files. The overlays are built from the Madlen files (*.asm) alone;
the .be files are an intermediate step of `make asm`, not kept in git. The
disassembly of the image (disbesm6) shows absolute addresses: its labels are
addresses, and nothing tells which address fields are relocatable, so a
relocatable Madlen module cannot be written from it directly. Instead:

  1. `ovsplit.py OV be` cuts the listing into the modules of the layout and
     writes each as BEMSH text (the listing is almost BEMSH already), with
     the references between modules, to common blocks and to the resident
     monitor made symbolic (below), and error numbers and offsets from a
     base register left as numbers;
  2. ../tools/debemsh.sh assembles NAME.be with BEMSH under dispak: an
     object module, with its relocation and its table of externals;
  3. DTRAN disassembles that object module into Madlen text, with local
     labels (*NNNNB) where the addresses are relocatable; NAME.dtr steers
     it (base:, log:, iso:, gost:, text:); the words of its log: ranges
     go into the .be as data in step 1 already, whatever the listing
     makes of them (no names of other overlays in them);
  4. ../tools/degak.py and `ovsplit.py OV asm NAME` finish it: the real
     names for the aliases (BEMSH keeps 6 characters), the LC of the common
     blocks, the DATA sections of their contents, the error texts as
     comments.

The .be files are also read back: the entries (`входн`) of the root's .be
files give the names a sub-overlay uses for places in the root, so the root
goes first in `make asm`.

In a .be file a label of another module is `X extrd X`, a label inside
another module becomes its entry (`входн X`), a label inside a common block is
rewritten as `Dccccc+offset`, and the block is declared as an external; the
`asm` filter turns that SUBP into the LC. The listing does not show the filler
`мода 0` (or a zero, `зп`) in the right half of a word after `пвл`, `пб` or
an extracode, and BEMSH does not add one, so it is written out.

Addresses the listing leaves as numbers are named too, so that the Madlen
text links right at other addresses (the Dubna edition in os-dubna, fortran/):
the operand of `мода`/`мод` without an index register that falls inside the
image; such an instruction in the right half after `пб`, which the listing
shows as data; `уиа` of the start of a common block; an indexed reference to
a common block of the root; `уиа` of a code label of the module before a
call of an error routine (a return address, not an error number).
"""
import importlib.util
import os
import re
import subprocess
import sys
import textwrap

M, C, L, S = 'M', 'C', 'L', 'S'
SYM = re.compile(r'\b([GD])([0-7]{5})\b([+-]\d+)?(?![\d\'])')
NUM = re.compile(r"^'([0-7]+)'(\(М\d+\))?$")
ADDR = re.compile(r' ?([0-7]{4,5})[: ]')
DATA_OPS = {'конд', 'конк', 'кк', 'дк', 'пам'}
# the register of these is not an index (link or counter), the address is a target
NOIDX = {'уиа', 'пв', 'пвл', 'пио', 'пино', 'цикл'}
JUMPS = {'пб', 'пв', 'пвл', 'по', 'пе', 'пио', 'пино', 'цикл'}


class Layout:
    def __init__(self, ov, path='.'):
        spec = importlib.util.spec_from_file_location(
            'layout_' + ov, os.path.join(path, ov + '.layout.py'))
        m = importlib.util.module_from_spec(spec)
        sys.dont_write_bytecode = True
        spec.loader.exec_module(m)
        self.ov, self.path = ov, path
        self.BASE, self.END = m.BASE, m.END
        self.STARTS = [a for a, _, _ in m.LAYOUT]
        self.ENDS = self.STARTS[1:] + [m.END]
        self.KIND = {a: k for a, k, _ in m.LAYOUT}
        self.NAME = {a: n for a, _, n in m.LAYOUT}
        self.LIB = getattr(m, 'LIB', {})
        self.RENAME = dict(getattr(m, 'RENAME', {}))
        for a, (n, e) in self.LIB.items():
            self.RENAME['G%05o' % a] = n
            for o, x in e.items():
                self.RENAME['G%05o' % (a + o)] = x
        r = getattr(m, 'ROOT', None)
        self.root = Layout(r, path) if r else None
        sh = getattr(m, 'SHARE', None)      # 'dir/ov': the overlay that has the S modules
        self.share = Layout(os.path.basename(sh), os.path.join(path, os.path.dirname(sh))) \
            if sh else None
        self.same = dict(getattr(m, 'SAME', {}))   # address here -> address there
        self.spath = [os.path.join(path, d) for d in getattr(m, 'SPATH', ())]
        self.forced = {}                    # address here -> the name an S module uses
        if self.share:
            self.share_names()
        for t, n in getattr(m, 'ALIASES', {}).items():
            self.RENAME['G%05o' % t] = n
            self.forced[t] = 'G%05o' % t
        self.errcalls = set(getattr(m, 'ERRCALLS', ())) | (self.root.errcalls if self.root else set())
        self.bases = {a: '%o' % r for a, r in getattr(m, 'BASES', {}).items()}
        self.rebase = dict(getattr(m, 'REBASE', {}))
        self.numbers = set(getattr(m, 'NUMBERS', ()))
        self.vectors = dict(getattr(m, 'VECTORS', {}))
        self.offsets = set(getattr(m, 'OFFSETS', ()))
        self.owner = dict(getattr(m, 'OWNER', {}))
        self.errmsg = dict(self.root.errmsg) if self.root else {}
        if getattr(m, 'ERRMSG', None):
            for l in open(os.path.join(path, m.ERRMSG), encoding='utf-8'):
                self.errmsg[int(l[:4], 8)] = l[5:].strip()
        self.low, self.lowend = {}, {}       # resident monitor: addr -> [(name, kind)]
        if getattr(m, 'LOW', None):
            skip = set(getattr(m, 'LOWSKIP', ()))
            marks = set()
            if m.LOW == 'dubna':             # the resident of the dubna emulator
                lines = []
                for l in subprocess.run(['dubna', '--help-resident'], capture_output=True,
                                        text=True, check=True).stdout.splitlines()[2:]:
                    f = l.split()
                    if len(f) >= 4:
                        k = 'E' if f[2] == '-' else 'C' if f[3] == 'data' else ''
                        lines.append('%s %s %05o' % (f[0], k, int(f[1], 8)))
                lines.append('CBOБOД %05o' % (self.root or self).BASE)
            else:
                lines = open(os.path.join(path, m.LOW), encoding='utf-8')
            for l in lines:
                for x in re.finditer(r'(\S+)\s+(?:([EC])\s+)?([0-7]{5})(?=\s|$)', l):
                    a = int(x.group(3), 8)
                    marks.add(a)
                    if x.group(1) != 'CBOБOД' and x.group(1) not in skip:
                        self.low.setdefault(a, []).append((x.group(1), x.group(2) or 'M'))
            marks = sorted(marks)
            for a in self.low:               # an item ends where the next one starts
                self.lowend[a] = next(b for b in marks if b > a)
            for a, items in self.low.items():
                for n, k in items:
                    self.RENAME[('K' if k == C else 'R') + '%05o' % a] = n

    def inside(self, t):
        """is address t in the image of this overlay?"""
        return self.BASE + 8 <= t < self.END

    def low_commons(self):
        return {'K%05o' % a: self.lowend[a] - a
                for a, items in self.low.items() for n, k in items if k == C}

    def item(self, a):
        p = None
        for s in self.STARTS:
            if s <= a:
                p = s
        return p if a < self.END else None

    def end(self, s):
        return self.ENDS[self.STARTS.index(s)]

    def real(self, n):
        return self.RENAME.get(n, n)

    def fname(self, s):
        return self.real(self.NAME[s]).lower().replace('*', '%')

    def file(self, s):
        """the Madlen file of module s (that of the other overlay for an S module)"""
        if self.KIND[s] == S and self.share:
            sh = self.share
            return os.path.join(sh.path, sh.fname(self.same[s]) + '.asm')
        if self.KIND[s] == S:            # a copy of it, here or in SPATH
            for d in [self.path] + self.spath:
                f = os.path.join(d, self.fname(s) + '.asm')
                if os.path.exists(f):
                    return f
        return self.fname(s) + '.asm'

    def shared_names(self, s):
        """{address there: name} of the entries of S module s, from its file"""
        sh, u = self.share, self.same[s]
        back = {v: k for k, v in sh.RENAME.items()}
        e = {u: sh.real(sh.NAME[u])}
        for l in open(self.file(s), encoding='utf-8'):
            m = re.match(r' (\S+):,ENTRY,', l)
            if m:
                g = re.match(r'[GED]([0-7]{5})$', back.get(m.group(1), m.group(1)))
                if g:
                    e[int(g.group(1), 8)] = m.group(1)
        return e

    def share_names(self):
        """The names of the S modules and of their entries, and the names
        they use for places in the modules here, get aliases Gaaaaa (BEMSH
        keeps 6 characters): RENAME turns them back in the .asm."""
        sh = self.share
        back = {v: k for k, v in sh.RENAME.items()}
        for o in self.STARTS:
            if self.KIND[o] != S:
                continue
            u0 = self.same[o]
            for u, n in self.shared_names(o).items():
                self.RENAME['G%05o' % (o + u - u0)] = n
            for l in open(self.file(o), encoding='utf-8'):
                m = re.match(r' (\S+):,SUBP,', l)
                g = m and re.match(r'[GED]([0-7]{5})$', back.get(m.group(1), m.group(1)))
                if not g:
                    continue
                t = self.here(int(g.group(1), 8))
                if t is not None and self.KIND[self.item(t)] == M:
                    self.RENAME['G%05o' % t] = m.group(1)
                    if t != self.item(t):
                        self.forced[t] = 'G%05o' % t

    def there(self, t):
        """address t here -> (its item there, the address there), by SAME"""
        o = self.item(t)
        if o in self.same:
            return self.same[o], self.same[o] + t - o
        return None, None

    def here(self, u):
        """address u in the other overlay -> address here, by SAME"""
        for a, b in self.same.items():          # an item that stands for that very word
            if b == u and self.share.item(u) != u:
                return a
        o = self.share.item(u)
        for a, b in self.same.items():
            if b == o:
                return a + u - o
        return None

    def commons(self):
        return {self.NAME[a]: self.end(a) - a for a in self.STARTS if self.KIND[a] == C}

    def entry_labels(self):
        """{address: label} of the entries declared in this overlay's .be files."""
        e = {}
        for s in self.STARTS:
            f = os.path.join(self.path, self.fname(s) + '.be')
            if self.KIND[s] != M or not os.path.exists(f):
                continue
            for l in open(f, encoding='utf-8'):
                m = re.match(r'\tвходн\t([GE]([0-7]{5}))$', l)
                if m:
                    e[int(m.group(2), 8)] = m.group(1)
        return e

    def words(self, which):
        d = open(os.path.join(self.path, '%s.%s.bin' % (self.ov, which)), 'rb').read()
        return [int.from_bytes(d[i:i + 6], 'big') for i in range(0, len(d) - 5, 6)]


def make_be(lay, dis):
    STARTS, KIND, NAME, item = lay.STARTS, lay.KIND, lay.NAME, lay.item
    body = {s: [] for s in STARTS if KIND[s] == M}   # -> [(addr, label, op, arg)]
    labels = {}                                      # address -> label in the listing
    halves = {}                                      # address -> instruction lines
    cur = None
    for l in open(dis, encoding='utf-8'):
        f = l.rstrip('\n').split('\t')
        m = ADDR.match(f[0])
        if m:
            cur = int(m.group(1), 8)
        if cur is None or cur < STARTS[0] or 'ФИНИШ' in l:
            continue
        if not m and f[0].strip() == '':
            f = ['', ''] + [x for x in f if x]       # second half of a two-line word
        if len(f) < 3:
            continue
        if f[1]:
            labels[cur] = f[1]
        s = item(cur)
        if KIND[s] != M:
            continue
        code = re.match(r'[ 0-7:]{6}[0-7]{2} [0-7]{2,3} [0-7]{4,5} ', f[0]) is not None
        body[s].append((cur, f[1], f[2], f[3] if len(f) > 3 else ''))
        if code:
            halves[cur] = halves.get(cur, 0) + 1
    g = lay.words('gold')
    for s in body:                       # words that NAME.dtr says are data (log:
        dtr = os.path.join(lay.path, lay.fname(s) + '.dtr')   # octal offsets) stay
        data = set()                     # data, whatever the listing makes of them
        for l in open(dtr) if os.path.exists(dtr) else ():
            if l.startswith('log:'):
                for r in l[4:].strip().split(','):
                    a, _, b = r.partition('-')
                    data.update(range(s + int(a, 8), s + int(b or a, 8) + 1))
        if data:
            body[s] = [t for t in body[s] if t[0] not in data or t[1]]
            body[s] = [(t[0], t[1], 'конд', "в'%016o'" % g[t[0] - lay.BASE])
                       if t[0] in data else t for t in body[s]]
            have = {t[0] for t in body[s]}
            for a in sorted(data - have):
                k = next(i for i, t in enumerate(body[s]) if t[0] > a)
                body[s].insert(k, (a, '', 'конд', "в'%016o'" % g[a - lay.BASE]))
    for s in body:                       # the listing omits the filler `мода 0` in
        lines = []                       # the right half after пвл and extracodes
        for t in body[s]:
            c = re.match(r"в'([0-7]{8})'$", t[3]) if t[2] == 'конк' else None
            if c and lines and lines[-1][0] == t[0] and lines[-1][2] == 'пб':
                v = int(c.group(1), 8)   # a right half after пб that the listing
                o = v >> 15 & 0o37       # shows as data: мода/мод with an address
                if v >> 19 & 1 and v >> 20 == 0 and o in (0o22, 0o23) and \
                        lay.inside(v & 0o77777):
                    t = (t[0], t[1], 'мода' if o == 0o22 else 'мод', 'D%05o' % (v & 0o77777))
            lines.append(t)
            if halves.get(t[0]) == 1 and g[t[0] - lay.BASE] & 0o77777777 == 0o02200000:
                lines.append((t[0], '', 'мода', ''))
            elif halves.get(t[0]) == 1 and g[t[0] - lay.BASE] & 0o77777777 == 0:
                lines.append((t[0], '', 'зп', ''))      # a zero right half
        body[s] = lines
    entries = {s: set() for s in body}
    ext = {s: {} for s in body}                      # label -> external name
    forced = lay.forced                              # address -> alias an S module uses
    for t, x in forced.items():
        entries[item(t)].add((t, x))
    labels.update(forced)
    out = {}
    errs = set()                                     # (file name, error number)
    root = lay.root
    rent = root.entry_labels() if root else {}
    for s in body:
        def fix(m, s=s, op=None, arg=''):
            a = int(m.group(2), 8)       # the label
            sym, off = m.group(1) + m.group(2), m.group(3) or ''
            t = a + int(off or 0)        # the word referred to
            o = item(t)
            if o is None or item(a) is None:
                sys.exit('%s: %s is outside the image' % (NAME[s], m.group(0)))
            if op not in NOIDX and '(' in arg and KIND[o] != C and (o != s or item(a) != s):
                return "'%o'" % t        # an indexed offset that only looks like an address
            if o == s and item(a) == s:
                return (NAME[s] if a == s else forced.get(a, sym)) + off
            if KIND[o] == S:             # a module of the other overlay: its names
                sh, u0 = (lay.share, lay.there(t)[0]) if lay.share else (lay, o)
                if t - o < sh.vectors.get(u0, 0) or u0 in sh.offsets:
                    x, k = 'G%05o' % o, t - o
                else:
                    if 'G%05o' % t not in lay.RENAME:  # as ../ has it: a number
                        print('%s: %s is not an entry of %s, left a number'
                              % (NAME[s], m.group(0), NAME[o]), file=sys.stderr)
                        return "'%o'" % t
                    x, k = 'G%05o' % t, 0
                ext[s][x] = x
                return x + ('+%d' % k if k else '')
            if KIND[o] == L:
                if t != o and t - o not in lay.LIB[o][1]:
                    sys.exit('%s: %s is not an entry of %s' % (NAME[s], m.group(0), lay.LIB[o][0]))
                ext[s]['G%05o' % t] = 1
                return 'G%05o' % t
            if KIND[o] == C:
                ext[s][NAME[o]] = NAME[o]
                return NAME[o] + ('+%d' % (t - o) if t != o else '')
            if t == o and o != s:
                ext[s][NAME[o]] = NAME[o]
                return NAME[o]
            if o == s:                   # own word reached from a foreign label
                if t == s:
                    return NAME[s]
                lab = labels.setdefault(t, 'E%05o' % t)
                return lab
            if t not in labels and op not in NOIDX:
                return "'%o'" % t        # an indexed offset that only looks like an address
            if t - o < lay.vectors.get(o, 0) or o in lay.offsets:
                ext[s][NAME[o]] = NAME[o]            # a word of the entry vector
                return NAME[o] + '+%d' % (t - o)
            lab = labels.setdefault(t, 'E%05o' % t)   # a word inside another module
            entries[o].add((t, lab))
            ext[s][lab] = lab
            return lab

        def rootref(op, arg, s=s):
            """A number that is an address in the root overlay -> its name."""
            m = NUM.match(arg)
            if not m or op in DATA_OPS:
                return arg
            t, idx = int(m.group(1), 8), m.group(2) or ''
            o = root.item(t)
            if o is None or t < root.STARTS[0]:
                return arg
            k = root.KIND[o]
            if idx and op not in NOIDX and k != C:
                return arg               # an indexed offset; into a common block of
            if k == C:                   # the root it is an address all the same
                x = root.NAME[o]
                ext[s][x] = 1
                return x + ('+%d' % (t - o) if t != o else '') + idx
            if k == L and (t == o or t - o in root.LIB[o][1]):
                x = 'G%05o' % t
            elif k == M and t == o:
                x = root.NAME[o]
            elif k == M and t in rent:
                x = rent[t]
            else:
                return arg
            ext[s][x] = 1
            return x + idx

        def errnum(i, s=s):
            """Is a register loaded at line i consumed by a call of an error routine?"""
            b = body[s]
            for _ in range(5):
                i += 1
                if i >= len(b):
                    return False
                o, r = b[i][2], b[i][3]
                m = re.match(r"(?:[GD]([0-7]{5})|'([0-7]+)')(\(М\d+\))?$", r)
                if o in ('пв', 'пвл', 'пб') and m:
                    t = int(m.group(1) or m.group(2), 8)
                    if t in lay.errcalls:
                        return True
                    if o == 'пб' and not m.group(3) and lay.item(t) == s:
                        i = next(k for k, x in enumerate(b) if x[0] == t) - 1
                        continue         # a shared tail: follow the jump
                    return False
                if o in JUMPS:
                    return False
            return False

        def lowref(op, arg, nxt, s=s):
            """A number that is an address in the resident monitor -> its name."""
            m = NUM.match(arg)
            if not m or op in DATA_OPS:
                return arg
            if op == 'уиа' and not any(o in ('счи', 'счим') and '(%s)' % r == m.group(2)
                                       or r == m.group(2) for o, r in nxt):
                return arg               # уиа loads an offset, unless the register is
                                         # then pushed (an address passed to a procedure)
                                         # or used as a pointer: X(Мr) then (Мr)
            t, idx = int(m.group(1), 8), m.group(2) or ''
            if idx and op not in NOIDX:
                return arg
            jump = op in JUMPS
            for n, k in lay.low.get(t, ()):          # exact: a routine or a block
                if (k == C) != jump or len(lay.low[t]) == 1:
                    x = ('K' if k == C else 'R') + '%05o' % t
                    ext[s][x] = 1
                    return x + idx
            for a, items in lay.low.items():         # inside a common block
                for n, k in items:
                    if k == C and a < t < lay.lowend[a] and not jump:
                        ext[s]['K%05o' % a] = 1
                        return 'K%05o+%d' % (a, t - a) + idx
            for a, items in lay.low.items():         # inside a routine: a word
                for n, k in items:                   # after its last entry
                    if k != C and a < t < lay.lowend[a]:
                        ext[s]['R%05o' % a] = 1
                        return 'R%05o+%d' % (a, t - a) + idx
            return arg

        out[s] = []
        mod = False                      # the previous instruction is мода/мод X:
        for i, (a, lab, op, arg) in enumerate(body[s]):   # this address field is then an offset
            nxt = [t[2:] for t in body[s][i + 1:i + 3]]      # the next two instructions
            rb = [t for r, t in lay.rebase.items() if item(r) == s and a >= r]
            if rb and op not in NOIDX | JUMPS | {'слиа'} and \
                    arg.endswith('(М%s)' % lay.bases.get(s)):
                k = SYM.sub(lambda m: "'%o'" % (int(m.group(2), 8) + int(m.group(3) or 0)), arg)
                m = re.match(r"^(?:'([0-7]+)'|(-?\d+))?\(М\d+\)$", k)   # '17' octal, 2 decimal
                t = max(rb) + (int(m.group(1), 8) if m and m.group(1) else
                               int(m.group(2)) if m and m.group(2) else 0)
                o = item(t)
                if m and o is not None and KIND[o] == C:
                    ext[s][NAME[o]] = NAME[o]        # a field of the new base: by name,
                    out[s].append((a, lab, op, NAME[o] + ('+%d' % (t - o) if t != o else '')))
                    mod = False                      # the .asm declares R,BASE, there
                    continue
            g = SYM.match(arg)
            ret = g and item(int(g.group(2), 8)) == s and \
                (labels.get(int(g.group(2), 8)) or '').startswith('G')   # a label of code here
            n = NUM.match(arg)
            if op == 'уиа' and n and n.group(2) and int(n.group(1), 8) > 0o7777 and \
                    KIND.get(int(n.group(1), 8)) == C:   # the address of a common
                arg = 'D%05o' % int(n.group(1), 8) + n.group(2)   # block, as a number
            if (op == 'уиа' and ((errnum(i) and not ret and not (arg.endswith('(М15)') and nxt[:1] and nxt[0][0] == 'пб'))  # уиа X(М15); пб ERR: a return address
                                 or a in lay.numbers or (a, (re.findall(r'\((М\d+)\)$', arg) or [''])[0]) in lay.numbers)) or \
                    (op != 'уиа' and arg.endswith('(М%s)' % lay.bases.get(s))):
                new = SYM.sub(lambda m: "'%o'" % (int(m.group(2), 8) + int(m.group(3) or 0)), arg)
                mod = False              # an error number or an offset from the base
                if op == 'уиа' and NUM.match(new):
                    errs.add((lay.fname(s), int(NUM.match(new).group(1), 8)))
                out[s].append((a, lab, op, new))
                continue
            if op in ('мода', 'мод') and NUM.match(arg) and not NUM.match(arg).group(2) and \
                    not (nxt and nxt[0][0] in NOIDX) and lay.inside(int(NUM.match(arg).group(1), 8)):
                arg = 'D%05o' % int(NUM.match(arg).group(1), 8)   # an address the
                                                                  # listing left a number
            new = SYM.sub(lambda m, op=op, arg=arg: fix(m, op=op, arg=arg), arg)
            if not mod:
                if root:
                    new = rootref(op, new)
                if lay.low:
                    new = lowref(op, new, nxt)
            mod = op in ('мода', 'мод') and arg != ''
            out[s].append((a, lab, op, new))
    with open(lay.ov + '.errnum', 'w') as f:     # for the comments of make_asm
        for n, x in sorted(errs):
            f.write('%s %o\n' % (n, x))
    for s in body:                       # labels may have been added by any module
        lines, seen = [], set()
        for a, lab, op, arg in out[s]:
            if a not in seen:
                lab = '' if a == s else labels.get(a, '')
            seen.add(a)
            lines.append((lab, op, arg))
        lines[0] = (NAME[s],) + lines[0][1:]
        out[s] = lines
    for s in body:
        with open(lay.fname(s) + '.be', 'w', encoding='utf-8') as f:
            f.write('\t'.join(out[s][0]).rstrip() + '\n')
            for a, x in sorted(entries[s]):
                f.write('\tвходн\t%s\n' % x)
            for t in out[s][1:]:
                f.write('\t'.join(t).rstrip() + '\n')
            for x in sorted(ext[s], key=lambda x: (x[1:], x)):
                f.write('%s\textrd\t%s\n' % (x, x))
        print('%-12s %05o-%05o  entries: %s' % (
            lay.fname(s) + '.be', s, lay.end(s) - 1,
            ' '.join(x for _, x in sorted(entries[s])) or '-'))


def data_section(lay, c, n):
    """Madlen DATA lines that set the non-zero words of common c."""
    w = lay.words('gold')[c - lay.BASE:lay.end(c) - lay.BASE]
    runs, i = [], 0
    while i < len(w):
        if not w[i]:
            i += 1
            continue
        j = i
        while j < len(w) and (w[j] or (j + 1 < len(w) and w[j + 1])):
            j += 1                       # a single zero does not end a run
        runs.append((i, j))
        i = j
    consts, sets = [], []
    for k, (i, j) in enumerate(runs):
        lab = 'V%d/%d' % (n, k)
        for x in range(i, j):
            o = '%016o' % w[x]
            consts.append(' %s,OCT,%s' % (lab + ':' if x == i else '',
                                          ' '.join(o[y:y + 4] for y in range(0, 16, 4))))
        sets.append(' %d,SET,%s\n 1,,%s%s' % (j - i, lab, lay.NAME[c], '+%d' % i if i else ''))
    return consts + sets


def make_asm(lay, name):
    STARTS, KIND, NAME = lay.STARTS, lay.KIND, lay.NAME
    s = next(a for a in STARTS if KIND[a] == M and lay.fname(a) == name.lower())
    commons, rename = lay.commons(), dict(lay.RENAME)
    commons.update(lay.low_commons())
    if lay.root:
        commons.update(lay.root.commons())
        rename.update(lay.root.RENAME)
    src = [l.rstrip('\n') for l in sys.stdin]
    head, decl, rest = [], [], []
    for l in src:
        m = re.match(r' (\S+):,SUBP,$', l)
        if m and not rest:
            decl.append(m.group(1))
        elif not decl and not rest and ',NAME,' in l:
            head.append(l)
        else:
            rest.append(l)
    if s == STARTS[0]:
        decl = [NAME[a] for a in STARTS[1:]] + [d for d in decl if d not in NAME.values()]
    # the commons that follow this module are its data
    own, i = [], STARTS.index(s) + 1
    while i < len(STARTS) and KIND[STARTS[i]] == C and STARTS[i] not in lay.owner:
        own.append(STARTS[i])
        i += 1
    own += [c for c, o in sorted(lay.owner.items()) if o == s]
    for c in own:
        if NAME[c] not in decl:
            decl.append(NAME[c])
    data = []
    for n, c in enumerate(own):
        data += data_section(lay, c, n)
    if not rest or rest[-1].strip() != ',END,':
        sys.exit('%s: no END' % name)
    for r, t in lay.rebase.items():
        if lay.item(r) != s:
            continue
        o = lay.item(t)
        x = '%s,VTM,%s' % (int(lay.bases[s], 8), NAME[o] + ('+%d' % (t - o) if t != o else ''))
        k = next((k for k, l in enumerate(rest) if l.endswith(x) and re.match(r' (?:\S+:)?' + re.escape(x) + '$', l)), None)
        if k is None:
            sys.exit('%s: no %s for REBASE' % (name, x))
        rest[k] = rest[k].replace(x, x.replace(',VTM,', ',BASE,'))
    if s in lay.bases and os.path.exists(name.lower() + '.dtr'):
        # an offset from the base that falls outside the module (data of
        # another one, reached through the base register) has no label
        # here: it goes back to a number with the register
        x = next(int(m.group(1), 8) for m in (re.match(r'base:\d+,([0-7]+)', l)
                                                for l in open(name.lower() + '.dtr')) if m)
        defined = set(re.findall(r'\*([0-7]{4})B(?::|\.=)', '\n'.join(rest)))
        for k, l in enumerate(rest):
            m = re.match(r'( (?:\S+:)?),([^,]+),\*([0-7]{4})B$', l)
            if m and m.group(3) not in defined:
                rest[k] = '%s%s,%s,%oB' % (m.group(1), lay.bases[s], m.group(2),
                                          int(m.group(3), 8) - x)
    ren = re.compile(r'(?<![\w/*])(%s)(?![\w/*])' % '|'.join(rename or ['\0']))
    for l in head:
        print(ren.sub(lambda m: rename[m.group(1)], l))
    for d in decl:
        print(' %s:,LC,%d' % (rename.get(d, d), commons[d]) if d in commons
              else ' %s:,SUBP,' % rename.get(d, d))
    try:
        errs = {int(l.split()[1], 8) for l in open(lay.ov + '.errnum')
                if l.split()[0] == name.lower()}
    except OSError:
        errs = set()
    for l in rest[:-1]:
        m = re.match(r' (?:\S+:)?\d+,VTM,([0-7]+)B$', l)
        if m and int(m.group(1), 8) in errs and int(m.group(1), 8) & 0o7777 in lay.errmsg:
            n = int(m.group(1), 8)       # an error number: its message as a comment
            t = re.sub(r' {3,}\S{1,2}$', '', lay.errmsg[n & 0o7777])   # a stray letter
            for k, t in enumerate(textwrap.wrap(' '.join(t.split()), 60)):
                print('C %s %s' % (' ' * len('%o:' % n) if k else '%o:' % n, t))
        print(ren.sub(lambda m: rename[m.group(1)], l))
    if data:
        print(' ,DATA,')
        for l in data:
            print(l)
    print(' ,END,')


def compare(lay, lst, verbose):
    g, s, base = lay.words('gold'), lay.words('silver'), lay.BASE
    want = {lay.real(lay.NAME[a]): a for a in lay.STARTS}
    got = {}
    for l in open(lst, encoding='utf-8', errors='replace'):
        for m in re.finditer(r'(\S+)\s+(?:C\s+)?([0-7]{5})(?=\s|$)', l):
            if m.group(1) in want:
                got.setdefault(m.group(1), int(m.group(2), 8))
    ok = True
    for n, a in sorted(want.items(), key=lambda t: t[1]):
        if n not in got:
            print('%-9s missing from the load map' % n)
            ok = False
            continue
        bad = [i for i in range(lay.end(a) - a) if not 0 <= got[n] - base + i < len(s)
               or s[got[n] - base + i] != g[a - base + i]]
        if bad or got[n] != a:
            ok = False
            print('%-9s want %05o got %05o (%+d)  %s' % (
                n, a, got[n], got[n] - a,
                'first diff +%o (%05o), %d words' % (bad[0], a + bad[0], len(bad))
                if bad else 'same words'))
            if verbose:
                for i in bad[:16]:
                    x = s[got[n] - base + i] if 0 <= got[n] - base + i < len(s) else 0
                    print('   +%04o %05o gold %016o silver %016o' % (i, a + i, g[a - base + i], x))
    print('all %d items in place and equal' % len(want) if ok else 'DIFFERENT')
    return ok


def check(lay):
    g = open(lay.ov + '.gold.bin', 'rb').read()
    try:
        s = open(lay.ov + '.silver.bin', 'rb').read()
    except OSError:
        s = b''
    diff = [i for i in range(max(len(g), len(s)))
            if i >= len(g) or i >= len(s) or g[i] != s[i]]
    with open(lay.ov + '.cmp.out', 'w') as f:
        for i in diff:
            f.write('%d %o %o\n' % (i + 1, g[i] if i < len(g) else 0, s[i] if i < len(s) else 0))
    if not s:
        print('%s: \033[1;31mBAD (build failed)\033[22;39m' % lay.ov)
    elif diff and diff[-1] >= 48:
        print('%s: \033[1;31mBAD (%d bytes differ)\033[22;39m' % (lay.ov, len(diff)))
    else:
        print('%s: \033[1;32mGOOD (%d bytes differ in the header)\033[22;39m' % (lay.ov, len(diff)))
        return True
    return False


def main():
    a = sys.argv[1:]
    if len(a) < 2 or not os.path.exists(a[0] + '.layout.py'):
        sys.exit(__doc__)
    lay = Layout(a[0])
    a = a[1:]
    if a[0] == 'be':
        make_be(lay, a[1] if len(a) > 1 else lay.ov + '.gold.dis')
    elif a[0] == 'asm' and len(a) > 1:
        make_asm(lay, a[1])
    elif a[0] == 'cmp':
        r = [x for x in a[1:] if x != '-v']
        sys.exit(0 if compare(lay, r[0] if r else 'build.lst', '-v' in a) else 1)
    elif a[0] == 'check':
        sys.exit(0 if check(lay) else 1)
    elif a[0] == 'map':
        for s in lay.STARTS:
            print(' %05o  %05o  %6o  %s  %s' % (s, lay.end(s) - 1, lay.end(s) - s,
                                                 lay.KIND[s], lay.real(lay.NAME[s])))
    elif a[0] == 'modules':
        print(' '.join(lay.fname(s) for s in lay.STARTS if lay.KIND[s] == M))
    elif a[0] == 'shared':
        print(' '.join(lay.file(s) for s in lay.STARTS if lay.KIND[s] == S))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
