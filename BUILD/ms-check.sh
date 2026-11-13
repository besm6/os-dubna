#! /bin/sh
# Compare the rebuilt MS perso (tape 200) with the permanent library of
# the archived 9/MONSYS: module names and sizes.
. ./env.sh
J=`mktemp` || exit 1
trap "rm -f -- '$J'" EXIT
cat > $J <<'EOF'
*name MS-CAT
*tape:200/ms,66
*perso:66000
*catalog
*end file
EOF
run_job $J ms-cat.list
python3 - ms-cat.list <<'EOF'
import re, sys
lines = open(sys.argv[1], encoding='utf-8').read().split('\n')
k = [i for i, l in enumerate(lines) if 'PERMANENT LIBRARY' in l][0]
pat = re.compile(r'(\S{1,8})\s+\d\d \d\d \d\d  (\d{5})')
new = dict(pat.findall('\n'.join(lines[:k])))
old = dict(pat.findall('\n'.join(lines[k:])))
new.pop('TCATALOG', None)       # loaded by *catalog itself
print('%d modules in 9/MONSYS, %d on tape 200' % (len(old), len(new)))
for n in sorted(set(old) | set(new)):
    if old.get(n) != new.get(n):
        print('%-8s  9/MONSYS %s  tape 200 %s' % (n, old.get(n, '-'), new.get(n, '-')))
EOF
