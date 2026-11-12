# Booting OS Dubna on the current SIMH besm6

Goal: start OS Dubna on the `besm6` simulator as it is today, and understand how the
pieces fit together. The 2017 scripts in `BUILD/` did this for an older simulator.

Tasks are done in order. Each one gets a "Findings" note when finished.

## Background

- **Two dispatchers.**
  - `monsys/monsys.9` (same data as `BUILD/data/mons9.d9`) carries the 1989 system:
    zones 0–077 Monitor System, zone 0420 the dispatcher call block (banner
    `ОТ 07/02/89 Д1`, entries 1000 and 1002), zones 0421–0422 the generation program.
    `besmdisp/macro67.dd1:311-345` puts the dispatcher body in zones 0440–0477, and the
    image ends at 0437.
  - The 2017 dispatcher (banner `ОТ 17.02.17 М1`) is linked under `dispak` from `besmdisp/`
    plus the patches in `BUILD/deck-b1/`, written to tape 1999, and cut into drum images by
    `BUILD/data/mkdrumdd.sh`. No binary of it is in the repo.
- **2017 boot sequence** (`BUILD/first-boot.ini`): clear page 0; panel program 9
  (`set cpu pult=9`) reads 25 tracks of drum 20 into memory using the control word in
  switch register 7; set switch registers 1–7 (`boot_dubna.b6`); `run 1000`.
- **Expected start-up output**

  ```
  ОИЯИ. ОС ДУБНА ОТ 17.02.17 М1
  !!!
  D
  00/00/00 Т=00.00.09
  13/
  Д-2000 МС-21,22
  МЛ ВВ/ВЫВ!
  А Я ЗАНЯТА
  ```

  `МЛ ВВ/ВЫВ!` means the disk files 1/D73INP and 3/D73OUT were not found
  (`besmdisp/sluga.dd4:7210`); a complete start goes on to `ВЫВОД БУФЕРИЗОВАН` and
  `ПЛАНИРОВЩИК`.
- **Simulator changes since 2017**
  - `disk0`/`disk4` are now `md00`/`md04`; `set disk debug` is `set md0 debug`.
  - No `boot` command. `load` sets PC=1 and puts words below 010 into the switch registers.
  - Disk status query never reports "powered up" (`besm6_disk.c:931`); unit and group
    selection changed.
  - Consul ready bit idles at 1 (`set tty25 invready` gives the old behaviour).
    On a console-bound line use bare `send`/`expect`, not `send tty:25`.
  - Clock is fixed at 250 Hz; the dispatcher is assembled for 300 Hz. Switch register 5
    bit 25 blocks the frequency check.
  - Some `033` addresses changed meaning; some still halt as unimplemented.

## Tasks

- [x] **T1. Workspace.** `TODO.md`, `.gitignore`, where tapes live.
  - Findings: `dispak` and `besmtool` both honour `BESM6_PATH` (`dispak/disk.c:63`), so
    tapes can live in `BUILD/tapes/` with
    `BESM6_PATH=$PWD/tapes:/usr/local/share/besm6` (set up in T3). `~/.besm6` is left
    untouched; it holds only stale symlinks to `../dubna-misha-popov`.
