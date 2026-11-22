"""How the section WRITLIB* is built: three sources, three perso tapes, COLLECT."""

from svg import Figure, LARGE, BLUE, GREEN, YELLOW, ORANGE, GRAY, GREY


def main():
    f = Figure(980, 380, LARGE)
    src = [
        ("writlib/writlib.asm\nroot WRITLIB*", "tape 244\nunit 44", "mk-ms-img.sh"),
        ("besmmons/system2.txt\nWRITLIBR, CATALOG", "tape 200\nperso of the MS", "mk-ms-src.sh"),
        ("besml21/libra211.l21\nFORTLIBR", "tape 221\nunit 61", "mk-lib21-src.sh"),
    ]
    for i, (s, t, script) in enumerate(src):
        y = 20 + i * 100
        f.box(20, y, 220, 64, GRAY, s, 8.5, mono=False)
        f.box(400, y, 150, 64, YELLOW, t, 9.5)
        f.arrow(240, y + 32, 398, y + 32)
        f.text(319, y + 24, script, 8, fill=GREY, mono=True)
        f.arrow(550, y + 32, 628, 152)
    f.box(630, 120, 150, 64, BLUE, "COLLECT\nWRITLIB*:44,61", 9.5)
    f.box(820, 120, 145, 64, GREEN, "COMTODRU\nms-splice.py", 9)
    f.arrow(780, 152, 818, 152)
    f.box(820, 230, 145, 64, ORANGE, "tape 203\nzone 77.26", 9.5)
    f.arrow(892, 184, 892, 228)
    f.text(20, 345, "Check: make in writlib/ links the same section under dubna and compares it",
           8.5, fill=GREY, anchor="start")
    f.text(20, 368, "with the archived tape monsys/monsys.9: GOOD.", 8.5, fill=GREY, anchor="start")
    f.write()


main()
