#! /bin/sh
. ../env.sh
# Make BRIDGE devices
set -x 
# Make bridges to
# DISK9
if [ -f disk9.bin ]; then
   rm -f $TAPES/209
   ln -s `pwd`/disk9.bin  $TAPES/209
fi
# DISK11
if [ -f disk11.bin ]; then
   rm -f $TAPES/211
   ln -s `pwd`/disk11.bin  $TAPES/211
fi
# DISK24 
if [ -f disk24.bin ]; then
   rm -f $TAPES/224
   ln -s `pwd`/disk24.bin  $TAPES/224
fi

ls -al $TAPES/2[0-2][0-9]
