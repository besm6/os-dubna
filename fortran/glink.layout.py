"""
GLINK, the assembler of Fortran inserts, of the Dubna installation tape
(monsys.9). From GASSTMT on it is the assembler: GASSTMT and GASINIT (the
editions of GLINK of ASMSTMT and ASMINIT, here), GASGEN and its second half
GAS43044 (ASMGEN and G43044 of ../asembler with these names, made by
`make sources`), ASMPRINT, SIMFAIL* (../asembler, shared with ASEMBLER).
The names GAS... keep those of ASEMBLER apart in one COLLECT run. GLINK keeps a variable of
D02144 that lies in the low memory (see fortran.layout.py). ASMPRINT keeps
its tables in a common block after its code. The modules made from the
disassembly are M items, those whose Madlen files are kept as they are S
items.
"""
M, C, L, S = 'M', 'C', 'L', 'S'
BASE = 0o34570                  # address of the overlay header
END = 0o50070
ROOT = 'fortran'
LAYOUT = [
    (0o34600, M, 'G34600'),     # GLINK
    (0o36255, S, 'G36255'),     # G36551
    (0o36505, C, 'D37001'),
    (0o37015, C, 'D37311'),
    (0o37021, C, 'D37315'),
    (0o37030, S, 'G37030'),     # TABFIND
    (0o37106, S, 'G37106'),     # LISTLINE
    (0o37313, S, 'G37313'),     # FLDADD
    (0o37326, M, 'G37326'),     # GASSTMT
    (0o41644, S, 'G41644'),     # GASGEN
    (0o42527, S, 'G42527'),     # GAS43044
    (0o43725, M, 'G43725'),     # GASINIT
    (0o44236, C, 'D44562'),
    (0o44503, M, 'G44503'),     # ASMPRINT
    (0o45026, C, 'D45026'),     # its tables
    (0o46371, M, 'G46371'),     # SIMFAIL*
    (0o46500, C, 'D46362'),     # as long as in ASEMBLER
    (0o47063, C, 'D47063'),     # the rest of the zeros up to D47000 (unused)
    (0o47400, C, 'D47000'),
    (0o50000, L, 'G50000'),     # ПEP6B81C
    (0o50035, L, 'G50035'),     # OCTTDEC
]
LIB = {
    0o50000: ('ПEP6B81C', {}),
    0o50035: ('OCTTDEC', {}),
}
# the modules made here (the S modules keep the names in their files)
RENAME = {'G34600': 'GLINK', 'G37326': 'GASSTMT', 'G43725': 'GASINIT',
          'G44503': 'ASMPRINT', 'G46371': 'SIMFAIL*'}
# what GASGEN and GAS43044 call in GASINIT, which is shorter here, and FLDADD
# in GASSTMT
ALIASES = {0o43726: 'GAS44243', 0o44235: 'GAS44561',
           0o37667: 'G40204'}    # FLDADD jumps into ASMSTMT
OWNER = {0o45026: 0o44503,
         0o47063: 0o34600}      # declared only by GLINK, which has all
OFFSETS = [0o42527]
# the names of the S modules and of their entries, at their addresses here
RENAME.update({'G35745': 'G36241', 'G35753': 'E36247', 'G36255': 'G36551',
               'G36256': 'G36552', 'G36257': 'G36553', 'G36357': 'G36653',
               'G36434': 'G36730', 'G36502': 'G36776', 'G37030': 'TABFIND',
               'G37031': 'TABHASH', 'G37106': 'LISTLINE',
               'G37213': 'LISTEND', 'G37313': 'FLDADD', 'G37325': 'E37621',
               'G41644': 'GASGEN', 'G41677': 'GAS42214', 'G42052': 'GAS42367',
               'G42261': 'GAS42576', 'G42456': 'GAS42773', 'G42527': 'GAS43044'})
# the places here that the S modules call by these names
ALIASES.update({0o35745: 'G36241', 0o35753: 'E36247'})
VECTORS = {0o41644: 27}   # ASMGEN: a vector of jumps
SPATH = ['../asembler']          # where the S modules of the assembler are
LOW = 'dubna'                   # Dubna resident: MONITOR*, /MONTRAN
BASES = {0o34600: 8}            # GLINK: уиа GLINK+2(М8), see glink.dtr; then
                                # D37315 from 34713 (REBASE)
REBASE = {0o34713: 0o37021}
