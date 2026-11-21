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
| 172–237 | Library 22 (also called 24): Madlen, Pascal tools and others | rebuilt, see section 7 |
| 240–317 | Library 21: system utilities | rebuilt, see section 7 |
| 320–377 | Library 23 | rebuilt, see section 7 |
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
| 0–777 | By M. Popov's notes: loader overlay (0–377, checked: the print part of the loader, see [Dynamic_Loader.md](Dynamic_Loader.md)), TRP (400–677), a copy of cells 0–77 (700–777). |
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
- **172–377: libraries 22/24, 21, 23.** Common libraries (ОБСП) in the packed format of
  `CRELIB`: the catalog of a perso (section 4), with the length of the full catalog less one
  in bits 37–25 of word 0; after the end mark the date (ISO, `DDMMYY`), a zero word, a table
  of references and a list of references. Modules follow from the first free record after
  the catalog; their places count from zone 01040, the first zone of the library. Library
  22 (dated 31.08.88) fills 172–237; library 21 (12.10.88) takes 240–314 of 240–317;
  library 23 (10.04.89) 320–375. Library 21 holds the tools that assemble the system:
  `COLLECT`, `COMTODRU`, `OVERLAY`, `OCATALOG`, `CRELIB`, and the modules of `INPUTCAL`.
  Library 22 holds the Madlen assembler, the Pascal runtime and ASPID; library 23 DTRAN
  and the terminal routines.
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
| Section `INPUTCAL` | 36–43 | **linked by `COLLECT`** from the perso of library 21 (tape 221), with `DATE`, `DTOI` of library 23 (tape 223) |
| Sections `FORTRAN`, `CBDPR`, `CONTROL`, `ENDPRO`, `GLINK`, `ASEMBLER` | 43–70 | **linked by `COLLECT`** from the Madlen sources in `fortran/` and `asembler/` |
| Sections `ALGOL`, `A/PRINTM` | 70–77 | copied from the archived tape |
| Section `WRITLIB*` | 77 | **linked by `COLLECT`**: the root from `writlib/`, `WRITLIBR` from `besmmons/`, `FORTLIBR` from the perso of library 21 |
| Dynamic loader | 0, zone 1 words 0–377 | **compiled** from `besmtask/loader.txt` by `mk-ld-img.sh`, see [Dynamic_Loader.md](Dynamic_Loader.md) |
| Other tables | rest of zone 1, 2–6 | copied from the running system by `COLLECT` |
| Libraries 22, 21, 23 | 172–375 | **compiled** from `besmtask/madlen.txt`, `besml21/`, `besml23/` and the disassembled modules in `besml2N/dtran/`, packed by `CRELIB` |
| Additional static part, dispatcher area | 100–171, 400–437 | the archived tape |

`ALGOL` and `A/PRINTM` cannot be rebuilt: the archive has neither their sources
nor their perso, only the linked sections. The Fortran compiler and the assembler were
taken apart from the linked sections into Madlen sources (`fortran/`, `asembler/`); `make`
there links them with `*CALL OVERLAY` (`tools/dubovl.pl`) into images identical to the
archived ones. `WRITLIB*` (it writes the modules made by a compiler into the temporary
library) is the module `WRITLIBR` of `besmmons/system2.txt` with its common `CATALOG`,
called through `FORTLIBR` of library 21; only its root of 14 words, the module
`WRITLIB*`, had no source and was written from the image (`writlib/writlib.asm`, `make`
there checks it the same way). The dynamic loader is built from `besmtask/loader.txt` into
two pages identical to the archived ones, see [Dynamic_Loader.md](Dynamic_Loader.md).

All the static sections of the archived tape were written by one run of `COLLECT` (bit 46
of each catalog word; the date 22/10/88 in words 1776–1777 of the catalog), with the tree of
section 5. The modules of a compiler were not in the temporary library, which becomes the
dynamic part, but in a library of their own: a card `NAME:n1,n2` in the tree (up to four
numbers; a number from 030 up is the unit of a tape with a library from zone 0, an ОБСП or a
perso) gives the libraries for the section `NAME` of the second level and all the sections
under it. `COLLECT` takes from them what it does not find in the temporary library. The
build does the same for the Fortran compiler, the assembler and the root of `WRITLIB*`. `*CALL OVERLAY` is an entry
of `COLLECT` and builds the catalog anew each time: there is no mode that adds to an old one.

