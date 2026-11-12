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

See [file-list.md](file-list.md) for a per-file list.

## Building and booting

The sources are compiled by batch jobs under the Dispak simulator, then disk
and drum images are assembled and booted in SIMH.

Requirements:

- `dispak` and `besmtool` on `PATH`, with Dispak system tapes 2048 and 2148;
- SIMH `besm6` binary, with the `SIMH` variable set to its directory;
- `expect` and `telnet`.

The scripts keep tape images in `$HOME/.besm6/` and overwrite tapes 9, 12
and 37 there.

```sh
cd BUILD
./bootstrap.sh
```

The script boots the system twice. When the second boot asks for it, start
`./expe.ex` in a separate window: it connects to the second console on telnet
port 4199 and rebuilds DD and the static library inside OS Dubna, placing the
new system on drum 25.

After that, run the system from `BUILD/` with:

```sh
besm6 -i ddubna.ini
```

More details are in `BUILD/`:

- [ReadMeFirst.txt](BUILD/ReadMeFirst.txt), [ReadMeBoot.txt](BUILD/ReadMeBoot.txt) — boot steps and known restrictions;
- [ReadMeTapes.txt](BUILD/ReadMeTapes.txt) — tape numbers used by the bootstrap;
- [ReadMeJobs.txt](BUILD/ReadMeJobs.txt) — how to submit jobs to the running system;
- [the-bootstrap-plan.txt](BUILD/the-bootstrap-plan.txt) — phases of the bootstrap.

## Documentation

[BUILD/elements/MonitorDubna.txt](BUILD/elements/MonitorDubna.txt) is a
description of Monitor Dubna (in Russian), based on the original 1988 texts.

`BUILD/cosy/` contains Go utilities converting between the COSY text format
and UTF-8; build them with `make`.
