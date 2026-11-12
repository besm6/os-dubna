#! /bin/sh
. ./env.sh
# Poluplate disk images in Dispak for the bootstrap  
# Copyright 2017, by Mikhail Popov
#
#  ReadMeTapes.txt file  contains more inforrmation
#
set -x

mkdir -p $TAPES

# 9
touch $TAPES/9
besmtool write 9 --from-file=../monsys/monsys.9

# 12
touch $TAPES/12
besmtool write 12 --from-file=../lib12/librar.12 

# 37
touch $TAPES/37
besmtool write 37 --from-file=../lib37/librar.37 

# 1990
touch $TAPES/1990

# 1999
touch $TAPES/1999

# 3000
touch $TAPES/3000

ls -al  $TAPES/
