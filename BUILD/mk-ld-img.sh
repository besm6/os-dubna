#! /bin/sh
# Make the memory image of the dynamic loader from its source on tape 100
# (mk-ld-src.sh), as ../besmtask/loadload.txt did: the editor cuts the source
# into the resident part LOADER and the non-resident part REDUOL, both are
# loaded at 66000 and their pages saved on math drum 25 (zones 35, 36).
# PHYSWR wrote them to physical drum 21; here LDWRITE puts them into zones 0
# and 1 of tape 101 instead, for ms-splice.py.  LDSHIFT, NEWLDR, NEWLDRS are
# taken from loadload.txt as they are.  The line numbers of the cuts are
# those of this source, not of loadload.txt.
. ./env.sh
rm -f $TAPES/101
: > $TAPES/101
J=`mktemp` || exit 1
trap "rm -f -- '$J'" EXIT

# Job 1: the editions and the helpers into perso on tape 101 from zone 100.
{ cat <<'EOF'
*name LD-PERSO
*tape:100/src,66
*tape:101/ldimg,65,w
*file:scratch,67,w
*edit
*r:66100
*w:67000
*d:loa 0001
 LOADER:,NAME,
*d:loa 0084,376
*r:66100
*d:loa 0377,728
 INCRAP:,BSS,
 LOADQUE:,BSS,
 READWP1:,BSS,
 WRITWP1:,BSS,
 BEGLOAD:,BSS,
 NZERO:,BSS,
 MNENT:,BSS,
 LOAD:,BSS,
*ee
*madlen
*read:67000
EOF
  sed -n '/^ LDSHIFT:,NAME,/,/^\*     PHYSWR/p' ../besmtask/loadload.txt | sed '$d'
  cat <<'EOF'
 LDWRITE:,NAME,
 ,*70,=0010 0400 0025 0035
 ,*70,=0000 0400 0065 0000
 ,*70,=0010 0400 0025 0036
 ,*70,=0000 0400 0065 0001
 13,UJ,
 ,END,
*to perso:65100
*end file
EOF
} > $J
run_job $J ld-perso.list
if grep -q 'БЫЛИ OШИБKИ\|Error' ld-perso.list ||
   grep 'ЧИCЛO OШИБ' ld-perso.list | grep -qv 'OПEPATOPOB  00'; then
    echo "loader perso failed, see ld-perso.list"
    exit 1
fi

# Job 2, in clean memory: the words of page 33 after LOADER (among them the
# shift constants, words 1776, 1777) must stay zero.
cat > $J <<'EOF'
*name LD-IMG
*tape:101/ldimg,65,w
*perso:65100
*call ficmemor
*call ldshift
*system load list
*call newldr
*call newldrs
*call ldwrite
*end file
EOF
run_job $J ld-img.list
if grep -q 'БЫЛИ OШИБKИ\|Error' ld-img.list; then
    echo "loader image failed, see ld-img.list"
    exit 1
fi
