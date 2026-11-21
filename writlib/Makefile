# WRITLIB*, the static section of the Dubna monitor system that writes the
# modules made by a compiler into the temporary library, as on its
# installation tape 9/MONSYS (../monsys/monsys.9), rebuilt identical to the
# original. Only its root, writlib.asm (module WRITLIB*: save 47B, call
# FORTLIBR, restore), has no source in the archive; the rest are library
# modules: FORTLIBR of library 21, WRITLIBR (with the common CATALOG) of
# ../besmmons/system2.txt. Linked under /MONTRAN by ../tools/dubovl.pl in
# the dubna emulator, which takes them from its libraries: it loads at 01604.
#
#   make            build, compare with the tape (GOOD or BAD)
#
# The build needs dubna, perl and a C compiler.
DUBOVL = ../tools/dubovl.pl
OVL2BIN = ../tools/ovl2bin

# the Madlen files
WRITLIB = writlib.asm

# the header (8 words) holds the place of the section in the catalog
all: writlib.silver.bin writlib.gold.bin
	@if cmp -s -i 48 writlib.gold.bin writlib.silver.bin; then \
	  printf 'writlib*: \033[1;32mGOOD\033[22;39m\n'; \
	else printf 'writlib*: \033[1;31mBAD\033[22;39m\n'; exit 1; fi

# the section on the tape (zone, word of its RLE stream; catalog at zone 1)
MONSYS9 = ../monsys/monsys.9
TAPE = 077 01300

writlib.gold.bin: $(MONSYS9) $(OVL2BIN)
	set -- $(TAPE); tail -c +$$(((0$$1 * 1024 + 0$$2) * 6 + 1)) $< | $(OVL2BIN) > $@

../tools/%: ../tools/%.c
	$(MAKE) -C ../tools $*

# dubovl.pl writes into wlovl.bin, which must exist
build.lst: $(WRITLIB)
	head -c $$((6144 * 128)) /dev/zero > wlovl.bin
	$(DUBOVL) wlovl.bin '/montran(writlib*)' 'writlib*' -- $(WRITLIB) > $@

# the catalog at the end of build.lst gives the zone and record
writlib.silver.ovl: build.lst
	set -- `awk '$$1 == "WRITLIB*" && $$2 == 60 { print $$3, $$4 }' build.lst`; \
	dd bs=192 skip=$$((0$$1 * 32 + 0$$2)) status=none < wlovl.bin > $@

writlib.silver.bin: writlib.silver.ovl $(OVL2BIN)
	$(OVL2BIN) < $< > $@

writlib.%.dis: writlib.%.bin
	disbesm6 -a1604 -e1614 $< > $@

# the Madlen files, for ../BUILD/mk-ms-img.sh: make print-WRITLIB
print-%:
	@echo $($*)

.PHONY: all
.SECONDARY:

clean:
	rm -f *.silver.* *.gold.* build.lst dubovl.dub wlovl.bin
