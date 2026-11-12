#! /bin/sh
# Compile the Monitor System (besmmons/) under dubna onto tape 200.
# Not used by the bootstrap: MS comes from 9/MONSYS.
. ./env.sh
run_src_job 200 ms-base-src.list ../besmmons/system*.txt <<'EOF'
*name MS-2017
*edit
*r:50000
*w:66100
*ee
*ftn
*read:66100
*to perso:66000,77
*end file
EOF
