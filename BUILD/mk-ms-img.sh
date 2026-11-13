#! /bin/sh
# Assemble the Monitor System from the perso on tape 200.
# COLLECT links the resident, the dynamic part and the static section
# INPUTCAL onto tape 201; COMTODRU turns that into a working copy of
# drums 21, 22 on tape 202.  The compilers have no perso: ms-splice.py
# takes their static sections from the archived 9/MONSYS.
# Result: tape 203, a 9/MONSYS with the rebuilt MS; tape 922, the same
# from zone 40 (drum 22); data/mons9.bin for the disk image.
. ./env.sh
for t in 201 202; do
    rm -f $TAPES/$t
    : > $TAPES/$t
done
J=`mktemp` || exit 1
trap "rm -f -- '$J'" EXIT
cat > $J <<'EOF'
*name MS-IMG
*tape:200/ms,66
*tape:201/msimg,67,w
*tape:202/msdrum,65,w
*library:21
*library:23
*perso:66000
*call collect:670000
MONITOR*(INPUTCAL)
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
