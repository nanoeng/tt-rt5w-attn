# Runs under MicroPython (unix port or on the board): firmware + protocol against a minimal register-level mock.
# micropython hil/tests/mp_selftest.py   (from the repo root, with hil/firmware on sys.path)
import sys
sys.path.append("hil/firmware")
from rt5w_fw import Rt5wFirmware, Protocol


class MockChip:
    """Register file + a pass that returns fixed codes (enough to exercise every firmware/protocol path)."""
    def __init__(self):
        self.reg = [0] * 128
        self.reg[0x7F] = 0x5A
        self.vw = []

    def xfer16(self, w):
        a, d = (w >> 8) & 0x7F, w & 0xFF
        if w & 0x8000:
            if a == 0x00 and d & 0x0C:
                self.reg[0x10:0x14] = [225, 30, 0, 0]
                self.reg[0x16] = 0x02 if d & 0x08 else 0
                return 0
            self.reg[a] = d
            return 0
        return self.reg[a]

    def start(self, l): pass
    def sleep_us(self, us): pass
    def vw_set(self, v): self.vw.append(v)
    def vb_read(self): return 1.298 + 0.0342 * (18.127 - 1.386)


chip = MockChip()
p = Protocol(Rt5wFirmware(chip))
cmds = ["ID", "W 05 e8", "R 05", "WIN 1000", "KEY 0 1.0", "KEY 5 0.0",
        "KEYS 1 1 1 1 0.889 0.889 0.889 0.889 0 0 0 0 0 0 0 0", "Q 15 15 15 15", "PASS", "CAL 225 30 0 0", "VBCAL", "BOGUS"]
ok = True
for c in cmds:
    r = p.handle(c)
    print(c, "->", r)
    if c in ("BOGUS", "VBCAL"):          # the mock's V_B is constant -> VBCAL must refuse, not store slope 0
        ok &= r.startswith("ERR")
    else:
        ok &= r.startswith("OK")
r = p.handle("PASS").split()
ok &= r[1:5] == ["225", "30", "0", "0"] and abs(float(r[5]) - 18.127) < 0.01
print("MICROPYTHON SELFTEST", "PASS" if ok else "FAIL")
