# WRITLIB*: Saving Compiled Modules

> Written for this repository from the sources, November 2026. The run-time behaviour was
> checked by tracing a Fortran job under `dubna` (`-d ie`); the section built from the
> sources is identical to the archived 9/MONSYS.

**WRITLIB\*** is a small part of the Monitor System "Dubna". It runs after a compiler and
stores the module the compiler made in the job's **temporary library**, where the loader
finds it later. Without it, a compiled program would be lost as soon as the compiler ends.

All numbers are octal. A few words first:

- **Standard array** (стандартный массив): an object module, the output of a compiler.
  It has a list of entries, a header (the *structure*) and the body: code, data, tables.
- **Temporary library**: the modules of the current job. It lives on drum 21 of the job:
  a catalog in zone 0, the modules from zone 2 on. It disappears when the job ends.
- **Section**: a piece of the MS kept ready-linked on 9/MONSYS. The monitor reads it into
  memory from 01604 up and starts it. `WRITLIB*` is one of the sections of the static part,
  see [Monsys9_Tape.md](Monsys9_Tape.md).
- **`*70`**: the extracode of drum exchange. It reads or writes one page (2000 words, a
  zone) or a part of it, as a control word in a memory cell says.

## Where it fits

A job like this

```
*NAME TEST
*FORTRAN
        PROGRAM HELLO
        CALL SUB
        END
        SUBROUTINE SUB
        ...
        END
*EXECUTE
*END FILE
```

goes so:

1. The monitor starts the compiler. It compiles `HELLO` and writes the standard array to
   drum 10, then returns to the monitor.
2. The monitor loads `WRITLIB*`. It copies the array from drum 10 into the temporary library
   and adds its names to the catalog.
3. The next card is not a control card, so the monitor calls the compiler again: it compiles
   `SUB`, and `WRITLIB*` runs a second time.
4. `*EXECUTE` starts the [dynamic loader](Dynamic_Loader.md). It finds `HELLO` and `SUB`
   in the catalog of the temporary library and links them.

So `WRITLIB*` runs once per program unit, one module each time.

![The compiler leaves the array on drum 10; WRITLIB* reads it through BUFFER, writes the
module through the exchange page to drum 21 and its names into the catalog.](figures/writlib_flow.svg)

## When the monitor calls it