A module taken from a library stays in the temporary library to the end of the run, and the
temporary library is searched first. So in one run a name means one module for all the
sections: a section linked later gets the module, or the entry, that an earlier one took,
whatever its own cards say, and no message tells it. Modules that differ must have different
names. `GLINK` and `ASEMBLER` share modules, but `ASMSTMT` and `ASMINIT` come in two
editions, and `ASMGEN` and `G43044`, the same text in both, call the entries `D44561` and
`G44243`, which are in different modules in each. `ASEMBLER` keeps the names `ASM...`;
the editions of `GLINK` are `GASSTMT`, `GASINIT` (with the entries `GAS44243`, `GAS44561`),
and `fortran/Makefile` makes the copies `GASGEN`, `GAS43044` from the files in `asembler/`
(`make sources`). `ASMPRINT` and `SIMFAIL*` are linked into both as they are.
`tools/ovltest/run.sh` shows the effects on two small overlays. The cards `NAME:n` take
effect only under the root `MONITOR*` (label `LOAD` in `besml21/libra211.l21`); under
another root they are ignored.

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
*tape:241/cmp41,41          perso of FORTRAN, CBDPR
*tape:242/cmp42,42          perso of CONTROL, ENDPRO, GLINK
*tape:243/cmp43,43          perso of ASEMBLER
*tape:244/cmp44,44          perso of the root of WRITLIB*
*tape:245/lib45,45          perso of COLLECT, changed (below)
*tape:221/lib21,61          perso of library 21
*tape:223/lib23,63          perso of library 23
*library:21
*library:23
*perso:66000
*perso:45000,cont
*call collect:670000
MONITOR*(INPUTCAL,FORTRAN,ASEMBLER,WRITLIB*)
FORTRAN(CBDPR,CONTROL,ENDPRO,GLINK)
INPUTCAL:61,63
FORTRAN:41,42,61
ASEMBLER:43,61
WRITLIB*:44,61
*end record
*call comtodru:670000,650000
```

- Four jobs before it compile the Madlen files of the Fortran compiler, of the
  assembler and of the root of `WRITLIB*` (the lists are in `fortran/Makefile`,
  `asembler/Makefile` and `writlib/Makefile`, `make print-FORTRAN`) and write them with
  `*TO PERSO:410000` … `*TO PERSO:440000` to tapes 241–244 (`ms-ftn41.list`,
  `ms-ftn42.list`, `ms-asm43.list`, `ms-wl44.list`): the input of a job is at most two
  drums.
- `*PERSO:66000` copies the perso of tape 200 into the temporary library of the job.
  Whatever is in the temporary library becomes the dynamic part. `*PERSO:45000,CONT` adds
  to it the perso of tape 245: the module `COLLECT` of library 21 with one change. A card
  `NAME:n1,n2` makes the list of libraries with `NEWLIBR/`, which always puts library 21
  first (`*NEW LIBRARY` does the same), and the libraries are searched in that order, so a
  module of library 21 would always come from the archived one. After `CALL NEWLIBR/` the
  changed `COLLECT` shifts library 21 out of the list (`,ASN,64+6` on cell 73B). It is
  found in the temporary library before library 21, and removes itself from there; no
  section links it. Patching `LIBRARY/` (where `NEWLIBR/` is) instead would not do:
  `INPUTCAL` links `LIBRARY/` and would get the patched copy from the temporary library.
  A `*MADLEN` in this job would not do either: the assembler stays in the temporary
  library (14 zones).
- **`COLLECT`** first jumps to `NEW//MON`, which loads a fresh resident and saves its page,
  then starts `COLLECT` again. It prints the map of the resident: check that `MONITOR*` is
  at 423 and `INFLOAD*` at 716, as before; DD and the old sections rely on these addresses.
  Then it removes itself and its helpers from the library, writes zones 0–6, the
  dynamic part and the catalogs to unit 67, links the sections named on the cards and
  writes them after the dynamic part, and puts the monitor page into zone 77.
  The cards give the tree, as in section 5, up to `*END RECORD`; `FORTRAN:41,42` makes it
  take the modules of `FORTRAN` and its sections from tapes 241, 242, `ASEMBLER:43` those
  of `ASEMBLER` from tape 243, `WRITLIB*:44` the root of `WRITLIB*` from tape 244 (the
  rest of it comes from the temporary library). The library modules of all sections come
  from the perso of library 21 (unit 61, tape 221); `INPUTCAL` needs `DATE` and `DTOI`
  of library 23 (unit 63, tape 223). The listing shows where each came from: `*LIBRA:61 = ...`.
