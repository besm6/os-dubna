 ЬRWNDЙ:,NAME,DTRAN  /01.06.84/
 *ЬFLCBЙ*:,LC,59
C     *ЬFLCBЙ*:LC,BLOCK,GAK/1(6)
 GAK/2:,EQU,*ЬFLCBЙ*+6
C     ,CONT,GAK/2(53)
 *REWIN:,SUBP,
 *BACKS:,SUBP,
 *ENDFI:,SUBP,
 9,VTM,*REWIN
 ,UJ,*0003B
C===========================================
 ЬBACKЙ:,ENTRY,
C===========================================
 9,VTM,*BACKS
 ,UJ,*0003B
C===========================================
 ЬENDFЙ:,ENTRY,
C===========================================
 9,VTM,*ENDFI
 ,UJ,*0003B
 *0003B:8,VTM,*0003B
 ,STI,10
 10,UTM,GAK/2.*ЬFLCBЙ*+6
 10,XTA,
 ,ASN,64-1
 ,ASN,64+44
 8,AEX,11B
 13,U1A,
 10,XTA,
 8,AAX,12B
 8,AEX,13B
 8,ATX,10B
 14,VTM,*0013B.=0
 ,ITS,14
 ,OCT,4700 0000 022
 *0013B:,LOG,
 ,LOG,5
 ,LOG,7 7777
 ,INT,0
 ,END,
