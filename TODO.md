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
- [ ] **T4. Drum images.** `data/mkdrumdd.sh`; check the banner at 0765 and the jump at 01000
  in zone 0 of drum 20, and that drums 21–22 equal MONSYS zones 0–077.
- [ ] **T5. First boot, drums only.** New ini with current device names, console log,
  `runlimit`, scripted input. Target: the banner line.
- [ ] **T6. Operator console** on `tty25`: empty line → `!!!`, `D`, date `040489D`, `T`.
  Target: `Д-2000 МС-21,22`.
- [ ] **T7. Disks.** Attach `md00`/`md04`, make the dispatcher find D73INP and D73OUT.
  Needs the simulator from branch `dubna` (disk status fix, see T2).
  Target: `ВЫВОД БУФЕРИЗОВАН`, `ПЛАНИРОВЩИК`.
- [ ] **T8. Second boot** with Monitor System drums modelled from 9/MONSYS and the roll
  track kept.
- [ ] **T9. Multitype** on `tty26` over telnet: `OP`, `REF`, password, buffer `7/M`; run a
  job and get its listing on `prn0`.
- [ ] **T10. Self-rebuild.** The `expe.ex` dialogue (jobs `newdd`, `newbsz`), then boot from
  drum 25.
- [ ] **T11. Write it down.** Working ini files and scripts in `BUILD/`, a document on how
  the boot fits together, `README.md` and `CLAUDE.md` updated.

## Rules

- Archived sources (`besmdisp/`, `besmmons/`, ...) and the simulator sources are not
  edited. OS changes go into `BUILD/deck-b1/`; simulator problems are reported.
- Every run is non-interactive (`besm6 file.ini` with `runlimit` and `quit`) and leaves a
  console log.
