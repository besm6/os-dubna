#! /bin/sh
# Compile library 23 (besml23/) under dubna onto tape 223.
# Not used by the bootstrap.
. ./env.sh
run_src_job 223 lib23-base-src.list ../besml23/[ld]*.l23 <<'EOF'
*name LIB23-STAGE
*edit
*r:50000
*w:66100
*ee
*madlen(L=FBGR)
*read:66100
*to perso:66000,77
*end file
EOF
