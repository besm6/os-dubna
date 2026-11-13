#!/usr/bin/env python3
"""Boot OS Dubna in SIMH and run one job non-interactively.

Starts besm6 with boot-run.ini. The simulator connects tty25 (operator
console) and tty26 (Multitype) to sockets opened here; both are driven
with send/expect. Transcripts: boot-run-tty25.txt, boot-run-tty26.txt,
listings: output.txt.
"""
import argparse, os, re, select, shutil, socket, subprocess, sys, time

A = None                # parsed options
SLOW = 1                # timeouts are multiplied by it (for traced runs)

# GOST output turns Latin lookalikes into Cyrillic: compare both as Latin.

LOOK = str.maketrans("АВЕКМНОРСТХУ", "ABEKMHOPCTXY")

def norm(s):
    return s.translate(LOOK)

class Fail(Exception):
    pass

class Line:
    def __init__(self, name, listener):
        self.name = name
        self.listener = listener
        self.sock = None
        self.text = ""          # unread output
        self.log = open("boot-run-%s.txt" % name, "w")

    def connect(self, timeout=10):
        """SIMH probes a Connect= address at attach time and hangs up;
        the real connection comes at the first poll, with a banner."""
        end = time.time() + timeout * SLOW
        while not self.text:
            if time.time() > end:
                raise Fail("%s: no connection" % self.name)
            if self.sock is None:
                self.sock, _ = self.listener.accept()
            self.read(0.5)

    def read(self, timeout):
        r, _, _ = select.select([self.sock], [], [], timeout)
        if not r:
            return
        d = self.sock.recv(4096)
        if not d:
            self.sock.close()
            self.sock = None
            if self.text:
                raise Fail("%s: connection closed" % self.name)
            return
        s = d.decode("utf-8", "replace").replace("\r", "")
        self.text += s
        self.log.write(s); self.log.flush()
        sys.stdout.write(s); sys.stdout.flush()

    def expect(self, pattern, timeout=10):
        """Wait for a regex (lookalikes ignored); consume output up to it."""
        rx = re.compile(norm(pattern))
        end = time.time() + timeout * SLOW
        while True:
            m = rx.search(norm(self.text))
            if m:
                self.text = self.text[m.end():]
                return m
            left = end - time.time()
            if left <= 0:
                raise Fail("%s: timeout waiting for %r" % (self.name, pattern))
            self.read(min(left, 0.5))

    def send(self, text):
        # One character at a time: the Consul input register holds one.
        for c in text:
            self.sock.sendall(c.encode())
            time.sleep(0.02)

def prn_bytes():
    return sum(os.path.getsize(f) for f in ("output.txt", "output1.txt")
               if os.path.exists(f))

def listing_done():
    """The printer file ends with the trailer of a job listing."""
    for f in ("output.txt", "output1.txt"):
        if os.path.exists(f):
            with open(f, "rb") as fd:
                fd.seek(max(0, os.path.getsize(f) - 600))
                tail = norm(fd.read().decode("utf-8", "replace")).rstrip()
            if norm("КОНЕЦ ЗАДАЧИ") in tail and tail.endswith("*" * 20):
                return True
    return False

def listen():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 0))
    s.listen(1)
    s.settimeout(30)
    return s

def fresh():
    """FRESH=1: start from the images saved in data/base."""
    for f in ("dubdrum1.bin", "dubdrum2.bin", "disk9.bin", "disk11.bin"):
        shutil.copyfile("data/base/" + f, "data/" + f)

