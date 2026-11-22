"""Memory of the section WRITLIB* when it is loaded (not to scale)."""

from svg import Figure, LARGE, BLUE, GREEN, YELLOW, PURPLE, GRAY, GREY, INK


def main():
    f = Figure(980, 230, LARGE)
    parts = [  # width, colour, label, start address
        (100, GRAY, "resident", "0"),
        (70, GRAY, "head", "01604"),
        (80, PURPLE, "root", "01614"),
        (120, BLUE, "FORTLIBR", "01630"),
        (140, BLUE, "BUFFER", "02000"),
        (140, GREEN, "WRITLIBR", "04000"),
        (300, YELLOW, "CATALOG", "06000"),
    ]
    x, y, h = 15, 80, 64
    for w, c, label, addr in parts:
        f.box(x, y, w, h, c, label, 9.5)
        f.text(x, y + h + 26, addr, 8.5, fill=GREY, mono=True, anchor="start")
        x += w
    f.text(x, y + h + 26, "26000", 8.5, fill=GREY, mono=True, anchor="end")
    # Brace over the section.
    x0, x1 = 115, x
    f.line(x0, 60, x1, 60, stroke=INK)
    f.line(x0, 60, x0, 72, stroke=INK)
    f.line(x1, 60, x1, 72, stroke=INK)
    f.text((x0 + x1) / 2, 46, "section WRITLIB*: 24174 words, on the tape from zone 77, record 26", 9)
    f.text(15, 215, "BUFFER and CATALOG are zeros: the packed section is little more than the code.",
           8.5, fill=GREY, anchor="start")
    f.write()


main()
