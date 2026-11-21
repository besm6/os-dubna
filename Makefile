# OS Dubna on the BESM-6: run, rebuild, check.  See README.md.

IMAGES = dubdrum1.bin dubdrum2.bin disk9.bin disk11.bin
DATA = $(addprefix BUILD/data/,$(IMAGES))

all help:
	@echo 'make run      run the system from the images in BUILD/data/base'
	@echo '              (console here, Multitype on telnet port 4199)'
	@echo 'make rebuild  rebuild everything from the sources (BUILD/bootstrap.sh)'
	@echo 'make check    verify the rebuilt images, run the tests'
	@echo 'make clean    remove the build artefacts'

# The images in BUILD/data keep what was done in the system between runs;
# a newer base (after a rebuild) replaces them.
run: $(DATA)
	cd BUILD && besm6 dubna.ini

BUILD/data/%.bin: BUILD/data/base/%.bin
	cp $< $@

rebuild:
	cd BUILD && ./bootstrap.sh

# FORTRAN, ASEMBLER, WRITLIB* and the loader equal the archived ones, the MS perso
# differs only where known, the rebuilt system boots and runs hello from
# Multitype (this restores BUILD/data from the base).
check:
	@test -f BUILD/tapes/203 || { echo 'No rebuilt images: make rebuild first'; exit 1; }
	$(MAKE) -C fortran
	$(MAKE) -C asembler
	$(MAKE) -C writlib
	cd BUILD && ./ld-check.py tapes/101 tapes/9 tapes/203
	cd BUILD && ./ms-check.sh
	cd BUILD && ./boot-run.py -f -d 25 -m 110 > boot-check.log 2>&1 || \
	    { echo 'Multitype check failed, see BUILD/boot-check.log'; exit 1; }
	@echo 'All checks passed'

clean:
	$(MAKE) -C fortran clean
	$(MAKE) -C asembler clean
	$(MAKE) -C writlib clean
	$(MAKE) -C tools clean
	rm -f fortran/*.gold.bin asembler/*.gold.bin
	rm -rf tools/ovltest/out BUILD/tapes
	rm -f BUILD/cosy/cosy2utf BUILD/cosy/utf2cosy BUILD/cosy/utf2iso
	cd BUILD && rm -f *.list *log*.txt *debug*.txt *.out *.tap mk-base.log boot-check.log \
	    output.txt output1.txt deck-b1.dub .job.dub card-run.deck FSINP.TXT \
	    data/disk*.bin data/dubdrum* data/dr00 data/mons9.bin data/CAMdrum20.bin \
	    data/*.pre-t10

.PHONY: all help run rebuild check clean