def by_multitype(con, mt):
    """Submit the job from zone ZONE of 7/M and wait until it ends."""
    # Multitype: password, buffer, list and submit the job.
    mt.connect()
    mt.send("  ");          mt.expect(r"PASS:")
    mt.send("MJPOP\r");     mt.expect(r"БУФЕР:")
    mt.send("7/M\r");       mt.expect(r"\n {5}")
    mt.send("ЛИС %s\r" % A.zone)
    mt.expect(r"\*END FILE\n")
    for cmd in A.before:
        mt.send(cmd + "\r")
        mt.expect(r"\n {5}\S.*\n")
        mt.read(2)
    # A listing that fills a page waits for a key: end it with an empty line.
    mt.send("\r")
    mt.read(1)
    # СЛА runs the job from the buffer; ПУС puts it into the input queue.
    submit = "ПУС" if A.queue else "СЛА"
    mt.send("%s %s,17\r" % (submit, A.zone))
    mt.expect(r"\n {5}\S.*\n")
    entry = ""
    if submit == "ПУС":
        entry = mt.expect(r"ВВОДА: (\d+)").group(1)

    # Orders after the submit are repeated every 15 s until the job
    # starts: too early, they are ignored.
    orders = [c.replace("{}", entry) for c in A.consubmit]
    end = time.time() + A.jobwait * SLOW
    while True:
        for cmd in orders:
            time.sleep(2)
            con.send(cmd + "\r")
        try:
            # The job starts from the input queue: its code is announced.
            con.expect(r"Ш\d\d:", 15 if orders else end - time.time())
            break
        except Fail:
            if time.time() >= end:
                raise
    for cmd in A.conafter:
        time.sleep(2)
        con.send(cmd + "\r")
        con.read(3)
    # The job has started, so "НЕТ ЗАДАЧ" means it has ended. A queued job
    # is not shown by КАК (СЧЕ shows all jobs); its listing ends the wait.
    poll = A.poll
    while not listing_done():
        mt.send(poll + "\r")
        m = mt.expect(re.escape(poll) + r"\n(.*\n)")
        if re.search(norm("ОКОНЧЕН|НЕТ ЗАДАЧ"), norm(m.group(1))):
            break
        if time.time() >= end:
            raise Fail("the job did not finish")
        time.sleep(0.3)
    # An empty command is an empty line (next page, or end of a listing).
    for cmd in A.after:
        mt.send(cmd + "\r")
        mt.read(3)
    return submit == "ПУС"         # a listing is printed

def by_cards(con):
    """Start a job from the deck in card reader vu0 (see boot-run.ini)."""
    wait = A.jobwait * SLOW
    con.send(A.card_order + "\r")
    con.expect(r"Ш\d\d:", wait)
    # The job ends: NNNN-КШnn-time-name.
    con.expect(r"-КШ\d\d-.*\n", wait)
    return True                     # a listing is printed

USAGE = """%(prog)s [options] deck
       %(prog)s [options] -m zone"""

DESCRIPTION = """Boot OS Dubna in SIMH (boot-run.ini) and run one job without a user.
The job is a deck of punch cards in reader vu0, started by an operator
order, or with -m the deck at a zone of the Multitype buffer 7/M (octal;
110 is hello.dub, written there by put-job.sh), submitted from Multitype."""

EPILOG = """examples:
  %(prog)s -f -d 25 deck         a deck of cards; it must end with a line
                                 of six backquotes (see card-run.sh)
  %(prog)s -f -d 25 -m 110       hello from 7/M through Multitype
  %(prog)s -f -d 25 -q -m 110    the same, queued, so the listing is printed

Transcripts: boot-run-tty25.txt, boot-run-tty26.txt; listings: output.txt.
The run ends when the job ends and its listing is printed; the exit
status is 0 on success."""

