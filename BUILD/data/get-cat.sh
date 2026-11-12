#! /bin/sh
. ../env.sh
set -x 
# retrieve disk catalog from the disk image
dd if=$TAPES/3000 bs=8256 skip=996 count=4 | od -c 
