# The Algol compiler of the Dubna monitor system (ALGOL-ГДР, 7.01.82), as on
# its installation tape 9/MONSYS (../monsys/monsys.9): the root overlay ALGOL
# and its sub-overlay A/PRINTM (the code listing of *FULL), rebuilt identical
# to the originals. Linked under /MONTRAN by ../tools/dubovl.pl in the dubna
# emulator: the root loads at 01604, A/PRINTM at 30355. ALGOL shares ASMPRINT
# with ASEMBLER (../asembler/asmprint.asm).
#
# The modules are made from the disassembly (M items of OV.layout.py,
# `make asm`), the Madlen files of the shared ones are kept as they are.
#
#   make            build, compare with the tape (GOOD or BAD)
#   make modcmp     after a BAD build: which module is misplaced or differs
#   make asm        regenerate the Madlen files made here (OWN_<ov>, OV=...)
#   make trace      run test*.alg under dubna with a trace: the code they
#                   execute, OV.tsym (for the disassembly, with OV.sym; the
#                   rest of the code marks there are by ../tools/codesym.py)
#
# The build needs dubna, perl and a C compiler; `make asm` also disbesm6 and
# dispak (BEMSH and DTRAN on volume WORKVOL) and a terminal.
WORKVOL = 80
OVSPLIT = ../tools/ovsplit.py
DUBOVL = ../tools/dubovl.pl
OVL2BIN = ../tools/ovl2bin
A = ../asembler/
OVERLAYS = algol aprintm

# The Madlen files of each overlay, in the order of the layout: those made
# here (OWN_<ov>, `ovsplit.py OV modules`) and the shared ones. Keep them in
# step with the layouts.
OWN_algol = algol.asm ag13666.asm ag14504.asm ag17223.asm ag22162.asm \
	ag23523.asm ag26260.asm ag26666.asm ag27126.asm ag27220.asm ag27645.asm \
	ag27733.asm ag30001.asm ag30034.asm ag30120.asm ag30257.asm
OWN_aprintm = aprintm.asm ag31206.asm ag31254.asm ag31307.asm ag31341.asm \
	ag31375.asm ag31421.asm
ALGOL = algol.asm $(A)asmprint.asm $(filter-out algol.asm,$(OWN_algol))
APRINTM = $(OWN_aprintm)

# the header (8 words) holds the place of the overlay in the catalog
all: $(addsuffix .silver.bin,$(OVERLAYS)) $(addsuffix .gold.bin,$(OVERLAYS))
	@for o in $(OVERLAYS); do \
	  if cmp -s -i 48 $$o.gold.bin $$o.silver.bin; then \
	    printf '%s: \033[1;32mGOOD\033[22;39m\n' $$o; \
	  else printf '%s: \033[1;31mBAD\033[22;39m\n' $$o; fail=1; fi; \
	done; test -z "$$fail"

# The overlays on the tape (zones of 1024 words, no service words; catalog
# at zone 1, word 01400): the place of the RLE stream of each (zone, word)
MONSYS9 = ../monsys/monsys.9
TAPE_algol = 070 01100
TAPE_aprintm = 077 00000
NAME_algol = ALGOL
NAME_aprintm = A/PRINTM

%.gold.bin: $(MONSYS9) $(OVL2BIN)
	set -- $(TAPE_$*); tail -c +$$(((0$$1 * 1024 + 0$$2) * 6 + 1)) $< | $(OVL2BIN) > $@

../tools/%: ../tools/%.c
	$(MAKE) -C ../tools $*

../tools/cosy2txt: ../tools/cosy2txt.cpp
	$(MAKE) -C ../tools cosy2txt

# dubovl.pl writes into algovl.bin, which must exist
build.lst: $(ALGOL) $(APRINTM)
	head -c $$((6144 * 128)) /dev/zero > algovl.bin
	$(DUBOVL) algovl.bin '/montran(algol)' 'algol(a/printm)' -- $(ALGOL) $(APRINTM) > $@

# the catalog at the end of build.lst gives the zone and record of each
%.silver.ovl: build.lst
	set -- `awk '$$1 == "$(NAME_$*)" && $$2 == 60 { print $$3, $$4 }' build.lst`; \
	dd bs=192 skip=$$((0$$1 * 32 + 0$$2)) status=none < algovl.bin > $@

%.silver.bin: %.silver.ovl $(OVL2BIN)
	$(OVL2BIN) < $< > $@

# The test programs, compiled under dubna with an instruction trace (*FULL
# for A/PRINTM, *NO LIST for the short path): the code they executed goes
# to OV.tsym. Only on demand: a trace is some hundred megabytes.
TESTS = test1.alg test2.alg test3.alg test4.alg
trace: algol.gold.bin aprintm.gold.bin $(TESTS)
	for t in $(TESTS); do \
	  for o in '' '*full' '*no list'; do \
	    { echo '*name test'; test -z "$$o" || echo "$$o"; echo '*algol'; \
	      cat $$t; echo '*end file'; } > trace.dub; \
	    dubna -d i --trace=trace.tmp trace.dub > /dev/null; \
	    cat trace.tmp; \
	  done; \
	done > trace.out
	../tools/ovltrace.py algol.gold.bin 1604 trace.out > algol.tsym
	../tools/ovltrace.py aprintm.gold.bin 30355 trace.out > aprintm.tsym
	rm -f trace.dub trace.tmp trace.out

# name, load address, first code address: the symbols of OV.sym and the
# code of the trace
dis = cat $(wildcard $(1).sym $(1).tsym) > $(1).dsym; disbesm6 -a$(2) -e$(3) -n$(1).dsym

algol.%.dis: algol.%.bin $(wildcard algol.sym algol.tsym)
	$(call dis,algol,1604,1614) $< > $@

aprintm.%.dis: aprintm.%.bin $(wildcard aprintm.sym aprintm.tsym)
	$(call dis,aprintm,30355,30365) $< > $@

# `make asm` regenerates the Madlen files made here from the disassembly,
# (OV=... for one overlay).
asm: $(addsuffix .gold.dis,$(OVERLAYS)) $(addsuffix .gold.bin,$(OVERLAYS)) ../tools/cosy2txt
	$(foreach o,$(or $(OV),$(OVERLAYS)),$(OVSPLIT) $(o) be && \
	  for f in $(OWN_$(o)); do m=`basename $$f .asm`; \
	    WORKVOL=$(WORKVOL) ../tools/debemsh.sh $$m.be `test -f $$m.dtr && echo $$m.dtr` | \
	    ../tools/degak.py -o | $(OVSPLIT) $(o) asm $$m > $$f; \
	  done;)

# after a BAD build: which module or common block is misplaced or different
modcmp: $(addsuffix .silver.bin,$(OVERLAYS))
	-for o in $(OVERLAYS); do $(OVSPLIT) $$o cmp; done

# the Madlen files of an overlay, for BUILD/mk-ms-img.sh: make print-ALGOL
print-%:
	@echo $($*)

.PHONY: all asm modcmp trace
.SECONDARY:

clean:
	rm -f *.silver.* *.out *.dsym build.lst dubovl.dub algovl.bin
