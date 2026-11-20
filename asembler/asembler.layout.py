"""
ASEMBLER of the Dubna installation tape (monsys.9), loaded at 01604 under
/MONTRAN: the Madlen assembler as an overlay of its own. ASMGEN and its
second half G43044, ASMPRINT and SIMFAIL* are those of GLINK
(../fortran/glink.layout.py), S items here; ASMINIT and ASMSTMT are the
editions of ASEMBLER (ASMINIT uses cells of its own where that of GLINK uses
cells of the root of the compiler). The modules made from the disassembly
are M items, those whose Madlen files are kept as they are S items.
"""
M, C, L, S = 'M', 'C', 'L', 'S'
BASE = 0o01604                  # address of the overlay header
END = 0o31432
LAYOUT = [
    (0o01614, M, 'G01614'),     # ASEMBLER: sets the registers, goes to ASMINIT
    (0o01621, M, 'G01621'),     # ASMINIT
    (0o02132, M, 'G02132'),     # ASMSTMT: a vector of 5 jumps
    (0o10505, L, 'G10505'),     # SAVE*
    (0o10556, M, 'G10556'),     # D44561: a variable
    (0o10557, C, 'D10557'),     # work area (zeros)
    (0o22557, C, 'D37001'),
    (0o23067, C, 'D44562'),
    (0o23334, S, 'G23334'),     # ASMGEN
    (0o24217, S, 'G24217'),     # G43044
    (0o25415, C, 'D46362'),
    (0o26000, C, 'D47000'),
    (0o26400, S, 'G26400'),     # ASMPRINT
    (0o26723, C, 'D45026'),     # its tables
    (0o30266, M, 'G30266'),     # called by ASMSTMT
    (0o31233, S, 'G31233'),     # SIMFAIL*
    (0o31342, L, 'G31342'),     # ПEP6B81C
    (0o31377, L, 'G31377'),     # OCTTDEC
]
LIB = {
    0o10505: ('SAVE*', {}),
    0o31342: ('ПEP6B81C', {}),
    0o31377: ('OCTTDEC', {}),
}
RENAME = {'G01614': 'ASEMBLER', 'G01621': 'ASMINIT', 'G02132': 'ASMSTMT',
          'G10556': 'D44561'}
# the names of the S modules and of their entries, at their addresses here
RENAME.update({'G23334': 'ASMGEN', 'G23367': 'G42214', 'G23542': 'G42367',
               'G23751': 'G42576', 'G24146': 'G42773', 'G24217': 'G43044',
               'G26400': 'ASMPRINT', 'G26401': 'G44504', 'G31233': 'SIMFAIL*'})
# the places here that the S modules call by these names
ALIASES = {0o01622: 'G44243'}
VECTORS = {0o02132: 5, 0o23334: 27}
OFFSETS = [0o24217]
OWNER = {0o23067: 0o01621,       # the table that ASMINIT sets
         0o26723: 0o26400}       # the tables of ASMPRINT
# ASEMBLER passes the constants 10000 (М4) and 2000 (М5), as G36551 of GLINK
NUMBERS = [(0o01617, 'М4'), (0o01620, 'М5')]
LOW = 'dubna'                   # Dubna resident: MONITOR*, /MONTRAN
