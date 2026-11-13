#!/bin/sh
# Boot OS Dubna and run a job from a deck of punch cards.
# Usage: ./card-run.sh job.dub      (text, one card per line, e.g. hello.dub)
# The end-of-deck card (a line of six backquotes) is added if missing.
# Options are those of mt-run.py; CARDORDER=ПВ goes through the input file.
[ -r "$1" ] || { echo "Usage: $0 job.dub" >&2; exit 1; }
deck=card-run.deck
tr -d '\r' < "$1" > $deck
[ "$(tail -n 1 $deck)" = '``````' ] || echo '``````' >> $deck
CARDS=$deck DRUM=${DRUM:-25} FRESH=${FRESH-1} exec ./mt-run.py
