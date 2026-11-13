# Building and Booting OS Dubna on SIMH

> Written for this repository. It describes how the scripts in [BUILD/](../BUILD) turn the
> archived sources into a system that boots on the SIMH `besm6` simulator, as of November
> 2026.

The build has two halves. First, the dispatcher (DD), the Monitor System (MS) and the standard tasks are compiled and
linked under the `dubna` simulator, which runs Monitor Dubna batch jobs with the extracodes
done in C++. Then the result is booted in SIMH. There OS Dubna builds the rest of itself: the task library and a
dispatcher linked by its own tools.

```sh
cd BUILD && ./bootstrap.sh     # about two minutes
besm6 dubna.ini                # run the system
```

## 1. Under dubna

All jobs are Monitor Dubna batch jobs (`.dub`), run by `run_job` from `env.sh`. Their
listings land in `BUILD/*.list`; errors show there (`БЫЛИ OШИБKИ`, `Error:`), not in exit
codes. Tapes live in `BUILD/tapes/`, named by number (`ReadMeTapes.txt`; the map is also in
`CLAUDE.md`). `env.sh` points `dubna` and `besmtool` there.

| Step | What it does |
| --- | --- |
| `populate-dsk.sh` | Writes the archived tape images 9/MONSYS, 12 and 37/LIBRAR. |
| `mk-dd-src.sh` | Puts the DD sources (`besmdisp/`) on tape 400 and compiles them. |
| `mk-ms-src.sh` | The same for the MS sources (`besmmons/`), tape 200. |
| `mk-ms-img.sh` | Assembles the MS: tapes 201–203, 922 and `data/mons9.bin` (below). |
| `mk-stl-src.sh` | The same for the standard tasks (`besmtask/`), tape 247, with Monitor Dubna's `*FOREX`. |
| `mk-ld-src.sh` | The loader, tape 100. |
| `data/mkdisk9.sh`, `mkdisk11.sh`, `mkbridges.sh` | Disk images and bridge tapes (below). |
| `deck-b1/mk-deck-b1.sh` | Writes the patch deck job `deck-b1.dub`. |
| `debmult.dub` | Runs DEBMULT. It copies the monitor's resident table into the Multitype area. |
| `deck-b1.dub` | Compiles the patch modules and links DD onto tape 999, with the Monitor System. |

The sources reach dubna as a local file: `run_src_job` concatenates them into `src.txt`,
which `*FILE:SRC,50` mounts (dubna converts it to cosy); the editor copies it to the tape
from zone 100.

The link job copies the Monitor System from units 40 and 41, the two MS drums 21 and 22.
Unit 40 is tape 203, a 9/MONSYS with the rebuilt MS; unit 41 is tape 922, the same image
from zone 40.

### The Monitor System

The MS is zones 0–77 of 9/MONSYS (drums 21 and 22): the dynamic loader and tables in
zones 0–6, the catalog of the dynamic part in 7–10, the dynamic part (166 modules) from
zone 11, the monitor page in zone 35, and the static part from zone 36 to the end:
sections `INPUTCAL`, `FORTRAN`, `CBDPR`, `CONTROL`, `ENDPRO`, `GLINK`, `ASEMBLER`, `ALGOL`,
`A/PRINTM`, `WRITLIB*`, with their catalog in zone 1 from word 1400.

`mk-ms-src.sh` compiles `besmmons/` (5 Fortran and 161 Madlen modules); the Madlen
compiler, which the job leaves in the temporary library, is taken out with `*EXCLUDE`.
`ms-check.sh` compares the result with the permanent library of the archived system: the
same 166 modules, of the same sizes except `CHKBEG*` and `EDIT***`.

`mk-ms-img.sh` runs the original tools from library 21:

```
*tape:200/ms,66
*tape:201/msimg,67,w
*tape:202/msdrum,65,w
*library:21
*library:23
*perso:66000
*call collect:670000
MONITOR*(INPUTCAL)
*end record
*call comtodru:670000,650000
```

`COLLECT` passes control to `NEW//MON`, which loads the resident `MONITOR*` afresh (it
lands at the same addresses as in the archive) and reloads `COLLECT`. That writes to
unit 67 zones 0–6 of the running system, the dynamic part with its catalog, the static
sections named on the cards, and the monitor page. `INPUTCAL` comes from library 21 and
needs `DATE` and `DTOI` from library 23. `COMTODRU` makes the drum form: catalog entries
become physical exchanges, the static part moves to the end of drum 22.

