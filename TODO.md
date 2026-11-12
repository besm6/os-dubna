# OS Dubna on SIMH besm6: what is left

The system boots on the current simulator (branch `dubna` of `simh-besm6`, `set cpu mem=128`),
reaches `ПЛАНИРОВЩИК`, and Multitype takes logins and runs jobs. The rebuild jobs `newbsz`
and `newdd` have run once: the spooler now loads from the new task library and asks for
`А1Р`. A job queued with `ПУС` prints its listing on `prn0` (needs `set cpu ext32`), and the
dispatcher rebuilt by `newdd` boots from drum 25.

Do the tasks in order; each one ends with a short "Findings" note.

## Where things are

- **Run:** from `BUILD/`, `./mt-run.py [zone]` boots with `boot-run.ini` and drives tty25
  (operator) and tty26 (Multitype) by send/expect, about 45 s. Options are in the script
  header: `FRESH=1` restores the images from `data/base/`, `SUBMIT=ПУС`, `DRUM=25`,
  `CONAFTER`, `BEFORE`, `AFTER`, `JOBWAIT`, `POLLS`, `SLOW`.
- **Baseline:** `BUILD/data/base/` (untracked) holds the drum and disk images as they were
  after `newbsz` and `newdd`. It is not produced by any script.
- **Commands and replies:** [docs/Dubna_Commands.md](docs/Dubna_Commands.md).
- **Tracing:** `set cpu debug`, `set md0 debug`, `set drum debug`, `set prn debug`. The
  filters in the earlier sessions kept only extracodes or reads of given cells; a full trace
  of a job is millions of lines.
- **Drums in debug output** are named `<unit+1><drum>`: 10–17 are unit 0
  (`data/dubdrum1.bin`), 20–27 unit 1 (`data/dubdrum2.bin`).

## Tasks

- [x] **T1. Queued job hangs the system.**
  - Findings: there is no hang. `ПУС 110,17` queues hello; it runs on Ш05 and ends within
    seconds, so `КАК` and `СЧЕ` already say `НЕТ ЗАДАЧ`. `КВЫ` shows its listing in the
    output file (`Т 0101`), and `РЕЗ 01` lists it on the terminal: compiled, ran, printed
    `НЕLLО FRОМ ОS DUВNА`.
    - The disk scan of units 03–07 is routine polling; it also runs for units 00–02.
    - The unanswered `D` came from the script sending it while the console was busy; sent
      later, it is answered.
    - `mt-run.py` got `POLL=` (e.g. `СЧЕ`), and `AFTER` commands may be empty lines.
- [x] **T2. Listing on the printer.**
  - Findings: the dispatcher's printer driver uses instruction 032 as a second `ext`
    (`,032,4031B` ready bits, `13,032,14B` motor and feed; `tasksav.dd2:3080,3390,3437`,
    `nrespost.dd3:6694,7695`). The 2017 simulator treated 032 as 033; the current one sends
    032 to КАДОПАМ, so the spooler printed into nothing and stayed `+` forever.
    - Fix in the simulator (branch `dubna`): `set cpu ext32` makes 032 act as 033; default
      unchanged (КАДОПАМ), all simulator tests pass. `boot-run.ini` sets it.
    - With it, `FRESH=1 SUBMIT=ПУС ./mt-run.py` prints the whole hello listing on `prn0`
      (`output.txt`, 3653 bytes) with only `А1Р`.
    - Also added `ex -v addr` (examine a virtual address through the page registers).
    - Found on the way: `СЛА`/`RUN` block printer output by design; `ВnР` toggles the
      "ЛВТА only" filter; `CCCNNЭnР` reprints.
