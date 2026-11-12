#! /bin/sh
# Write a Dubna deck into the Multitype buffer 7/M on disk9.bin.
# Usage: put-job.sh deck.dub [zone]     (zone of 7/M, octal, default 110)
# Check the deck with "dubna deck.dub" first. Run while SIMH is not running.
. ./env.sh
DECK=${1:?deck file}
ZONE=${2:-110}
# 7/M starts at zone 0700 of the disk
ADDR=`printf '%o' $((0700 + 0$ZONE))`
JOB=`mktemp` || exit
trap "rm -f -- '$JOB'" EXIT
{
cat <<END
*name PUT-JOB
*tape:209/disk9,67,w
*edit
*ro
*w:67$ADDR
END
# first and last cards go in as *l: lines, the rest as inline text
sed -n '1s/^/*l:/p' "$DECK"
echo '*((('
sed '1d;$d' "$DECK"
echo '*)))'
sed -n '$s/^/*l:/p' "$DECK"
cat <<END
*EE
*END FILE
END
} > $JOB
run_job $JOB put-job.list
grep -a 'ЗAПИCAHO' put-job.list
