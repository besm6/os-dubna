# Building and Booting OS Dubna on SIMH

> Written for this repository. It describes how the scripts in [BUILD/](../BUILD) turn the
> archived sources into a system that boots on the SIMH `besm6` simulator, as of November
> 2026.

The build has two halves. First, the dispatcher (DD) and the standard tasks are compiled and
linked under the `dispak` simulator, which runs a different BESM-6 OS (Диспак). Then the
result is booted in SIMH. There OS Dubna builds the rest of itself: the task library and a
dispatcher linked by its own tools.

```sh
cd BUILD && ./bootstrap.sh     # about 20 minutes
besm6 dubna.ini                # run the system
```

## 1. Under dispak

All jobs are Диспак batch jobs. Their listings land in `BUILD/*.list`; errors show there, not
in exit codes. Tapes live in `BUILD/tapes/`, named by number (`ReadMeTapes.txt`; the map is
also in `CLAUDE.md`). `env.sh` points `dispak` and `besmtool` there.

| Step | What it does |
| --- | --- |
| `populate-dsk.sh` | Writes the archived tape images 9/MONSYS, 12 and 37/LIBRAR. |
| `mk-dd-src.sh` | Loads the DD sources (`besmdisp/`) to tape 1400 and compiles them. |
| `mk-stl-src.sh` | The same for the standard tasks (`besmtask/`), tape 1247. |
| `mk-ld-src.sh` | The loader, tape 1100. |
| `data/mkdisk9.sh`, `mkdisk11.sh`, `mkbridges.sh` | Disk images and bridge tapes (below). |
| `deck-b1/mk-deck-b1.sh` | Writes the patch deck job `deck-b1.b6`. |
| `debmult.b6` | Runs DEBMULT, a separate job because of Диспак. |
| `deck-b1.b6` | Compiles the patch modules and links DD onto tape 1999, with the Monitor System. |

The patch deck holds whole replacement modules, compiled after the archived ones:

| File | Content |
| --- | --- |
| `conf-sys.s` | Configuration. `*DRUMBAS` (`,LOG,12000 67000`): write DD with the system to tape 1999, base drum 20. |
| `conf-tty.s`, `fix-tty.s` | Terminal lines: the two Consuls, tty25 and tty26. |
| `fix-dsk.s` | Disk driver changes for SIMH. |
| `fix-io.s` | Main I/O task changes. |
| `fix-misc.s` | Bootstrap settings, Multitype configuration. |
| `fix-aux.s` | `SPECMON` with the monitor common blocks pinned to the Monitor Dubna addresses (`INFLOAD*` 716 and others). Linked against Диспак's monitor they landed elsewhere, and the task launcher crashed. |

`deck-b1/deck.notes` lists the restrictions of this build: the date accepts only 1989, the
clock is assumed to run at 300 Hz, and so on.

## 2. The images

### Disks

`data/mkdisk9.sh` concatenates a catalog, 9/MONSYS and filler into `disk9.bin` (SIMH `md00`);
`mkdisk11.sh` does the same with the libraries for `disk11.bin` (`md04`). DD models tapes as
files on these disks. At boot it lists them on the console:

| Model | Disk | Use |
| --- | --- | --- |
| `MONSYS/9` | 9 | Monitor System; also models MS drums 21, 22 (ТР2 bits 41, 40). |
| `D73LIB/5` | 9 | Task library (STL), built by job `newbsz`. |
| `M/7` | 9 | Multitype buffer, disk zones 0700–1077: user decks. |
| `D73INP/1` | 9 | Input file: queued jobs. |
| `D73OUT/3` | 9 | Output file: listings waiting for the printer. Zones 1200–1377. |
| `D73STA/6`, `USESTA/0` | 9 | Statistics. |
| `LINBUF/1` | 9 | Screen editor buffers; also carries perso for the rebuild jobs. |
| `ROLLIB/1` | 9 | Roll tracks. |
| `LIBRAR/2`, `LIBRAR/7`, `CATALO/8` | 11 | Libraries. |

Bridge tapes 2209 and 2211 are symlinks to the two disk images, so a `dispak` job can write
into them. `tra-libs.b6` copies libraries and the rebuild jobs this way, and `put-job.sh deck
[zone]` puts a user deck into 7/M.

### Drums

`data/mkdrumdd.sh` cuts the drum images out of tape 1999. Each image file holds 256 zones;
the second half repeats the first.

| File | SIMH unit | Drums | Content |
| --- | --- | --- | --- |
| `dubdrum1.bin` | `drum0` | 10–17 | Working drums: paging, Multitype polling. |
| `dubdrum2.bin` | `drum1` | 20–27 | 20: DD (zones 0–34) and Multitype data; 21, 22: Monitor System; 23: password and name tables, Multitype; 25: the rebuilt DD. |

A zone in the file is 64 bytes of header and 1024 words of 8 bytes, little-endian, the
48-bit value in the low bits. Drum 25 starts at zone 0240 of `dubdrum2.bin`.

The link job copies MS zones 40–77 from the wrong tape, so `mkdrumdd.sh` overlays drum 22
from `mons9.d9`.

## 3. Booting in SIMH

`boot-run.ini` (scripted) and `dubna.ini` (interactive) do the same steps:

