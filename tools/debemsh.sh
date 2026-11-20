#!/bin/sh
if [ "$WORKVOL" = "" ]; then echo Need env var WORKVOL ; exit 1; fi
line=1
if [ "$1" = '-v' ]; then line=0; shift; fi
first=`head -1 $1`
name=`echo $first | awk '{print $1}'`
rest=`echo "$first" | sed s/$name//`
cat > debemsh$$.b6 << EOF
шифр 419900зс5^
dis 67($WORKVOL-wr)^
еев1а3
*name
*bemsh
inp\$\$\$
$name	СТАРТ	'1'
M1      equ     1
M2      equ     2
M3      equ     3
M4      equ     4
M5      equ     5
M6      equ     6
M7      equ     7
M10     equ    '10'
M11     equ    '11'
M12     equ    '12'
M13     equ    '13'
M14     equ    '14'
M15     equ    '15'
M16     equ    '16'
M17     equ    '17'
$rest
EOF
tail +2 "$1" >> debemsh$$.b6
cat >> debemsh$$.b6 << EOF
	ФИНИШ
eoi\$\$\$
trn\$\$\$
$line-$line
бтмалф
end\$\$\$
*libra:2
*call dtran($name)
EOF
if [ "$2" != '' ]; then cat "$2" >> debemsh$$.b6; fi
cat >> debemsh$$.b6 << EOF
*stand
*super
*edit
*r:1
*w:67
*ee
*end file
\`\`\`\`\`\`
еконец
EOF
dispak -l debemsh$$.b6 > /dev/tty
rm debemsh$$.b6
besmtool dump $WORKVOL --length=32 --to-file=/dev/stdout | `dirname $0`/cosy2txt
