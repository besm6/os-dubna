#! /bin/sh
set -x
cat cat.d9 mons9.bin tail.d9 tail.d9 tail.d9| dd iflag=fullblock bs=8256 count=1024 of=disk9.bin
ls -al disk9.bin