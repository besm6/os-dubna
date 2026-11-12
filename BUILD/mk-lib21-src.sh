#! /bin/sh
# Compile library 21 (besml21/) under dubna onto tape 221.
# Not used by the bootstrap.
. ./env.sh
run_src_job 221 lib21-base-src.list ../besml21/libra21[123].l21 <<'EOF'
*name LIB21-STAGE
*edit
*r:50000
*w:66100
*ee
*madlen(l=fbgr)
*read:66100
*to perso:66000,77
*end file
EOF
