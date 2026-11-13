# DUBNA
Bring up OS DUBNA on BESM-6@SIMH
27/03/2017 by M.Popov

The components of OS Dubna listed here were put into an archive 30 years
ago, with the aim of bringing the system up from the saved sources, if such
an opportunity ever arose in the future...

Few people counted on such an opportunity (and not everything made it from
the past), but the opportunity did arise and, strangely enough, the system
came up!
 M.P.

## Contents

This repository holds the surviving sources and binary images of OS Dubna
for the BESM-6 (archived circa 1988), together with the scripts that rebuild
the system and boot it on the SIMH `besm6` simulator.

| Directory | Contents |
| --- | --- |
| `besmdisp/` | Dubna Dispatcher (DD) sources, in sections |
| `besmmons/` | Monitor System (MS) Dubna sources, in sections |
| `besmtask/` | Madlen assembler, loader and system tasks |
| `besml21/`, `besml23/` | sources of libraries 21 and 23 |
| `dub_besm/` | DD and MS sources as single files, for reference |
| `monsys/`, `lib12/`, `lib37/` | original tape images 9/MONSYS, 12/LIBRAR, 37/LIBRAR |
| `drums/` | drum images with hardware tests |
| `tapes/`, `jobs/` | MS sources as a tape image and the job to compile them |
| `d_besm6/` | miscellaneous old files |
| `BUILD/` | bootstrap scripts, patches for SIMH, simulator configs |
| `docs/` | reference articles on the BESM-6, Madlen and the simulator |

See [file-list.md](file-list.md) for a per-file list.

## Building and booting

The sources are compiled by Monitor Dubna batch jobs under the
[dubna](https://github.com/besm6/dubna) simulator, then disk and drum images are
assembled and booted in SIMH.

The ready images are in the repository, in `BUILD/data/base/`. To just run the system you
need only the simulator:

```sh
cd BUILD
cp data/base/*.bin data/
besm6 dubna.ini
```

To rebuild everything from the sources:

- `dubna` (November 2026 or later) and `besmtool` on `PATH`;
- SIMH `besm6` on `PATH`, built from branch `master` of
  [simh-besm6](https://github.com/besm6/simh) (it needs `set cpu mem=128` and `set cpu ext32`);
- Python 3.

The scripts keep tape images in `BUILD/tapes/`.

```sh
cd BUILD
./bootstrap.sh
```

The script compiles the dispatcher and libraries under `dubna` and builds the drum and
disk images. Then `mk-base.sh` boots them in SIMH twice, feeding each job as a deck of
punch cards (in reader `vu0`): the job `newbsz` builds the task library (the print spooler is in it), and the
job `newdd` writes a rebuilt dispatcher to drum 25. The resulting images are saved in
`BUILD/data/base/`. This part takes about a minute and a half. Commit the new images only
when the system has changed: each version adds about 4 MB to the history.

Run the system from `BUILD/` with `besm6 dubna.ini`.

A step-by-step guide for users is [docs/OS_Dubna_Tutorial.md](docs/OS_Dubna_Tutorial.md).

This terminal is the operator console; Multitype is on telnet port 4199. Commands and
replies are described in [docs/Dubna_Commands.md](docs/Dubna_Commands.md).
`./mt-run.py` boots and runs a job non-interactively (`FRESH=1 SUBMIT=ПУС ./mt-run.py`
prints the hello job on `output.txt`); `./card-run.sh hello.dub` runs it from a deck of
punch cards, with a plain SIMH script (`card-run.ini`). How the pieces fit together is described in
[docs/Boot_Process.md](docs/Boot_Process.md).

More details are in `BUILD/`:

- [deck-b1/deck.notes](BUILD/deck-b1/deck.notes) — known restrictions of the 2017 build;
- [ReadMeTapes.txt](BUILD/ReadMeTapes.txt) — tape numbers used by the bootstrap;
- [ReadMeJobs.txt](BUILD/ReadMeJobs.txt) — how to submit jobs to the running system;
- [the-bootstrap-plan.txt](BUILD/the-bootstrap-plan.txt) — phases of the bootstrap.

## Documentation

Reference articles in [docs/](docs/):

- [Madlen.md](docs/Madlen.md) — the Madlen autocode assembler;
- [Besm6_Instruction_Set.md](docs/Besm6_Instruction_Set.md) — CPU registers and instructions;
- [Besm6_Data_Representation.md](docs/Besm6_Data_Representation.md) — how numbers, characters and pointers are stored in a 48-bit word;
- [Memory_Mapping.md](docs/Memory_Mapping.md) — memory mapping and protection;
- [Peripherals.md](docs/Peripherals.md) — peripherals and their control registers;
- [Simh_Simulator.md](docs/Simh_Simulator.md) — building and using the SIMH BESM-6 simulator;
- [KOI7_Encoding.md](docs/KOI7_Encoding.md) — the KOI-7 character set.

Written for this repository:

- [OS_Dubna_Tutorial.md](docs/OS_Dubna_Tutorial.md) — start the system and run your own jobs;
- [Boot_Process.md](docs/Boot_Process.md) — how the bootstrap builds and boots the system;
- [Dubna_Commands.md](docs/Dubna_Commands.md) — operator console and Multitype commands;
- [Switch_Registers.md](docs/Switch_Registers.md) — the switch registers ТР1–ТР7 in DD.

The other articles are taken from other BESM-6 projects
([simh](https://github.com/besm6/simh), [v7besm](https://github.com/besm6/v7besm),
[c-compiler](https://github.com/besm6/c-compiler)); each one names its origin
under the title.

[BUILD/elements/MonitorDubna.txt](BUILD/elements/MonitorDubna.txt) is a
description of Monitor Dubna (in Russian), based on the original 1988 texts.

`BUILD/cosy/` contains Go utilities converting between the COSY text format
and UTF-8; build them with `make`.
