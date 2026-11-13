# OS Dubna Bootstrap (in Dispak until 2026, now in dubna)
# Assumptions and requisitions 
#
# Copyright, 2017 by Mikhail Popov 
# 
# Rev A. 2017/03/03
# Rev B. 2017/03/27
#
##### TAPE NUMBERS AND FORMATS
#
### TAPE LABELS:
# The following tape labels are fixed in OS Dubna
# these lebels are for labeled (named) tapes models 
# on system disks

# Allocations in DD:

 1/ROLLIB    - roll tracks
 1/D73INP    - input buffer
 3/D73OUT    - output buffer
 5/D73LIB    - STL
 6/D73STA    - system logs and statisitc
 7/M         - Multitype
 8/CATALO    - grafor buffer
 9/MONSYS    - system objects
10/USESTA    - user logs and statistic
11/LINBUF    - screen editid buffers	
12/LIBRAR    - library objects
37/LIBRAR    - library objects

# Allocations in MS (library tapes)
 8/CATALO
 9/MONSYS
12/LIBRAR
37/LIBRAR

#
### THE FOLLLOWING IS CORREPONDING TO TAPE NUMBERS:
# Please NOTE, the FIXED TAPE NUMBERS are used in
# the bootstrap sequence and scripts. All tapes are 
# generated during the bootstrap and in used by the
# bootstrap scripts.
# 
# All tapes have the following format:
#-----------------------------------
#   ZONE  | CONTENT
#-----------------------------------
# 00 - 77 | perso of the compiled source
#     100 | sources in the cosy format
#----------------------------------- 
# Pre-fixed tape number ranges in DD bootstrap.
# dubna takes tape numbers up to 999: the 2017 numbers lost
# their thousands digit in 2026 (1400 -> 400, 2209 -> 209).
#
#   1- 99 Original tapes  
# 100-199 Compilers
# 200-399 Monitor System (MS) & libraries
# 400-899 OS Dubna Dispatcher (DD)
# 900-999 Temp/Scratch tapes 
# 209, 211, 224 Bridge tapes dubna/SIMH: 2NN = disk NN

## original tape images (as is)
#
   9 - monsys-9
  12 - librar-12
  37 - librar-37

## 100-199 Compilers
#
100 - loader

## 200-399 Monitor System (MS) & libraries
#
200 - Мониторная Система
201 - MS: common library written by COLLECT
202 - MS: working copy of drums 21, 22 written by COMTODRU
203 - 9/MONSYS with the rebuilt MS (ms-splice.py)
221 - libra21 
223 - libra23
247 - task11+task47 (compilation in FOREX)
301 - exfor - not used (partial source code)

## 400-899 OS Dubna Dispatcher (DD)
#
400 - Диспетчер

## 900-999 Temp/Scratch tapes
922 - tape 203 from zone 40: MS drum 22 for the link job
990 - DD perso for linking
999 - DD with the system, cut into drum images

## Bridge tapes
#
209  - disk9    - 7Mb system disk
211  - disk11   - 7Mb library disk
224  - disk24   - 7Mb source code DD,MS,STL disk
