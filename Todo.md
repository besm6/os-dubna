# ЕС printer in SIMH besm6

## Context

Setting ТР7 bit 34 (bit 33 for printer 1) makes DD drive printer 0 as an ЕС printer, using
the driver in module `PRINTL` ([dubna.dd:23587](dub_besm/dubna.dd#L23587)) instead of the
АЦПУ-128 hammers. SIMH only stubs that interface: `033 070` is ignored, and `033 04070`
always returns `01000`. So the driver fails its first handshake, prints `ОШ.LР1 0000`
and retries forever, and nothing is printed. The goal is a device model that this driver
accepts, with its output going to the same attached file as the АЦПУ.

No hardware documentation is at hand, so the protocol below is worked out from the driver
alone. The model only needs to give the answers the driver checks for.

## Protocol, as the driver uses it (n = printer 0/1, index register NP)

- **Command/data out:** `033 070+n`, one word.
- **Status in:** `033 04070+n`. Routine `CHAT` ([23688](dub_besm/dubna.dd#L23688)) writes
  the word, then reads the status at most **twice, right away**. It succeeds if
  `status & mask` ≠ 0, and then returns the whole status.

  This means status must be ready as soon as the word is written. Only the end of a line
  or a paper feed is asynchronous.

| Word written | Driver's name | Mask | Expected status |
|---|---|---|---|
| `02000` (bit 11), idle | проверить ВВ | `06000` | `02000`; `& 05422` must be 0 |
| `01000` (bit 10), not after a print command | развязка | `06000` | **0**: no answer, or `ОШ` "не развязались" |
| `02001` | печать строки | `06000` | `02000` |
| `02003 \| k<<3`, k = 1..3 (bit 2 set) | протяжка на k строк | `06000` | `02000`, then the driver goes to `LPWAIT` |
| `01000` right after `02001` | пуск канала | `04000` | `04000` |
| `04000 \| c` (bit 12 + ЕС code) | символ ([WRSUM](dub_besm/dubna.dd#L23704)) | `04000` | `04000`, bit 11 clear |
| `02000` while in data | кончай строку ([ESTRLP](dub_besm/dubna.dd#L22839)) | `02000` | `02000`; `& 01422` must be 0 |
| `02004` | уточнить состояние (error path) | | `02000` |
| `010000` (bit 13) | сброс контроллера | | reset, status 0 |

- **Data:** each line starts with 7 blanks (`0100`, the ЕС space; loop `SHIFT`). Characters
  are the first byte of the GOST-indexed table `ALLTOISO`
  ([dubna.dd:37067](dub_besm/dubna.dd#L37067), column "EC"). A line has at most 128
  positions.
- **Completion interrupt:** in `WAIT` ([22771](dub_besm/dubna.dd#L22771)) the driver sends
  развязка, then `COMLP |= bit (4−n)` and writes `COMLP` to mask register `033 026`
  (followed by a dummy read of `033 04000`). It then enables ГРП bit 11 with `PERMIR` and
  sleeps.
  - ГРП bit 11 goes to `ECMEДЛ` ([16937](dub_besm/dubna.dd#L16937)). That reads
    `033 04027` and ANDs the result with `COMLP`: bit 4 is printer 0, bit 3 is printer 1.
  - It then clears that bit in `COMLP`, rewrites `026`, and wakes the task.
  - Without the interrupt, a timer fallback (`CHTLP`) resumes the task, but slowly.
- **Feeds before text:** paper feeds come before a line's text (`MOVE`, at most 3 per
  command; `02033` is a triple feed). Two prints without a feed between them overprint.

## Design (simh-besm6, branch `master`)

Make the ЕС printer a mode of the existing `PRN` units: `set prn0 es` / `set prn0 acpu`.
This follows `set mg4 es`, keeps `attach prn0 output.txt` as it is, and reuses the line
buffer with overstrikes and the GOST→Unicode output (`offset_gost_write`, `set cpu latin`).

### `BESM6/besm6_printer.c`

- **Mode switch:** add a unit flag `UNIT_ES` and `MTAB` entries `ES`/`ACPU`.
- **Per-unit state:**
  - `es_state`: `IDLE`, `CMD_PRINT`, `DATA`, `LINE_END`, `FEED(k)`;
  - `es_status`, the word returned by `04070+n`;
  - position `es_pos`.
- **ЕС→GOST table:** a 256-entry table, the inverse of `ALLTOISO`'s ЕС column over GOST
  codes 0–0137. Take the bytes from the ALLTOISO source above, and add a comment saying
  where they came from. Codes not in the table become blank.
- **`es_prn_write(num, word)`:** implements the table above.
  - Characters go into `acpu[num].line[pos][strike]` the same way `printer_hammer` does,
    with `pos` counting from 0, so the 7 leading blanks are kept.
  - Развязка from `LINE_END` or `FEED` schedules `sim_activate(u, delay)`:
    - about 1 ms for a line;
    - k × 1 ms for a feed (fast, like `LINEFEED_SYNC`).

  Any write first clears that unit's interrupt request.
- **`es_prn_status(num)`:**
  - not attached → `01000`, the current "not ready" value, so the driver behaves as it
    does today;
  - otherwise → `es_status`.
- **Event:** `printer_event` sends ES units to `es_prn_event`.
  - For a feed, it calls `offset_gost_write` k times, the same as the АЦПУ's linefeed
    command 1, and updates `u->pos`.
  - For a line, the text is already in the buffer and is flushed by the next feed.
  - Then it sets `es_irq |= 010 >> num` and calls `es_prn_update_grp()`.
- **Interrupt registers:**
  - `es_mask`, written by `033 026`, and `es_irq`, read back by `033 04027`;
  - `es_prn_update_grp()`: `if (es_irq & es_mask) GRP |= GRP_ES_SLOW`. Call it from the
    event and from the mask write.

    Clearing the mask bit (KOPMAC) stops a second interrupt, and DD clears the ГРП bit
    itself (bit 11 is not wired).
- **Odds and ends:**
  - `printer_reset` clears the ES state;
  - `printer_detach` flushes a pending line;
  - add `REG` entries for the state, for save/restore;
  - debug messages under `printer_dev.dctrl`, like the existing ones.

### `BESM6/besm6_cpu.c`, `cmd_033`

- Replace the stubs:
  - `case 070: case 071:` → `es_prn_write(Aex & 1, ACC)`;
  - `case 04070: case 04071:` → `ACC = es_prn_status(Aex & 1)`.
- Add new cases:
  - `case 026:` → `es_prn_mask(ACC)`;
  - `case 04027:` → `ACC = es_prn_irq()`;
  - `case 04000:` → `ACC = 0`, so the driver's dummy read no longer logs "invalid I/O
    address". Its real meaning is unknown and the result is discarded.

### `BESM6/besm6_defs.h`

- Replace the unused `GRP_WATCHDOG` (bit 11) with `GRP_ES_SLOW` ("ЕС slow devices: ЕС
  printers"). Nothing references the old name.
- Declare the new `es_prn_*` functions.

### Docs

- `BESM6/Peripherals.md` in simh-besm6, and its copy `docs/Peripherals.md` here:
  - registers `070/071`, `04070/04071`, `026`, `04027`, ГРП 11;
  - the status protocol table;
  - `set prnN es`.
- `docs/Switch_Registers.md`, ТР7 rows 34/33: say that they need `set prnN es`.
- The simulator requirements line in `CLAUDE.md`.

### os-dubna (optional)

- `BUILD/boot-run.ini`: an `ESPRN` variable that does `set prn0 es` and sets ТР7 bit 34,
  i.e. `d 7` = `0000 1300 0140 0000` after `:regs`. Setting bit 34 also changes the machine
  number to 1.
- A matching `boot-run.py` option, `-e`.

## Verification

1. **SIMH regression test** `BESM6/tests/esprn.ini` + `esprn.b6`, modelled on
   `tests/esml.ini`/`esml.b6`. A panel program goes through: check, развязка, `02001`,
   пуск, the codes for "HELLO", end of line, развязка. It waits for `04027` bit 4 with
   mask `026` set, then does feed `02013`.
   - Success is a loop at a known address, checked with `br`.
   - Then compare the attached file with an expected `HELLO` line.

   Run the existing tests (`tests/README.md`) for regressions.
2. **End to end in os-dubna:** after building `besm6`, run
   `ESPRN=1 ./boot-run.py -f card-run.deck` from `BUILD/`. Expect:
   - no `ОШ.LР1` on tty25;
   - the job ends `0100-КШ01-…-НЕLLО`;
   - `output.txt` matches the АЦПУ baseline except for the 7-column left margin:
     `diff <(sed 's/^       //' output.txt) <baseline>`.

   Repeat for printer 1: ТР7 bit 33 with `set prn1 es`, printing to `output1.txt`.
3. **Timeout path:** with `set prn debug`, check in `boot-run-debug.txt` that every line
   ends by interrupt (`04027` read) and never by the `CHTLP` timer fallback.
