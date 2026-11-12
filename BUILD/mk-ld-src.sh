#! /bin/sh
# Compile the loader (besmtask/loader.txt) under dubna onto tape 100.
. ./env.sh
run_src_job 100 ld-base-src.list ../besmtask/loader.txt <<'EOF'
*name LD-2017
*edit
*r:50000
*w:66100
*n:loa 0001
*ee
*madlen(L=FBGR)
*read:66100
*to perso:66000,77
*end file
EOF
