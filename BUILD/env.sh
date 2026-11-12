# Sourced by the build scripts, from BUILD/ or a subdirectory of it.
# Tapes live in BUILD/tapes; dubna and besmtool find them via BESM6_PATH.
case `pwd` in
*/data|*/deck-b1) B=`cd .. && pwd` ;;
*) B=`pwd` ;;
esac
TAPES=${TAPES:-$B/tapes}
BESM6_PATH=$TAPES:/usr/local/share/besm6
export TAPES BESM6_PATH

# run_job job.dub listing [dir]: run a dubna job in dir (default: here).
# Tabs become spaces: dispak read them so, dubna would not.
run_job() {
    expand "$1" > "${3:-.}/.job.dub" &&
    (cd "${3:-.}" && dubna .job.dub) > "$2" 2>&1
    rm -f "${3:-.}/.job.dub"
}

# run_src_job tape listing sources... < cards
# Run the cards (from *name on) with the concatenated sources mounted as
# unit 50 and an empty tape on unit 66 for writing.
run_src_job() {
    _tape=$1 _list=$2
    shift 2
    _w=`mktemp -d` || exit 1
    cat "$@" > $_w/src.txt
    rm -f $TAPES/$_tape
    : > $TAPES/$_tape
    read -r _name
    { echo "$_name"
      echo "*tape:$_tape/src,66,w"
      echo "*disc:1/local"
      echo "*file:src,50"
      cat
    } > $_w/job
    run_job $_w/job "$_list" $_w
    rm -rf $_w
}
