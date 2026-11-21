#! /bin/sh
# Compile library 21 (besml21/: the sources, then the modules disassembled
# by DTRAN, dtran/*.asm) under dubna onto tape 221.  The sources begin with
# Fortran and switch to Madlen with a card of their own.  Units that are
# not in library 21 are left out.
. ./env.sh
S=`mktemp` || exit 1
trap "rm -f -- '$S'" EXIT
./unitcut.py '*GOST*' '*MISTAKE' 'TAPENAM*' -- ../besml21/libra21[123].l21 > $S
run_src_job 221 lib21-base-src.list $S ../besml21/dtran/*.asm <<'EOF'
*name LIB21
*edit
*r:50000
*w:66100
*ee
*ftn
*read:66100
*to perso:66000,77
*end file
EOF
