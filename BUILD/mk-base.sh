#! /bin/sh
# Make the baseline images in data/base, used by "./mt-run.py -f".
# Fresh disks and drums from the dubna build, then two jobs run in SIMH:
# newbsz builds the task library 5/D73LIB (the print spooler is in it),
# newdd writes the rebuilt dispatcher to drum 25.
. ./env.sh
set -e
(cd data && ./mkdisk9.sh && ./mkdisk11.sh && ./mkdrumdd.sh) > mk-base.log 2>&1
run_job tra-libs.dub tra-libs.list
./put-job.sh hello.dub 110 >> mk-base.log

# The jobs are also on 7/M (tra-libs.dub), but here they come from punch
# cards: order 01В starts a job at once, without Multitype and the planner.
DECK=`mktemp`
trap "rm -f -- '$DECK'" EXIT
deck() {
    awk -v n="$1" '$0 == "*l:*name " n { on = 1; print substr($0, 4); next }
        on && /^\*l:/ { print substr($0, 4); exit }
        on && $0 != "*(((" && $0 != "*)))"' tra-libs.dub |
    expand | tr a-z A-Z > $DECK
    echo '``````' >> $DECK      # end-of-deck card
}
# Boot drum 20 and keep the images (no -f, -d).

deck newbsz
./mt-run.py $DECK >> mk-base.log 2>&1 && grep -q -- "-КШ" mt-run-tty25.txt ||
    { echo "newbsz failed, see mk-base.log"; exit 1; }

deck newdd
./mt-run.py $DECK >> mk-base.log 2>&1 && grep -q "НА 25/" mt-run-tty25.txt ||
    { echo "newdd failed, see mk-base.log"; exit 1; }

mkdir -p data/base
cp data/dubdrum1.bin data/dubdrum2.bin data/disk9.bin data/disk11.bin data/base/
echo "Baseline images are in data/base"

# Check the new dispatcher and Multitype: hello from 7/M.
./mt-run.py -f -d 25 -m 110 >> mk-base.log 2>&1 ||
    { echo "Multitype check failed, see mk-base.log"; exit 1; }
