#! /bin/sh
# Make the baseline images in data/base, used by "FRESH=1 ./mt-run.py".
# Fresh disks and drums from the dispak build, then two jobs run in SIMH:
# newbsz builds the task library 5/D73LIB (the print spooler is in it),
# newdd writes the rebuilt dispatcher to drum 25.
. ./env.sh
set -e
(cd data && ./mkdisk9.sh && ./mkdisk11.sh && ./mkdrumdd.sh) > mk-base.log 2>&1
dispak -l tra-libs.b6 > tra-libs.list
./put-job.sh hello.dub 110 >> mk-base.log

# Queue each job and start it at once (its time limit keeps the planner waiting).
export SUBMIT=ПУС CONSUBMIT={}БП POLL=СЧЕ POLLS=200 JOBWAIT=120 PRNWAIT=600

./mt-run.py 105 >> mk-base.log 2>&1 && grep -q -- "-КШ" mt-run-tty25.txt ||
    { echo "newbsz failed, see mk-base.log"; exit 1; }

./mt-run.py 100 >> mk-base.log 2>&1 && grep -q "НА 25/" mt-run-tty25.txt ||
    { echo "newdd failed, see mk-base.log"; exit 1; }

mkdir -p data/base
cp data/dubdrum1.bin data/dubdrum2.bin data/disk9.bin data/disk11.bin data/base/
echo "Baseline images are in data/base"