- **`COMTODRU`** turns that tape into the drum form: catalog entries become physical
  exchanges, the static part moves to the end of zone 77, the monitor page goes to the
  zone before it, and word 1377 of zone 1 is set. It prints where the page is:
  `МОНИТОР НА 650071`.

Failures show in `ms-img.list`: `OTCYTCTBYET name` (a module is missing), `MAЛO MЛ` (more
than 64 zones), `CИCTEMA BEЛИKA`.

### Step 3: splice — `BUILD/ms-splice.py`

Tape 202 now is a correct MS with the static sections `INPUTCAL`, `FORTRAN` with its four,
`ASEMBLER` and `WRITLIB*`. The script makes the final 64 zones:

1. everything up to the end of the dynamic part from tape 202;
2. the static part: the sections of the archived catalog in its order, those that
   `COLLECT` linked from tape 202, `ALGOL` and `A/PRINTM` from the archived tape, packed
   to end with zone 77, as `COMTODRU` does;
3. the monitor page from tape 202, put into the zone before the static part;
4. in zone 1 the static catalog, made anew: the root with the gap between the two parts,
   each section with its new place (its other bits, length and load address, as in its
   source), the end mark with the place after zone 77; and word 1377 pointing to the page;
5. zone 0 and words 0–377 of zone 1, the dynamic loader, from tape 101 (5th argument).

A section may change its size: the others move, and so may the page. With the present
sizes everything stays at the archived places (static part from 36.12, page in zone 35)
and the catalog equals the archived one but for the gap. Against the archive,
`INPUTCAL` differs in five words (three after the end of zone 37 and two of `LFSYST`,
edited in the archived library after its source was saved), the sections of the Fortran
compiler and `ASEMBLER` only in words of the header (see below), `WRITLIB*` not at all
(but three words of junk after its end in zone 77 are zeros now).

It stops if the dynamic part reaches the zone of the page. The result is written twice: tape 203
(a full 9/MONSYS for the DD link job, which copies zones 0–77 to drums 21 and 22) and
`data/mons9.bin` (for `mkdisk9.sh`, the disk image). Tape 922 is tape 203 from zone 40.

### Libraries 21, 22, 23

Of the 734 modules of the three libraries, 371 are compiled from sources: 177 in
`besml21/`, 188 in `besml23/`, the 6 modules of Madlen in `besmtask/madlen.txt`. The other
363 (the I/O runtime of Fortran-GDR in library 21, the Pascal runtime, ASPID and others in
library 22, `LASCII`, `MAK*TRT`, `PRINTER` and `SERVER` in library 23) were disassembled
from the archived libraries by DTRAN into `besml2N/dtran/*.asm` (file names: `*` is `%`,
`/` is `-`). `BUILD/dtran.py` made them and checks each one; it is not part of the build.

- DTRAN reads only a plain library, so `dtran.py` copies the library from tape 9 with bits
  37–25 of word 0 cleared, and calls `*CALL DTRAN:320000(NAME)`. The text goes to editor
  drum 1, then to a tape, then through `tools/cosy2txt`.
- Each text is assembled and the object compared with the archived one. *Equal*: the same
  words (168 modules). *Equivalent* (195): DTRAN of the new object gives the same text,
  after `tools/degak.py` and a few normalisations (names DTRAN makes up, `*NNNNB+d`, the
  short commands from address 70000, strings split differently). The compilers that made
  these modules order the table of designations in ways Madlen does not, so the words
  that refer to it differ.
- DTRAN's text cannot always be assembled back. A string with control characters loses
  them in the editor; a word DTRAN takes for BSS inside the code, or a command Madlen
  writes otherwise (`15,Z00,-1`), would change. Such words are given to DTRAN as `OCT:`
  directives, listed in `NAME.dtr` (85 modules). An address past the module (`*10157`) is
  written `*0000B+10157B`; BSS lines whose counts disagree with their labels are mended.
- The entry `PAIB` of `LIBSUB` lies past the end of the module (067, length 054); Madlen
  cannot make it, and an older copy of the catalog, left in the free part of library 22,
  has it too. `mk-libs.sh` adds it to the catalog of the perso (`libcat.py -e`).
- Entries are in the catalog in the order of the text; some compilers wrote them in
  another, which does not matter to the loader.

