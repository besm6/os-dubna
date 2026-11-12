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
шифр 419999 зс5^
лен 41(2048)^
лен 40(9)^
лен 67(2209-ЗП)^
eeв1а3
*name PUT-JOB
*     no list
*call putflag*
5
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
\`\`\`\`\`\`
еконец
END
} > $JOB
dispak -l $JOB > put-job.list
grep -a 'ЗAПИCAHO' put-job.list
