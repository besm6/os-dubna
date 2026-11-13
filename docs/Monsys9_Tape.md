# The 9/MONSYS Tape

> Written for this repository. It describes the system tape of the Monitor System "Dubna"
> as found in `monsys/monsys.9`, and how the bootstrap rebuilds a part of it from sources,
> as of November 2026. The layout was read from the image and from the sources of the
> tools; places that were not checked are marked.

## 1. What it is

9/MONSYS is the tape (in our system, a file on disk 9) that holds the Monitor System (MS):
the program that reads a job's control cards, calls compilers, loads and starts programs.
The name means "reel 9, label MONSYS". Everything a batch job needs before its own code
runs comes from here: the monitor itself, the loaders, the runtime library, the compilers.

The tape has 288 zones (octal 0–437). Only the first 64 zones are the MS proper. The
rest are libraries and an area of the dispatcher (DD) that shares the file.

| Zones (octal) | Content | In our build |
| --- | --- | --- |
| 0–77 | The Monitor System: drums 21 and 22 | rebuilt, see section 6 |
| 100–171 | Additional static part: compilers Fortran-GDR, Forex, Pascal | binary |
| 172–237 | Library 22 (also called 24): Madlen, Pascal tools and others | binary |
| 240–317 | Library 21: system utilities | binary |
| 320–403 | Library 23 | binary |
| 400–437 | Dispatcher area: "special tracks" | binary, changed by the running system |

## 2. Units and addresses

- A **word** is 48 bits. Numbers below are octal unless said otherwise.
- A **zone** is 1024 words (2000 octal). On a drum the same thing is called a tract.
- A **record** is 32 words (40 octal), so a zone has 32 records. The Russian sources
  call it "40B-ка".
- A **drum** has 32 zones (0–37). The MS was made for two drums, numbers 21 and 22.
  Our machine has no such drums: DD models drum 21 by zones 0–37 of 9/MONSYS and drum 22
  by zones 40–77 (switch register ТР2, bits 41 and 40). So "drum 22, zone 3" and "zone 43
  of the tape" are the same place.
- Text inside the system is in the **TEXT** code: 6 bits per character, 8 characters in a
  word. All names in catalogs are written so.

### The image file

`BUILD/tapes/9` is a tape image as `dubna` and `besmtool` use it:

- 4 blocks of 8256 bytes at the start, all zero;
- then one block of 8256 bytes per zone: 64 bytes of service words, then 1024 words of
  8 bytes each, little-endian. The 48-bit value is in the low bits; bits above it are the
  tag (1 = instruction, the only tag dubna writes).

`BUILD/data/mons9.d9` is the same 288 zones without the 4 leading blocks and with other
service bytes. It is the form that goes into the disk image `disk9.bin`.

`besmtool view 9 --start=1 --length=1` prints a zone (with `BESM6_PATH` set as in
`BUILD/env.sh`).

## 3. Zones 0–77: the Monitor System

| Zones | Content |
| --- | --- |
| 0 | Dynamic loader |
| 1 | Tables of the monitor, see below |
| 2–6 | System code, copied as is from the running system (not examined). Zone 6 has the table of libraries at words 1720–1777. |
| 7–10 | Catalog of the dynamic part |
| 11–33 | Dynamic part: 166 modules |
| 34 | Free: the gap between the two parts |
| 35 | Monitor page: a copy of memory page 0 with the resident monitor |
| 36–77 | Static part: linked sections, mostly compilers |

### How the monitor uses memory

| Addresses | Content |
| --- | --- |
| 0–77 | Tuning constants of the monitor |
| 100–277 | "S area" |
| 300–422 | Data of the resident |
| 423–777 | The resident: module `MONITOR*` with its common blocks |
| 1000–… | Non-resident programs: `/MONTRAN`, `STAR*`, then compilers or the user's program |
| 76000–77777 | Exchange page and the dynamic loader |

The **resident** is the small part that stays in memory all the time. It is kept on the
tape as a ready memory picture, the monitor page. A job starts by reading that page.

### Zone 1

