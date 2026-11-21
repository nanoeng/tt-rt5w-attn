#!/usr/bin/env python3
"""A software TT demo board on a pseudo-terminal: the HIL firmware (hil/firmware/rt5w_fw.py) runs against the
virtual chip and answers the line protocol on /dev/pts/N, so the host HIL backend (pyserial) can be tested end to
end without hardware:  python3 hil/tests/fake_board.py [--seed 3] &   then  --backend hil --port <printed path>"""
import argparse
import os
import pty
import sys
import tty

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "hil", "firmware"))
from rt5w_fw import Rt5wFirmware, Protocol    # noqa: E402
from rt5w.vchip import VirtualChip           # noqa: E402


class HW:
    def __init__(self, chip):
        self.chip = chip

    def xfer16(self, w):
        return self.chip.xfer16(w)

    def start(self, level):
        pass

    def sleep_us(self, us):
        pass

    def vw_set(self, v):
        self.chip.vw_set(v)

    def vb_read(self):
        return self.chip.vb_read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int)
    ap.add_argument("--link", default="/tmp/rt5w_hil_tty")
    a = ap.parse_args()
    master, slave = pty.openpty()
    tty.setraw(slave)
    path = os.ttyname(slave)
    if os.path.lexists(a.link):
        os.unlink(a.link)
    os.symlink(path, a.link)
    proto = Protocol(Rt5wFirmware(HW(VirtualChip(seed=a.seed))))
    print(f"fake TT board on {path} (link {a.link})", flush=True)
    os.write(master, b"RT5W HIL ready\r\n")
    buf = b""
    while True:
        buf += os.read(master, 4096)
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            reply = proto.handle(line.decode(errors="replace"))
            os.write(master, (reply + "\r\n").encode())


if __name__ == "__main__":
    main()