The resident module `MONITOR*` decides
([system1.txt:391](../besmmons/system1.txt#L391)). After a compiler ends (register 12 = 1):

- if the compiler found errors, the monitor counts them and does **not** call `WRITLIB*`:
  the bad module is not stored, and `*EXECUTE` later refuses to run with
  `БЫЛИ OШИБKИ ПPИ BBOДE ИЛИ TPAHCЛЯЦИИ`;
- otherwise it calls `LOADANGO` with the name `WRITLIB*`, which reads the section
  from the static part and jumps to it;
- then it goes back to the compiler, or to the next control card.

## The three parts

The section is linked from three modules:

| Module | Source | Address | Job |
| --- | --- | --- | --- |
| `WRITLIB*` | [writlib/writlib.asm](../writlib/writlib.asm) | 01614 | Root: save the exchange page and cell 47B, call `FORTLIBR` |
| `FORTLIBR` | library 21, [libra211.l21:15590](../besml21/libra211.l21#L15590) | 01630 | Read the array from drum 10, word by word |
| `WRITLIBR` | [system2.txt:9703](../besmmons/system2.txt#L9703) | 04000 | The librarian: write the module and the catalog |

Two common blocks: `BUFFER` (2000 words, from 02000) of `FORTLIBR` and `CATALOG` (20000
words, 06000–25777) of `WRITLIBR`. `PRINT8`, which prints error messages, is in the
resident.

![Memory of the section: the resident below 01604, then the header, the root, FORTLIBR with
its BUFFER, WRITLIBR and the big CATALOG up to 26000.](figures/writlib_memory.svg)

The section is 24174 words long, but most of it is the two empty blocks. On the tape it is
stored packed (runs of zeros take one word), so it fits into the end of zone 77.

### The root WRITLIB*

14 words (12 decimal), the only part with no source in the archive. It was written anew from the
image. It does five things:

1. Saves register 13 (the return address) and cell 47B.
2. Puts the word of cell 715B into 47B.
3. Saves the exchange page 76000 to drum 20, zone 4 (`*70 46B`).
4. Calls `FORTLIBR`.
5. Reads the exchange page back (`*70 45B`), restores 47B and returns to the monitor.

The cells are control words of `*70` in the low memory of the monitor:

| Cell | Content |
| --- | --- |
| 45B | Read the exchange page from drum 20, zone 4 |
| 46B | Write the exchange page to drum 20, zone 4 |
| 47B | Read the catalog of the temporary library (drum 21, zone 0) into page 76000 |
| 54B | The free place in the temporary library: 2104000 at start, drum 21, word 4000 (zone 2) |
| 715B | `RM*+4`: the copy of 47B the monitor made when it started ([system2.txt:4850](../besmmons/system2.txt#L4850)) |

`WRITLIBR` writes the module through the exchange page, so the page is saved first. The
loader and others change 47B as they work; the root sets it back to the monitor's own
value while the section runs. `STWRIT*` (below) does the same.

### FORTLIBR: the reader

`WRITLIBR` does not read anything itself. It takes the address of a routine that gives it
the next word of the array; each caller brings its own. `FORTLIBR` is the one for
compilers:

- it calls `WRITLIBR+1` with its reading routine;
- the routine reads the array from drum 10 into `BUFFER`, one zone at a time (`*70`), and
  hands it out word by word;
- if `WRITLIBR` reports an error, it prints `ERROR IN STANDARD ARRAY` and ends the job
  (extracode `*74`).

### WRITLIBR: the librarian

It has two entries: `WRITLIBR` for an array in the *compact* form, `WRITLIBR+1` for the
*long* form that compilers make; the long header of 6 words is packed into the compact one.
The steps ([CHKENTRY](../besmmons/system2.txt#L9745) and on):

1. **Read the catalog.** Up to 8 zones from drum 21 into `CATALOG`, until the end mark
   (a word of all ones). No mark: `ИCПOPЧEH KATAЛOГ TEMPORARY LIB`.
2. **Entries.** The array starts with pairs *name, info word*. A pair with a mark in bits
   48–46 is an entry point of the module; it goes into the catalog at once.
3. **Header.** The first pair without the mark is the structure. From it come the lengths
   of all parts: header, declarations, calls, long names, data, instructions, constants.
   A table of declarations of 2000 words or more: `ПEPEПOЛHEHA TAБЛИЦA OПИCAHИЙ`.
4. **Room.** The module goes to the free place of cell 54B. If it does not fit on the drum:
   `ПEPEПOЛHEHИE БИБЛИOTEKИ`.
5. **Copy.** The words go into the exchange page 76000. Each full page is written to
   drum 21 with `*70`. If the free place is in the middle of a zone, that zone is read first,
   so the module before it stays.
6. **Main entry.** After the last page, 54B moves to the next free record (40 words), and
   the name of the module goes into the catalog with this info word:

   | Bits | Content |
   | --- | --- |
   | 48–46 | 6 |
   | 45–42 | Number of segments |
   | 41–31 | Drum and zone |
   | 30–16 | Length of the body |
   | 15–1 | Entry |

7. **Write the catalog back** to drum 21, unless there were errors. Return 0, or 1 on error.

### The catalog

Word 0 of the catalog holds the free place (a copy of 54B). Then come pairs of words: a
name in TEXT and its info word. A word of all ones ends the list.

`WRTENTRY` ([system2.txt:9948](../besmmons/system2.txt#L9948)) adds each pair **at the head**:
the catalog moves down by two words. Then it looks further down for the same name and
deletes the old pair. So a module compiled again replaces the old one, and the newest
names are found first. As the main entry is written last, it stands before its own entries.

![Before and after: WRITLIB* writes module SUB with entry SUBE. The new pairs go to the head,
the old SUB is deleted.](figures/writlib_catalog.svg)

A full catalog (the end mark reached the last word of 8 zones): `ПEPEПOЛHEHИE KATAЛOГA`.

### Errors

| Message | Meaning |
| --- | --- |
| `ИCПOPЧEH KATAЛOГ TEMPORARY LIB` | No end mark in the catalog |
| `ПEPEПOЛHEHA TAБЛИЦA OПИCAHИЙ` | The module has too many declarations |
| `ПEPEПOЛHEHИE БИБЛИOTEKИ` | Drum 21 is full |
| `ПEPEПOЛHEHИE KATAЛOГA` | The catalog is full |
| `ERROR IN STANDARD ARRAY` | Printed by `FORTLIBR` after any of the above; the job ends |

## Other users of WRITLIBR

The same librarian is used, with other readers, by two modules of the dynamic part:

- `STWRIT*` ([system2.txt:8363](../besmmons/system2.txt#L8363)) stores standard arrays
  punched on cards, one after another (entry `WRITLIBR+1`);
- `RLIBLIS` ([system2.txt:6959](../besmmons/system2.txt#L6959)) copies modules from
  libraries into the temporary library (entry `WRITLIBR`, compact form).

## How it is built

![Three sources become three perso tapes; COLLECT links them into the section, which ends up
in zone 77 of tape 203.](figures/writlib_build.svg)

In the bootstrap (`BUILD/bootstrap.sh`):

1. `mk-ms-src.sh` compiles the MS sources, `WRITLIBR` and `CATALOG` among them, into the
   perso on tape 200.
2. `mk-lib21-src.sh` compiles library 21, `FORTLIBR` among it, into the perso on tape 221.
3. `mk-ms-img.sh` compiles the root, `writlib/writlib.asm`, into perso on tape 244
   (listing `ms-wl44.list`). Then `COLLECT` links all sections. Its card `WRITLIB*:44,61`
   means: take the root from unit 44 (tape 244), library modules from unit 61 (tape 221);
   `WRITLIBR` comes from the temporary library, that is from tape 200.
4. `COMTODRU` and `ms-splice.py` put the section into zone 77, record 26 of tape 203, the
   last section of the static part.

The check is separate. `make` in [writlib/](../writlib/)
(also run by `make check`) links the section alone under `dubna` with `*CALL OVERLAY`
(`tools/dubovl.pl`, the resident replaced by `/MONTRAN`), cuts it out of the result and
compares it with the section on the archived tape `monsys/monsys.9`:

```sh
cd writlib && make
writlib*: GOOD
```

The rebuilt section equals the archived one word for word. Only three words of junk after
its end in zone 77 are zeros now.

## Files

| File | What |
| --- | --- |
| [writlib/writlib.asm](../writlib/writlib.asm) | The root, Madlen |
| [writlib/Makefile](../writlib/Makefile) | Builds the section alone and compares it with the tape |
| [besmmons/system2.txt](../besmmons/system2.txt) | `WRITLIBR`, `STWRIT*`, `RLIBLIS`, the cells `RM*` |
| [besmmons/system1.txt](../besmmons/system1.txt) | `MONITOR*`: the call of `WRITLIB*` |
| [besml21/libra211.l21](../besml21/libra211.l21) | `FORTLIBR` |
| [BUILD/mk-ms-img.sh](../BUILD/mk-ms-img.sh) | Links the section into 9/MONSYS |
| [figures/](figures/) | `writlib_*.py` make the pictures |