| Words | Content |
| --- | --- |
| 0–777 | By M. Popov's notes: loader overlay (0–377), TRP (400–677), a copy of cells 0–77 (700–777). Not checked here. |
| 1000–1376 | TRP of the monitor with the initiator. Read at the start of every job. |
| 1377 | Where the monitor page is: `0014 0000 0021 0035` = physical drum 21, zone 35 |
| 1400–1433 | Catalog of the static part |
| after it | Static loader `STATICLO` |
| 1776–1777 | Date of the assembly, 6 characters per word. It is printed in the banner of every listing. |

**TRP** (таблица распределения памяти, the memory allocation table) lists the names
already in memory with their addresses: two words per name. The loader looks there first.
The monitor's TRP begins with `MONITOR*` at 423.

### The table of libraries

Zone 6, word 1720 + N holds the tape of library N (name in TEXT and the reel number in
binary-coded decimal), word 1750 + N the starting zone. Control card `*LIBRARY:21` is
resolved through it. `dubna --help-libs` prints the table:

| Library | Tape | Zone |
| --- | --- | --- |
| 1, 12, 25, 27 | 12/LIBRAR | 0, 375, 640, 600 |
| 2, 3, 5, 6, 7, 10, 11 | 37/LIBRAR | 0, 340, 545, 650, 1061, 1220, 1370 |
| 21 | 9/MONSYS | 240 |
| 22 and 24 | 9/MONSYS | 172 |
| 23 | 9/MONSYS | 320 |

## 4. The dynamic part

It is the **permanent library**: modules that the dynamic loader brings into memory by
name when something calls them. The Fortran runtime (`IOCONT*`, `SIN*`, …), the control
card interpreter `STAR*`, the text editor `EDIT***`, the library tools and the second
resident `/MONTRAN` are all here. Each module is stored as *perso*: relocatable object
code, the output of a compiler.

Control card `*CATALOG` prints the list. There are 166 modules with 225 more entry names.

### Its catalog (zones 7–10)

Word 0 is the first free place: `0000 0000 0216 6040` = drum 21, zone 33, word 40.
Word 1 is zero. Then two words per name:

| Word | Content |
| --- | --- |
| first | Name in TEXT |
| second, a module | bit 48 = 1: physical exchange; bits 46–42: record in the zone; 41–36: drum; 35–31: zone; 30–16: length in words; 15–1: entry address |
| second, an entry | bits 48–16 are zero; 15–1: address inside the module named last |

The catalog ends with a zero word followed by `7777 7777 7777 7777`.

Example: `FMRTAPE  7350 7200 7270 0000` is drum 21, zone 32, record 27, length 727.

## 5. The static part

A **static section** is a program already linked for fixed addresses, with all the
library modules it needs inside. It loads fast and needs no search. Compilers are kept so.
Sections form a tree: the root is the resident `MONITOR*`, a compiler loads above it from
1604, and a compiler may have sections of its own that overlay each other.

The tree of this tape:

```
MONITOR*(INPUTCAL,FORTRAN,ASEMBLER,ALGOL,WRITLIB*)
FORTRAN(CBDPR,CONTROL,ENDPRO,GLINK)
ALGOL(A/PRINTM)
```

| Section | Place (zone.record) | Length | Loads at | What |
| --- | --- | --- | --- | --- |
| `INPUTCAL` | 36.12 | 33070 | 1604 | Reading the job and its resource cards |
| `FORTRAN` | 43.37 | 32764 | 1604 | Fortran compiler |
| `CBDPR`, `CONTROL`, `ENDPRO`, `GLINK` | 46.31, 50.32, 56.24, 57.23 | | 34570 | Its phases |
| `ASEMBLER` | 63.15 | 27626 | 1604 | Assembler |
| `ALGOL` | 70.22 | 26551 | 1604 | Algol compiler |
| `A/PRINTM` | 77.00 | 1271 | 30355 | Its section |
| `WRITLIB*` | 77.26 | 24174 | 1604 | Writing compiled modules to the library |

The static part ends exactly at the end of zone 77. That is the rule: it is pushed to
the end of drum 22, and the gap between the dynamic and the static parts is left free.

### Its catalog (zone 1, from word 1400)

Two words per section: the name in TEXT, then:

