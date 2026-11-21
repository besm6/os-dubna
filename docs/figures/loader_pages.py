"""Where the dynamic loader lives: drum 21 zones 0, 1 and 6, drum 20, memory pages 1 and 37."""

from svg import Figure, LARGE, BLUE, GREEN, YELLOW, GRAY, GREY, INK


def main():
    f = Figure(1060, 480, LARGE)
    # Drum 21 = 9/MONSYS.
    f.text(130, 26, "drum 21 (9/MONSYS)", 10.5, weight="bold")
    f.box(20, 40, 220, 32, GREEN, "zone 1, 0–377: REDUOL", 9)
    f.box(20, 72, 220, 30, GRAY, "zone 1, 400–1777: tables", 9)
    f.box(20, 120, 220, 70, BLUE, "zone 0\nLOADER", 10.5)
    f.box(20, 290, 220, 60, YELLOW, "zone 6\nlibrary search", 10.5)
    # Memory.
    f.text(730, 26, "memory", 10.5, weight="bold")
    f.box(600, 40, 260, 32, GREEN, "76000–76377", 9.5, mono=True)
    f.box(600, 72, 260, 118, BLUE, "76400–77777\n\npage 37", 9.5, mono=True)
    f.box(600, 290, 260, 60, YELLOW, "02000–03777\npage 1", 9.5, mono=True)
    # Exchanges with drum 21.
    f.arrow(240, 155, 598, 155)
    f.text(420, 146, "1. *70 61B: the whole page", 9.5)
    f.arrow(240, 56, 598, 56)
    f.text(420, 47, "3. at the end: the print part", 9.5)
    f.arrow(240, 320, 598, 320)
    f.text(420, 311, "4b. *70 74B: library search", 9.5)
    f.lines(730, 220, ["2. LOAD reads tables and", "modules into free pages"], 9, fill=GREY)
    # Drum 20.
    f.text(730, 400, "drum 20", 10.5, weight="bold")
    f.box(600, 410, 120, 44, GRAY, "zone 26", 10)
    f.box(740, 410, 120, 44, GRAY, "zone 4", 10)
    f.path("M860,100 L920,100 L920,432", stroke=GREY, width=1.2)
    f.arrow(920, 432, 862, 432, stroke=GREY)
    f.lines(930, 200, ["0. *70 46B:", "the exchange", "page out first,", "back at the", "end (45B)"], 9,
            fill=GREY, anchor="start")
    f.arrow(660, 350, 660, 408, stroke=GREY)
    f.lines(560, 375, ["4a. page 1 out first,", "back on RELOAD"], 9, fill=GREY, anchor="end")
    f.write()


main()
