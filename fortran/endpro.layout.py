"""
ENDPRO: the end of a unit, of the Dubna installation tape (monsys.9); the
Madlen files of all its modules are kept as they are (S items).
"""
M, C, L, S = 'M', 'C', 'L', 'S'
BASE = 0o34570                  # address of the overlay header
END = 0o36555
ROOT = 'fortran'
LAYOUT = [
    (0o34600, S, 'G34600'),     # ENDPRO
    (0o36346, S, 'G36346'),     # IDXERR
    (0o36377, S, 'G36377'),     # ENDDUMP
]
# the names of the S modules and of their entries, at their addresses here
RENAME = {'G34600': 'ENDPRO', 'G36346': 'IDXERR', 'G36377': 'ENDDUMP'}
LOW = 'dubna'                   # Dubna resident: MONITOR*, /MONTRAN
