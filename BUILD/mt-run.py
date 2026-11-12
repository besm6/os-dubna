#!/usr/bin/env python3
"""Boot OS Dubna and run a job from 7/M through Multitype.

Usage: mt-run.py [zone]     (zone of 7/M, octal, default 110 = hello.dub)

Starts besm6 with boot-run.ini. The simulator connects tty25 (operator
console) and tty26 (Multitype) to sockets opened here; both are driven
with send/expect. Transcripts: mt-run-tty25.txt, mt-run-tty26.txt.
"""
import os, re, select, shutil, socket, subprocess, sys, time

ZONE = sys.argv[1] if len(sys.argv) > 1 else "110"

# GOST output turns Latin lookalikes into Cyrillic: compare both as Latin.
# Timeouts are multiplied by SLOW (for traced runs).
SLOW = float(os.environ.get("SLOW", "1"))

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
        self.log = open("mt-run-%s.txt" % name, "w")

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

def main():
    if os.environ.get("FRESH"):
        fresh()
    l25, l26 = listen(), listen()
    env = dict(os.environ,
               TTY25=str(l25.getsockname()[1]),
               TTY26=str(l26.getsockname()[1]))
    out = open("boot-run.out", "w")
    sim = subprocess.Popen(["besm6", os.environ.get("INI", "boot-run.ini")], env=env,
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
        if norm("ДАЙТЕ ПРИКАЗ") in norm(m.group(1)):
            con.send(os.environ.get("ORDER", "A1P") + "\r")

        # Multitype: password, buffer, list and submit the job.
        mt.connect()
        mt.send("  ");          mt.expect(r"PASS:")
        mt.send("MJPOP\r");     mt.expect(r"БУФЕР:")
        mt.send("7/M\r");       mt.expect(r"\n {5}")
        mt.send("ЛИС %s\r" % ZONE)
        mt.expect(r"\*END FILE\n")
        # Extra Multitype commands before the submit, separated by "|".
        for cmd in filter(None, os.environ.get("BEFORE", "").split("|")):
            mt.send(cmd + "\r")
            mt.expect(r"\n {5}\S.*\n")
            mt.read(2)
        # A listing that fills a page waits for a key: end it with an empty line.
        mt.send("\r")
        mt.read(1)
        # СЛА runs the job from the buffer; ПУС puts it into the input queue.
        submit = os.environ.get("SUBMIT", "СЛА")
        mt.send("%s %s,17\r" % (submit, ZONE))
        mt.expect(r"\n {5}\S.*\n")
        entry = ""
        if submit == "ПУС":
            entry = mt.expect(r"ВВОДА: (\d+)").group(1)

        # Operator orders after the submit, separated by "|"; {} is the input
        # file entry of a ПУС job, e.g. "{}БП" starts it at once. They are
        # repeated every 15 s until the job starts: too early, they are ignored.
        orders = [c.replace("{}", entry) for c in
                  filter(None, os.environ.get("CONSUBMIT", "").split("|"))]
        end = time.time() + int(os.environ.get("JOBWAIT", "180")) * SLOW
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
        # Extra operator orders after the job starts, separated by "|".
        for cmd in filter(None, os.environ.get("CONAFTER", "").split("|")):
            time.sleep(2)
            con.send(cmd + "\r")
            con.read(3)
        # Poll until the job ends: "СЧЕТ ОКОНЧЕН" for a queued job,
        # "НЕТ ЗАДАЧ" once it has been seen running.
        seen = False
        poll = os.environ.get("POLL", "KAK")    # СЧЕ shows all jobs
        for _ in range(int(os.environ.get("POLLS", "60"))):
            mt.send(poll + "\r")
            m = mt.expect(re.escape(poll) + r"\n(.*\n)")
            if norm("ОКОНЧЕН") in m.group(1):
                break
            if norm("НЕТ ЗАДАЧ") in m.group(1):
                if seen:
                    break
            else:
                seen = True
            time.sleep(1)
        else:
            print("\n--- the job was not seen to finish")
        # Extra Multitype commands, separated by "|".
        # An empty command is an empty line (next page, or end of a listing).
        after = os.environ.get("AFTER")
        for cmd in after.split("|") if after else []:
            mt.send(cmd + "\r")
            mt.read(3)
        # Wait for printing to start, then until it stops for 3 s.
        end = time.time() + int(os.environ.get("PRNWAIT", "20"))
        size, still = 0, 0
        while time.time() < end and (not size or still < 3):
            con.read(0.5); mt.read(0.5)
            n = prn_bytes()
            still = still + 1 if n == size else 0
            size = n
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
