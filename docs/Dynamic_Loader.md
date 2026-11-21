# The Dynamic Loader of Monitor Dubna

> Written for this repository from the sources, November 2026. The run-time behaviour was
> checked by tracing jobs under `dubna` (`-de`); the pages of the loader built from the
> source are identical to the archived 9/MONSYS.

The **dynamic loader** links a program while the job runs. It takes the object modules
(perso) the program needs, puts them into memory one after another, connects their
names and starts the program. Its source is [besmtask/loader.txt](../besmtask/loader.txt),
module **REDUOL** (Madlen, about 2000 lines). Every `*CALL`, `*EXECUTE` and every compiler
start goes through it.

All numbers are octal. Cells written `NNB` are memory words; `*70 X` is the drum exchange
extracode with the control word in cell X.

## The address space of a job

![The address space of a job: the resident at the bottom, the program from 1000 up,
the stack, the hole, the loader page at the top.](figures/user_memory.svg)

| Addresses | Content |
| --- | --- |
| 0–77 | Tuning constants of the monitor; the loader keeps its work cells here (2B–74B) |
| 100–277 | S area |
| 300–422 | Data of the resident |
| 423–777 | Resident monitor `MONITOR*`; `INFLOAD*` at 716/717 |
| 1000 – | The program: its modules and common blocks, placed upward by the loader |
| up to 53377 | Free memory. The limit is in cell 16B |
| 53401 – | The stack (магазин), register 15. It grows upward |
| above it, to 75777 | The hole: unmapped, an access traps |
| 76000–77777 | Page 37: the exchange page of the monitor, and the loader while it runs |

- Before the user's program, the same space from 1000 holds the monitor's
  non-resident parts: `/MONTRAN`, `STAR*` (the control cards), a compiler. They are
  loaded the same way, one at a time.
