# OS Dubna on SIMH besm6: what is left

The system boots on the current simulator (branch `dubna` of `simh-besm6`, `set cpu mem=128`),
reaches `ПЛАНИРОВЩИК`, and Multitype takes logins and runs jobs. The rebuild jobs `newbsz`
and `newdd` have run once: the spooler now loads from the new task library and asks for
`А1Р`. What does not work yet: a job listing on the printer, and booting the rebuilt
dispatcher from drum 25.

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

- [ ] **T1. Queued job hangs the system.** `FRESH=1 SUBMIT=ПУС ./mt-run.py` puts hello into
  the input file (`ПАКЕТ В ФАЙЛЕ ВВОДА: 01`), the planner starts it (`01Ш05:НЕLLО`), it reads
  Monitor System zones from `md00`, writes and reads zone 1205, reads drum 20 zone 23. Then
  DD queries the status of disk units 03–07 once (commands `2410`, `2420`, `2440`, `2500`,
  `2600`; only 04 answers 1400, the rest 1000) and nothing more happens. `КАК` says
  `НЕТ ЗАДАЧ`, the operator `D` gets no reply. Ideas:
  - Find the code that issues the scan: the archived driver or `BUILD/deck-b1/fix-dsk.s`.
    See what it waits for next: an interrupt, a status bit, or a reply from the operator
    (a volume request on the console that is never printed).
  - Compare with what the simulator does for an unattached unit (status 1000,
    `besm6_disk.c`). Try attaching dummy images on `md03`–`md07`.
  - Trace a short window after the scan with `set cpu debug` (trigger on `Ш05:`).
  - One run from non-fresh images did finish (`СЧЕТ ОКОНЧЕН ВЫ/ВВ=0101`, an entry in
    `КВЫ`). Find what differed: the images, or the order of commands.
- [ ] **T2. Listing on the printer.** Note that `СЛА` and `RUN` block printer output by
  design (`БЛОКАЦПУ`, see the commands doc), so the test must use `ПУС`. Once T1 lets the
  job finish, its listing should be in 3/D73OUT and in `КВЫ`. In the run that finished, the
  entry was ready (`-`) and the spooler in automatic mode, but `prn0` got no command. Ideas:
  - Trace task 47 (the spooler) after `А1Р`: does it read the output catalogue, does it see
    the entry?
  - Try `ПЕЧ NN` from Multitype, and `CCCNNЭ1Р` from the console.
  - Check the printer driver against `besm6_printer.c` (status bits, ready, the two
    printers, ТР7 bits 46–45 are 0).
- [ ] **T3. Check `newbsz` and `newdd`.** Both ran with `СЛА`, so they left no listings and
  their success is not known. Run them with `ПУС` once T2 works and read the listings.
  Expected: `newbsz` writes the task library 5/D73LIB, `newdd` writes the new dispatcher
  to drum 25.
- [ ] **T4. Boot from drum 25.** `DRUM=25 ./mt-run.py` stops at once with an instruction
  parity error at 01000: the word there is tagged as a number. The banner text is only on
  drum 20, and zones 0240–0266 changed already during `newbsz`. Ideas:
  - Read the job text of `newdd` (7/M zone 100) for where it writes, and compare with the
    control word in `pult9-25.b6` (`0140 1200`) and the drum-to-file mapping in the
    simulator. One of them may address the wrong drum or zone.
  - Check the tags: a dispatcher written by a job may need a tag-setting step that the
    2017 simulator did not enforce.
- [ ] **T5. Keep the catalogues across a reboot.** The second boot still uses ТР2
  `3730 0000 0000 0001`, whose bits 47–43 clean the catalogues and the roll track. Use the
  `0730…` value of `boot_dubna-25.b6` and check that queued input and output survive.
- [ ] **T6. Other monitor common blocks.** Only `SPECMON` is pinned to the Monitor Dubna
  addresses (`BUILD/deck-b1/fix-aux.s`). Search the link listing of the dispatcher for other
  modules that use `INFLOAD*`, `RM*`, `A/I0`, `A/MINUS`, `*REGIM//` or `/VERE/`, and pin them
  the same way. A wrong address there may be behind T1 or T2.
- [ ] **T7. Bootstrap from scratch.** `bootstrap.sh` still calls the 2017 `expect1.ini`,
  `expect2.ini` and `expe.ex`. Replace them with the current steps: build, first boot,
  second boot, then the `newbsz`/`newdd` dialogue scripted in `mt-run.py` style, so that
  `data/base/` is produced by a script. `boot-drums.ini`, `boot-disks.ini`,
  `boot-second.ini` and `boot-tty26.ini` have not been rerun with `mem=128`; convert them to
  send/expect or drop them.
- [ ] **T8. Write it down.** A document on how the boot fits together; update `README.md`
  and `CLAUDE.md`; remove what is obsolete in `BUILD/`.

## Rules

- Archived sources (`besmdisp/`, `besmmons/`, …) are not edited. OS changes go into
  `BUILD/deck-b1/`. Simulator changes go to branch `dubna` of `simh-besm6`.
- Runs are non-interactive and leave transcripts (`mt-run-tty25.txt`, `mt-run-tty26.txt`,
  `boot-run-log.txt`). Stop SIMH with `quit`, never a kill, or image writes are lost.
