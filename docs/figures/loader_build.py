"""How the two pages of the dynamic loader are built: loader.txt → tape 101 → 9/MONSYS."""

from svg import Figure, LARGE, BLUE, GREEN, YELLOW, ORANGE, GRAY, GREY


def main():
    f = Figure(980, 470, LARGE)
    # Row 1: source and editions.
    f.box(20, 30, 170, 64, GRAY, "loader.txt\n2024 lines", 10.5)
    f.box(260, 30, 170, 64, YELLOW, "tape 100\nfrom zone 100", 10.5)
    f.lines(345, 118, ["mk-ld-src.sh"], 9.5, fill=GREY, mono=True)
    f.arrow(190, 62, 258, 62)
    f.box(500, 8, 210, 50, BLUE, "LOADER\nlines 84–376 cut", 10)
    f.box(500, 68, 210, 50, GREEN, "REDUOL\nlines 377–728 cut", 10)
    f.arrow(430, 55, 498, 33)
    f.arrow(430, 69, 498, 93)
    f.lines(465, 18, ["*EDIT"], 9.5, fill=GREY, mono=True)
    f.box(780, 30, 180, 64, YELLOW, "tape 101\nperso, zone 100", 10.5)
    f.arrow(710, 33, 778, 55)
    f.arrow(710, 93, 778, 69)
    f.lines(745, 18, ["*MADLEN"], 9.5, fill=GREY, mono=True)
    f.lines(870, 118, ["job 1"], 9.5, fill=GREY, anchor="start")
    # Row 2: loading at 66000.
    f.box(20, 200, 210, 64, GRAY, "LDSHIFT\naddresses ≥ 60000 +10000", 10)
    f.box(300, 190, 230, 40, BLUE, "NEWLDR: LOADER at 66000", 9.5)
    f.box(300, 236, 230, 40, GREEN, "NEWLDRS: REDUOL at 66000", 9.5)
    f.arrow(230, 220, 298, 210)
    f.arrow(230, 244, 298, 256)
    f.box(600, 190, 150, 40, ORANGE, "drum 25, zone 35", 9.5)
    f.box(600, 236, 150, 40, ORANGE, "drum 25, zone 36", 9.5)
    f.arrow(530, 210, 598, 210)
    f.arrow(530, 256, 598, 256)
    f.lines(565, 300, ["page 33"], 9.5, fill=GREY)
    f.box(820, 200, 140, 64, YELLOW, "tape 101\nzones 0, 1", 10.5)
    f.arrow(750, 210, 818, 222)
    f.arrow(750, 256, 818, 244)
    f.lines(785, 300, ["LDWRITE"], 9.5, fill=GREY, mono=True)
    f.lines(140, 300, ["job 2"], 9.5, fill=GREY)
    f.curve(820, 96, 800, 160, 140, 140, 125, 196, stroke=GREY, dash="4 3")
    # Row 3: splice.
    f.box(300, 370, 230, 64, BLUE, "ms-splice.py\nzone 0, zone 1 words 0–377", 10)
    f.box(620, 370, 200, 64, GREEN, "tape 203\ndata/mons9.bin", 10.5)
    f.curve(890, 266, 890, 330, 600, 330, 532, 392)
    f.arrow(530, 402, 618, 402)
    f.lines(150, 395, ["mk-ms-img.sh: the rest of", "zones 0–77 from COLLECT"], 9.5, fill=GREY)
    f.write()


main()
