# ЕС printer in SIMH besm6

## Context

Setting ТР7 bit 34 (bit 33 for printer 1) makes DD drive printer 0 as an ЕС printer, using
the driver in module `PRINTL` ([dubna.dd:23587](dub_besm/dubna.dd#L23587)) instead of the
АЦПУ-128 hammers.

simh-besm6 `master` has had an ЕС-7032/7033 mode since commits `d30bb19d` and `e9c60b8c`:

- `set prnN es`; code in `BESM6/besm6_printer.c`: `es_prn_write`, `es_prn_read`;
- КУС out through `033 070/071`, status in through `033 04070/04071`;
- the end of an operation raises ГРП 18.

It was built for DISPAK's driver (section А0ЕС in ВЫДИНС; see `BESM6/doc/ОСА.md` §4), and
it already handles the ДКОИ characters, overprinting and the output file. Checked on
2026-11-13 with the hello job, `set prn0 es` and ТР7 = `0000 1300 0140 0000`: DD still
fails.

- `033 04070` returns `02000`, even right after развязка (КУС `1000`).
- DD reports `ОШ.LР1 2000`, resets the printer (КУС `10000`) and loops forever. Nothing
  is printed.

What is left is to make the SIMH model also accept DD's driver, without breaking DISPAK.

## DD's driver (n = printer 0/1, index register NP)

Routine `CHAT` ([23688](dub_besm/dubna.dd#L23688)) writes one КУС to `070+n`. It then reads
`04070+n` **at most twice, right away**. It succeeds if `status & mask` ≠ 0, and then
returns the whole status.

| КУС | Driver's name | Mask | Expected status | Current SIMH |
|---|---|---|---|---|
| `02000`, idle | проверить ВВ | `06000` | `02000`; `& 05422` = 0 | `02000` ✓ |
| `01000` | развязка (= квитанция) | `06000` | **0** | `02000` ✗ |
| `02001` | писать, без пропуска | `06000` | `02000`; `& 05422` = 0 | `06000` ✗: data request already up |
| `01000` right after `02001` | пуск канала | `04000` | `04000` | ✓ |
| `04000 \| c`, c in ДКОИ | символ ([WRSUM](dub_besm/dubna.dd#L23704)) | `04000` | `04000`, bit 11 clear | `06000` ✗ |
| `02000` while writing | кончай строку ([ESTRLP](dub_besm/dubna.dd#L22839)) | `02000` | `02000`; `& 01422` = 0 | prints the line, but no end of operation follows ✗ |
| `02003 \| k<<3`, k = 1..3 | пропуск k строк | `06000` | `02000`, then `LPWAIT` | feeds, end of operation ✓ |
| `02004` | уточнить состояние (error path) | | `02000` | ✓ |
| `010000` | сброс | | | ✓ |

Notes on the driver:

- **Line shape.** A line is 7 blanks (`0100`, loop `SHIFT`) followed by the text. It is
  shorter than 128 characters and is ended by `02000`, not by a count.
- **Order.** Paper feeds come before a line's text (`MOVE`).
- **Characters.** They are the "EC" column of `ALLTOISO`
  ([dubna.dd:37067](dub_besm/dubna.dd#L37067)). Compared with SIMH's `dkoi_to_unicode`, all
  letters and digits agree. Only GOST symbols that ДКОИ lacks are substituted (`×`→`*`,
  `≠`→`#`, `Ъ`→`Ь` and so on), and `E0`, `C0`, `D0` (‾ ⩽ ⩾) come out blank. Nothing to
  change here.
- **Interrupt.** It is not ГРП 18. In `WAIT` ([22771](dub_besm/dubna.dd#L22771)) the driver
  first sends развязка. Then it sets `COMLP |= bit (4−n)`, writes `COMLP` to mask register
  `033 026`, does a dummy read of `033 04000`, enables **ГРП 11** (`PERMIR`) and sleeps.
  - ГРП 11 goes to `ECMEДЛ` ([16937](dub_besm/dubna.dd#L16937)). That reads `033 04027`
    and ANDs it with `COMLP`: bit 4 is printer 0, bit 3 is printer 1.
  - It then clears that bit in `COMLP` and rewrites `026`.
  - Without the interrupt, a slow timer fallback (`CHTLP`) resumes the task.
- **ГРП 18 under DD.** DD's vector for ГРП 18 is `33,18` (a stop). DD never unmasks it, so
  SIMH can keep raising ГРП 18 for DISPAK. Check this with a trace of МГРП.

## Changes in simh-besm6 (`BESM6/besm6_printer.c`, `besm6_cpu.c`, `besm6_defs.h`)

1. **Status bit 11 (`02000`) means "status byte pending".**
   - It is set when a command (КУС bit 11) is accepted and when an operation ends (event).
   - It is cleared by the квитанция (КУС `01000`).
   - Add a per-unit flag `pending` next to `status`. `es_prn_read` returns `02000` only
     while it is set.
2. **Data request (`04000`) only after the квитанция:** `writing && !pending`. DISPAK sends
   the квитанция before its data too, so this should not affect it. Confirm that.
3. **Command `02000` (byte 0) while writing:** print the line, as now, then call
   `es_prn_done()`, so that an end of operation follows. A short line is then finished the
   same way as a full 128-character one.
4. **DD's interrupt path, alongside ГРП 18:**
   - `es_irq`, set to `010 >> num` by the end-of-operation event and cleared by the
     квитанция or the next command;
   - `es_mask`, written by `033 026`;
   - `033 04027` returns `es_irq`;
   - `033 04000` returns 0;
   - whenever `es_irq & es_mask` ≠ 0, set `GRP |= GRP_ES_SLOW` (ГРП 11; replace the unused
     `GRP_WATCHDOG`). Check this in the event and in the mask write.
5. **Save/restore and debug:** `REG` entries for `pending`, `es_irq`, `es_mask`, and a debug
   line for `026`/`04027`.
6. **Docs:** `BESM6/Peripherals.md` (`026`, `04027`, `04000`, ГРП 11, the meaning of status
   bit 11) and `BESM6/doc/ОСА.md` §4 (DD's driver next to DISPAK's).

If DISPAK turns out to need `02000` to stay up, make changes 1–3 a unit option instead,
for example `set prn0 es=dd`.

## Changes in os-dubna

- `BUILD/boot-run.ini`: an `ESPRN` variable that does `set prn0 es` before the attach and
  sets ТР7 bit 34, i.e. `d 7 0000 1300 0140 0000` after `:regs`. Setting bit 34 also changes
  the machine number to 1.
- A matching `boot-run.py` option, `-e`.
- `docs/Peripherals.md`: copy the updated version from simh-besm6.
- `docs/Switch_Registers.md`, ТР7 rows 34/33: they need `set prnN es`.
- `CLAUDE.md`, the simulator requirements line: mention `set prnN es`.

## Verification

1. **DISPAK regression:** the existing ES check, `sim/esprn.sh` in `re-disporig`, still
   passes. Run the simh-besm6 tests (`BESM6/tests/README.md`).
2. **DD, printer 0:** run `ESPRN=1 ./boot-run.py -f card-run.deck` from `BUILD/`. Expect:
   - no `ОШ.LР1` on tty25;
   - the job ends `0100-КШ01-…-НЕLLО`;
   - `output.txt` matches the АЦПУ baseline except for the 7-column left margin and the
     ДКОИ substitutions: `diff <(sed 's/^       //' output.txt) <baseline>`.
3. **DD, printer 1:** the same with ТР7 bit 33 and `set prn1 es`, printing to `output1.txt`.
4. **Interrupt path:** with `set prn debug` and `set cpu debug`, every line ends with a read
   of `04027` through ГРП 11, not with the `CHTLP` timer fallback.
