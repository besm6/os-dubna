"""WRITLIB*: the compiler's standard array goes from drum 10 into the temporary library on drum 21."""

from svg import Figure, LARGE, BLUE, GREEN, YELLOW, ORANGE, GRAY, GREY


def main():
    f = Figure(980, 500, LARGE)
    # Column 1: the compiler and its output.
    f.box(20, 30, 200, 64, GRAY, "compiler\nFORTRAN, ALGOL …", 10)
    f.box(20, 180, 200, 64, ORANGE, "drum 10\nstandard array", 10)
    f.arrow(120, 94, 120, 178)
    f.lines(130, 142, ["writes"], 9, fill=GREY, anchor="start")
    # Column 2: memory of the section.
    f.box(300, 30, 220, 64, YELLOW, "CATALOG, 06000\ncopy of the catalog", 10)
    f.box(300, 180, 220, 64, BLUE, "BUFFER, 02000\none zone", 10)
    f.box(300, 330, 220, 64, GREEN, "WRITLIBR\nword by word", 10)
    f.arrow(220, 212, 298, 212)
    f.lines(259, 200, ["*70"], 9, fill=GREY, mono=True)
    f.arrow(410, 244, 410, 328)
    f.lines(420, 292, ["FORTLIBR"], 9, fill=GREY, anchor="start", mono=True)
    f.curve(520, 345, 580, 320, 580, 140, 480, 96)
    f.lines(588, 230, ["entries"], 9, fill=GREY, anchor="start")
    # Column 3: drum 21, the temporary library.
    f.box(600, 30, 360, 64, ORANGE, "drum 21, zone 0\ncatalog of the temporary library", 10)
    f.box(600, 330, 160, 64, GRAY, "page 76000\nexchange page", 10)
    f.box(820, 330, 140, 64, ORANGE, "drum 21\nfrom zone 2", 10)
    f.arrow(520, 62, 598, 62, both=True)
    f.lines(559, 50, ["*70"], 9, fill=GREY, mono=True)
    f.lines(780, 122, ["read first, written back at the end"], 9, fill=GREY)
    f.arrow(520, 362, 598, 362)
    f.arrow(760, 362, 818, 362)
    f.lines(789, 350, ["*70"], 9, fill=GREY, mono=True)
    # The saved page.
    f.box(600, 430, 160, 54, GRAY, "drum 20, zone 4", 9.5)
    f.arrow(680, 394, 680, 428, both=True)
    f.lines(692, 418, ["root: *70 46B, 45B"], 9, fill=GREY, anchor="start", mono=True)
    f.write()


main()
