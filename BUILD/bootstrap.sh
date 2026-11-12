#! /bin/sh
. ./env.sh
#
#  Bootstrap sequence for OS Dubna: compile and link under dubna,
#  then build the rest in SIMH.
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
./mk-dd-src.sh

#echo Build MS
#./mk-ms-src.sh

echo compile STL
./mk-stl-src.sh

echo compile LD
./mk-ld-src.sh

echo "Making disk images for SIMH"
( cd data; ./mkdisk9.sh; ./mkdisk11.sh; ./mkbridges.sh)

echo "Making the patch deck"
( cd deck-b1; ./mk-deck-b1.sh) > deck-b1.dub

echo "Run DEBMULT"
rm -f $TAPES/999 $TAPES/990
touch $TAPES/999 $TAPES/990
run_job debmult.dub debmult.list

echo "Compiling the PATCH DECK ... and linking DD...."
run_job deck-b1.dub deck-b1.list

# Drum images, tra-libs.dub, and the jobs newbsz and newdd run in SIMH.
echo "Building the images, the task library and drum 25 in SIMH"
./mk-base.sh
