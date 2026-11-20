# ASEMBLER of 9/MONSYS

The Madlen assembler as an overlay of its own (`ASEMBLER`, loaded at 01604
under `/MONTRAN`), rebuilt identical to the tape by `make` here. Its modules
`ASMGEN`, `G43044`, `ASMPRINT` and `SIMFAIL*` are also linked into `GLINK` of
the Fortran compiler (`../fortran`), whose `make asm` regenerates
`asmprint.asm` and `simfail%.asm`; `make asm` here regenerates `ASEMBLER`,
`ASMINIT`, `ASMSTMT`, `D44561` and `G30266`. See the Makefile.
