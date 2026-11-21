#! /bin/sh
# Compare the rebuilt libraries 21, 22, 23 with the archived ones on
# 9/MONSYS (libcat.py cmp): every module and entry, the same lengths.
# Without arguments the libraries in tape 203, with -p those of mk-libs.sh
# (tapes 251-253).  *DRIVER* and W1LOOK are built from older sources than
# the archived ones.
. ./env.sh
lib() {
    if [ "$1" = -p ]; then echo $TAPES/25$3 0; else echo $TAPES/203 $2; fi
}
./libcat.py cmp $TAPES/9 240 `lib "$1" 240 1` '*DRIVER*' &&
./libcat.py cmp $TAPES/9 172 `lib "$1" 172 2` &&
./libcat.py cmp $TAPES/9 320 `lib "$1" 320 3` W1LOOK