- [x] **T2. Probe the 1989 call block.** Build `disk9.bin` and `disk11.bin`
  (`data/mkdisk9.sh`, `mkdisk11.sh`). Load zone 0420 of 9/MONSYS into page 0, start at 1000
  with CPU and disk tracing, record which device and zones it asks for. Confirms or refutes
  "the tape lacks the dispatcher body".
  - Findings: the 1989 dispatcher cannot be booted from this tape; go on with T3.
    - How it was run: zone 0420 (zone 272 of `mons9.d9`, all words tagged as instructions)
      was put on a scratch drum as drum 20 track 0, read into page 0 with
      `d -ml 4 xta 7, ext 2` / `d -ml 5 stop, uj 5` / `d 7 0000 0000 0140 0000` / `run 4`,
      then `reset`, `d PC 1000`, `step N`.
    - Entries: 1000 loads the dispatcher from disk; 1001, 1002, 1003 jump to 4433, 2000,
      5125 after a checksum of words 1000–7177, so they need zones 0420–0427 in pages 0–7
      (1002 is the generation program).
    - The block talks through the panel only: it draws scrolling dot-matrix text on the БРЗ
      lamps (font at 0601…) and waits for the "request" button. Read it with
      `ex BRZ0-BRZ7`, one row per register, BRZ7 on top.
    - Entry 1000 polls units 0–7 of disk controller 3 and ends with `НЕТ ДИСКА С СИСТЕМОЙ`.
      It accepts a unit only if the high status half is 01400 and the low half has 0400
      (code at 1657–1667, mask at 1705). The 2017 simulator returned exactly that for an
      attached unit (`STATUS_GOOD 014000400`); today `besm6_disk.c:931` returns 01000 for
      every unit, attached or not. Fixed on branch `dubna` of `simh-besm6`: an attached
      unit answers 01400 again, and the block then accepts `md00` unpatched.
    - Past that check it reads zones 0
      and 1 of `md00` (the catalog) seven times each, rejects them, and shows the same
      message. Why the catalog is rejected was not pursued.
    - The dispatcher body itself is not on the tape: the source puts it in zones 0440–0477
      of 9/MONSYS, the image has zones 0–0437 only, and in `disk9.bin` those zones are
      empty filler from `tail.d9`. This is from the layout, not from a traced read.
- [x] **T3. Rebuild the 2017 dispatcher under dispak.** Run the steps of `bootstrap.sh` one
  by one, read each listing, fix what the current dispak breaks. Done when tape 1999 exists.
  - Findings: the build works unchanged with the current dispak; the whole of it takes
    under a minute.
    - Tapes now live in `BUILD/tapes/`. `BUILD/env.sh` sets `TAPES` and `BESM6_PATH`; every
      script sources it instead of using `$HOME/.besm6`. `spl/load` no longer asks before
      deleting tape 1999.
    - Steps run, from `BUILD/`: `populate-dsk.sh`; `mk-dd-src.sh`; `mk-stl-src.sh`;
      `mk-ld-src.sh` (tape 1999 removed before each); `data/mkdisk9.sh`, `mkdisk11.sh`,
      `mkbridges.sh`; `deck-b1/mk-deck-b1.sh > deck-b1.b6`; `dispak -l debmult.b6`;
      `dispak -l deck-b1.b6`; `dispak -l tra-libs.b6`.
    - Listings: no assembly errors except one in each of the four dummy `FREQ…` system-text
      modules (`ДВАЖДЫ ОПРЕДЕЛЕННЫЙ КОП: ГМАС`), which comes from the job text itself. The
      expected `E50 0076` at the end of the link did not appear; the job ended normally.
    - Tape 1999 holds 128 zones after the 4-zone header. Its first zone is page 0 of the
      dispatcher: banner `ОИЯИ. ОС ДУБНА ОТ 11.11.26 М1` at 0765 (the date is the build
      date), a jump at 01000.
    - `tra-libs.b6` wrote the rebuild jobs and libraries into `disk9.bin` through bridge
      tape 2209.
- [x] **T4. Drum images.** `data/mkdrumdd.sh`; check the banner at 0765 and the jump at 01000
  in zone 0 of drum 20, and that drums 21–22 equal MONSYS zones 0–077.
  - Findings: `dubdrum1.bin` and `dubdrum2.bin` are built and checked.
    - Layout of each image (256 zones; the second 128 repeat the first, so drums 24–27
      mirror 20–23): drum 20 tracks 0–034 dispatcher, 036–037 Multitype data; drums 21–22
      Monitor System; drum 23 tracks 0–2 password and name tables (MONSYS zones
      0402–0404), 034–037 Multitype.
    - Drum 20 track 0 has the banner at 0765 and a jump at 01000; every word of the
      dispatcher is tagged as an instruction.
    - **Bug inherited from 2017:** drum 22 came out as zones 0–037 of Dispak tape 2048, not
      MONSYS zones 040–077. The copy loop in `deck-b1/fix-misc.s` (`ПЕРЕМС`) steps its
      source with drum arithmetic, which moves from unit 40 (tape 9) to unit 41 (tape 2048)
      after 32 zones. `mkdrumdd.sh` now overlays drum 22 from `mons9.d9`; the deck itself is
      unchanged. Drums 21–22 now equal MONSYS zones 0–077.
