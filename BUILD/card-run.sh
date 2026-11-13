#!/bin/sh
# Boot OS Dubna and run a job from a deck of punch cards; see card-run.ini.
# Usage: ./card-run.sh job.dub      (text, one card per line, e.g. hello.dub)
# The listing goes to output.txt.
[ -r "$1" ] || { echo "Usage: $0 job.dub" >&2; exit 1; }

# Start from the ready images.
cp data/base/*.bin data/

# The deck ends with the end-of-deck card, a line of six backquotes.
deck=card-run.deck
tr -d '\r' < "$1" > $deck
[ "$(tail -n 1 $deck)" = '``````' ] || echo '``````' >> $deck

exec besm6 card-run.ini $deck
