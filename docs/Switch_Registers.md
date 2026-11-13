# Switch Registers in OS Dubna

> Written for this repository from the Dubna Dispatcher (DD) sources in
> [dub_besm/dubna.dd](../dub_besm/dubna.dd). Line links point into that file.

The BESM-6 front panel has seven 48-bit **switch registers** (тумблерные регистры, ТР1–ТР7).
They occupy physical addresses 1–7. The operator uses them to pass options to DD: what to
clean at start, which devices to lock out, how the planner runs, and so on.

The original operator's description is the comment block `COMMENT` at
[dubna.dd:180](../dub_besm/dubna.dd#L180) (copied into `BUILD/boot_dubna.b6`). This article
follows it, adds what the code does with each bit, and fills the gaps (ТР3, the panel commands,
ТР5 bits 48–17).

## How DD reads them

- **Kernel code** runs unmapped in supervisor mode, so a plain `,XTA,7` reads ТР7 directly.
  (A *store* to 1–7 does not change a switch; it flushes the БРЗ cache, see
  [Memory_Mapping.md](Memory_Mapping.md).)
- **Service tasks** (planner, DISPINIT, utilities) run as tasks and read a register with
  extracode `,*65,N`: "read word N of the system".
- **User programs** read one with `,*63,N`: "read physical word". For N=4 it returns ТР4
  with bits 43–25 replaced by today's date ([MACRO60:20116](../dub_besm/dubna.dd#L20116)).
- **Software copies.** DD ORs some registers with configuration words, so a bit can be on even
  when its switch is off:
  - ТР7 | `COPY7` (= `TYP/PL+1`, "программная копия ТР7"). The SIMH configuration sets
    bits 26–25 (both УВВК present). See `BUILD/deck-b1/conf-sys.s`.
  - ТР7 | `*TYPELP` (printer type and paper economy), ТР7 | `*TYP/MEM` (memory size).
- **Live vs. start.** Bits marked *start* are only looked at when the dispatcher is called
  (boot or restart, "при вызове диспетчера"). The others are read while the system runs.
  DD watches ТР1 bits 16–1 and the whole of ТР7 and reacts within a timer tick when they
  change ([IC1/2:18091](../dub_besm/dubna.dd#L18091), [PR/TIMER:5011](../dub_besm/dubna.dd#L5011)).

### Bit numbering and SIMH masks

Bits are numbered 48 (MSB) to 1 (LSB). In SIMH a register is written as four groups of four
octal digits, covering bits 48–37, 36–25, 24–13 and 12–1:

```
sim> d 7 0000 0300 0140 0000     ; ТР7 := bits 32, 31, 19, 18
sim> e 1-7                        ; show all seven
```

The *Mask* columns below use that form.

## Summary

| Reg | Main use |
| --- | --- |
| ТР1 | Locking out drums and disks; start-time printing; job input format |
| ТР2 | What to clean at start; MS drums on disk; terminal subsystems; statistics |
| ТР3 | Operand word: per-task privilege scale, tape/zone for task dumps, utility parameters |
| ТР4 | Terminals allowed to bypass the input queue; translator options |
| ТР5 | Operand for panel commands; tape drives withheld from tasks |
| ТР6 | Planner control, link lines, debugging stops, panel command number |
| ТР7 | Hardware configuration: memory, devices locked out, machine number, logging |

---

## ТР1 — drums, disks, start options

| Bits | Mask | Meaning | Read in |
| --- | --- | --- | --- |
| 48 | `4000 0000 0000 0000` | Job input with a passport as in Д68. Applies to console commands `В`/`ПВ` and panel command 1. | [TTANAL:6966](../dub_besm/dubna.dd#L6966), [EXTINTER:16874](../dub_besm/dubna.dd#L16874) |
| 47 | `2000 0000 0000 0000` | *Start.* Don't model drums on disks: no disk extents are taken for drum models. | [NRSMDREC:27132](../dub_besm/dubna.dd#L27132) |
| 46 | `1000 0000 0000 0000` | Don't identify (mount) disks on direction 3. | [RECMDT:26151](../dub_besm/dubna.dd#L26151) |
| 45 | `0400 0000 0000 0000` | Same for direction 4. | same |
| 24 | `0000 0000 4000 0000` | *Start.* Print tape-file models on the operator terminal. | [NRSMDREC:26934](../dub_besm/dubna.dd#L26934) |
| 23 | `0000 0000 2000 0000` | Don't start Multitype. *No reader found in this DD.* | — |
| 16–1 | `0000 0000 0017 7777` | Lock out drums 10₈–27₈. Bit 16 = drum 10₈ … bit 1 = drum 27₈ (bit = 24 − drum number in decimal). | see below |

Drum lockout is live. When a bit goes on, the drum is closed: no new tracks are given out on
it ([IC1/2:18100](../dub_besm/dubna.dd#L18100), [MAЛOMБ:23548](../dub_besm/dubna.dd#L23548)), and
exchanges with it are treated as done
([TRAM70:56846](../dub_besm/dubna.dd#L56846)). The header suggests this for killing a task
stuck on a drum. When the bit goes off, the drum is reopened. DISPINIT and TESTTRAK skip locked drums when
placing catalogs and the roll track ([DISPINIT:61638](../dub_besm/dubna.dd#L61638)).

## ТР2 — start-up cleaning, MS drums, subsystems

| Bits | Mask | Meaning | Read in |
| --- | --- | --- | --- |
| 48 | `4000 0000 0000 0000` | *Start.* Input/output catalogs live with the input/output areas (on tape), not on drum. | [DISPINIT:61621](../dub_besm/dubna.dd#L61621) |
| 47 | `2000 0000 0000 0000` | *Start.* Clear the auto-input catalog. | DISPINIT (`BCATO`, [61813](../dub_besm/dubna.dd#L61813)) |
| 46 | `1000 0000 0000 0000` | *Start.* Clear the auto-output catalog. | same |
| 45 | `0400 0000 0000 0000` | *Start.* Clear the catalog of dumped (rolled-out) tasks, i.e. the roll track. | [TESTTRAK:14580](../dub_besm/dubna.dd#L14580), [NRSMDREC:27057](../dub_besm/dubna.dd#L27057) |
| 44 | `0200 0000 0000 0000` | *Start.* Don't print the list of bad tracks. *No reader found.* | — |
| 43 | `0100 0000 0000 0000` | Obsolete: "отныне нельзя заблокировать TESTTRAK". | [TESTTRAK:14562](../dub_besm/dubna.dd#L14562) |
| 42 | `0040 0000 0000 0000` | *Start.* Don't search for input/output buffers, don't start the print task, no output buffering. | DISPINIT (`BBLS`, [61769](../dub_besm/dubna.dd#L61769)) |
| 41 | `0020 0000 0000 0000` | MS drum 21 is modelled by zones 0–37 of disk file 9/MONSYS. | [TESTTRAK:14726](../dub_besm/dubna.dd#L14726), [ПYCKAЧ:18540](../dub_besm/dubna.dd#L18540) |
| 40 | `0010 0000 0000 0000` | MS drum 22 is modelled by zones 40–77 of 9/MONSYS. The tape is described in [Monsys9_Tape.md](Monsys9_Tape.md). | same |
| 39 | `0004 0000 0000 0000` | Graphics catalog is `CATALO/8` instead of `D73GRF/12`. | [PROC/OUT:45541](../dub_besm/dubna.dd#L45541) |
| 33–31 | `0000 0700 0000 0000` | *Start.* Number (0–7) of the DD copy to load from disk. Copy N sits in 9/MONSYS from zone 440₈ + 40₈·N ([dubna.dd:332](../dub_besm/dubna.dd#L332)). | loader, not DD |
| 30 | `0000 0040 0000 0000` | Collect statistics on terminal users. Tested through word `530B`, which holds this mask. | [MDRECOGN:26473](../dub_besm/dubna.dd#L26473), [STAT TT:28189](../dub_besm/dubna.dd#L28189) |
| 29 | `0000 0020 0000 0000` | Don't bind new channels to `OPERTERM`. | [STRINGER:3283](../dub_besm/dubna.dd#L3283) |
| 28 | `0000 0010 0000 0000` | … to Multitype. | same |
| 27 | `0000 0004 0000 0000` | … to the screen editor. | same |
| 26 | `0000 0002 0000 0000` | … to the subsystem monitor. | same |
| 6–1 | `0000 0000 0000 0077` | Number of the main operator terminal, as configured. *No reader found.* | — |

Catalogs are not cleared if the file is shared and the neighbour machine is alive
([DISPINIT:61821](../dub_besm/dubna.dd#L61821)).

## ТР3 — operand word

ТР3 has no fixed layout. Each user gives it its own meaning.

**Per-task privilege scale (live).** One bit per math-task slot, from bit 48 downward. Bit 48
is the first slot (`NMAT1`), bit 47 the next, and so on. A set bit gives that task the
privileged physical-access extracodes, as if bit 48 of its `REGSCAL` were set. The code
packs the bit with `APX` and tests it in:

- physical-address exchange via extracode 070 ([MACRO70:19617](../dub_besm/dubna.dd#L19617)),
- physical mode on/off ([MACRO76:20050](../dub_besm/dubna.dd#L20050)),
- write to a physical word ([WRPHYSM:49501](../dub_besm/dubna.dd#L49501); counts from
  `NFM` = `NMAT1`+1, one slot later),
- register changes via the extracode emulator ([EMULATOR:13193](../dub_besm/dubna.dd#L13193)).

**Tape address of task dumps.** On the first task dump (`TASKSAV`) the place is read from
ТР3 ([TASKSAV:36574](../dub_besm/dubna.dd#L36574)):

| Bits | Mask | Meaning |
| --- | --- | --- |
| 15–10 | `0000 0000 0007 7000` | Physical tape unit (a tape model by standard name if the unit is not a tape) |
| 9–1 | `0000 0000 0000 0777` | Starting zone |

**Panel command 5** writes ТР3 into memory (see [Panel commands](#panel-commands)).

**Utility parameters.** Operator utilities in the DD source take their arguments from ТР3:

- `ПPOOБMEH`, copy between external storage ([41090](../dub_besm/dubna.dd#L41090)):
  bits 30–16 source and 15–1 destination (unit in the top 6 bits, zone in the low 9), bits
  40–31 zone count (≤ 1000₈). The header also lists bit 41/42 (+1000₈ zones on the write/read
  file) and 43/44 (write to/read from a tape model).
- `OCTOPOЖHO` ([40833](../dub_besm/dubna.dd#L40833)): bits 15–10 unit, 9–1 zone, bit 16 shifts
  the file by 1000₈ zones.
- `PAЗHИЦA` ([40501](../dub_besm/dubna.dd#L40501)): bits 5–1 drum holding the dumped working
  dispatcher.
- `ДИCПHAMБ`, DISPBASE writer ([37046](../dub_besm/dubna.dd#L37046)): bits 6–4 and 3–1 select
  the drum to save the dispatcher image to.
- `TARES` ([35857](../dub_besm/dubna.dd#L35857)): bits 9–1 zone.

## ТР4 — terminals and translators

| Bits | Mask | Meaning | Read in |
| --- | --- | --- | --- |
| 48–44 | `7600 0000 0000 0000` | "Don't touch: they affect the translator." Read by user programs via `*63,4`. | outside DD |
| 43–25 | `0177 7777 0000 0000` | Unused by DD. `*63,4` returns the date here. | [MACRO60:20116](../dub_besm/dubna.dd#L20116) |
| 24–1 | `0000 0000 7777 7777` | Terminals whose jobs may start directly, bypassing the input queue and the planner. Bit N = virtual channel N. ANDed with the `*PL/MT` mask. | [MULTITYP:48162](../dub_besm/dubna.dd#L48162) |

## ТР5 — command operand, tape drives

| Bits | Mask | Meaning | Read in |
| --- | --- | --- | --- |
| 48–17 | `7777 7777 7760 0000` | Tape drives withheld from automatic assignment of scratch tapes requested in a passport. Bit 48 = drive 0 … bit 17 = drive 37₈. *Not in the original header.* | [NRES73:35124](../dub_besm/dubna.dd#L35124) |
| 25 | `0000 0001 0000 0000` | *Start.* Don't check the timer frequency. *No reader found.* | — |
| 15–1 | `0000 0000 0007 7777` | Operand of panel commands 2, 3, 5, 6 and 7. | [EXTINTER:16884](../dub_besm/dubna.dd#L16884) |

## ТР6 — planner, lines, debugging

| Bits | Mask | Meaning | Read in |
| --- | --- | --- | --- |
| 48 | `4000 0000 0000 0000` | Close TASK70 link line to the ЕС-1010 (ЛВТА). | [NR7CH:34081](../dub_besm/dubna.dd#L34081) |
| 47 | `2000 0000 0000 0000` | … to the М-6000 (ОНМУ). | same |
| 46 | `1000 0000 0000 0000` | … to the Минск-2 (РХЛ). | same |
| 45 | `0400 0000 0000 0000` | … to the М-6000 (ЛВТА). | same |
| 40–25 | `0017 7777 0000 0000` | Planner scale: job classes (шифры) allowed to load. 25 = Ш01 … 31 = Ш07, 32 = Ш10 … 38 = Ш16, up to 40 = Ш20. All clear means all allowed. | [AEROPLAN:61305](../dub_besm/dubna.dd#L61305), [MULTITYP:48214](../dub_besm/dubna.dd#L48214) |
| 40 | `0010 0000 0000 0000` | Also: log signals in the TASK70 link protocol. | [NR7CH:34364](../dub_besm/dubna.dd#L34364) |
| 24 | `0000 0000 4000 0000` | Don't check resources (tapes, disks) when the planner starts a job. | [AEROPLAN:60935](../dub_besm/dubna.dd#L60935) |
| 16 | `0000 0000 0010 0000` | Flip the paper-economy mode (squeezing listings) for running jobs. XORed with `*TYPELP`. | [NRES064:43792](../dub_besm/dubna.dd#L43792) |
| 13 | `0000 0000 0001 0000` | *Start.* Restart jobs that died in the input file, with stream priority. | [DISPINIT:61884](../dub_besm/dubna.dd#L61884) |
| 12–11 | `0000 0000 0000 6000` | With the ГОИ multiplexer: allow it on ПРП bits 12–11. ANDed with `MPXMASK`. | [CIO*TL:2615](../dub_besm/dubna.dd#L2615) |
| 9 | `0000 0000 0000 0400` | Don't wait for the operator's answer after punching in auto-output. | service tasks, e.g. `besmtask/task11.ts1:16417` |
| 8 | `0000 0000 0000 0200` | Allow identification of Dispak magnetic tapes. *No reader found.* | — |
| 7 | `0000 0000 0000 0100` | Always stop on КК and КЧ (instruction and data parity errors). | [MAINBLCS:15820](../dub_besm/dubna.dd#L15820) |
| 6 | `0000 0000 0000 0040` | Planner debug mode (daytime rules). Off = production mode (evening rules). | [AEROPLAN:61007](../dub_besm/dubna.dd#L61007) |
| 5 | `0000 0000 0000 0020` | Always print crash (авост) diagnostics on the line printer. | [NRERRMAC:51661](../dub_besm/dubna.dd#L51661) |
| 3–1 | `0000 0000 0000 0007` | Panel command number, see below. | [EXTINTER:16633](../dub_besm/dubna.dd#L16633) |

The code takes bits 48–41 as eight line-lockout bits, matched against `SC/CONC`. Only the four
above are configured. The planner's two modes are described at the top of
[dubna.dd:31](../dub_besm/dubna.dd#L31): in debug mode Ш01 takes jobs over 15 min, Ш02 under
31, Ш03 under 11, Ш04 under 6. In production mode Ш01 takes jobs over 21 min, Ш04 under 10,
the rest by class only.

### Panel commands

Pressing the **request** button (ГРП bit 32; `set cpu req` in SIMH) makes DD read ТР6 bits 3–1
and run a command ([EXTINTER:16869](../dub_besm/dubna.dd#L16869)). Set the operand
first, then press the button.

| Code | Command | Operand |
| --- | --- | --- |
| 0 | None. | — |
| 1 | Start a job from the input device, like console `В`. | ТР1 bit 48 |
| 2 | Kill the task (выброс). | ТР5 bits 5–1 = task number |
| 3 | Save (roll out). Non-zero: that task only. Zero: all tasks, via the standard ROLLOUT job. | ТР5 bits 5–1 |
| 4 | Reset interrupt masks (reserved; "установка 0" does the same). | — |
| 5 | Write ТР3 into memory word ТР5. Refused for address `LIBBOSS`. | ТР5 bits 15–1 = address, ТР3 = value |
| 6 | Start standard job number ТР5. | ТР5 bits 15–1 |
| 7 | `ДКО`: stop exchanges with disk unit ТР5, so it can be removed. | ТР5 = 30₈–47₈ |

## ТР7 — hardware configuration

Most ТР7 bits are ORed with configuration words (see above). DD notices any change of ТР7 and
wakes the temporarily closed tasks ([PR/TIMER:5011](../dub_besm/dubna.dd#L5011)).

| Bits | Mask | Meaning | Read in |
| --- | --- | --- | --- |
| 48 | `4000 0000 0000 0000` | Memory is 32K: don't use the second memory segment. ORed with `*TYP/MEM`. | [SWING:28569](../dub_besm/dubna.dd#L28569) |
| 47 | `2000 0000 0000 0000` | *Start.* With 128K, work only in the segment chosen by the ПСП button. | [STARTDD:11405](../dub_besm/dubna.dd#L11405) |
| 46 | `1000 0000 0000 0000` | Lock out line printer (АЦПУ) 0. | [NRES064:43660](../dub_besm/dubna.dd#L43660) |
| 45 | `0400 0000 0000 0000` | Lock out line printer 1. | same |
| 44 | `0200 0000 0000 0000` | Lock out card punch ПИ-80 0. | [ПEPФOPAЦ:50803](../dub_besm/dubna.dd#L50803) |
| 43 | `0100 0000 0000 0000` | Lock out card punch ПИ-80 1. | same |
| 42 | `0040 0000 0000 0000` | Lock out tape punch (ПЛ) 0. | [ПEPФOPAЦ:50996](../dub_besm/dubna.dd#L50996) |
| 41 | `0020 0000 0000 0000` | Lock out tape punch 1. | same |
| 40 | `0010 0000 0000 0000` | Compress listings on printer 0. ORed with `*TYPELP`. | [PRINTASK:22576](../dub_besm/dubna.dd#L22576) |
| 39 | `0004 0000 0000 0000` | Compress listings on printer 1. | same |
| 38 | `0002 0000 0000 0000` | Don't check the array passport in extracode 073. | [NRES73:35013](../dub_besm/dubna.dd#L35013) |
| 36–34 | `0000 7000 0000 0000` | Machine number (0–7). Goes into statistics, into the task name, and is returned by extracode 114. | [NRESLINE:9606](../dub_besm/dubna.dd#L9606), [EMULATOR:13628](../dub_besm/dubna.dd#L13628), [MULTITYP:46900](../dub_besm/dubna.dd#L46900) |
| 34 | `0000 1000 0000 0000` | Also: printer 0 is an ЕС printer (ЕС-7032/7033, driver `PRINTL`). Needs `set prn0 es` in SIMH; `./boot-run.py -e 0` sets both. | [NRES064:43709](../dub_besm/dubna.dd#L43709) |
| 33 | `0000 0400 0000 0000` | Printer 1 is an ЕС printer. Needs `set prn1 es`; `./boot-run.py -e 1`. | same |
| 32 | `0000 0200 0000 0000` | Don't write DAYFILE records to the statistics file. | [OPERTERM:4246](../dub_besm/dubna.dd#L4246), [TTANAL:6137](../dub_besm/dubna.dd#L6137), [NRESLINE:8469](../dub_besm/dubna.dd#L8469), [NRES072:31823](../dub_besm/dubna.dd#L31823) |
| 31 | `0000 0100 0000 0000` | Don't mount LIBRARY tapes. *No reader found.* | — |
| 30 | `0000 0040 0000 0000` | `*PASS` card is mandatory; user statistics are collected. | [NRESLINE:9965](../dub_besm/dubna.dd#L9965) |
| 27 | `0000 0004 0000 0000` | Background priority possible for Ш01. | [MAINBLCS:15682](../dub_besm/dubna.dd#L15682) |
| 26 | `0000 0002 0000 0000` | УВВК 0 is present (usually from `COPY7`). | [TA2M60:21599](../dub_besm/dubna.dd#L21599) |
| 25 | `0000 0001 0000 0000` | УВВК 1 is present. | same |
| 25–3 | `0000 0001 7777 7774` | Drum address (КУС) for booting DD with hardwired panel program 9. Read by the boot program, not by DD. | — |
| 2 | `0000 0000 0000 0002` | Photo reader number. In Dubna it also means "no CDC-405". | [MACRO60:20229](../dub_besm/dubna.dd#L20229), [EFSMNRS:22079](../dub_besm/dubna.dd#L22079) |
| 1 | `0000 0000 0000 0001` | Which УВВК to start when both are ready. | [TA2M60:21592](../dub_besm/dubna.dd#L21592) |

Bits 34 and 25 have two meanings each. Both readers see the same bit.

## Settings used by the BUILD scripts

`BUILD/boot_dubna.b6` loads these values, and the `.ini` files adjust them:

| Reg | Value | Bits set → effect |
| --- | --- | --- |
| ТР1 | `2000 0000 4000 0364` | 47 no drum models on disk; 24 print tape models; 8, 7, 6, 5, 3 lock drums 20₈–23₈ and 25₈ |
| ТР2 | `1730 0000 0000 0001` | 46, 45 clear auto-output and roll catalogs; 44 no bad-track list; 43 obsolete; 41, 40 MS drums 21/22 on 9/MONSYS; 6–1 = 1 operator terminal 1 |
| ТР4 | `0000 0000 7777 7777` | 24–1 all terminals may bypass the input queue |
| ТР5 | `0000 0001 0000 0000` | 25 no timer frequency check |
| ТР6 | `7417 7777 0000 0160` | 48–45 all TASK70 lines closed; 40–25 all planner classes; 7 stop on parity errors; 6 planner debug mode; 5 always print crash diagnostics |
| ТР7 | `0000 0300 0140 0000` | 32 no DAYFILE; 31 no LIBRARY tapes; 19, 18 boot drum address |

Variants:

- `boot-run.ini` (drum 20, the boots of `mk-base.sh`) sets ТР2 = `3730 0000 0000 0001`:
  also clear the auto-input catalog, and model MS drums 21/22 on 9/MONSYS. ТР3 = 0.
- `boot_dubna-25.b6` (drum 25: `DRUM=25` in `boot-run.ini`, and `dubna.ini`) has
  ТР2 = `0730 0000 0000 0001`, keeping the input and output catalogs across a reboot, and
  ТР7 = `0000 0000 0140 1200`, the boot drum address of drum 25₈.
- At `ПЛАНИРОВЩИК`, `boot-run.ini` and `dubna.ini` set ТР6 = `7417 7777 4000 0160`, adding bit 24 so the
  planner skips the resource check, and ТР3 = `7777 7777 0000 0000`, which gives all math-task
  slots the privileged physical-access extracodes (job `newdd` writes drum 25₈ with them).
  The 2017 scripts also set ТР1 = `… 0360` to reopen drum 25₈. Don't: an open drum gets
  paging tracks, and with 128K of memory the system pages over the dispatcher being written.
  A locked drum still takes physical exchanges from a privileged job.

## Open questions

- No reader was found in DD for ТР1 bit 23, ТР2 bits 44 and 6–1, ТР5 bit 25, ТР6 bit 8, ТР7
  bit 31. They may be read in code outside the DD source, or have dropped out of this version.
- The task-slot numbering of the ТР3 privilege scale is off by one between `WRPHYSM` and the
  other checks.
- In the extracode tracer, ТР3 bits 15–1 = `71717` apparently turns off the filter that hides
  extracode 070 calls from the loader ([EMULATOR:14356](../dub_besm/dubna.dd#L14356)).
