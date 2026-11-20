"""
FORTRAN of the Dubna installation tape (monsys.9), loaded at 01604 under
/MONTRAN: the root overlay of the compiler. Its head (01614-02136) is a
driver and the first 037 words of D02144 (the rest of that block, the
variables of CBDPR, lie in the low memory, 0214-0333). DATAPR is DATAPR*
of /MONTRAN. The modules made from the disassembly are M items, those whose
Madlen files are kept as they are S items.
"""
M, C, L, S = 'M', 'C', 'L', 'S'
BASE = 0o1604                   # address of the overlay header
END = 0o34570
LAYOUT = [
    (0o01614, M, 'G01614'),     # FORTRAN: the driver
    (0o02100, C, 'D02144'),
    (0o02137, M, 'G02137'),     # SCANSTMT: D02144 is shorter here
    (0o03465, C, 'D03740'),
    (0o04022, S, 'G04022'),     # SYMOUT
    (0o04134, S, 'G04134'),     # PUTAWAY
    (0o06134, S, 'G06134'),     # WRDECL
    (0o06135, M, 'G06135'),     # WROUT: templates with addresses
    (0o06210, M, 'G06210'),     # ERRCODE: the data of D33143, D34621
    (0o06213, C, 'D06466'),
    (0o06363, C, 'D06636'),     # IFLIST
    (0o07154, C, 'D07427'),
    (0o07715, C, 'D10170'),
    (0o23165, C, 'D23440'),     # DIMENLIS
    (0o32224, C, 'D32477'),
    (0o32670, C, 'D33143'),
    (0o33230, S, 'G33230'),     # BANNER
    (0o33242, C, 'D33515'),
    (0o33276, S, 'G33276'),     # GETCARD
    (0o33300, S, 'G33300'),     # ADDTEXT
    (0o33337, S, 'G33337'),     # LISTCARD
    (0o33465, S, 'G33465'),     # ERRVEC
    (0o33471, L, 'G33471'),     # DUBLPREC
    (0o33723, L, 'G33723'),     # D*PO*I
    (0o33770, S, 'G33770'),     # PUTNAME
    (0o33776, S, 'G33776'),     # PUTSYMB
    (0o34012, S, 'G34012'),     # DBGPRINT
    (0o34045, S, 'G34045'),     # ERRPRINT
    (0o34333, M, 'G34333'),     # DECTEXT: an address in its data
    (0o34346, C, 'D34621'),
    (0o34463, C, 'D34756'),
    (0o34464, C, 'D34757'),
    (0o34467, C, 'D34762'),
    (0o34473, S, 'G34473'),     # DBGSTUB
    (0o34474, C, 'D34767'),
    (0o34477, S, 'G34477'),     # OCTTODEC
    (0o34530, L, 'G34530'),     # SDEC
]
RENAME = {'G01614': 'FORTRAN', 'G02137': 'SCANSTMT', 'G06135': 'WROUT',
          'G06136': 'WRLIST', 'G06210': 'ERRCODE', 'G34333': 'DECTEXT',
          'D06636': 'IFLIST', 'D23440': 'DIMENLIS'}
LIB = {
    0o33471: ('DUBLPREC', {0o1: 'D*AD*D', 0o104: 'D*MU*D', 0o116: 'D*DI*D',
                           0o134: 'D*SU*D', 0o165: 'D*COMP', 0o167: 'D*LN*D',
                           0o173: 'D*LO*D', 0o175: 'D*ST*D'}),
    0o33723: ('D*PO*I', {}),
    0o34530: ('SDEC', {}),        # SDEC* is its entry at +0
}
# the names of the S modules and of their entries, at their addresses here
RENAME.update({'G04022': 'SYMOUT', 'G04134': 'PUTAWAY', 'G06134': 'WRDECL',
               'G33230': 'BANNER', 'G33276': 'GETCARD', 'G33300': 'ADDTEXT',
               'G33337': 'LISTCARD', 'G33465': 'ERRVEC', 'G33770': 'PUTNAME',
               'G33776': 'PUTSYMB', 'G34012': 'DBGPRINT',
               'G34013': 'DBGDUMP', 'G34014': 'DBGHOOK',
               'G34045': 'ERRPRINT', 'G34047': 'ERRPRIN2',
               'G34473': 'DBGSTUB', 'G34477': 'OCTTODEC'})
# the places here that the S modules call by these names
ALIASES = {0o6136: 'WRLIST'}
LOW = 'dubna'                   # Dubna resident: MONITOR*, /MONTRAN
# the error routines: ERRVEC, ERRPRINT, ERRPRIN2, ERRCODE, 05130 (inside PUTAWAY), 03207 (the common error exit of SCANSTMT)
ERRCALLS = [0o33465, 0o34045, 0o34047, 0o06210, 0o05130, 0o03207]
NUMBERS = [0o03224]             # error number 5003, kept in a cell
ERRMSG = 'errmsg.txt'
