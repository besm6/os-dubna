#!/usr/bin/env python3
"""Drive a Multitype session on OS Dubna over telnet (tty26, port 4199).

Usage: mt-session.py ZONE   -- list and run the job in zone ZONE of 7/M.
"""
import socket, sys, time

zone = sys.argv[1] if len(sys.argv) > 1 else "110"
s = socket.create_connection(("127.0.0.1", 4199))
s.settimeout(1)
buf = b""

def pump(seconds):
    """Read for a while, answer telnet options, echo what arrives."""
    global buf
    end = time.time() + seconds
    while time.time() < end:
        try:
            d = s.recv(4096)
        except socket.timeout:
            continue
        if not d:
            break
        out = bytearray()
        i = 0
        while i < len(d):
            if d[i] == 255 and i + 2 < len(d) and d[i+1] in (251, 252, 253, 254):
                # refuse every option
                reply = 254 if d[i+1] in (251, 252) else 252
                s.sendall(bytes([255, reply, d[i+2]]))
                i += 3
            else:
                out.append(d[i]); i += 1
        buf += bytes(out)
        sys.stdout.write(out.decode("utf-8", "replace")); sys.stdout.flush()

def expect(text, timeout=120):
    global buf
    end = time.time() + timeout
    while time.time() < end:
        if text.encode() in buf:
            buf = buf.split(text.encode(), 1)[1]
            return True
        pump(1)
    print("\n[timeout waiting for %r]" % text)
    return False

def send(text, wait=3):
    s.sendall(text.encode())
    pump(wait)

pump(5)
send("OP"); send("\r"); send("\r")      # become an operator console
expect("!!!")
send("REF\r", 20)                       # release it again
send("  ", 20)                          # two spaces: Multitype
expect("SS:")
send("MJPOP\r")
expect("ФЕР:")
send("7/M\r")
send("ЛИС %s\r" % zone)                 # list the job text
expect("END FILE")
send("СЛА %s,17\r" % zone)              # submit it
pump(10)
for _ in range(20):                     # poll until no jobs are left
    send("KAK\r", 8)
    if "ЗАДАЧ".encode() in buf:
        break
print("\n[session done]")