| Bits | Content |
| --- | --- |
| 15–1 | Load address |
| 30–16 | Length when loaded |
| 35–31 | Record in the zone |
| 40–36 | Zone on the drum |
| 45–41 | Drum |
| 46 | 1: a piece of TRP follows the section |
| 47 | 0: physical drum; 1: drum of the job |
| 48 | 1: the section is on a tape; then bits 45–36 are the zone counted from the catalog |

The first entry is the root, `MONITOR*`: load address 413, length 100, and in bits 45–31
the size of the gap between the two parts, in records. A zero name ends the catalog; the
word after it points to the place after the last section (drum 23, zone 0).

In the archived tape an entry `MT*PUNCH` stands after the end mark. It is a leftover of
an earlier assembly and is not used.

### How a section is stored

Packed, to save room on long runs of equal words. A service word comes first: bits 15–1
= N, bits 30–16 = M. Then N different words follow, and after them M equal words are
meant. If bit 48 of the service word is 1, the repeated word is given right after it;
otherwise zeros repeat. The piece of TRP, if any, comes after the last group: the word
`FRAG ТРП`, the start address, the entries, a zero word.

## 6. The rest of the tape

- **100–171: additional static part.** One more tree with its own catalog at the start of
  zone 100: `INITFTN` (by its name, the Fortran-GDR compiler of card `*FTN`) with `BCDAPRT*`, `F/OPT`,
  `ERRDIAG*`; `FOREX*83` with `LO*SYN`, `LO*GEN`; `PASCAL*`. Here bit 48 is set: places
  are counted from zone 100. Card `*TRANS-name` looks here first.
- **172–403: libraries 22/24, 21, 23.** Ordinary libraries of perso with the same catalog
  format as in section 4 (two zones of catalog, then modules). Library 21 holds the tools
  that assemble the system: `COLLECT`, `COMTODRU`, `OVERLAY`, `OCATALOG`, and the modules of
  `INPUTCAL`. Library 22 holds the Madlen assembler.
- **400–437: dispatcher area.** DD keeps here what used to live on special drum tracks:
  statistics buffer (400), roll track (401), passwords (402), names (403–404), departments
  (405), tables of extracode 66 (410–417), the "service" (420–427), planner track (430),
  paper limits (431), messages (432–433), starters of standard tasks (434–436), news (437). A dispatcher booted from disk would follow from
  zone 440; our tape ends before it.

## 7. Rebuilding

### What comes from where

| Part | Zones | Source |
| --- | --- | --- |
| Resident `MONITOR*`, monitor page, TRP | 35, zone 1 | **compiled** from `besmmons/` |
| Dynamic part and its catalog | 7–33 | **compiled** from `besmmons/` |
| Section `INPUTCAL` | 36–43 | relinked from library 21 (binary perso) and the new dynamic modules |
| Sections `FORTRAN` … `WRITLIB*` | 43–77 | copied from the archived tape |
| Loaders and tables | 0, 2–6 | copied from the running system by `COLLECT` |
| Everything from zone 100 | 100–437 | the archived tape |

The compilers and `WRITLIB*` cannot be rebuilt: the archive has neither their sources nor
their perso, only the linked sections. The dynamic loader has a source
(`besmtask/loader.txt`, compiled to tape 100) but it is not yet put into the image.

### Step 1: compile — `BUILD/mk-ms-src.sh`

`besmmons/system1.txt` and `system2.txt` are 5 Fortran subroutines and 161 Madlen modules.
The job copies them to tape 200 from zone 100 and compiles them; `*TO PERSO:66000,77` saves
the job's temporary library to zones 0–77 of the same tape. The Madlen compiler was loaded
into that library too, so an `*EXCLUDE` card removes it first, with all its entry names.

`BUILD/ms-check.sh` compares the result with the archived permanent library. Names and
sizes are the same except two modules, whose sources are of another version:

| Module | Archived | Rebuilt |
| --- | --- | --- |
| `CHKBEG*` | 264 | 311 |
| `EDIT***` | 3712 | 3711 |

### Step 2: assemble — `BUILD/mk-ms-img.sh`