- The loader places modules and common blocks upward from the first free address, the
  low 15 bits of cell 17B (`AP`), and checks against the limit `AU` in 16B (`INCRAP`,
  [loader.txt:714](../besmtask/loader.txt#L714)). The load map ends with `СВОБОДНО`, the
  first free address after the load. Out of room: `МАЛО ПАМЯТИ`.
- `*CALL FULLMEMORY`, `FICMEMORY`, `ALLMEMORY`
  ([system1.txt:13180](../besmmons/system1.txt#L13180)) move the stack up and raise the
  limit: 55377, 73377, 75377 instead of 53377 (example `freemem.dub` of `dubna`).
- There is no heap. A program gets memory only from the loader, at load time, as common
  blocks and arrays. ALGOL keeps its strings in a common block `*HEAP*`, made the same way.

## Where the loader lives

![Drum 21 zones 0, 1, 6, drum 20 and memory pages 1 and 37: the numbered exchanges of a
load.](figures/loader_pages.svg)

The loader is one page of code linked to run at 76000, in two parts:

- **`LOADER`**, the resident part: zone 0 of 9/MONSYS (physical drum 21, zone 0), a full
  page. It does the loading proper.
- **`REDUOL`**, the print part: words 0–377 of zone 1. It finishes a load: prints the map,
  calls the library search, returns. It takes the place of the first quarter of the page,
  code that is no longer needed by then.

The rest of zone 1 holds tables of the monitor. Zone 6 holds a third program, the
**library search** (`LOADLIBR`), which the loader runs in page 1 (2000–3777).

Cell 61B (`RLOAD`) is the control word that reads the loader into page 37. At job start
it is set to read physical drum 21, zone 0 (`0014 3700 0021 0000`, as DD writes it in
`WRITDISP`, [macro67.dd1:11883](../besmdisp/macro67.dd1#L11883)). The loader reads its
second part with the same word, changed to a sector exchange.

## How the monitor calls it

All callers do the same three things
([system2.txt:4729](../besmmons/system2.txt#L4729), `LOADANGO` in the resident):

1. `*70 46B`: write page 37, the exchange page, to drum 20, zone 4.
2. `*70 61B`: read the loader into page 37.
3. Jump into it, with the name of the program to load:
   - **76000** (`L`, [loader.txt:377](../besmtask/loader.txt#L377)): load and go. The
     loader starts the loaded program at its entry.
   - **76002** (`SPENT`, [380](../besmtask/loader.txt#L380)) through `,WTC,43B` /
     `13,VJM,2` (cell 43B holds 76000): load and return. The caller passes a block of 8
     words at the free address; the loader returns to the address in register 13 with
     the entry of the program in word 7 of the block. `LOADANGO` then jumps there.

Who calls:

- **The initiator** at job start loads `MONITOR*`, which loads the section `INPUTCAL` and
  `CHEKJOB*` ([system1.txt:462](../besmmons/system1.txt#L462)).
- **`LOADANGO`** (resident, entries `LOADGO`, `LOADCALL`): `/MONTRAN` calls it for `STAR*`
  and the compilers, `STAR*` for each `*CALL` card. If the job uses the static loader
  (cell `ALOAD` at 716 not zero), it calls that one instead (`INFLOA` at 717).
- **`*EXECUTE`** (`EXECUT`, [system1.txt:12952](../besmmons/system1.txt#L12952)) loads the
  main program, `PROGRAM` by default.
- **ALGOL** (`A/LOADGO`, [system1.txt:1556](../besmmons/system1.txt#L1556)) and **Madlen**
  (`STEXTLDR`, [madlen.txt:92](../besmtask/madlen.txt#L92), "CALL REDUOL") do the same
  sequence themselves.

## A load step by step

1. **`MNENT`** ([393](../besmtask/loader.txt#L393)) saves the registers and the mode,
   **`LOAD`** ([403](../besmtask/loader.txt#L403)) sets up the load list.
2. For each name in the queue: look in the load list (`CHEKLIST`,
   [753](../besmtask/loader.txt#L753)), then in the catalog of the temporary library
   (`SUBP`, [804](../besmtask/loader.txt#L804)). At job start the catalog of the dynamic
   part of the MS (zones 7–10) is copied there, so both are searched as one. The loader
   reads catalogs and modules into free pages under the stack (`*70 53B`), relocates the
   module, adds its unknown names to the queue.
3. **`ENDLOAD`** ([1197](../besmtask/loader.txt#L1197)) reads the print part over
   76000–76377 (`READEND`: cell 61B plus a sector flag) and jumps to it.
4. If names are still missing and libraries are named (`*LIBRARY`, list in cell 73B),
   **`SRCHLIBS`** ([372](../besmtask/loader.txt#L372)) writes page 1 to drum 20 zone 26,
   reads the library search from zone 6 into page 1 (`*70 74B`) and jumps to 2000. It
   copies the modules it finds from the library tapes into the temporary library and
   comes back to **`RELOAD`** ([2009](../besmtask/loader.txt#L2009)): page 1 back, `LOAD`
   again for the new modules.
5. **`PRINT`** ([106](../besmtask/loader.txt#L106)) prints the load map, unless bit 48 of
   cell 44B is set (it is cleared by `*SYSTEM LOAD LIST` and by `*EXECUTE`). Four columns;
   two if bit 48 of `*REGIM//` is set. Errors are printed with the name
   ([340](../besmtask/loader.txt#L340)): `ОТСУТСТВУЕТ` (not found), `МАЛО ПАМЯТИ`,
   `ДЛИННЫЙ СПИСОК`, `ДЛИННЫЙ АДРЕС`, `НЕВЕРНАЯ ДЛИНА`, `ПЕРЕПОЛНЕНИЕ S-ОБЛАСТИ`,
   `ОШИБКА В РАССЫЛКЕ DATA`, `ИСПОРЧЕНА ПОДПРОГРАММА`, `ПЛОХАЯ ЭКВИВАЛЕНТНОСТЬ`.
6. **`CRETN`** ([246](../besmtask/loader.txt#L246)) reads the exchange page back from drum
   20 zone 4 (`*70 45B`), so the loader is gone, and jumps to the entry of the program,
   or returns to the caller (`SRETN`).

`*REGIM//` is a word in the resident; its bits are the job's modes (table at
[system2.txt:7397](../besmmons/system2.txt#L7397): 48 `ONE`, 47 `LONG`, 43 `MODUL`, 42
`DEBUGE`, …).

### Cells

| Cell | Name in loader.txt | Content |
| --- | --- | --- |
| 16B | `ALF1` | Pointers `AC`, `AS`, `AU`; `AU` is the upper limit of loading |
| 17B | `ALF2` | Length of the load list; `AP`, the first free address |
| 43B | — | 76000, the loader page |
| 44B | `ALFA` | Bit 48: no load map |
| 45B, 46B | `RLEX`, `WLEX` | Read, write the exchange page (drum 20, zone 4) |
| 47B | `RCAT` | Catalog of the temporary library |
| 61B | `RLOAD` | Read the loader into page 37 |
| 73B, 74B | `LTAPES`, `LOADLIBR` | Libraries of the job; read the library search |

## Inside the source

The two parts come from the same text by deleting lines:

| Part | Lines kept | Words | Where |
| --- | --- | --- | --- |
| `LOADER` | 1–83 and 377–2024 | 1712 | zone 0 |
| `REDUOL` | 1–376 and 729–2024 | 1676, of which 0–377 are kept | zone 1, words 0–377 |

- Lines 84–376 are the print part: map, error texts, `CHEKLIBS`, `SRCHLIBS`. Lines 377–728
  are the start of a load: entries `L`, `SPENT`, `MNENT`, `LOAD`, the queue (`BEGLOAD`,
  `LOADQUE`), relocation (`INCRAP`). The text from line 729 on is in both parts.
- The print part (293 lines) and lines 377–728 make the same number of words, so the
  common code from line 729 lies at the same addresses in both pages: the print part can
  call it. In `REDUOL` the entries of the deleted part are empty `BSS` labels.
- Words 1776, 1777 of the page are `BSHIFT` and `CSHIFT`. When not zero, the loader adds
  `CSHIFT − BSHIFT` to every address from `BSHIFT` up (`LDSHIFT`,
  [943](../besmtask/loader.txt#L943)). They are zero in the system; the build sets them to
  60000 and 70000 to load a new loader at 66000 linked for 76000.

## Building the pages

![The build: loader.txt to tape 100, two editions, perso on tape 101, loaded at 66000,
saved on drum 25, written to tape 101 zones 0 and 1, spliced into 9/MONSYS.](figures/loader_build.svg)

[BUILD/mk-ld-img.sh](../BUILD/mk-ld-img.sh) does what the original job
[besmtask/loadload.txt](../besmtask/loadload.txt) did in 1988, under `dubna`:

1. `mk-ld-src.sh` copies the source to tape 100 from zone 100, numbered `LOA 0001` on.
2. **Job 1**: the editor makes the two editions (`*D:LOA 0084,376` for `LOADER`, renamed
   from `REDUOL`; `*D:LOA 0377,728` with the empty labels for `REDUOL`). Madlen compiles
   them with the helpers `LDSHIFT`, `NEWLDR`, `NEWLDRS` from `loadload.txt` and the new
   `LDWRITE`, into perso on tape 101 from zone 100.
3. **Job 2**, in clean memory:
   - `FICMEMOR` opens memory up to 73377;
   - `LDSHIFT` puts 60000, 70000 into the running loader;
   - `NEWLDR` loads `LOADER` at 66000 and writes page 33 to drum 25, zone 35;
   - `NEWLDRS` does the same for `REDUOL` (zone 36) and switches the job to the new
     loader (61B);
   - `LDWRITE`, loaded by the new loader, writes the two zones to tape 101, zones 0 and 1.
4. `mk-ms-img.sh` passes tape 101 to `ms-splice.py`, which puts zone 0 and words 0–377 of
   zone 1 into tape 203 and `data/mons9.bin`.

Changes against `loadload.txt`:

- The line numbers of the cuts are those of this source; the 1988 ones (`0143,453` and
  `0455,830`) belong to a longer text and give Madlen errors here.
- `PHYSWR` wrote to physical drum 21. Under `dubna` that is the read-only 9/MONSYS built
  into the simulator, so `LDWRITE` writes to a tape instead.
- Two jobs instead of one: the words after `LOADER` in page 33 must be zero, and Madlen,
  run in the same job, leaves data there. Words 1776, 1777 then hold garbage, the new
  loader shifts addresses, and the next program is loaded wrong.

## Checking

- Both pages equal the archived ones word for word (zone 0; zone 1 words 0–377).
- `ld-img.list` has the load map of `LDWRITE`, printed by the new loader.
- A changed text in the source (say `FRIE:,TEXT,8HCBOБOДHO`) shows up in zone 1 of tape 203
  and in that map.
- `*SYSTEM LOAD LIST` before `*EXECUTE` prints the map of any job.
