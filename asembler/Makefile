# ASEMBLER, the Madlen assembler of the Dubna monitor system, as on its
# installation tape 9/MONSYS (../monsys/monsys.9), rebuilt identical to the
# original. Linked under /MONTRAN by ../tools/dubovl.pl in the dubna
# emulator: it loads at 01604. Some of its modules are also linked into
# GLINK of the Fortran compiler (../fortran): ASMPRINT and SIMFAIL* as they
# are, ASMGEN and G43044 as copies with other names (GASGEN, GAS43044).
#
# Some modules are made from the disassembly (M items of asembler.layout.py,
# `make asm`), the Madlen files of the others are kept as they are (S items:
# ASMGEN, G43044, ASMPRINT, SIMFAIL*; `make asm` in ../fortran regenerates
# ASMPRINT and SIMFAIL*).
#
#   make            build, compare with the tape (GOOD or BAD)
#   make modcmp     after a BAD build: which module is misplaced or differs
#   make asm        regenerate the Madlen files made here
#
# The build needs dubna, perl and a C compiler; `make asm` also disbesm6 and
# dispak (BEMSH and DTRAN on volume WORKVOL) and a terminal.
WORKVOL = 80
OVSPLIT = ../tools/ovsplit.py
DUBOVL = ../tools/dubovl.pl
OVL2BIN = ../tools/ovl2bin

# the Madlen files, in the order of the layout: those made here and the
# kept ones; keep them in step with asembler.layout.py
OWN = asembler.asm asminit.asm asmstmt.asm d44561.asm g30266.asm
ASEMBLER = asembler.asm asminit.asm asmstmt.asm d44561.asm asmgen.asm \
	g43044.asm asmprint.asm g30266.asm simfail%.asm

# the header (8 words) holds the place of the overlay in the catalog
all: asembler.silver.bin asembler.gold.bin
	@if cmp -s -i 48 asembler.gold.bin asembler.silver.bin; then \
	  printf 'asembler: \033[1;32mGOOD\033[22;39m\n'; \
	else printf 'asembler: \033[1;31mBAD\033[22;39m\n'; exit 1; fi

# the overlay on the tape (zone, word of its RLE stream; catalog at zone 1)
MONSYS9 = ../monsys/monsys.9
TAPE = 063 00640

asembler.gold.bin: $(MONSYS9) $(OVL2BIN)
	set -- $(TAPE); tail -c +$$(((0$$1 * 1024 + 0$$2) * 6 + 1)) $< | $(OVL2BIN) > $@

../tools/%: ../tools/%.c
	$(MAKE) -C ../tools $*

../tools/cosy2txt: ../tools/cosy2txt.cpp
	$(MAKE) -C ../tools cosy2txt

# dubovl.pl writes into asmovl.bin, which must exist
build.lst: $(ASEMBLER)
	head -c $$((6144 * 128)) /dev/zero > asmovl.bin
	$(DUBOVL) asmovl.bin '/montran(asembler)' 'asembler' -- $(ASEMBLER) > $@

# the catalog at the end of build.lst gives the zone and record
asembler.silver.ovl: build.lst
	set -- `awk '$$1 == "ASEMBLER" && $$2 == 60 { print $$3, $$4 }' build.lst`; \
	dd bs=192 skip=$$((0$$1 * 32 + 0$$2)) status=none < asmovl.bin > $@

asembler.silver.bin: asembler.silver.ovl $(OVL2BIN)
	$(OVL2BIN) < $< > $@

asembler.%.dis: asembler.%.bin asembler.sym
	disbesm6 -a1604 -e1614 -nasembler.sym $< > $@

# `make asm` regenerates the Madlen files made here from the disassembly
asm: asembler.gold.dis asembler.gold.bin ../tools/cosy2txt
	$(OVSPLIT) asembler be
	for f in $(OWN); do m=`basename $$f .asm`; \
	  WORKVOL=$(WORKVOL) ../tools/debemsh.sh $$m.be `test -f $$m.dtr && echo $$m.dtr` | \
	  ../tools/degak.py -o | $(OVSPLIT) asembler asm $$m > $$f; \
	done

# after a BAD build: which module or common block is misplaced or different
modcmp: asembler.silver.bin
	-$(OVSPLIT) asembler cmp

# the Madlen files, for ../BUILD/mk-ms-img.sh: make print-ASEMBLER
print-%:
	@echo $($*)

.PHONY: all asm modcmp
.SECONDARY:

clean:
	rm -f *.silver.* *.out build.lst dubovl.dub asmovl.bin
