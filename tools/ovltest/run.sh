#!/bin/sh
# run.sh - what *CALL OVERLAY / COLLECT do with modules of the same name in
# sibling overlays, as GLINK (under FORTRAN) and ASEMBLER share ASMSTMT,
# ASMINIT and the entries G44243, D44561 in different editions.
#
#     cd tools/ovltest && ./run.sh        (needs dubna; output in out/)
#
# Overlays A and B load side by side under a root and each calls SUB (or G).
# Edition 1 of SUB (sub1.asm) is 2 words with 1111..., edition 2 (sub2.asm)
# 3 words with 2222...; the words of each image show which one it got.
#   1. both editions in the deck: the later replaces the earlier, A and B
#      both get edition 2, no message;
#   2. SUB in libraries, edition 1 on unit 41, edition 2 on unit 42, cards
#      A:41, B:42: A takes SUB from 41 into the temporary library, and B gets
#      it from there; library 42 is never looked at, no message;
#   3. modules SUBA (unit 41) and SUBB (unit 42) both have an entry G;
#      A calls SUBA, B calls SUBB and G: B gets SUBB and also SUBA, and its
#      call of G goes to the G of SUBA;
#   4. as 2 with B first in the scheme: both get edition 2 from 42; the
#      overlay linked first decides for all.
# The cards NAME:n work only under the root MONITOR* (LOAD, besml21/
# libra211.l21: the library list of a section of level 2 is taken only when
# the head of the scheme is MONITOR*); under /MONTRAN they are ignored, and
# A gets "OTCYTCTBYET SUB". So the root here is a stub MONITOR* (monitor.asm),
# which is not written into the catalog.
cd `dirname $0` || exit 1
make -s -C .. ovl2bin || exit 1
mkdir -p out && cd out || exit 1
BESM6_PATH=$PWD:${BESM6_PATH:-/usr/local/share/besm6}
export BESM6_PATH

# perso of units 41, 42 on tapes 741-744: lib tape unit file.asm
lib() {
    : > $1
    { echo "*name lib$2"; echo "*tape:$1/lib$2,$2,w"; echo "*no list"
      echo "*madlen"; cat ../$3; echo "*to perso:${2}0000"; echo "*end file"
    } > lib$1.dub
    dubna lib$1.dub > lib$1.lst
}

# link: case tapes files... -- scheme lines...
link() {
    _c=$1 _t1=$2 _t2=$3
    shift 3
    { echo "*name ovltest"; echo "*disc:1/local"
      test $_t1 = - || echo "*tape:$_t1/lib41,41"
      test $_t2 = - || echo "*tape:$_t2/lib42,42"
      echo "*file:ovl$_c,60,w"; echo "*no list"; echo "*madlen"
      while [ "$1" != -- ]; do cat ../$1; shift; done
      shift
      echo "*call overlay:600000"
      for l; do echo " $l"; done
      echo "*end record"; echo "*call ocatalog:600000"; echo "*end file"
    } > case$_c.dub
    head -c $((6144 * 8)) /dev/zero > ovl$_c.bin
    dubna case$_c.dub > case$_c.lst
    echo "=== case $_c"
    grep -v '^ *$' case$_c.lst | sed -n '/^\*END RECORD/,/ДЛИHA/p' |
        grep -v '^\*END RECORD\|ДЛИHA\|^≠\|/MONTRAN\|TR\*CALL\|RM/\|READ\* '
    # the images of A, B, from the catalog at the end (zone, record); the
    # first 8 words are the header
    for o in A B; do
        set -- `awk -v o=$o '$1 == o && $2 == 60 { print $3, $4 }' case$_c.lst`
        dd bs=192 skip=$((0$1 * 32 + 0$2)) status=none < ovl$_c.bin | ../../ovl2bin |
        od -An -v -tx1 | tr -s ' \n' '  ' | sed 's/^ //' | awk -v o=$o '{
            s = o ":"
            for (i = 49; i + 5 <= NF; i += 6) {
                w = 0; for (j = 0; j < 6; j++) w = w * 256 + strtonum("0x" $(i+j))
                s = s sprintf(" %016o", w) }
            print s }'
    done
}

lib 741 41 sub1.asm
lib 742 42 sub2.asm
lib 743 41 suba.asm
lib 744 42 subb.asm
link 1 - - a.asm sub1.asm b.asm sub2.asm -- '/montran(a,b)'
link 2 741 742 monitor.asm a.asm b.asm -- 'monitor*(a,b)' a:41 b:42
link 3 743 744 monitor.asm ga.asm gb.asm -- 'monitor*(a,b)' a:41 b:42
link 4 741 742 monitor.asm a.asm b.asm -- 'monitor*(b,a)' a:41 b:42
