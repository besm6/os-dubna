"""
CBDPR: the declarations, of the Dubna installation tape (monsys.9). The
variables of the block D02144 past its first 037 words lie in the low
memory (0214-0333), not in the root. The modules are made from the
disassembly (M items) except MKITEM, PUTLABEL and LABTEXT, whose Madlen
files are kept as they are (S items).
"""
M, C, L, S = 'M', 'C', 'L', 'S'
BASE = 0o34570                  # address of the overlay header
END = 0o40645
ROOT = 'fortran'
LAYOUT = [
    (0o34600, M, 'CBDPR'),
    (0o35417, C, 'D35713'),
    (0o35434, M, 'G35434'),     # CBPROC
    (0o35554, M, 'G35554'),     # CBBSS
    (0o35616, M, 'G35616'),     # CBCE
    (0o35716, M, 'G35716'),     # CBEQU
    (0o35761, C, 'D36255'),
    (0o36023, M, 'G36023'),     # CDIMSR
    (0o36042, M, 'G36042'),     # CFRCH
    (0o36074, M, 'G36074'),     # CBTRACE
    (0o36102, M, 'G36102'),     # CBERROR
    (0o36106, S, 'G36106'),     # MKITEM
    (0o36112, M, 'G36112'),     # CBPRCZ
    (0o40432, M, 'G40432'),     # PUTDAT
    (0o40441, C, 'D40735'),
    (0o40531, S, 'G40531'),     # PUTLABEL
    (0o40623, S, 'G40623'),     # LABTEXT
    (0o40644, C, 'D41140'),
]
RENAME = {
    'G35434': 'CBPROC', 'G35554': 'CBBSS', 'G35616': 'CBCE', 'G35716': 'CBEQU',
    'G36023': 'CDIMSR', 'G36042': 'CFRCH', 'G36112': 'CBPRCZ', 'G37022': 'CBPRDM',
    'G36074': 'CBTRACE', 'G36102': 'CBERROR', 'G37472': 'MKITEM2',
    'G37236': 'CBDUMP', 'G40432': 'PUTDAT',
}
# the names of the S modules and of their entries, at their addresses here
RENAME.update({'G36106': 'MKITEM', 'G40531': 'PUTLABEL', 'G40621': 'D41115',
               'G40623': 'LABTEXT'})
LOW = 'dubna'                   # Dubna resident: MONITOR*, /MONTRAN
ERRCALLS = [0o36102]            # CBERROR (and those of the root)
