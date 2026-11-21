"""
ALGOL of the Dubna installation tape (monsys.9), loaded at 01604 under
/MONTRAN: the root overlay of the Algol compiler (ALGOL-ГДР, 7.01.82). Its
head (01614-01735) is the driver, which calls the passes and, with *FULL,
loads A/PRINTM; 01736-11777 are its tables (the keyword table at 02166);
ASMPRINT is that of ASEMBLER (../asembler), an S item. The modules are made
from the disassembly (M items).
"""
M, C, L, S = 'M', 'C', 'L', 'S'
BASE = 0o1604                   # address of the overlay header
END = 0o30355
PREFIX = 'A'                    # FORTRAN has the names Gaaaaa, Daaaaa too
LAYOUT = [
    (0o01614, M, 'G01614'),     # ALGOL: the driver
    (0o01736, C, 'D01736'),
    (0o02000, C, 'D02000'),
    (0o02166, C, 'D02166'),     # the keyword table
    (0o02736, C, 'D02736'),
    (0o03771, C, 'D03771'),
    (0o04000, C, 'D04000'),
    (0o05754, C, 'D05754'),
    (0o06000, C, 'D06000'),
    (0o12000, S, 'G12000'),     # ASMPRINT
    (0o12323, C, 'D12323'),     # D45026, its tables
    (0o13666, M, 'G13666'),
    (0o14504, M, 'G14504'),
    (0o17223, M, 'G17223'),
    (0o22162, M, 'G22162'),
    (0o23523, M, 'G23523'),
    (0o26260, M, 'G26260'),
    (0o26666, M, 'G26666'),
    (0o27126, M, 'G27126'),
    (0o27220, M, 'G27220'),
    (0o27245, C, 'D27245'),
    (0o27645, M, 'G27645'),
    (0o27733, M, 'G27733'),
    (0o30001, M, 'G30001'),
    (0o30034, M, 'G30034'),
    (0o30120, M, 'G30120'),
    (0o30257, M, 'G30257'),
]
RENAME = {'G01614': 'ALGOL'}
# the names of the S module and of its entries, at their addresses here
RENAME.update({'G12000': 'ASMPRINT', 'G12001': 'G44504', 'D12323': 'D45026'})
SPATH = ['../asembler']
LOW = 'dubna'                   # Dubna resident: MONITOR*, /MONTRAN
