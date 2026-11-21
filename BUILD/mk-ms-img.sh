#! /bin/sh
# Assemble the Monitor System from the perso on tape 200.
# COLLECT links the resident, the dynamic part and the static sections
# INPUTCAL, FORTRAN (with CBDPR, CONTROL, ENDPRO, GLINK), ASEMBLER, ALGOL
# (with A/PRINTM) and WRITLIB* onto tape 201; COMTODRU turns that into a
# working copy of drums 21, 22 on tape 202.  The modules of the Fortran
# compiler (../fortran), of ASEMBLER (../asembler), of the Algol compiler
# (../algol) and the root of WRITLIB* (../writlib) are put into perso on
# tapes 241-244, 246 first; the cards FORTRAN:41,42, ASEMBLER:43, WRITLIB*:44
# and ALGOL:46 make COLLECT take them from there (as units 41-44, 46), so they stay
# out of the temporary library, which becomes the dynamic part.  A
# module taken from a library stays in the temporary library for the rest
# of the run and is found there first, so modules that differ must have
# different names in all sections (GLINK's editions of the ASEMBLER modules
# are named GAS..., those of ALGOL A...; ../tools/ovltest shows what happens
# otherwise; ALGOL gets the ASMPRINT of ASEMBLER, as it should).  All the
# static sections are linked here; ms-splice.py takes the dynamic loader
# from tape 101 (mk-ld-img.sh); lib-splice.py the libraries 21, 22, 23
# rebuilt by mk-libs.sh.
# Result: tape 203, a 9/MONSYS with the rebuilt MS; tape 922, the same
# from zone 40 (drum 22); data/mons9.bin for the disk image.
. ./env.sh
for t in 201 202; do
    rm -f $TAPES/$t
    : > $TAPES/$t
done
J=`mktemp` || exit 1
trap "rm -f -- '$J'" EXIT

# perso tape unit listing dir overlays...: the Madlen files of the overlays
# (make print-OVERLAY in dir; at most two drums of input) into perso on the
# tape, mounted as the unit; the first module is OVERLAY or OVERLAY*
perso() {
    _t=$1 _u=$2 _l=$3 _d=$4
    shift 4
    : > $TAPES/$_t
    { echo "*name perso$_u"; echo "*tape:$_t/cmp$_u,$_u,w"
      echo "*no list"; echo "*madlen"
      for _o; do
          for _f in `make -s -C $_d print-$_o`; do
              grep -v '^[[:space:]]*$' "$_d/$_f"
          done
      done
      echo "*to perso:${_u}0000"; echo "*call plcatalog:${_u}0000"; echo "*end file"
    } > $J
    run_job $J $_l
    if grep -q 'БЫЛИ OШИБKИ\|Error' $_l || ! grep -q "^ *$1\*\{0,1\} " $_l; then
        echo "perso of $* failed, see $_l"
        exit 1
    fi
}
make -s -C ../fortran sources || exit 1
perso 241 41 ms-ftn41.list ../fortran FORTRAN CBDPR
perso 242 42 ms-ftn42.list ../fortran CONTROL ENDPRO GLINK
perso 243 43 ms-asm43.list ../asembler ASEMBLER
perso 244 44 ms-wl44.list ../writlib WRITLIB
perso 246 46 ms-alg46.list ../algol ALGOL APRINTM

# A card NAME:n1,n2 gives the libraries 21,n1,n2 (NEWLIBR/ puts library 21
# first), so a module of library 21 would come from the archived one.  The
# module COLLECT of library 21, with 21 dropped from that list, goes into
# perso on tape 245; appended to the temporary library, it is found before
# library 21.  The cards INPUTCAL:61,63 ... then take the library modules
# from the perso of libraries 21, 23 (tapes 221, 223).  No section links
# COLLECT, and it removes itself from the temporary library.
: > $TAPES/245
{ echo '*name perso45'; echo '*tape:245/lib45,45,w'; echo '*no list'; echo '*madlen'
  sed -n '/^ COLLECT:,NAME,/,/^ ,END,$/p' ../besml21/libra211.l21 |
      sed '/^  ,CALL,NEWLIBR\/$/a\
  ,XTA,LIB\
  ,ASN,64+6.БEЗ LIBRARY 21\
  ,ATX,LIB' | grep -v '^[[:space:]]*$'
  echo '*to perso:450000'; echo '*call plcatalog:450000'; echo '*end file'
} > $J
run_job $J ms-lib45.list
if grep -q 'БЫЛИ OШИБKИ\|Error' ms-lib45.list || ! grep -q '^ *COLLECT ' ms-lib45.list; then
    echo "perso of COLLECT failed, see ms-lib45.list"
    exit 1
fi

cat > $J <<'EOF'
*name MS-IMG
*tape:200/ms,66
*tape:201/msimg,67,w
*tape:202/msdrum,65,w
*tape:241/cmp41,41
*tape:242/cmp42,42
*tape:243/cmp43,43
*tape:244/cmp44,44
*tape:245/lib45,45
*tape:221/lib21,61
*tape:223/lib23,63
*tape:246/cmp46,46
*library:21
*library:23
*perso:66000
*perso:45000,cont
*call collect:670000
MONITOR*(INPUTCAL,FORTRAN,ASEMBLER,ALGOL,WRITLIB*)
FORTRAN(CBDPR,CONTROL,ENDPRO,GLINK)
ALGOL(A/PRINTM)
INPUTCAL:61,63
FORTRAN:41,42,61
ASEMBLER:43,61
WRITLIB*:44,61
ALGOL:46,61
*end record
*call comtodru:670000,650000
*end file
EOF
run_job $J ms-img.list
if ! grep -q 'MOHИTOP HA' ms-img.list || grep -q 'OTCYTCTBYET\|MAЛO MЛ' ms-img.list; then
    echo "MS image failed, see ms-img.list"
    exit 1
fi
./ms-splice.py $TAPES/202 $TAPES/9 $TAPES/9 $TAPES/203 $TAPES/101 &&
./ms-splice.py $TAPES/202 $TAPES/9 data/mons9.d9 data/mons9.bin $TAPES/101 &&
./lib-splice.py $TAPES/203 data/mons9.bin || exit 1
{ head -c $((8256*4)) $TAPES/203; dd if=$TAPES/203 bs=8256 skip=36 status=none; } > $TAPES/922
