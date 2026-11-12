#! /bin/sh
# Compile DD (besmdisp/) under dubna: sources to tape 400 from zone 100,
# perso to zones 0-77.
. ./env.sh
run_src_job 400 dd-base-src.list ../besmdisp/*.dd* <<'EOF'
*name DD-2017
*edit
*r:50000
*w:66100
*ee
*MADLEN(L=FBG)
  FREQ300:,NAME,
  FREQ300:,STEXT,. *** ЧACTOTA = 300 ГEPЦ
COMMENTS ARE IN THE DD SOURCE CODE
  FREQ:,EQU,300
  B*START:,EQU,0
  ГMAC:,MACRO,KOП
  ,KOП,.HET ПPИOPИTETOB
  ГMAC:,ENDM,
  ,END,
*MADLEN(L=FBG,I=66100,SТЕХТ=FRЕQ300)
*to perso:66000,77
*end file
EOF
