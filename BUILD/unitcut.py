#!/usr/bin/env python3
"""Copy Madlen source files to stdout without the named units.

    unitcut.py NAME... -- file...

A Madlen unit runs from its `NAME:,NAME,` line to the next `,END,`, a
Fortran one from SUBROUTINE (FUNCTION, PROGRAM) NAME to END.  Spaces in
labels are ignored, as Madlen does.  Used instead of *EXCLUDE, which also
throws out the module EXCLUDE that the source of library 21 makes.
"""
import re
import sys

k = sys.argv.index('--')
names = {n.replace(' ', '') for n in sys.argv[1:k]}
cut = False
for f in sys.argv[k + 1:]:
    for line in open(f, encoding='utf-8'):
        if not cut and line[:1] not in 'CcСс*':
            m = re.match(r'^\s*([^:,]+?)\s*:\s*,\s*NAME\s*,', line)
            g = re.match(r'^ {6,}(?:[A-Z]+\s+)*(?:SUBROUTINE|FUNCTION|PROGRAM)'
                         r'\s+([^\s(]+)', line)
            n = m or g
            cut = bool(n) and n.group(1).replace(' ', '') in names
            end = r'^\s*,\s*END\s*,' if m else r'^ {6,}END\s*$'
        if not cut:
            sys.stdout.write(line)
        elif re.match(end, line):
            cut = False
