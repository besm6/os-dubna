# Sourced by the build scripts, from BUILD/ or a subdirectory of it.
# Tapes live in BUILD/tapes; dispak and besmtool find them via BESM6_PATH.
case `pwd` in
*/data|*/spl|*/deck-b1) B=`cd .. && pwd` ;;
*) B=`pwd` ;;
esac
TAPES=${TAPES:-$B/tapes}
BESM6_PATH=$TAPES:/usr/local/share/besm6
export TAPES BESM6_PATH
