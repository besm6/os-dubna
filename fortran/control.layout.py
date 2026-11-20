"""
CONTROL: the executable statements, of the Dubna installation tape
(monsys.9). The modules that hold addresses in their data (code that the
listing shows as data, tables of instruction templates) are made from the
disassembly (M items), the Madlen files of the others are kept as they are
(S items).
"""
M, C, L, S = 'M', 'C', 'L', 'S'
BASE = 0o34570                  # address of the overlay header
END = 0o51470
ROOT = 'fortran'
LAYOUT = [
    (0o34600, M, 'G34600'),     # CONTROL
    (0o37656, M, 'G37656'),     # G40152
    (0o40511, M, 'G40511'),     # ASSIGNST
    (0o40605, S, 'G40605'),     # IFSTMT
    (0o40700, M, 'G40700'),     # ARITHEXP
    (0o42244, M, 'G42244'),     # OPERAND
    (0o44176, M, 'G44176'),     # FUNCREF
    (0o44457, S, 'G44457'),     # PUTOP
    (0o44467, S, 'G44467'),     # ERRJUMP
    (0o44472, S, 'G44472'),     # ASFTRACE
    (0o44521, M, 'G44521'),     # G45015
    (0o44537, C, 'D45033'),
    (0o44667, M, 'G44667'),     # LOGEXPR
    (0o45564, S, 'G45564'),     # IFLTRACE
    (0o45613, M, 'G45613'),     # G46107
    (0o46510, S, 'G46510'),     # TABTRACE
    (0o46523, C, 'D47017'),
    (0o47713, M, 'G47713'),     # PROSIG
    (0o47740, C, 'D50234'),
    (0o50205, S, 'G50205'),     # G50501
    (0o50214, S, 'G50214'),     # G50510
    (0o50223, S, 'G50223'),     # G50517
    (0o50235, S, 'G50235'),     # G50531
    (0o50314, S, 'G50314'),     # G50610
    (0o50341, S, 'G50341'),     # G50635
    (0o50361, S, 'G50361'),     # G50655
    (0o50400, S, 'G50400'),     # G50674
    (0o50445, M, 'G50445'),     # G50741
]
RENAME = {}
RENAME.update({'G%05o' % (int(k[1:], 8) - 0o274): v for k, v in {
    'G35074': 'CONTROL', 'G41005': 'ASSIGNST', 'G41101': 'IFSTMT',
    'G41174': 'ARITHEXP', 'G42540': 'OPERAND', 'G44472': 'FUNCREF',
    'G44753': 'PUTOP', 'G44763': 'ERRJUMP', 'G44766': 'ASFTRACE',
    'G45163': 'LOGEXPR', 'G46060': 'IFLTRACE', 'G47004': 'TABTRACE',
    'G50207': 'PROSIG'}.items()})
# the modules without a name keep the names in their Madlen files
RENAME.update({'G37656': 'G40152', 'G44521': 'G45015', 'G45613': 'G46107',
               'G50445': 'G50741'})
BASES = {0o40700: 7,             # ARITHEXP: уиа ARITHEXP+6(М7), see arithexp.dtr
         0o42244: 7,             # OPERAND: уиа OPERAND+2(М7), see operand.dtr
         0o44176: 7}             # FUNCREF: уиа FUNCREF+5(М7), see funcref.dtr
OWNER = {0o46523: 0o45613}       # the tables after TABTRACE belong to G46107
ERRCALLS = [0o44467, 0o44471]    # jumps to ERRPRINT and ERRPRIN2
# the names of the S modules and of their entries, at their addresses here
RENAME.update({'G37643': 'D40137', 'G45612': 'D46106', 'G50205': 'G50501',
               'G50214': 'G50510', 'G50221': 'D50515', 'G50223': 'G50517',
               'G50224': 'G50520', 'G50235': 'G50531', 'G50236': 'G50532',
               'G50314': 'G50610', 'G50315': 'G50611', 'G50341': 'G50635',
               'G50361': 'G50655', 'G50400': 'G50674', 'G51340': 'D51634',
               'G51345': 'D51641'})
# the places here that the S modules call by these names
ALIASES = {0o37643: 'D40137', 0o51340: 'D51634', 0o51345: 'D51641'}
LOW = 'dubna'                   # Dubna resident: MONITOR*, /MONTRAN