1. **Simulator settings.** `set cpu mem=128`: DD keeps flags in the page-number bits above 7,
   which a bigger memory would take as address bits. `set cpu ext32`: DD drives the printer
   with instruction 032, which current SIMH would otherwise send to КАДОПАМ. Terminals are
   `unicode,authbs`, so Cyrillic can be typed or sent.
2. **Clear page 0** with a three-instruction loop at 1–3 (`run 1`).
3. **Read DD from the drum** with panel program 9 (`set cpu pult=9`). `pult9.b6` puts the
   drum control word into ТР7: `0140 0000` reads drum 20, `0140 1200` (`pult9-25.b6`)
   drum 25.
4. **Switch registers** from `boot_dubna.b6` or `boot_dubna-25.b6`; their meaning is in
   [Switch_Registers.md](Switch_Registers.md). The drum-20 boot sets ТР2 `3730…`, which
   cleans the catalogs and takes the MS drums from 9/MONSYS. The drum-25 boot has `0730…`,
   which keeps the input and output catalogs.
5. **Start at 1000.** `STARTDD` checks the sum of the image against word 0101 and halts at
   `STARTDD`+7 on a mismatch; the 2017 scripts also deposit `7777…` at 2257.
6. **Operator dialogue** on tty25: the banner, the tape models, then empty line → `!!!`,
   `040489D` (date), `T`. DD reports `Д-2000 МС-Ф10` (`Д-2500` from drum 25) and
   `ВЫВОД БУФЕРИЗОВАН`.
7. **Print spooler.** Task 11 (`SPECMON`) loads `TASK11` from D73LIB. With an empty library
   it prints `ТАSК!`; otherwise it asks `УСТАНОВИТЕ ЛИСТ НА АЦПУ-1, ЗАТЕМ ДАЙТЕ ПРИКАЗ А1Р`.
8. **`ПЛАНИРОВЩИК`**: the planner runs. An `expect` rule then sets ТР3 `7777 7777 0000 0000`
   (privileged physical exchanges for all task slots; job `newdd` needs them) and ТР6
   `…4000 0160` (no resource check).

Drum 25 stays locked by ТР1 (`…0364`). The 2017 scripts unlocked it at this point, but an
open drum receives paging tracks: with 128K of memory, the system paged `newdd`'s memory onto
drum 25 while the job wrote the dispatcher there. A locked drum still takes physical
exchanges from a privileged job.

## 4. The rebuild in SIMH

`mk-base.sh` makes fresh images, runs `tra-libs.b6` (jobs `newdd` and `newbsz` into 7/M zones
100 and 105) and `put-job.sh hello.dub 110`, then boots drum 20 twice through `mt-run.py`:

1. **`newbsz`** links the standard tasks (compiled under dispak, perso on 11/LINBUF) with the
   Monitor Dubna loader into the task library 5/D73LIB. It must run in SIMH: `dispak` has no
   Monitor Dubna loader. On this first boot there is no spooler yet.
2. **`newdd`** compiles `*DRUMBAS` with `,LOG,2500` (drum 25, track 0), links DD and writes it:
   `ОС 'ДУБНА' НА 25/000-037/. Д=035 ЗОН.` Its listing is printed: about 1400 lines, most of
   the quarter hour this step takes.

Each job is queued with `ПУС` and started at once with the operator order `{}БП`: both ask
for 24 minutes, and in debug mode (ТР6 bit 6) the planner starts such jobs only on Ш01. The images are then saved
in `data/base/`. These images are kept in the repository, so a user can run the system with
the simulator alone.

## 5. Running

- `besm6 dubna.ini`: the system from drum 25. The terminal is the operator console;
  Multitype is on telnet port 4199 (two spaces, password `MJPOP`, buffer `7/M`). Listings go
  to `output.txt`. The images are changed in place; `cp data/base/*.bin data/` restores them.
- `./mt-run.py [zone]`: boots with `boot-run.ini` and runs the deck at 7/M `zone` (default
  110, hello). Python listens on two ports and SIMH dials out to them, so both Consuls are
  driven by send/expect. Options are environment variables, listed in the script:
  `FRESH=1` (start from `data/base`), `DRUM=25`, `SUBMIT=ПУС` (queue the job, so it is
  printed), `CONSUBMIT`, `POLL`, `BEFORE`, `AFTER`, `JOBWAIT`, `POLLS`, `PRNWAIT`, `SLOW`.
  Transcripts go to `mt-run-tty25.txt` and `mt-run-tty26.txt`.

`FRESH=1 DRUM=25 SUBMIT=ПУС ./mt-run.py` checks the whole chain in about a minute: hello is
compiled, run and printed on `output.txt`.

Commands and replies on both lines are in [Dubna_Commands.md](Dubna_Commands.md).

## Pitfalls

- Stop SIMH with `quit`. Killed, it loses buffered writes to the images.
- SIMH probes a `Connect=` address at attach time and hangs up; the real connection comes
  later (`mt-run.py` waits for the banner).
- Jobs started with `СЛА` or `RUN` never print: their printer output is blocked. Use `ПУС`.
- A Multitype listing that fills a page waits for a key; the first character typed after it
  is lost.
- An operator order like `NNБП` sent before the job is ready for planning is ignored.
- Each `mt-run.py` run recreates `output.txt` and the transcripts.
