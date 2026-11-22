"""The catalog of the temporary library before and after WRITLIB* writes module SUB with entry SUBE."""

from svg import Figure, LARGE, GREEN, YELLOW, GRAY, GREY, RED


def table(f, x, y, rows):
    h = 40
    for name, info, colour in rows:
        if info is None:
            f.box(x, y, 340, h, colour, name, 9, mono=True)
        else:
            f.box(x, y, 150, h, colour, name, 9, mono=True)
            f.box(x + 150, y, 190, h, colour, info, 9)
        y += h
    return y


def main():
    f = Figure(980, 330, LARGE)
    f.text(190, 30, "before", 10)
    f.text(790, 30, "after", 10)
    table(f, 20, 50, [
        ("word 0: free place on drum", None, GRAY),
        ("word 1", None, GRAY),
        ("ALPHA", "module", YELLOW),
        ("SUB", "old module", YELLOW),
        ("7777 7777 7777 7777", None, GRAY),
    ])
    table(f, 620, 50, [
        ("word 0: free place on drum", None, GRAY),
        ("word 1", None, GRAY),
        ("SUB", "new module", GREEN),
        ("SUBE", "its entry", GREEN),
        ("ALPHA", "module", YELLOW),
        ("7777 7777 7777 7777", None, GRAY),
    ])
    f.line(20, 190, 360, 190, stroke=RED, width=2)
    f.arrow(380, 150, 598, 150)
    f.text(490, 138, "WRITLIB*", 9.5, mono=True)
    f.text(490, 180, "new pairs at the head", 8.5, fill=GREY)
    f.text(490, 205, "same name further", 8.5, fill=GREY)
    f.text(490, 225, "down: deleted", 8.5, fill=GREY)
    f.text(20, 315, "Two words per name: the name in TEXT and an info word. All ones end the catalog.",
           8.5, fill=GREY, anchor="start")
    f.write()


main()