def options():
    p = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION, epilog=EPILOG,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cards", nargs="?", metavar="deck",
                   help="deck of punch cards, a text file, one card per line")
    p.add_argument("-f", "--fresh", action="store_true",
                   help="start from the images in data/base")
    p.add_argument("-d", "--drum", choices=("20", "25"), default="20",
                   help="boot the dispatcher from drum 20 (default) or the one "
                        "rebuilt by newdd on drum 25")
    p.add_argument("-o", "--order", default="A1P", metavar="ORDER",
                   help="answer to the spooler's paper request (default %(default)s)")
    g = p.add_argument_group("card job")
    g.add_argument("-r", "--card-order", default="01В", metavar="ORDER",
                   help="order that starts it (default %(default)s; ПВ puts "
                        "the deck into the input file)")
    g.add_argument("-u", "--updk", action="store_true",
                   help="punch the deck in the UPDK code (default UPP)")
    g.add_argument("-v", "--vu-debug", action="store_true",
                   help="trace the card reader")
    g = p.add_argument_group("Multitype job")
    g.add_argument("-m", "--multitype", dest="zone", metavar="ZONE",
                   help="run the job at ZONE of 7/M instead, octal")
    g.add_argument("-q", "--queue", action="store_true",
                   help="submit with ПУС into the input queue, so the listing "
                        "is printed (default: СЛА, run from the buffer)")
    g.add_argument("-b", "--before", action="append", default=[], metavar="CMD",
                   help="Multitype command before the submit (repeatable)")
    g.add_argument("-s", "--consubmit", action="append", default=[], metavar="ORDER",
                   help="console order after the submit, repeated until the job "
                        "starts; {} is the input file entry of a ПУС job, "
                        "e.g. {}БП (repeatable)")
    g.add_argument("-n", "--conafter", action="append", default=[], metavar="ORDER",
                   help="console order after the job starts (repeatable)")
    g.add_argument("-p", "--poll", default="KAK", metavar="CMD",
                   help="Multitype command polled until the job ends "
                        "(default %(default)s; СЧЕ shows all jobs)")
    g.add_argument("-a", "--after", action="append", default=[], metavar="CMD",
                   help="Multitype command after the job; an empty one is an "
                        "empty line (repeatable)")
    g = p.add_argument_group("limits and debugging")
    g.add_argument("--jobwait", type=int, default=600, metavar="SEC",
                   help="limit for the job to start and end (default %(default)s)")
    g.add_argument("--prnwait", type=int, default=600, metavar="SEC",
                   help="limit for the listing to be printed (default %(default)s)")
    g.add_argument("--slow", type=float, default=1, metavar="N",
                   help="multiply all timeouts by N, for traced runs")
    g.add_argument("--ini", default="boot-run.ini", metavar="FILE",
                   help="SIMH script (default %(default)s)")
    if len(sys.argv) == 1:
        p.print_help()
        sys.exit(2)
    a = p.parse_args()
    if (a.zone is None) == (a.cards is None):
        p.error("give either a deck or -m zone")
    return a

def main():
    global A, SLOW
    A = options()
    SLOW = A.slow
    if A.fresh:
        fresh()
    l25, l26 = listen(), listen()
    # boot-run.ini takes its parameters from the environment.
    env = dict(os.environ,
               TTY25=str(l25.getsockname()[1]),
               TTY26=str(l26.getsockname()[1]),
               DRUM=A.drum, CARDS=A.cards or "",
               UPDK="1" if A.updk else "",
               VUDEBUG="1" if A.vu_debug else "")
    out = open("boot-run.out", "w")
    sim = subprocess.Popen(["besm6", A.ini], env=env,
                           stdin=subprocess.PIPE, stdout=out, stderr=out)
    try:
        con, mt = Line("tty25", l25), Line("tty26", l26)
        con.connect()

        # Operator console: date, time, printer ready.
        con.expect(r"W23\n", 30)
        con.send("\r");        con.expect(r"!!!")
        con.send("040489D\r"); con.expect(r"04/04/89.*\n")
        con.send("T\r")
        # The spooler asks for paper, unless the task library is still empty (ТАSК!).
        m = con.expect(r"([\s\S]*?)ПЛАНИРОВЩИК", 40)
        spooler = norm("ДАЙТЕ ПРИКАЗ") in norm(m.group(1))
        if spooler:
            con.send(A.order + "\r")

        if A.cards:
            listing = by_cards(con)
        else:
            listing = by_multitype(con, mt)
        # Wait for the trailer of the listing, if there is a spooler to print it.
        end = time.time() + A.prnwait * SLOW
        while listing and spooler and not listing_done():
            if time.time() > end:
                raise Fail("the listing was not printed to the end")
            con.read(0.2)
            if mt.sock:
                mt.read(0.05)
        print("\n--- printers: %d bytes" % prn_bytes())
        return 0
    except Fail as e:
        print("\nFAIL:", e)
        return 1
    finally:
        # Stop the run and quit, so that SIMH flushes and closes the images.
        sim.terminate()
        try:
            sim.stdin.write(b"quit\n")
            sim.stdin.close()
            sim.wait(30)
        except (BrokenPipeError, subprocess.TimeoutExpired):
            print("\nFAIL: the simulator did not quit; images may be stale")
            sim.kill()

sys.exit(main())