The compilers and `WRITLIB*` cannot be on the cards: they exist only as linked static
sections in the archived image, without perso or sources. So `ms-splice.py` builds the final
image: everything from the new drums, the static part and its catalog from the archive
at the old place, and in it the relinked `INPUTCAL` (the same size; six words differ). The
result goes to tape 203 and to `data/mons9.bin` for `mkdisk9.sh`.

The date in the banner of a listing, `МОНИТОРНАЯ СИСТЕМА 'Д У Б Н А' - 13/11/26`, is
the date of this assembly; the archived system shows `20/10/88`.

Until 2026 these jobs ran under `dispak`, which runs Диспак with its own monitor; DD was
linked against that monitor, and unit 41 was a Диспак system tape. dubna runs the
real Monitor Dubna from 9/MONSYS. Differences in the output: the compilation stamps in
the perso, the resident table that DEBMULT copies, and the tag bits (dubna writes every
word with the instruction tag, which SIMH accepts both for fetch and for operands).

The patch deck holds whole replacement modules, compiled after the archived ones:

| File | Content |
| --- | --- |
| `conf-sys.s` | Configuration. `*DRUMBAS` (`,LOG,12000 67000`): write DD with the system to tape 999, base drum 20. |
| `conf-tty.s`, `fix-tty.s` | Terminal lines: the two Consuls, tty25 and tty26. |
| `fix-dsk.s` | Disk driver changes for SIMH. |
| `fix-io.s` | Main I/O task changes. |
| `fix-misc.s` | Bootstrap settings, Multitype configuration. |
| `fix-aux.s` | `SPECMON` with the monitor common blocks pinned to the Monitor Dubna addresses (`INFLOAD*` 716 and others). Linked against Диспак's monitor they landed elsewhere, and the task launcher crashed. |

`deck-b1/deck.notes` lists the restrictions of this build: the date accepts only 1989, the
clock is assumed to run at 300 Hz, and so on.

## 2. The images

### Disks

`data/mkdisk9.sh` concatenates a catalog, 9/MONSYS (`mons9.bin`, with the rebuilt MS) and filler into `disk9.bin` (SIMH `md00`);
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

Bridge tapes 209 and 211 are symlinks to the two disk images, so a `dubna` job can write
into them. `tra-libs.dub` copies libraries and the rebuild jobs this way, and `put-job.sh deck
[zone]` puts a user deck into 7/M.

### Drums

`data/mkdrumdd.sh` cuts the drum images out of tape 999. Each image file holds 256 zones;
the second half repeats the first.

| File | SIMH unit | Drums | Content |
| --- | --- | --- | --- |
| `dubdrum1.bin` | `drum0` | 10–17 | Working drums: paging, Multitype polling. |
| `dubdrum2.bin` | `drum1` | 20–27 | 20: DD (zones 0–34) and Multitype data; 21, 22: Monitor System; 23: password and name tables, Multitype; 25: the rebuilt DD. |

A zone in the file is 64 bytes of header and 1024 words of 8 bytes, little-endian, the
48-bit value in the low bits. Drum 25 starts at zone 0240 of `dubdrum2.bin`.

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

`mk-base.sh` makes fresh images, runs `tra-libs.dub` (jobs `newdd` and `newbsz` into 7/M zones
100 and 105) and `put-job.sh hello.dub 110`, then boots drum 20 twice through `boot-run.py deck`,
each time with one of these jobs as a deck of punch cards:

1. **`newbsz`** links the standard tasks (compiled under dubna, perso on 11/LINBUF) with the
   Monitor Dubna loader into the task library 5/D73LIB. On this first boot there is no spooler yet.
2. **`newdd`** compiles `*DRUMBAS` with `,LOG,2500` (drum 25, track 0), links DD and writes it:
   `ОС 'ДУБНА' НА 25/000-037/. Д=035 ЗОН.` Its listing is printed: about 1400 lines.

