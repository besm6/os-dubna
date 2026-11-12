#! /bin/sh
. ./env.sh
# Populate tape images for the bootstrap
# Copyright 2017, by Mikhail Popov
#
#  ReadMeTapes.txt file  contains more inforrmation
#
set -x

mkdir -p $TAPES

# 9
touch $TAPES/9
besmtool write 9 --from-file=../monsys/monsys.9

# 922: MS drum 22, i.e. 9/MONSYS from zone 40, for the link job
{ head -c $((8256*4)) $TAPES/9; dd if=$TAPES/9 bs=8256 skip=36 status=none; } > $TAPES/922

# 12
touch $TAPES/12
besmtool write 12 --from-file=../lib12/librar.12 

# 37
touch $TAPES/37
besmtool write 37 --from-file=../lib37/librar.37 

ls -al  $TAPES/
