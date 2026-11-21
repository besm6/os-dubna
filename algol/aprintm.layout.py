"""
A/PRINTM of the Dubna installation tape (monsys.9), loaded at 30355 after
ALGOL: the listing of the object code that *FULL asks for. G31206 is a copy
of G27733 of ALGOL. The modules are made from the disassembly (M items).
"""
M, C, L, S = 'M', 'C', 'L', 'S'
BASE = 0o30355                  # address of the overlay header
END = 0o31646
ROOT = 'algol'
LAYOUT = [
    (0o30365, M, 'G30365'),     # A/PRINTM
    (0o31206, M, 'G31206'),
    (0o31254, M, 'G31254'),
    (0o31307, M, 'G31307'),
    (0o31341, M, 'G31341'),
    (0o31375, M, 'G31375'),
    (0o31421, M, 'G31421'),
]
RENAME = {'G30365': 'A/PRINTM'}
LOW = 'dubna'                   # Dubna resident: MONITOR*, /MONTRAN
