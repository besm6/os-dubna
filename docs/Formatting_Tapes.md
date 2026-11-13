# Formatting Magnetic Tapes under OS Dubna

> Written for this repository. It describes how to prepare a new magnetic tape for OS Dubna
> on the SIMH `besm6` simulator, as of November 2026. Everything shown here was run with
> [tape-format.sh](../BUILD/tape-format.sh), except where a note says "from the source".

## Why a tape must be formatted

A BESM-6 tape is not a plain stream of bytes. It is cut into numbered **zones** of 1024
words, and the tape drive finds a zone by the marks written in front of it. A new reel has
no marks, so the system can neither read it nor write to it. Formatting (*разметка*)
writes the marks for every zone, and, if you ask, the name of the tape.

OS Dubna checks the name each time a reel is put on a drive. A reel it cannot identify
gets the console message

```
НЕ ОПОЗН.МЛ-60
```

("tape on drive 60 not recognised"). A blank reel always gets it. That is normal, and it is
the starting point for formatting.

## What you need

- The system built by `./bootstrap.sh` in [BUILD/](../BUILD), or the ready images in
  `BUILD/data/base`. See [Boot_Process.md](Boot_Process.md).
- SIMH `besm6` from branch `master` of [simh-besm6](https://github.com/besm6/simh),
  November 2026 or later. Older simulators write garbage in place of the zones.

## The short way

```sh
cd BUILD
./tape-format.sh            # makes tape60.tap
./tape-format.sh my.tap     # or any other file name
```

The script boots the system, puts a blank reel on drive 60 and plays the operator. It
takes about a minute and ends after the line

```
РАЗМЕЧЕНО 0010 ЗОН.
```

("formatted 10 zones"; the number is octal, so 8 zones). The file now holds a tape named
`DEMO`, reel number 1234. The rest of this article explains what the script does, so you
can do it by hand or change it.

## Words used below

| Word | Meaning |
| --- | --- |
| Drive (МФ, магнитофон) | A tape unit. Drives have octal numbers 30–67. Drive 60 is SIMH unit `mg60`, drive 61 is `mg61`, and so on. |
| Reel (бобина) | One tape. In SIMH it is a file. |
| Zone (зона) | A piece of tape holding 1024 words. Jobs read and write whole zones. |
| Order (приказ) | A line the operator types on the console. |
| Task 62 | The system program that formats tapes. Its name is РАЗМЕТКА. |
| ТР3 | Switch register 3, a row of 48 switches on the panel of the machine. In SIMH it is memory word 3. |

All numbers in the dialogue are **octal**: `10` zones means eight.

## Step by step

### 1. Make a blank reel

A blank reel is an empty file:

```sh
: > tape60.tap
```

Create the file before you attach it. If the file does not exist, SIMH makes it and
formats it in its own way, for another operating system (Диспак). OS Dubna would not take
that tape for its own. For the same reason do not use `attach -n`.

### 2. Start the system

Boot as usual and answer the first questions: Enter, the date `040489D`, the time `T`,
and `A1P` when the system asks for paper. This is described in
[OS_Dubna_Tutorial.md](OS_Dubna_Tutorial.md). Wait for the word `ПЛАНИРОВЩИК`.

### 3. Put the reel on a drive

```
sim> attach mg60 tape60.tap
```

Only drives 60–67 can format. On the real machine the formatting electronics was wired to
one tape controller, and the simulator follows it.

The system notices the new reel, tries to read its name, and prints:

```
НЕ ОПОЗН.МЛ-60
```

### 4. Allow formatting

Formatting destroys everything on the tape, so the system wants a second proof that you
mean this drive. The operator had to set the drive number on the switches of ТР3, in the
top six positions (bits 48–43). In SIMH:

```
sim> d 3 6077 7777 0000 0000
```

The first two digits, `60`, are the drive number. The other digits are what the boot
scripts keep in ТР3 (privileges for jobs); leave them as they are.

Without this step the answer is `РАЗМЕТКА ЗАПРЕЩЕНА !` ("formatting forbidden").

### 5. Give the order

Type on the console:

```
ИМР
```

The system starts task 62, which answers:

```
Ш23(S)-Б6 РАЗМЕТКА
МФ !
```

Look at the letter in brackets, here `S`. The console is shared by the whole system, so
the task must know which lines are meant for it. **Every answer to the task ends with that
letter and `N`**: to answer `60`, type `60SN`. A line without this ending is taken as an
ordinary order and usually gets the reply `!!!` or `НЕТ !`.

### 6. Answer the questions

| The task asks | Meaning | Answer | Example |
| --- | --- | --- | --- |
| `МФ !` | Which drive? | The drive number | `60SN` |
| `ЧИСЛО ЗОН !` | How many zones? | Octal, up to four digits | `10SN` |
| `ИМЯ !` | The name of the tape? | Up to six characters | `DEMOSN` |
| `N БОБ!` | The reel number? | Up to four digits | `1234SN` |

Then the task shows what it understood and asks for a yes:

```
DЕМО  /1234 (0010) МФ-60-ТАК ?
```

This reads: name `DEMO`, reel 1234, 10 zones, drive 60 — "right?". Answer with the ending
alone:

```
SN
```

Any other answer means "no", and the task starts over from the first question (from the
source).

### 7. Wait

Nothing happens for about 15 seconds: the task rests before it starts. Then it erases the
beginning of the tape and writes the zones, about three per second. At the end it prints:

```
РАЗМЕЧЕНО 0010 ЗОН.
```

The tape is ready. In SIMH, take it off with `detach mg60`.

## The whole dialogue

Lines typed by the operator are marked with `<`.

```
НЕ ОПОЗН.МЛ-60                       a blank reel is on drive 60
ИМР                                < format and name
Ш23(S)-Б6 РАЗМЕТКА                   the task; its letter is S
МФ !
60SN                               < drive 60
ЧИСЛО ЗОН !
10SN                               < 10 (octal) zones
ИМЯ !
DEMOSN                             < the name is DEMO
N БОБ!
1234SN                             < reel number 1234
DЕМО  /1234 (0010) МФ-60-ТАК ?
SN                                 < yes
РАЗМЕЧЕНО 0010 ЗОН.                  done
```

The system prints `DЕМО` with Cyrillic `Е`, `М`, `О`: it does not tell lookalike Latin and
Cyrillic letters apart. Type `И` of `ИМР` in Cyrillic, and `S`, `N`, `D` in Latin. See
[Dubna_Commands.md](Dubna_Commands.md).

## Other forms of the order

| Order | What it does |
| --- | --- |
| `ИМР` | Format and name the tape, as above. |
| `МР` | Format only. The task asks for the drive and the number of zones and starts at once, with no confirmation. The tape gets no name: it is a scratch tape. |
| `1ИМР` … `7ИМР` | Format and give one of the standard system names: 1 `D73INP`, 2 `D73ЗАД`, 3 `D73OUT`, 4 `D68LIB`, 5 `D73LIB`, 6 `D73STA`, 7 `ЦЫПЦЫП`. The task does not ask for the name. From the source. |

A `МР` run looks like this:

```
МР
Ш23(S)-Б6 РАЗМЕТКА
МФ !
60SN
ЧИСЛО ЗОН !
20SN
РАЗМЕЧЕНО 0020 ЗОН.
```

## When something goes wrong

| You see | Why | What to do |
| --- | --- | --- |
| `ОШ23-ТАSК62` after the order | The task library has an empty stub in place of task 62 (builds before November 2026). | Rebuild with `./bootstrap.sh`. |
| `РАЗМЕТКА ЗАПРЕЩЕНА !` right after the drive number | ТР3 does not hold the drive number. | Do step 4 and give the order again. |
| `РАЗМЕТКА ЗАПРЕЩЕНА !` after the number of zones, then `РАЗМЕЧЕНО 1774 ЗОН.` | The first zone could not be written: an old simulator, or the drive is not one of 60–67. | Update `besm6`. |
| `!!!` or `НЕТ !` after an answer | The line did not end with the task's letter and `N`, so it went to the system and not to the task. | Type the answer again with the ending. The task is still waiting. |
| The echo of an answer misses its first character (`0SN` for `60SN`), or nothing happens after `SN` | The character was lost: it was typed while the question was still being printed. | Type the answer again. A script should pause before every answer (`step 3000000` in `tape-format.ini`). |
| `СПЕШИШЬ !` | Task 62 is already running, or the drive is an ЕС tape drive. From the source. | Wait for the first run to end. |
| Nothing for 15 seconds after the last answer | The task rests before it starts. | Wait. |

## How long it takes

The task writes two blocks for every zone and eight more, about 0.3 seconds each. The
simulator keeps real time here, so a tape of 1000 (octal) zones needs about five minutes.
For a demo, 10 or 20 zones are enough.

## What is on the tape

The file is a SIMH tape image. Each block is one record: 8 service words, then 1024 data
words. After formatting the data words are filled with a test pattern, and the service
words of every block say what the tape is:

| Word | Contents |
| --- | --- |
| 0 | `2245 1252 5122 4512`, a fixed code |
| 1, 2 | The name of the tape and the reel number, twice. A scratch tape has the fixed code of word 0 here. |
| 3, 6 | `0007 0707`, then the zone number and the block number |
| 4 | `7163 4760 3471 6347`, a fixed code |
| 5 | A checksum |
| 7 | All ones |

Every zone is written twice, in two blocks one after the other: the second copy is a
spare in case the first one cannot be read. So a tape of `N` zones has `2N+8` blocks: `N`+4 zones of two blocks.

So the name is not kept in one place at the start of the tape: every zone carries it. The
system reads it from whatever zone is under the head.

## Using the tape

Boot the system with the reel on a drive. The system reads the name from the tape and
prints nothing: a known tape is quiet. A job asks for the tape by reel number and name
on a `*TAPE` card, and gives it a unit number, here 40:

```
*TAPE:1234/DEMO,40,W
```

`W` allows writing; without it the job can only read. When the job starts, the console
shows which drive it got:

```
Ш01:ТАРЕ
МЛ-Ш01:60
```

("tape for job Ш01 is on drive 60"). The job then addresses zone `NNNN` of the tape as
`40NNNN`. This job writes a line to zone 1 and reads it back with the text editor:

```
*NAME TAPE
*TAPE:1234/DEMO,40,W
*EDIT
*RO
*W:400001
*L:HELLO, TAPE
*EE
*EDIT
*R:400001
*LL
*EE
*END FILE
```

The listing shows:

```
         *W:400001
         *L:НЕLLО, ТАРЕ
               ФАЙЛ 400001   :ЗАПИСАНО      1 КАРТ (0001 ЗОН)
         ...
         *R:400001
         *LL
         НЕLLО, ТАРЕ
               ФАЙЛ 400001   :СЧИТАНО       1 КАРТ (0001 ЗОН)
```

The data stays on the reel: after a new boot, a job with `*TAPE:1234/DEMO,40` (no `W`)
reads the same line. Zones can be used in any order; the system winds the tape forward or
back to find each one.

Winding takes time, as on the real machine: about 0.2 seconds of system time per zone
passed. A job on a long tape needs a larger time limit than the default: a job that wrote
zone 767 and zone 3 of a 770-zone tape and read them back took 17 minutes of system time
and needed a `*TIME:24.00` card. The system charges this time by the zones passed, not by the
clock: the simulator moves its tapes five times faster than the real drive and ran the job in
three seconds. Without the card the job stops with `ИСТЕК. ВРЕМЯ` ("time expired").

To run such a job from a deck of punch cards with the tape mounted, put the line
`attach mg60 tape60.tap` into [card-run.ini](../BUILD/card-run.ini) before `send "01В\r"`.

**Room on the tape.** For `N` zones the formatter writes `N`+4: the first four are kept by
the system, so zone 1 of a job is the sixth zone on the tape. A tape of 10 (octal) zones
has room for job zones 0–7; zone 7 is the last one written by the formatter.

## How it works inside

For the curious; you do not need this to format a tape.

- **The order.** `МР` and `ИМР` are parsed in the dispatcher
  ([macro67.dd1:6853](../besmdisp/macro67.dd1#L6853)); they start task 62 of the task
  library 5/D73LIB. `62/` and `362/` do the same (from the source).
- **The task.** [task47.ts2:10871](../besmtask/task47.ts2#L10871), written in 1977. It
  runs partly inside the dispatcher: it takes over the interrupt of the tape controller and
  a timer entry.
- **The answers.** A line ending with `N` is the order "pass this text to a task". The
  character before `N` selects the task: the letter stands for the шифр the task runs on,
  and the task's banner shows it, `Ш23(S)`.
- **The drive.** Register `033 0141` of the controller switches the formatting modes: 2
  erases the tape, 3 writes the marks of a zone (the synchrotrack), 0 is normal work. For
  each block the task gives a write exchange and starts the tape in mode 2; the timer
  interrupt of the dispatcher switches to mode 3 after about 30 ms, back to mode 2 after
  0.154 s, and wakes the task ([macro67.dd1:5094](../besmdisp/macro67.dd1#L5094)). See
  [Peripherals.md](Peripherals.md) for the controller.
- **Reading and writing.** The exchange word gives the memory page and the zone number
  (bits 26–36, for the dispatcher's own use). A forward move of the tape after an exchange
  word does that one exchange; every other forward move only reads the service words of the
  zone it passes. That is how the dispatcher counts zones while it winds the tape.
- **The simulator.** In mode 3 `besm6` writes the zone given by the pending exchange as one
  tape record. Its delays in the formatting modes follow the clock, since the dispatcher
  times the modes by clock ticks.
- **The dispatcher.** A change made for SIMH in 2017 put a fake volume name into service
  words 3 and 7 after every read, for disks. It did the same to tapes and spoiled the zone
  number, so no tape was recognised. Now it applies to disks only
  ([fix-dsk.s](../BUILD/deck-b1/fix-dsk.s)).
