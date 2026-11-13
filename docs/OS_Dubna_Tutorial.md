# OS Dubna Tutorial: Running Your First Jobs

> Written for this repository. Everything below was tried on the SIMH `besm6` simulator in
> November 2026.

OS Dubna ran on the BESM-6 mainframes of the Joint Institute for Nuclear Research in the
1970s and 80s. Here it runs on a simulator. This tutorial shows how to start the machine,
log in, run a Fortran program and read its printout.

## What you will use

The simulated machine has two typewriter terminals ("Consuls") and a line printer:

| Device | What it is | How you reach it |
| --- | --- | --- |
| Operator console (tty25) | The machine operator's terminal: date, time, printer. | The window where you start the simulator. |
| Multitype terminal (tty26) | A user terminal: write jobs, start them, see results. | `telnet localhost 4199` in a second window. |
| Line printer | Prints job listings. | The file `BUILD/output.txt`. |

A *job* is a deck of punched cards: control cards starting with `*` and your program in
between. You keep decks in a *buffer*, a storage area on disk named `7/M`, and send them to
the machine from Multitype.

## 1. Before you start

You need the simulator `besm6`, built from branch `master` of
[simh-besm6](https://github.com/besm6/simh), on your `PATH`, and a `telnet` client.

The repository comes with a ready system: `BUILD/data/base/` holds a clean copy of its
disks and drums. To rebuild them from the sources instead, run `./bootstrap.sh` in `BUILD/`
(about 15 minutes, needs `dubna`; see [Boot_Process.md](Boot_Process.md)).

All commands below are run in `BUILD/`.

## 2. Start the machine

Start from the clean copy, then boot:

```sh
cp data/base/*.bin data/
besm6 dubna.ini
```

The simulator boots OS Dubna and prints on your window, the operator console:

```
ОИЯИ. ОС ДУБНА ОТ 04/04/89
МОNSУS/9 W10
...
САТАLО/8 W23
```

The list shows the files the system found on its disks. Now it waits for the operator.

## 3. The operator console

Type these lines, each followed by Enter:

| You type | The system answers | Meaning |
| --- | --- | --- |
| (just Enter) | `!!!` | "I'm listening." `!!!` also means "I didn't understand." |
| `040489D` | `04/04/89 Т=00.00.03` | Set the date: day, month, year, then `D`. The year must be 89. |
| `T` | `Д00.00.04 Ж00.00.04` | Show the time used by the system (`Д`) and the idle task (`Ж`). |

After a few seconds the system reports that it is ready:

```
Д-2500  МС-Ф10,
ВЫВОД БУФЕРИЗОВАН
УСТАНОВИТЕ ЛИСТ НА АЦПУ-1, ЗАТЕМ ДАЙТЕ ПРИКАЗ  А1Р
ПЛАНИРОВЩИК
```

The third line says "put paper into printer 1, then give the order А1Р". Type:

```
A1P
```

Now the printer is on, and `ПЛАНИРОВЩИК` (the job scheduler) is running. Leave this window
open: it shows when jobs start (`01Ш05:SUМ`).

**Letters.** Many Latin and Cyrillic letters look alike (A/А, P/Р, T/Т, ...), and the system
treats them as the same letter. So `A1P` typed in Latin is fine. Letters without a Latin
twin (Б, Д, Л, П, Ш, Ы, ...) must be typed in Cyrillic: switch your keyboard layout.

## 4. Log in to Multitype

In a second window:

```sh
telnet localhost 4199
```

| You type | The system answers |
| --- | --- |
| two spaces | `МУЛЬТИТАЙП (ВЕРСИЯ ОТ 15/12/87) ЭВМ-0` and `PASS:` |
| `MJPOP` and Enter | `БУФЕР:` (the password is shown as `*****`) |
| `7/M` and Enter | a new line with five spaces: the command prompt |

You are logged in, working in buffer `7/M`. Multitype logs you out after a while without
typing (`ВРЕМЯ`, `К О Н Е Ц`); log in again the same way.

Only the first three letters of a command count: `ЛИС` and `ЛИСТ` are the same command.
Numbers are octal.

## 5. Run the sample job

The buffer already holds a small Fortran job at zone 110. List it:

```
ЛИС 110
```

```
*NАМЕ НЕLLО
*FОRТRАN
        РRОGRАМ НЕLLО
        РRINТ 1000
        SТОР
 1000   FОRМАТ(' НЕLLО FRОМ ОS DUВNА')
        ЕND
*ЕХЕСUТЕ
*ЕND FILЕ
```

Press Enter once more to end the listing. Then send the job to the machine:

```
ПУС 110
```

```
     ЖДИТЕ ОТВЕТА
ПАКЕТ В ФАЙЛЕ ВВОДА: 01
```

"Wait for the answer. The deck is in the input file as entry 01." The scheduler starts it
within seconds; the operator console shows `01Ш05:НЕLLО` (input entry 01 runs on channel
Ш05). A small job like this ends in a few seconds.

After `ПУС` Multitype forgets your buffer. The next line you type is answered with `БУФЕР:`;
type `7/M` again, then your command.

## 6. See the result

**On the printer.** Open `BUILD/output.txt`. After a banner page you find your program, the
compiler's listing, a load map, and then the program's output:

```
 НЕLLО FRОМ ОS DUВNА
...
 КОНЕЦ ЗАДАЧИ  ПОТОК Ш-05  ВЫ/ВВ=0001  ОТДЕЛ=041 - ПОПОВ М.Ю.
```

`КОНЕЦ ЗАДАЧИ` means "end of job". The printer is slow, like the real one: a long listing
takes minutes.

**On the terminal.** See what listings you have:

```
КВЫ
```

```
00.00-   Т*0101  2       НЕLLО
```

`Т` = sent from a terminal; the sign after it is the state (`*` printed, `+` printing,
`<` waiting for the printer, blank = ready); `01` is the listing number. To read listing 01
on the terminal, page by page with Enter:

```
РЕЗ 01
```

## 7. Write your own job

### The deck

A job looks like this:

```
*NAME SUM
*FORTRAN
      PROGRAM SUM
      K = 0
      DO 10 I = 1, 100
   10 K = K + I
      PRINT 20, K
   20 FORMAT(' SUM IS ', I6)
      STOP
      END
*EXECUTE
*END FILE
```

- `*NAME` gives the job a name.
- `*FORTRAN` starts the Fortran program; `*EXECUTE` runs it after compiling.
- `*END FILE` ends the deck.
- Fortran lines follow the punched-card layout: statement labels in columns 1–5, the
  statement from column 7.

### Typing it in

Pick a free zone, for example 120, and start input:

```
ВВО 120
```

Multitype numbers each card (`0001`, `0002`, ...). Type the cards one by one. **An empty line
ends the input.**

After `*NAME` Multitype helps you: it fills the next card with `*ТIМЕ:` and waits for a
time limit. Don't use it: erase the prompt with Backspace (six times) and type `*FORTRAN`
instead. With a `*TIME` card the scheduler may hold the job back. A prompt you erase this
way doesn't come back.

```
0001 *NАМЕ SUМ
0002 *FОRТRАN            ← *ТIМЕ: erased with Backspace
0003       РRОGRАМ SUМ
...
0014 *ЕND FILЕ
0015                     ← empty line: input ends
```

Check it with `ЛИС 120`, then run it with `ПУС 120`. The printer shows:

```
 SUМ IS   5050
```

### Putting a deck from a file

If you prefer your own text editor, write the deck to a file and copy it into the buffer
while the simulator is **not** running:

```sh
./put-job.sh mydeck.dub 130
```

Then start the machine and run `ПУС 130`. This uses `dubna`, as the build does.

### Feeding a deck of punch cards

A job can also come from the card reader, with no Multitype at all. The deck is a text file,
one card per line, and it must end with the end-of-deck card, written as a line of six
backquotes:

~~~
*NAME HELLO
...
*END FILE
``````
~~~

On the operator console press Ctrl-E to get the `sim>` prompt, put the deck into the reader
and go on:

```
sim> attach vu0 mydeck.txt
sim> go
```

Then give the order `01В`: the job starts at once on channel 01 (`Ш01:НЕLLО`), and its
listing is printed. The order `ПВ` instead reads every deck in the reader into the input
file, and the scheduler runs them like `ПУС` jobs. `ВУ НЕ ВКЛ` means the reader is empty.
This needs a recent `besm6` (simh-besm6 of November 2026, with the card reader fixes).

## 8. Watch and control jobs

On Multitype:

| Command | What it does |
| --- | --- |
| `КАК` | Your running jobs (`НЕТ ЗАДАЧ` = none). |
| `СЧЕ` | All running jobs. |
| `КВЫ` | Your listings in the output file. |
| `РЕЗ NN` | Show listing NN on the terminal. |
| `ПЕЧ NN` | Print listing NN again. |
| `ОТК` | Kill your jobs (`ОТК NN`: only the one on channel NN). |
| `СТО` | Log out. |

On the operator console:

| Order | What it does |
| --- | --- |
| `D` | Show the date and time. |
| `NNБП` | Start input entry NN at once, if the scheduler holds it back. |
| `NN.` | Kill the job on channel ШNN. |
| `CCCNNЭ1Р` | Print listing NN again, from page CCC (CCC may be left out). |

Avoid `СЛА` and `RUN`: they start a job directly, but its printout is thrown away.

All commands are explained in [Dubna_Commands.md](Dubna_Commands.md).

## 9. Stop the machine

In the operator console window press **Ctrl-E**. The simulator stops and shows `sim>`.
Type `quit`. Don't just close the window or kill the program: the simulator saves the disks
only when it quits.

The disks keep your decks and listings for the next start. Start with `besm6 dubna.ini`
again; give the date, time and `A1P` as before. To return to the clean state:
`cp data/base/*.bin data/`. The file `output.txt` is started anew at every boot.

## 10. When something goes wrong

| You see | What to do |
| --- | --- |
| `!!!` on the console | The order was not understood. Check the spelling and the letters (Cyrillic or Latin). |
| `ОШ.Н.` or `ОШ.НАБОР` in Multitype | Bad arguments. Check the command. |
| `БУФЕР:` unexpectedly | Multitype has no buffer (after `ПУС`, or a mistyped command). Type `7/M`. |
| `ПАКЕТ В ФАЙЛЕ ВВОДА`, but the job never starts | The scheduler holds it, often because of a `*TIME` card. Give `NNБП` on the console, NN being the entry number. |
| The first letter of your command is lost | Multitype was still finishing a listing. Press Enter, then type the command again. |
| `ИСПОРЧЕН ТЕКСТОВЫЙ ФАЙЛ` | The deck is damaged or there is no deck at that zone. List it with `ЛИС`. |
| Nothing on the printer | Did you answer `A1P`? Was the job sent with `ПУС`, not `СЛА`? Check `КВЫ`. |
| No `ПЛАНИРОВЩИК` after the date and time | Start over from the clean copy: `cp data/base/*.bin data/`. |

## 11. Without typing

`mt-run.py` does all of the above by itself and saves the conversation in
`mt-run-tty25.txt` and `mt-run-tty26.txt`:

```sh
FRESH=1 DRUM=25 SUBMIT=ПУС ./mt-run.py 110
```

It starts from the clean copy, boots, logs in, runs the deck at zone 110 and waits for the
printout in `output.txt`. Its options are listed at the top of the script.

`./card-run.sh hello.dub` does the same with a deck of punch cards: it adds the end-of-deck
card, puts the deck into the reader and gives the order `01В`.
