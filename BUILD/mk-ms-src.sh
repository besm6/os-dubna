#! /bin/sh
# Compile the Monitor System (besmmons/) under dubna: sources to tape 200
# from zone 100, perso to zones 0-77.
. ./env.sh
run_src_job 200 ms-base-src.list ../besmmons/system*.txt <<'EOF'
*name MS-2017
*edit
*r:50000
*w:66100
*ee
*ftn
*read:66100
*     the compiler is not a part of MS
*exclude:MADLENI*,*PUNCHER,/MACPAR/,BUFPER,DISCRIPT,GSTEXT*,INITLIB,
 QRESET,STOLIB,WTOLIB,MADLEN*3,MDL*REF,MDL*6T8S,MDL*6T8W,MDLCARD*,
 FOMA***,PRINT8**,SAVE*,TEXISO
*to perso:66000,77
*end file
EOF
