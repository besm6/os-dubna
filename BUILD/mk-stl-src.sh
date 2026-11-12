#! /bin/sh
# Compile the standard tasks (besmtask/task*) under dubna onto tape 247.
# The sources begin with *FOREX: the compiler of Monitor Dubna.
. ./env.sh
run_src_job 247 stl-base-src.list ../besmtask/task??.ts[12] <<'EOF'
*name STL-2017
*edit
*r:50000
*w:66100
*d.*forex
*ee
*forex
*read:66100
*to perso:66000,77
*end file
EOF
