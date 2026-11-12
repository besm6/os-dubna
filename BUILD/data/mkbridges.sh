#! /bin/sh
. ../env.sh
# Make BRIDGE devices
set -x 
# Make bridges to
# DISK9
if [ -f disk9.bin ]; then
   rm -f $TAPES/2209
   ln -s `pwd`/disk9.bin  $TAPES/2209
fi
# DISK11
if [ -f disk11.bin ]; then
   rm -f $TAPES/2211
   ln -s `pwd`/disk11.bin  $TAPES/2211
fi
# DISK24 
if [ -f disk24.bin ]; then
   rm -f $TAPES/2224
   ln -s `pwd`/disk24.bin  $TAPES/2224
fi

ls -al $TAPES/22*
