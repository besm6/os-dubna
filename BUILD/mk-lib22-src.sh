#! /bin/sh
# Compile library 22 (the Madlen assembler, besmtask/madlen.txt, and the
# modules disassembled by DTRAN, besml22/dtran/*.asm) under dubna onto
# tape 222.
. ./env.sh
run_src_job 222 lib22-base-src.list ../besmtask/madlen.txt ../besml22/dtran/*.asm <<'EOF2'
*name LIB22
*edit
*r:50000
*w:66100
*ee
*madlen
*read:66100
*to perso:66000,77
*end file
EOF2
