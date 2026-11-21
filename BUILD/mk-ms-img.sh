#! /bin/sh
# Assemble the Monitor System from the perso on tape 200.
# COLLECT links the resident, the dynamic part and the static sections
# INPUTCAL, FORTRAN (with CBDPR, CONTROL, ENDPRO, GLINK) and ASEMBLER onto
# tape 201; COMTODRU turns that into a working copy of drums 21, 22 on tape
# 202.  The modules of the Fortran compiler (../fortran) and of ASEMBLER
# (../asembler) are put into perso on tapes 241-243 first; the cards
# FORTRAN:41,42 and ASEMBLER:43 make COLLECT take them from there (as units
# 41-43), so they stay out of the temporary library, which becomes the
# dynamic part.  A module taken from a library stays in the temporary
# library for the rest of the run and is found there first, so modules that
# differ must have different names in all sections (GLINK's editions of the
# ASEMBLER modules are named GAS...; ../tools/ovltest shows what happens
# otherwise).  ms-splice.py takes the other static sections (ALGOL,
# A/PRINTM, WRITLIB*) from the archived 9/MONSYS.
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
# (at most two drums of input) into perso on the tape, mounted as the unit
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
    if grep -q 'БЫЛИ OШИБKИ\|Error' $_l || ! grep -q "^ *$1 " $_l; then
        echo "perso of $* failed, see $_l"
        exit 1
    fi
}
make -s -C ../fortran sources || exit 1
perso 241 41 ms-ftn41.list ../fortran FORTRAN CBDPR
perso 242 42 ms-ftn42.list ../fortran CONTROL ENDPRO GLINK
perso 243 43 ms-asm43.list ../asembler ASEMBLER

cat > $J <<'EOF'
*name MS-IMG
*tape:200/ms,66
*tape:201/msimg,67,w
*tape:202/msdrum,65,w
*tape:241/cmp41,41
*tape:242/cmp42,42
*tape:243/cmp43,43
*library:21
*library:23
*perso:66000
*call collect:670000
MONITOR*(INPUTCAL,FORTRAN,ASEMBLER)
FORTRAN(CBDPR,CONTROL,ENDPRO,GLINK)
FORTRAN:41,42
ASEMBLER:43
*end record
*call comtodru:670000,650000
*end file
EOF
run_job $J ms-img.list
if ! grep -q 'MOHИTOP HA' ms-img.list || grep -q 'OTCYTCTBYET\|MAЛO MЛ' ms-img.list; then
    echo "MS image failed, see ms-img.list"
    exit 1
fi
./ms-splice.py $TAPES/202 $TAPES/9 $TAPES/9 $TAPES/203 &&
./ms-splice.py $TAPES/202 $TAPES/9 data/mons9.d9 data/mons9.bin || exit 1
{ head -c $((8256*4)) $TAPES/203; dd if=$TAPES/203 bs=8256 skip=36 status=none; } > $TAPES/922
