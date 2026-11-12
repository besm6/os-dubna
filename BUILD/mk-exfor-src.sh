#! /bin/sh
# Compile EXFOR (besmtask/*.vv) under dubna onto tape 301 and try it.
# Not used by the bootstrap.
. ./env.sh
run_src_job 301 exfor-base-src.list ../besmtask/*.vv <<'EOF'
*name exfor-2017
*edit
*r:50000
*w:66100
*c All main source are numbered
*n:    0001
*ee
*MADLEN(L=FBGR,I=66100)
*to perso:66000,77
*       perso:66000
*madlen.
 SCANNER:,NAME,
  13,uj,
 ,bss, 511+128
 ,END,
 GIV*PG:,NAME,
 TAK*PG:,ENTRY,
 13,UJ,
 ,END,
 FORT2017:,NAME, 
 *CONSD :LC,BLOCK,(7)
   ,CONT,B21,B20,B16(6)
   ,CONT,C3,INT1(3),B24/22
   ,CONT,(10),B48(8),B30/16
 *CONSE:LC,BLOCK,(5),B6(28),B17/16
 NONDECL*:,LC,1
 FLGEX*:,LC ,1
 NOLISFL*:,LC,1
 FULISFL*:,LC,1
 EXFOR:,SUBP,
 ,uj,EXFOR
 ,END,
*main FORT2017
*execute
        programma
        end
*end file
EOF