- [x] **T3. Check `newbsz` and `newdd`.**
  - Findings: both work when queued with `ПУС` and started at once with the operator order
    `01БП` (`CONSUBMIT=01БП`; their `*ТIМЕ:24.00` keeps the planner from starting them in
    debug mode). Listings come out on `prn0`.
    - `newbsz` (zone 105): links 42 tasks into 5/D73LIB, ends normally.
    - `newdd` (zone 100) first failed with `ПЛОХ.ОБМЕН`: its physical drum exchanges need
      privilege, and ТР3 `7700…` did not cover its slot (Ш04). ТР3 `7777 7777 0000 0000`
      (the 2017 value) fixes it: `ОС 'ДУБНА' НА 25/000-037/. Д=035 ЗОН.`
    - Multitype drops the first character after a listing that fills a page;
      `mt-run.py` now ends `ЛИС` with an empty line before the submit.
- [x] **T4. Boot from drum 25.**
  - Findings: `DRUM=25 ./mt-run.py` boots the rebuilt dispatcher
    (`ОИЯИ. ОС ДУБНА ОТ 04/04/89`, `Д-2500 МС-Ф10`), and a queued hello prints on `prn0`.
    - It used to halt at 25412: `STARTDD` checks the image sum (`CALCSUM`, word 0101).
      Drum 25 zones 017 and 020 held the job's own pages: the ini unlocked drum 25
      (ТР1 `…0360`), so the system paged there while `newdd` wrote the dispatcher. With
      128K memory paging is common; with 512K in 2017 it probably never happened.
    - Fix: leave drum 25 locked (ТР1 `…0364`). Physical exchanges of a privileged job still
      reach it. `boot-run.ini` now only sets ТР3 and ТР6 at the planner.
    - `data/base/` now holds the images after `newbsz` and a good `newdd`.
- [x] **T5. Keep the catalogues across a reboot.**
  - Findings: the drum-25 boot (`boot_dubna-25.b6`, ТР2 `0730 0000 0000 0001`) keeps both
    catalogues: after a reboot `КВЫ` still lists `NЕWDD` (entry 01, printed) and a new job
    becomes entry 02. The drum-20 boot keeps ТР2 `3730…`, which cleans them: it is the clean
    first start of the bootstrap, so that is intended.
- [x] **T6. Other monitor common blocks.**
  - Findings: none. In the dispatcher source (`dd-base-src.list`) only `SPECMON` declares
    `INFLOAD*`, `/VERE/`, `RM*`, `A/I0`, `A/MINUS`, `*REGIM//`, and it is pinned in
    `deck-b1/fix-aux.s`. Other hits are unrelated local names.
- [x] **T7. Bootstrap from scratch.**
  - Findings: `cd BUILD && ./bootstrap.sh` runs end to end without a terminal in about
    20 minutes and leaves `data/base/` with the task library and the rebuilt DD on drum 25;
    a fresh drum-25 boot then prints hello on `prn0`.
    - `mk-base.sh` does the SIMH part: fresh disk and drum images, `tra-libs.b6`, hello into
      7/M, then `newbsz` and `newdd`, each queued with `ПУС` and started with `{}БП`.
    - `mt-run.py` sends `А1Р` only when the spooler asks (an empty task library gives
      `ТАSК!`), and repeats `CONSUBMIT` orders until the job starts.
    - New `dubna.ini`: the system from drum 25 for interactive use, console on the terminal,
      Multitype on telnet port 4199.
    - Removed: `expect1.ini`, `expect2.ini`, `expe.ex`, `first-boot.ini`,
      `first-dd-boot.ini`, `second-boot*.ini`, `d@dubna.ini`, `ddubna.ini`,
      `boot-drums.ini`, `boot-disks.ini`, `boot-second.ini`, `boot-tty26.ini`,
      `ReadMeBoot.txt`, `ReadMeFirst.txt`. `README.md`, `CLAUDE.md` and the docs follow.
- [ ] **T8. Write it down.** A document on how the boot fits together; update `README.md`
  and `CLAUDE.md`; remove what is obsolete in `BUILD/`.

## Rules

- Archived sources (`besmdisp/`, `besmmons/`, …) are not edited. OS changes go into
  `BUILD/deck-b1/`. Simulator changes go to branch `dubna` of `simh-besm6`.
- Runs are non-interactive and leave transcripts (`mt-run-tty25.txt`, `mt-run-tty26.txt`,
  `boot-run-log.txt`). Stop SIMH with `quit`, never a kill, or image writes are lost.
