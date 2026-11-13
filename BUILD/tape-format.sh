#!/bin/sh
# Boot OS Dubna, mount a blank magnetic tape on drive 60 and format it;
# see tape-format.ini.
# Usage: ./tape-format.sh [image]       (default tape60.tap)
tape=${1:-tape60.tap}

# Start from the ready images.
cp data/base/*.bin data/

# An empty file is a blank reel.
: > "$tape"

exec besm6 tape-format.ini "$tape"
