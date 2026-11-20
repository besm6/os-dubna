# The helpers of ../fortran (built from there as needed): ovl2bin expands an
# overlay of the catalog into its image; cosy2txt turns the text that DTRAN
# writes on the volume (cosy) into lines, for debemsh.sh.
all: ovl2bin cosy2txt

ovl2bin: ovl2bin.c
	$(CC) -O2 -o $@ $<

cosy2txt: cosy2txt.o encoding.o
	$(CXX) -o $@ $^

encoding.o: encoding.cpp encoding.h gost10859.h

cosy2txt.o: cosy2txt.cpp encoding.h

clean:
	rm -f *.o ovl2bin cosy2txt
