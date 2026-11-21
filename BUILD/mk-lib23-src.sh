#! /bin/sh
# Compile library 23 (besml23/: the sources, Fortran first, then the
# modules disassembled by DTRAN, dtran/*.asm) under dubna onto tape 223.
# Units that are not in library 23 are left out.
. ./env.sh
S=`mktemp` || exit 1
trap "rm -f -- '$S'" EXIT
./unitcut.py BACKWR EXCLNAME 'GOST*ISO' 'ISO*GOST' TEROUT TBUFF FELIS RPWORD TEACH SERVER -- \
    ../besml23/lib23[fitv].l23 > $S
run_src_job 223 lib23-base-src.list $S ../besml23/dtran/*.asm <<'EOF2'
*name LIB23
*edit
*r:50000
*w:66100
*ee
*ftn
*read:66100
*to perso:66000,77
*end file
EOF2
