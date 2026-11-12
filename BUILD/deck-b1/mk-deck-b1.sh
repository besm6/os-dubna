#! /bin/sh
#
#  Script to make a patch desk for DD system build in dubna
#
#  Copyright 2017, Mikhail Popov.  
#
# 03/03/2017:  
#
#  LDSHIFT has to be set for correct environment. 
#  Configuration for DD BOOTSTRAP
#
#  Unit 41 is MS drum 22: tape 922 holds 9/MONSYS from zone 40.
#
cat << END1
*name OS-Dubna-SIMH
*     deck-b1
*tape:400/dd,50
*tape:9/monsys,40
*tape:922/monsys,41
*tape:990/,66,w
*tape:999/dd,67,w
*MADLEN,L=B.
 LDSHIFT:,NAME,
 ,XTA,61B
 ,XTA,=0010 3700 0040 0000
 ,AAX,=7777 0077 7777 7777
 ,AOX,=:0000 03
 ,ATX,C
 ,ARX,=1
 ,ATX,C+1
 ,DRUM,C
 ,XTA,BSHIFT
 ,ATX,7776B
 ,XTA,CSHIFT
 ,ATX,7777B
 ,DRUM,=0000 0300 0066 0036
 ,DRUM,C+1
 ,DRUM,=0000 0300 0066 0037
 ,XTA,=0010 3700 0066 0036
 ,ATX,61B
 13,UJ,
 BSHIFT:,LOG,64000
 CSHIFT:,LOG,70000
 C:,BSS,2
 ,END,
*CALL FICMEMOR:75550
*CALL LDSHIFT
*perso:50000
*MADLEN,L=BRF,MODEL=SIMH,STEXT=FREQ300.
END1

#
# General system config
cat conf-sys.s
#
# Optional terminal config
if [ -f conf-tty.s ]; then
  cat conf-tty.s
fi
#
# Fixes
#
# terminal
if [ -f fix-tty.s ]; then
  cat fix-tty.s
fi
# tram70 
if [ -f fix-io.s ]; then
  cat fix-io.s
fi
# disk driver
if [ -f fix-dsk.s ]; then
  cat fix-dsk.s
fi
cat <<EOF2 
*      preserve for linking DD
*to perso:66040
EOF2

# misc stuff
if [ -f fix-misc.s ]; then
  cat fix-misc.s
fi
# aux of the misc
if [ -f fix-aux.s ]; then
  cat fix-aux.s
fi

#  deck's notes
if [ -f deck.notes ]; then
  cat deck.notes
fi
cat <<EOF3 
*MAIN DD86
*CALL DATAPR*
*EXECUTE
*READ OLD 
*END FILE
EOF3
