"""The address space of a job under Monitor Dubna (not to scale)."""

from svg import Figure, LARGE, BLUE, GREEN, YELLOW, ORANGE, GRAY, GREY, INK


def hatch(f, x, y, w, h, step=14):
    """Diagonal lines inside a rectangle."""
    for k in range(-h, w, step):
        x1, y1 = x + max(k, 0), y + max(-k, 0)
        x2, y2 = x + min(k + h, w), y + min(h, w - k)
        f.line(x1, y1, x2, y2, stroke="#c8c8c8", width=1)


def band(f, y, h, colour, label, lo, hi=None, note=None):
    f.box(200, y, 300, h, colour, label, 10)
    if hi:
        f.text(190, y + 12 * f.scale * 0.8, hi, 9.5, anchor="end", mono=True)
    f.text(190, y + h - 4, lo, 9.5, anchor="end", mono=True)
    if note:
        f.lines(520, y + h / 2 - (len(note) - 1) * 7 + 4, note, 9, fill=GREY, anchor="start")


def main():
    f = Figure(900, 640, LARGE)
    band(f, 10, 50, ORANGE, "exchange page / loader", "76000", "77777",
         ["page 37: the monitor's buffers;", "the loader while it runs"])
    f.rect(200, 60, 300, 120, fill="white", stroke=GREY)
    hatch(f, 200, 60, 300, 120)
    f.box(260, 100, 180, 40, GRAY, "hole", 10)
    f.lines(520, 100, ["unmapped: a trap on access;", "FULLMEMORY, FICMEMORY,", "ALLMEMORY give part of it"],
            9, fill=GREY, anchor="start")
    band(f, 180, 60, GREEN, "stack (магазин) ↑", "53401", None,
         ["register 15; grows upward"])
    band(f, 240, 100, GRAY, "free", "", "53377",
         ["limit in 16B (AU)"])
    f.arrow(450, 335, 450, 290, stroke=INK)
    band(f, 340, 130, BLUE, "program, its modules,\ncommon blocks", "01000", None,
         ["placed upward by the loader;", "first free address in 17B (AP),", "СВОБОДНО in the load map",
          "", "before that: /MONTRAN, STAR*,", "a compiler — one at a time"])
    band(f, 470, 50, YELLOW, "resident monitor", "00423", None, ["MONITOR*, INFLOAD* at 716/717"])
    band(f, 520, 30, YELLOW, "resident data", "00300")
    band(f, 550, 30, GRAY, "S area", "00100")
    band(f, 580, 40, GRAY, "tuning constants", "00000", None, ["the loader's work cells 2B–74B"])
    f.write()


main()