The decks are cut out of `tra-libs.dub` and started with the operator order `01В`, which
needs neither Multitype nor the planner (queued with `ПУС` the jobs had to be pushed with
`{}БП`: both ask for 24 minutes, and in debug mode, ТР6 bit 6, the planner starts such jobs
only on Ш01). The images are then saved in `data/base/`. These images are kept in the
repository, so a user can run the system with the simulator alone. Last, `boot-run.py` boots
drum 25 and runs hello from 7/M, as a check of the new dispatcher and of Multitype. The
whole step takes about a minute and a half.

## 5. Running

- `besm6 dubna.ini`: the system from drum 25. The terminal is the operator console;
  Multitype is on telnet port 4199 (two spaces, password `MJPOP`, buffer `7/M`). Listings go
  to `output.txt`. The images are changed in place; `cp data/base/*.bin data/` restores them.
- `./boot-run.py [options] deck`: boots with `boot-run.ini` and runs a deck of punch cards
  from reader `vu0`, started by the console order `01В`; the deck ends with a line of six
  backquotes. Python listens on two ports and SIMH dials out to them, so both Consuls are
  driven by send/expect. `./boot-run.py` alone prints all options: `-f` (start from
  `data/base`), `-d 25` (boot the rebuilt DD), `-r ПВ` (send the deck through the input
  file), `-u` (punch it in the UPDK code instead of UPP), `-v` (trace the reader).
- `./boot-run.py [options] -m zone`: the job is the deck at 7/M `zone` (110 is hello),
  submitted from Multitype with `СЛА`, or with `-q` queued with `ПУС`, so it is printed;
  `-b`, `-s`, `-n`, `-p`, `-a` add Multitype commands and console orders.
- Transcripts go to `boot-run-tty25.txt` and `boot-run-tty26.txt`. The run ends on an event,
  not on a timer: `НЕТ ЗАДАЧ` for a terminal job, the trailer of the listing
  (`КОНЕЦ ЗАДАЧИ`) in `output.txt` for a queued or card job. `--jobwait` and `--prnwait`
  (600 s each) only bound a run that has gone wrong.
- `./card-run.sh job.dub`: a demo without Python. It restores `data/base`, adds the
  end-of-deck card and runs `besm6 card-run.ini deck`. The script boots drum 25 with the
  console on the terminal and plays the operator: `go until "text"` runs until the console
  prints the text, `send "text\r"` types a line (`send delay=100000`: the console takes one
  character at a time). After `-КШ01-` it steps the simulator until `fgrep` finds the
  trailer line of stars in `output.txt`; `on step` and `on error` (with `set on`) make the
  loop, since both the end of a step and a failed `!` command are errors. About 35 seconds.
- `./tape-format.sh [image]`: a demo of magnetic tapes, in the same style
  (`tape-format.ini`). It makes an empty file, a blank reel, and attaches it as `mg60`
  when the system is up; the console prints `НЕ ОПОЗН.МЛ-60`. Then it puts the drive
  number into switch register 3 and gives order `ИМР`: task 62 formats the tape and names
  it `DEMO`, reel 1234, 10 (octal) zones. The dialogue is described in
  [Dubna_Commands.md](Dubna_Commands.md#formatting-a-tape). About a minute. The image is a
  SIMH tape file with one record of 8 service words and 1024 data words per block. It needs
  a `besm6` whose formatting modes of `mg6` write real zones (November 2026), and the
  real task 62 in 5/D73LIB: until then job `newbsz` in `tra-libs.dub` put an empty stub
  in its place.

`./boot-run.py -f -d 25 -q -m 110` checks the whole chain in a little over a minute: hello is compiled, run and printed on `output.txt`.

Commands and replies on both lines are in [Dubna_Commands.md](Dubna_Commands.md).

## Pitfalls

- The card reader needs a recent simh-besm6 (November 2026): without the "feed" ready
  flag DD answers `ВУ НЕ ВКЛ`, and a reader stopped at the start of a card (DD does that
  after an end-of-deck card) must keep that card for the next start.

- Stop SIMH with `quit`. Killed, it loses buffered writes to the images.
- SIMH probes a `Connect=` address at attach time and hangs up; the real connection comes
  later (`boot-run.py` waits for the banner).
- Jobs started with `СЛА` or `RUN` never print: their printer output is blocked. Use `ПУС`.
- A Multitype listing that fills a page waits for a key; the first character typed after it
  is lost.
- An operator order like `NNБП` sent before the job is ready for planning is ignored.
- Each `boot-run.py` run recreates `output.txt` and the transcripts.
