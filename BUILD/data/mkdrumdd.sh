#! /bin/sh
. ../env.sh
# Make DRUM images
set -x 
# DRUMS 20, 21, 22, 23
# 20 -  DD
# 21,22 MS
# 23 DEBMULT 
dd if=$TAPES/1999 bs=8256 skip=4 of=./dubdrum00 seek=0 count=128
# The link job copies MS zones 40-77 from the wrong tape (unit 41 instead
# of 40), so drum 22 gets garbage. Take them from MONSYS directly.
dd if=mons9.d9 bs=8256 skip=32 of=./dubdrum00 seek=64 count=32 conv=notrunc
cat dubdrum00 dubdrum00 > dr00
ls -al dr00
cp dr00 dubdrum1.bin
cp dr00 dubdrum2.bin
ln -sf `/bin/pwd`/dubdrum2.bin $TAPES/2027
ls -al dubdrum[12]*.bin