- [x] **T5. First boot, drums only.** New ini with current device names, console log,
  `runlimit`, scripted input. Target: the banner line.
  - Findings: `besm6 boot-drums.ini` (run from `BUILD/`) prints
    `ОИЯИ. ОС ДУБНА ОТ 11.11.26 М1` on the console and in `boot-drums-log.txt`.
    - The 2017 sequence works as it was: clear page 0, `set cpu pult=9`, `load pult9.b6`,
      `go` (reads drum 20), `load boot_dubna.b6`, `set cpu pult=0`, set switch register 2,
      deposit at 2257, start at 1000. The ini starts with `reset`, `d PC 1000`,
      `step 300000000` instead of `run 1000`, so the run is bounded.
    - The banner needs patience: the dispatcher first does about 2100 drum exchanges
      (the first-boot cleanup), reaches its idle loop at 72163 after 13.5M instructions, and
      prints the banner only later. A 30M-instruction run shows nothing; 300M (8 seconds)
      is enough.
    - The idle loop at 72163–72207 walks a pattern through the index registers and is where
      the PC sits when the system has nothing to do.
    - Switch register 3 is now cleared; the old scripts left the page-clearing loader in it.
    - The boot writes to both drum images. Rebuild them with `data/mkdrumdd.sh` for a
      clean first boot.
- [x] **T6. Operator console** on `tty25`: empty line → `!!!`, `D`, date `040489D`, `T`.
  Target: `Д-2000 МС-21,22`.
  - Findings: the console works with the current simulator as it is; `boot-drums.ini` now
    carries the dialogue and reaches `Д-2000  МС-21,22` (about 1.5 minutes of host time).
    - Settings: `attach tty25 console`, `set tty25 qwerty,authbs`, `set tty25 vt`. Neither
      `invready` nor the `consul` type was needed.
    - Scripted input is bare `send "...\r"` followed by `step N`; it works with stdin not a
      terminal. Output goes to stdout and the console log.
    - Replies seen: empty line → `!!!`; `D` → `00/00/00 Т=00.00.07`; `040489D` →
      `04/04/89 Т=…`; `T` → `Д00.00.13 Ж00.00.13`.
    - About 16 seconds of BESM-6 time after the start the dispatcher prints
      `Д-2000  МС-21,22`, then `МЛ ВВ/ВЫВ!` every 20 seconds or so, since no disks are
      attached. `13/` at that point answers `А Я ЗАНЯТА`. This is exactly the sample output.
    - Speed: the 1.9G instructions of this run took about 1.5 minutes of host time and
      about 45 seconds of BESM-6 time.
- [x] **T7. Disks.** Attach `md00`/`md04`, make the dispatcher find D73INP and D73OUT.
  Needs the simulator from branch `dubna` (disk status fix, see T2).
  Target: `ВЫВОД БУФЕРИЗОВАН`, `ПЛАНИРОВЩИК`.
  - Findings: `besm6 boot-disks.ini` reaches `ВЫВОД БУФЕРИЗОВАН` and `ПЛАНИРОВЩИК` in under
    a minute. No change to the dispatcher or the disk images was needed once the simulator
    returned the old disk status.
    - Devices: `attach -e md00 data/disk9.bin`, `attach -e md04 data/disk11.bin` (the old
      `disk0` and `disk4`).
    - Right after the banner the dispatcher lists the tape models it found on the disks:
      `MONSYS/9 W10`, `D73LIB/5 W11`, `M/7 W12`, `D73INP/1 W13`, `D73OUT/3 W14`,
      `D73STA/6 W15`, `USESTA/0 W16`, `LINBUF/1 W17`, `ROLLIB/1 W20`, `LIBRAR/2 W21`,
      `LIBRAR/7 W22`, `CATALO/8 W23` (switch register 1 bit 24 asks for this list).
    - `МЛ ВВ/ВЫВ!` is gone; `Д-2000  МС-21,22` is followed by `ВЫВОД БУФЕРИЗОВАН`.
    - Open: `ОШ22-ТАSК11` appears before `ПЛАНИРОВЩИК`. Not traced yet. Likely the static
      library task 11 failing because 5/D73LIB is still empty (`deck.notes`: "NO STL!"); the
      2017 first boot stopped at `ПЛАНИРОВЩИК` regardless.
    - The boot writes to the disk images as well as the drums. To start over, rebuild them
      (`data/mkdisk9.sh`, `mkdisk11.sh`, `mkdrumdd.sh`) and rerun `dispak -l tra-libs.b6`.