The original tools run under `dubna`:

```
*tape:200/ms,66             the perso
*tape:201/msimg,67,w        output of COLLECT
*tape:202/msdrum,65,w       output of COMTODRU
*library:21
*library:23
*perso:66000
*call collect:670000
MONITOR*(INPUTCAL)
*end record
*call comtodru:670000,650000
```

- `*PERSO:66000` makes tape 200 the temporary library of the job. Whatever is in the
  temporary library becomes the dynamic part.
- **`COLLECT`** first jumps to `NEW//MON`, which loads a fresh resident and saves its page,
  then starts `COLLECT` again. It prints the map of the resident: check that `MONITOR*` is
  at 423 and `INFLOAD*` at 716, as before; DD and the old sections rely on these addresses.
  Then it removes itself and its helpers from the library, writes zones 0–6, the
  dynamic part and the catalogs to unit 67, links the sections named on the cards and
  writes them after the dynamic part, and puts the monitor page into zone 77.
  The cards give the tree, as in section 5, up to `*END RECORD`. Only `INPUTCAL` can be
  named: the other sections have no perso. `INPUTCAL` needs `DATE` and `DTOI` from library 23.
- **`COMTODRU`** turns that tape into the drum form: catalog entries become physical
  exchanges, the static part moves to the end of zone 77, the monitor page goes to the
  zone before it, and word 1377 of zone 1 is set. It prints where the page is:
  `МОНИТОР НА 650071`.

Failures show in `ms-img.list`: `OTCYTCTBYET name` (a module is missing), `MAЛO MЛ` (more
than 64 zones), `CИCTEMA BEЛИKA`.

### Step 3: splice — `BUILD/ms-splice.py`

Tape 202 now is a correct MS with one static section. The script makes the final 64 zones:

1. everything up to the end of the dynamic part from tape 202;
2. the monitor page from tape 202, put into the old zone (35);
3. the static part from the archived tape, at the old place;
4. each section that `COLLECT` relinked replaces the old one if it takes the same number
   of records (`INPUTCAL`: 181 records, six words differ from the old);
5. in zone 1 the old static catalog and the old word 1377; the gap in the root entry is
   computed anew.

It stops if the dynamic part grows past zone 34. The result is written twice: tape 203
(a full 9/MONSYS for the DD link job, which copies zones 0–77 to drums 21 and 22) and
`data/mons9.bin` (for `mkdisk9.sh`, the disk image). Tape 922 is tape 203 from zone 40.

### What to check after a change

- `./ms-check.sh` prints only the two modules above.
- `ms-base-src.list`: every Madlen module ends with `ЧИCЛO OШИБ. OПEPATOPOB  00`.
- `./bootstrap.sh` runs through; it boots the new MS three times in SIMH.
- `./boot-run.py -f -d 25 -q -m 110`: the listing in `output.txt` has the banner
  `МОНИТОРНАЯ СИСТЕМА 'Д У Б Н А' - DD/MM/YY` with the date of the assembly
  (`20/10/88` is the archived system) and the line `HELLO FROM OS DUBNA`.

### Things to keep in mind

- `dubna` itself always runs the monitor built into it, not the files in `BUILD/tapes`. A
  broken tape 203 cannot break the build, only the system booted in SIMH.
- Old static sections contain old copies of library modules. A change in, say, `PRINT8`
  reaches user programs and `INPUTCAL`, but not the Fortran compiler.
- The resident must keep its addresses. If `MONITOR*` changes size, the old sections
  (linked from 1604) and the addresses pinned in `BUILD/deck-b1/fix-aux.s` no longer fit.
- The room is tight: 64 zones, of which the static part takes 34 and the dynamic part 19.
- No compiler is rebuilt. The job `hello` uses `*FORTRAN`, the section `FORTRAN` of the
  static part (banner `Ф О Р Т Р А Н /16.07.73/`); `*FTN` calls Fortran-GDR from zone 100,
  `*MADLEN` the assembler from library 22. All three are archived binaries. What such jobs
  exercise in the rebuilt MS is the resident, `STAR*`, `INPUTCAL`, the catalogs, the
  spliced static part and the runtime library.
