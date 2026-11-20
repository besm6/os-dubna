# The Fortran compiler of the Dubna monitor system, as on its installation
# tape 9/MONSYS (../monsys/monsys.9): the root overlay FORTRAN and its
# sub-overlays CBDPR, CONTROL, ENDPRO, GLINK, rebuilt identical to the
# originals. Linked under /MONTRAN by ../tools/dubovl.pl in the dubna
# emulator: the root loads at 01604, the sub-overlays at 34570. GLINK, the
# assembler of Madlen inserts, shares modules with ASEMBLER (../asembler).
#
# Some modules are made from the disassembly (M items of OV.layout.py,
# `make asm`), the Madlen files of the others are kept as they are (S items).
#
#   make            build, compare with the tape (GOOD or BAD)
#   make modcmp     after a BAD build: which module is misplaced or differs
#   make asm        regenerate the Madlen files made here (OWN_<ov>, OV=...)
#
# The build needs dubna, perl and a C compiler; `make asm` also disbesm6 and
# dispak (BEMSH and DTRAN on volume WORKVOL) and a terminal.
WORKVOL = 80
OVSPLIT = ../tools/ovsplit.py
DUBOVL = ../tools/dubovl.pl
OVL2BIN = ../tools/ovl2bin
A = ../asembler/
OVERLAYS = fortran cbdpr control endpro glink
SUBS = cbdpr control endpro glink

# The Madlen files of each overlay, in the order of the layout: those made
# here (OWN_<ov>, `ovsplit.py OV modules`) and the copies (`... shared`).
# Keep them in step with the layouts.
OWN_fortran = fortran.asm scanstmt.asm wrout.asm errcode.asm dectext.asm
OWN_cbdpr = cbdpr.asm cbproc.asm cbbss.asm cbce.asm cbequ.asm cdimsr.asm cfrch.asm \
	cbtrace.asm cberror.asm cbprcz.asm putdat.asm
OWN_control = control.asm g40152.asm assignst.asm arithexp.asm operand.asm \
	funcref.asm g45015.asm logexpr.asm g46107.asm prosig.asm g50741.asm
OWN_glink = glink.asm asmstmt.asm asminit.asm $(A)asmprint.asm $(A)simfail%.asm
FORTRAN = fortran.asm scanstmt.asm symout.asm putaway.asm \
	wrdecl.asm wrout.asm errcode.asm banner.asm getcard.asm \
	addtext.asm listcard.asm errvec.asm putname.asm putsymb.asm \
	dbgprint.asm errprint.asm dectext.asm dbgstub.asm octtodec.asm
CBDPR = cbdpr.asm cbproc.asm cbbss.asm cbce.asm cbequ.asm cdimsr.asm cfrch.asm \
	cbtrace.asm cberror.asm mkitem.asm cbprcz.asm putdat.asm \
	putlabel.asm labtext.asm
CONTROL = control.asm g40152.asm assignst.asm ifstmt.asm arithexp.asm \
	operand.asm funcref.asm putop.asm errjump.asm asftrace.asm \
	g45015.asm logexpr.asm ifltrace.asm g46107.asm tabtrace.asm prosig.asm \
	g50501.asm g50510.asm g50517.asm g50531.asm g50610.asm \
	g50635.asm g50655.asm g50674.asm g50741.asm
ENDPRO = endpro.asm idxerr.asm enddump.asm
GLINK = glink.asm g36551.asm tabfind.asm listline.asm fldadd.asm asmstmt.asm \
	$(addprefix $(A),asmgen.asm g43044.asm) asminit.asm \
	$(addprefix $(A),asmprint.asm simfail%.asm)

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
TAPE_fortran = 043 01740
TAPE_cbdpr = 046 01440
TAPE_control = 050 01500
TAPE_endpro = 056 01200
TAPE_glink = 057 01140

%.gold.bin: $(MONSYS9) $(OVL2BIN)
	set -- $(TAPE_$*); tail -c +$$(((0$$1 * 1024 + 0$$2) * 6 + 1)) $< | $(OVL2BIN) > $@

../tools/%: ../tools/%.c
	$(MAKE) -C ../tools $*

../tools/cosy2txt: ../tools/cosy2txt.cpp
	$(MAKE) -C ../tools cosy2txt

# The input of one job is at most two drums: the modules of the
# sub-overlays other than CBDPR go into a personal library first.
# dubovl.pl writes into ftnlib.bin and ftnovl.bin, which must exist.
lib.lst: $(CONTROL) $(ENDPRO) $(GLINK)
	head -c $$((6144 * 128)) /dev/zero > ftnlib.bin
	$(DUBOVL) -l ftnlib.bin $(CONTROL) $(ENDPRO) $(GLINK) > $@

build.lst: $(FORTRAN) $(CBDPR) lib.lst
	head -c $$((6144 * 128)) /dev/zero > ftnovl.bin
	$(DUBOVL) -p ftnlib.bin ftnovl.bin '/montran(fortran)' \
	  'fortran(cbdpr,control,endpro,glink)' -- $(FORTRAN) $(CBDPR) > $@

# the catalog at the end of build.lst gives the zone and record of each
%.silver.ovl: build.lst
	set -- `awk '$$1 == "$(shell echo $* | tr a-z A-Z)" && $$2 == 60 { print $$3, $$4 }' build.lst`; \
	dd bs=192 skip=$$((0$$1 * 32 + 0$$2)) status=none < ftnovl.bin > $@

%.silver.bin: %.silver.ovl $(OVL2BIN)
	$(OVL2BIN) < $< > $@

# name, load address, first code address
dis = disbesm6 -a$(2) -e$(3) $(if $(wildcard $(1).sym),-n$(1).sym)

fortran.%.dis: fortran.%.bin $(wildcard fortran.sym)
	$(call dis,fortran,1604,1614) $< > $@

cbdpr.%.dis: cbdpr.%.bin $(wildcard cbdpr.sym)
	$(call dis,cbdpr,34570,34600) $< > $@

control.%.dis: control.%.bin $(wildcard control.sym)
	$(call dis,control,34570,34600) $< > $@

endpro.%.dis: endpro.%.bin $(wildcard endpro.sym)
	$(call dis,endpro,34570,34600) $< > $@

glink.%.dis: glink.%.bin $(wildcard glink.sym)
	$(call dis,glink,34570,34600) $< > $@

# `make asm` regenerates the Madlen files made here from the disassembly,
# (OV=... for some overlays).
asm: $(addsuffix .gold.dis,$(OVERLAYS)) $(addsuffix .gold.bin,$(OVERLAYS)) ../tools/cosy2txt
	$(foreach o,$(or $(OV),$(OVERLAYS)),$(if $(OWN_$(o)),$(OVSPLIT) $(o) be && \
	  for f in $(OWN_$(o)); do m=`basename $$f .asm`; \
	    WORKVOL=$(WORKVOL) ../tools/debemsh.sh $$m.be `test -f $$m.dtr && echo $$m.dtr` | \
	    ../tools/degak.py -o | $(OVSPLIT) $(o) asm $$m > $$f; \
	  done;))

# after a BAD build: which module or common block is misplaced or different
modcmp: $(addsuffix .silver.bin,$(OVERLAYS))
	-for o in $(OVERLAYS); do $(OVSPLIT) $$o cmp; done

.PHONY: all asm modcmp
.SECONDARY:

clean:
	rm -f *.silver.* *.out build.lst lib.lst dubovl.dub ftnlib.bin ftnovl.bin
