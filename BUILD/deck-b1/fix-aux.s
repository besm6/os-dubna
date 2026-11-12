Cs
Cs SPECMON - launcher of standard tasks     11/11/2026
Cs
 SPECMON:,NAME,
 DLIBMT:,LC,2.BTOPOЙ PEЗИДEHT
  *113:B,BLOCK,PULT,PASS
  *YCЫ:LC,BLOCK,ГYC
 MN*TL:,EQU,1067B
C......   MOHИTOPHЫE COMMON'Ы.
Cs
Cs  Monitor common blocks pinned to the Monitor Dubna
Cs  addresses (9/MONSYS). Linked under Dispak they land
Cs  elsewhere, and the MS loader then finds no INFLOAD*.
Cs
 INFLOAD*:,EQU,716B
 M/STL:,EQU,510B
 A/CAT:,EQU,511B
 INF0:,EQU,512B
 RM*:,EQU,711B
 A/I0:,EQU,517B
 A/MINUS:,EQU,520B
 *REGIM//:,EQU,523B
 BASE:,BSS,
 1,BASE,BASE
C====================================
 'ПPOBEPKA CПEЦИФИKИ ЗAДA4И
C---------
  ,FUN,70100B+PASS.N TT
  ,ASN,64-40
 ,AAX,=:016
  ,ATX,N*TT
 ,ITA,3
 ,AAX,=77
 ,AEX,=77
  ,UZA,SETDELTA
  ,ITA,3
  ,ASN,64-42
  ,AUX,=6H'''''''''7''7'
  ,AOX,=6HTASK00
  ,ATX,NAME
 14,VTM,NAME
 ,ITA,14
 ,FUN,64B.= ЗAПИCЬ NAME
C
C...   ЗAXBAT ЛEHTЫ C БCЗ :
C
  GT:13,VTM,66B
  ,*63,DLIBMT+1.ИMЯ
  ,U1A,*+1.ЗAДAHO
  ,XTA,LIBMT.CTAHДAPT
  :,*57,2050B
  ,UZA,STOP.HET MЛ
  ,AAX,=:3
  ,U1A,STOP.HEГOT/ЗAHЯT
  ,*65,DLIBMT
  ,AOX,/FIZIM
  ,FUN,112B
  ,*72,=:11 40 35 00 37 77
C
C...   ПPOБA HAЛИЧИЯ CTAT.ЗAГPYЗЧИKA
C      B KATAЛOГE БCЗ
C
  ,*70,=0010 3500 0066 0000
  ,XTA,73400B
  ,AEX,=6HSTALOA
  ,U1A,R/SYS.-HET
  4,VTM,-1023
  :4,XTA,73777B.ПEPEПИCЬ
  4,ATX,-1.KATAЛOГA HA
  4,VLM,*-1.OБM.ЛИCT
  ,UJ,R/SYS+1.OБXOД ЧT.ЗAГP.
  R/SYS:,BSS,
  ,*70,INFLOA.ПOCAДKA
                           'ЗAГPYЗЧИKA'
C---------OФOPMЛEHИE MOHИTOPHЫX CBЯЗEЙ
 ,XTA,ALOAD
 ,ATX,INFLOAD*
 ,ATX,RM*+2
 ,ATI,15
 ,XTA,=1100
 ,ATX,17B.MECTO PAЗДEЛA
  ,XTA,
  ,ATX,*REGIM//
 ,XTA,=76000.
 ,ATX,43B.ЛИCT OБMEHA
 ,XTA,=I0
 ,ATX,A/I0
 ,XTA,=:002
 ,ATX,A/MINUS
 ,XTA,STOP
 ,CTX,20B
 'ПOДПPABKA ЗAГPYЗЧИKA'
 CHLOAD:,BSS,
  ,XTA,/FIZIM
  ,ATX,M/STL
  ,ATX,A/CAT
  ,ATX,INF0
C=========================================
 'OФOPMЛEHИE ИMEHИ PAЗДEЛA=CЛ.ЗAДAЧИ'
C---------
 ,ITA,3.ИMЯ ИЗ 3 И.P.
 ,ASN,64+6
 ,ATX,INFORTA.ИHФ ДЛЯ ЗAДA4И
 ,YTA,
 ,AUX,TMASK.ПPEOБP. B TEXT
 ,ARX,STAND.OФOPMЛEHИE
 ,ATX,NAME
C==================================
 'ПEPECЫЛKA БЛOKA OTKAЗA OT ЛEHTЫ
C---------
 LENTGH:,EQU,HEAD-ENDHEAD
 4,VTM,LENTGH
 LOOP:,BSS,
 4,XTA,ENDHEAD
 ,UTC,1000B
 4,CTX,-LENTGH
 4,VLM,LOOP
C=======================================
 'ПY HA CЛYЖEБHYЮ ЗAДA4Y
C---------
 ,XTA,
 ,ATX,1077B.
 ,XTA,NAME
 ,ATX,1070B
 ,WTC,ALOAD
 13,VJM,
C===================================
 'ECЛИ HET ЗAДAЧИ HA MЛ'
C---------
 13,VTM,MIST
  TO TEL:,ITA,13
  ,AOX,N*TT
  ,FUN,76B
  STOP:,SJ,
 MIST:,ISO,6HTASK'041'
 ,OCT,
 SETDELTA:,BSS,
 ,ITA,3
  ,ASN,64+6
C---------  YCTAHOBKA ДEЛЬTЫ
  ,ATI,14
  14,UTM,-777B
  14,VZM,SETNAM
  ,*52,DLIBMT
  PRIZ:,*63,DLIBMT+1
  :,UZA,FST
  ,AUX,=6H'137''137''137''137''137''137'
  FN:,ATX,ZONE
  ,*63,DLIBMT
  ,ASN,64-39
 ,AUX,=6H'7''7''7''0''0''0'
  ,ARX,=6H000''''''
 ,ATX,ZONE+2
 13,VTM,ZONE
  ,UJ,TOTEL
  FST:,XTA,=6HD73LIB
  ,UJ,FN
C
C...   ЗAПPOC HOBOГO ИMEHИ БCЗ
C      ( ПPИKAЗ 77777/ )
C
  SETNAM :12,VTM,TGN
  ,*63,ГYC
  ,ASN,64+15
  ,ASN,64-40
  ,AOX,=6H'100':ИMЯ
  12,ATX,
  ,ITA,12
  ,AOX,N*TT
  ,FUN,76B
  ,XTA,=1
  ,FUN,66B
  ,ASN,64+12
  ,ATX,ZONE
  NORM:,XTA,ZONE
  ,UZA,WRN
  ,AAX,=:77
  ,U1A,WRN
  ,XTA,ZONE
  ,ASN,64-6
  ,ATX,ZONE
  ,UJ,NORM
  WRN:,XTA,ZONE
  ,*52,DLIBMT+1
  ,UZA,PRIZ
  ,FUN,66B.ЗA NБOБ
  ,APX,=171717170000
  ,ASN,64+32
  ,FUN,203B
  ,AEX,
  ,XTA,=7777
  ,*53,DLIBMT+1
  ,UJ,PRIZ
 ZONE:,ISO,12HD73LIB ЗOHA
 ,OCT,
  TGN:,ISO,12HQ:ИMЯ БCЗ '77'''
C====================
 ' OTKAЗ OT ЛEHTЫ OT ИMEHИ ЗAДA4И
C---------
 HEAD:,BSS,
 1,BAS,*
 1,VTM,1000B
  ,XTA,N*TT
 ,ATX,MN*TL
 15,VTM,73401B.
  ,*70,ПOДBOД
  ,XTA,BIT66
  ,*57,4000B
 ,XTA,INFORTA
 ,ATI,1
 ,WTC,1077B
 ,UJ,
  ПOДBOД:,030,
  ,066,
  BIT66:,OCT,0000 0000 004
  N*TT:,LOG,
 ENDHEAD:,BSS,
 INFORTA:,BSS,1
C---------
C====================================
 'BCЯKAЯ BCЯЧИHA'
C---------
 INFLOA:8,014,3503B.
 ,021,101B.C 2101 - 1 CEKT
  /FIZIM:,LOG,10 0000 0066 0000
C---------
 ALOAD:,LOG,73401.
 LIBMT:,TEXT,8HD73LIB '05'
 TMASK:,TEXT,8H    '07''07'
 TRACENAM:,BSS,
C---------
 STAND:,TEXT,8HTASK00
 NAME:,BSS,1
 ,BSS,2
 ,END,SPECMON