- [x] **T8. Second boot** with Monitor System drums modelled from 9/MONSYS and the roll
  track kept.
  - Findings: `besm6 boot-second.ini`, run after `boot-disks.ini`, starts cleanly in under
    a minute.
    - Only switch register 2 differs at start: `3730 0000 0000 0001` (bits 41 and 40 added).
      The dispatcher then reports `Д-2000  МС-Ф10,` instead of `Д-2000  МС-21,22`: the
      Monitor System comes from disk file W10 (9/MONSYS), not from drums 21 and 22.
    - After `ПЛАНИРОВЩИК` the ini changes the switch registers on the running system, as
      `second-boot.ini` did in 2017: register 1 `…0360` (drum 25 opened), register 3
      `7700 0000 0000 0000`, register 6 `…4000 0160` (no resource check). The console keeps
      answering afterwards.
    - `ОШ22-ТАSК11` appears here too (see T7).
    - Bits 47–43 of register 2 are still set, as in 2017, so catalogs and the roll track
      are cleaned again on this boot. Keeping them (the `0730…` value of
      `boot_dubna-25.b6`) is left for T10.
- [ ] **T9. Multitype** on `tty26` over telnet: `OP`, `REF`, password, buffer `7/M`; run a
  job and get its listing on `prn0`.
  - Progress (not finished): the second terminal works as an operator console, Multitype
    starts, but never asks for the password.
    - Telnet: `attach tty line=26 4199` is rejected now ("Unit disabled: TTY0"); use
      `attach tty26 Line=26,4199` (`boot-mt.ini`, driven by `mt-session.py`).
    - Deterministic variant without telnet: `boot-tty26.ini` makes `tty26` the SIMH console
      and sends the 2017 dialogue with `send`. Same result, and it can be traced.
    - On `tty26`: `OP` + Enter → `!!!` (operator console); date entry works; `REF` is
      accepted; two spaces are echoed and nothing follows. Further input (`MJPOP`, `7/M`)
      gets `!!!`, so the line stays unbound.
    - Trace after the two spaces (`set cpu debug`, idle loop filtered out): task 5 starts
      module `MULTITYP` at 20211, runs its first-time setup — fixes its pages, reads its
      non-resident part from the drum, installs the event branch `VALERINA` — and ends with
      extracode 74 at 23274. That is the normal end of the setup
      (`besmdisp/nrespost.dd3:9648-9750`), not a crash. No terminal output follows.
    - Not yet known: why the line is not handed to Multitype after the setup. Next: trace
      the second pair of spaces and follow the binding code (`*TLCONN`, tables in
      `deck-b1/conf-tty.s`), where the 2017 patches zeroed several channel descriptors.
    - Test job: `hello.dub` (checked with `dubna hello.dub`); `put-job.sh deck [zone]`
      writes a deck into 7/M on `disk9.bin` through dispak. 7/M starts at disk zone 0700,
      so zone 110 is address 1010.
    - `ОШ22-ТАSК11` is unrelated to this: Multitype is not loaded through the static
      library.
- [ ] **T10. Self-rebuild.** The `expe.ex` dialogue (jobs `newdd`, `newbsz`), then boot from
  drum 25.
- [ ] **T11. Write it down.** Working ini files and scripts in `BUILD/`, a document on how
  the boot fits together, `README.md` and `CLAUDE.md` updated.

## Rules

- Archived sources (`besmdisp/`, `besmmons/`, ...) and the simulator sources are not
  edited. OS changes go into `BUILD/deck-b1/`; simulator problems are reported.
- Every run is non-interactive (`besm6 file.ini` with `runlimit` and `quit`) and leaves a
  console log.
