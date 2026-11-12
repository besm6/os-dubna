#! /bin/sh
. ./env.sh
#
#  Bootstrap sequence for OS Dubna in dispak
#
#  Copyright 2017, Mikhail Popov.  
#
# 03/03/2017:  
#
#  


set -x 

echo Populating disks in $TAPES

./populate-dsk.sh


echo compile DD
rm -f $TAPES/1999
./mk-dd-src.sh

#echo Build MS
#rm -f $TAPES/1999
#./mk-ms-src.sh

echo compile STL
rm -f $TAPES/1999
./mk-stl-src.sh

echo compile LD
rm -f $TAPES/1999
./mk-ld-src.sh

echo "Making disk images for SIMH"
( cd data; ./mkdisk9.sh; ./mkdisk11.sh; ./mkbridges.sh)

echo "Making the patch deck"
touch $TAPES/1999

( cd deck-b1; ./mk-deck-b1.sh) > deck-b1.b6 

echo "Run DEBMULT"
touch $TAPES/1999
dispak -l debmult.b6 > debmult.list

echo "Compiling the PATCH DECK ... and linking DD...."
dispak -l deck-b1.b6 > deck-b1.list

# Drum images, tra-libs.b6, and the jobs newbsz and newdd run in SIMH.
echo "Building the images, the task library and drum 25 in SIMH"
./mk-base.sh