The build:

- `mk-lib21-src.sh`, `mk-lib22-src.sh`, `mk-lib23-src.sh` compile the sources and the
  disassembled modules into perso on tapes 221–223. The sources of libraries 21 and 23
  begin with Fortran (`*FTN`) and switch to Madlen by a card of their own. Units that are
  not in the libraries are cut out by `unitcut.py` (`*EXCLUDE` would also remove the module
  `EXCLUDE` of library 21). `SERVER` is taken from DTRAN: its source compiles neither with
  `*FTN`, `*FOREX` nor `*FORTRAN`.
- `mk-libs.sh` packs each perso with `*CALL CRELIB:TAPE,670000` into tapes 251–253 and runs
  `lib-check.sh -p`; `lib-splice.py`, called by `mk-ms-img.sh`, puts them into tape 203 and
  `data/mons9.bin` at the old zones, so the table of libraries in zone 6 stays.
- `lib-check.sh` (`libcat.py cmp`) requires every module and entry of the archived library,
  with the same length in memory. Two modules differ, as their sources are older than the
  archived editions: `*DRIVER*` of library 21 (761 words against 786) and `W1LOOK` of
  library 23 (616 against 677). Of the modules built from sources, some differ from the
  archive in words only: equivalent (compiled with other options), based differently by
  this Madlen (`12,UTC,111B` for `,UTC,*0111B`), or edited after the sources were saved
  (`GIVETIME`, `BTLOOK`, `LFSYST`, `PRINT80`, `TEXOUT`, `CTLOOK`).
- The jobs of the build keep using the archived libraries of tape 9 (`*LIBRARY:21`; dubna
  has 9/MONSYS built in). The static sections take their library modules from the perso
  of the rebuilt libraries (tapes 221, 223). The archived `INPUTCAL` was linked with the
  edition of `GIVETIME` that the source has, not with the later one of library 21.

### What to check after a change

- `./ms-check.sh` prints only the two modules above.
- `./lib-check.sh` prints only `*DRIVER*` and `W1LOOK`, marked allowed.
- `ms-base-src.list`: every Madlen module ends with `ЧИCЛO OШИБ. OПEPATOPOB  00`.
- `./bootstrap.sh` runs through; it boots the new MS three times in SIMH.
- `./boot-run.py -f -d 25 -q -m 110`: the listing in `output.txt` has the banner
  `МОНИТОРНАЯ СИСТЕМА 'Д У Б Н А' - DD/MM/YY` with the date of the assembly
  (`20/10/88` is the archived system) and the line `HELLO FROM OS DUBNA`.

### Things to keep in mind

- `dubna` itself always runs the monitor built into it, not the files in `BUILD/tapes`. A
  broken tape 203 cannot break the build, only the system booted in SIMH.
- Old static sections contain old copies of library modules. A change in, say, `PRINT8`
  reaches user programs and the relinked sections, but not `ALGOL` or `A/PRINTM`.
- Words 5 and 6 of a section header are the registers 16B and 17B of the loader after it
  has linked the section (and words 1, 2 of a section under it, the same of its parent):
  16B the pointers AC, AS, AU, of which AS gives out the S arrays (`,LS,`) in the low
  memory from 0100; 17B the length of the load list and the first free address. The
  layouts declare the S arrays of `FORTRAN` (0100–0213) and `CBDPR` (0214–0421), so 16B
  is that of the archive; the length of the load list is not (FORTRAN 310 against 550 in
  the archive, ASEMBLER 236 against 206): it counts the names of the modules and entries,
  which the archive does not keep.
- The resident must keep its addresses. If `MONITOR*` changes size, the old sections
  (linked from 1604) and the addresses pinned in `BUILD/deck-b1/fix-aux.s` no longer fit.
- The room is tight: 64 zones, of which the static part takes 34 and the dynamic part 19.
- The job `hello` uses `*FORTRAN`, the section `FORTRAN` of the static part (banner
  `Ф О Р Т Р А Н /16.07.73/`), linked from `fortran/`; `*FTN` calls Fortran-GDR from zone
  100, an archived binary, `*MADLEN` the assembler from library 22. A change in
  `fortran/` or `asembler/` may change the size of a section: `ms-splice.py` moves the
  sections and the page and makes the catalog anew. Moved so, `ALGOL` and `A/PRINTM` work
  (an Algol job printed the right result).
