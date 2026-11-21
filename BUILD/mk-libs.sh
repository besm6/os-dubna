#! /bin/sh
# Pack the perso of libraries 21, 22, 23 (tapes 221-223, mk-lib2N-src.sh)
# with CRELIB into common libraries (packed ОБСП) on tapes 251-253, and
# compare them with the archived ones on 9/MONSYS (lib-check.sh).
# The entry PAIB of LIBSUB lies beyond the module, so Madlen cannot make
# it; the archived catalog has it, as had an older one: it is added to
# the catalog of the perso.
. ./env.sh
J=`mktemp` || exit 1
trap "rm -f -- '$J'" EXIT
./libcat.py $TAPES/222 0 | grep -q '(PAIB)' ||
    ./libcat.py -e $TAPES/222 0 LIBSUB PAIB 67 || exit 1
for n in 21 22 23; do
    : > $TAPES/25${n#2}
    cat > $J <<EOF
*name CRELIB$n
*tape:22${n#2}/lib$n,67
*tape:25${n#2}/obsp$n,66,w
*library:21
*call crelib:tape,670000
*end file
EOF
    run_job $J lib$n-crelib.list
    if ! grep -q 'ЧИCЛO ПOДПPOГPAMM И BXOДOB' lib$n-crelib.list; then
        echo "CRELIB of library $n failed, see lib$n-crelib.list"
        exit 1
    fi
done
./lib-check.sh -p
