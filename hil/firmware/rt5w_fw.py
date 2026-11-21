# RT5W HIL firmware core. Runs unchanged on:
#   - the TT demo board (MicroPython on RP2040/RP2350, see board_tt.py + main.py),
#   - the host (CPython) against the virtual chip (rt5w/vchip.py)          -> "hil-sim",
#   - cocotb (RTL in Icarus / Verilator) through a cocotb pin driver          -> firmware-in-the-loop.
# MicroPython-compatible: no typing, no f-strings with format specs that MicroPython lacks, no numpy.
#
# Line protocol (USB serial, 115200, '\n' terminated). Replies start with "OK" or "ERR".
#   ID                      -> OK <id hex> <fw version>
#   W <addr> <data>         -> OK                      (hex)
#   R <addr>                -> OK <data>               (hex)
#   WIN <cycles>            -> OK                      settle window (clocks)
#   WAKE <n>                -> OK                      bias wake-up, 4n+1 clocks (register 0x07, default 30)
#   KEY <cell> <k>          -> OK <V_W volts>          cell 0..15 = k[r][c] at 4r+c, k in [0, 1] (0 = masked)
#   KEYS <k00> ... <k33>    -> OK                      16 keys, row-major
#   Q <q0> <q1> <q2> <q3>   -> OK                      4-bit query codes
#   PASS                    -> OK <c0> <c1> <c2> <c3> <lse|nan>
#   CAL <t0> <t1> <t2> <t3> -> OK <c0> <c1> <c2> <c3> <upd hex>   one sign-sign calibration pass
#   VBCAL                   -> OK <V_B0> <slope>       fit V_B against two known patterns (needs a V_B ADC)

import math

FW_VERSION = "0.3.0"
CTRL, Q01, Q23, K01, K23, WIN_L, WIN_H, WAKE, WSEL, PULSE = 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x09, 0x0A
TGT0, RES0, STATUS, LASTUPD, ID = 0x0C, 0x10, 0x14, 0x16, 0x7F
CTRL_GATE, CTRL_START, CTRL_CAL, CTRL_VBPROBE = 0x02, 0x04, 0x08, 0x10
STATUS_BUSY = 0x02
WSEL_EN = 0x20

# Key write (buffered gate offset key cell): the cell stores h = V_W on its grounded C_W and the DDA sets the array
# gate to g = dcol + (h - w_j), so k = exp(-(h - w_j) / nU_T,p): h = W_REF - nU_T,p ln k (h >= W_REF for k <= 1).
W_REF = 2.27          # (sky130 tt: column-line level at I_u) row trim reference w_j (written to the trim cells first); h and w share this common mode
V_DCOL_REF = W_REF    # legacy name
NUT_P = 0.0528        # PMOS array n*U_T (V), sky130 key-cell schematic (design/tb/tech.py) (design/tb/tb_keycell.py)
K_MIN = 1e-3          # k below this is written as "masked" (V_W far below -> k ~ 0)


class Rt5wFirmware:
    """hw must provide: xfer16(word) -> int (8-bit read data), start(level), sleep_us(us),
    vw_set(volts) (key DAC on ua[2]), vb_read() -> volts or None (ADC on ua[1])."""

    def __init__(self, hw):
        self.hw = hw
        self.vb0 = 1.298      # V_B at LSE = ln 4 (all x = 0); refined by VBCAL
        self.vb_slope = 0.0342  # V per e-fold of log-sum-exp (ngspice, rev 2b)
        self.win = 1000
        self.wake = 30        # register 0x07 reset value: 4*30+1 clocks = 6 us

    # ---------------------------------------------------------------- register access
    def wr(self, addr, data):
        self.hw.xfer16(0x8000 | ((addr & 0x7F) << 8) | (data & 0xFF))

    def rd(self, addr):
        return self.hw.xfer16((addr & 0x7F) << 8) & 0xFF

    def init(self):
        ident = self.rd(ID)
        self.wr(K01, 0xFF)
        self.wr(K23, 0xFF)          # row scale codes (spare in rev 2b) at full scale
        self.set_window(self.win)
        return ident

    def set_wake(self, n):
        self.wake = int(n) & 0xFF
        self.wr(WAKE, self.wake)

    def _vb_sample_us(self):
        # V_B is sampled at 80 % of the settle window, which starts after the bias wake-up
        return int((4 * self.wake + 1 + 0.8 * self.win) * 1e6 / 20e6)

    def set_window(self, cycles):
        self.win = int(cycles)
        self.wr(WIN_L, self.win & 0xFF)
        self.wr(WIN_H, (self.win >> 8) & 0xFF)

    # ---------------------------------------------------------------- keys and query
    def write_key(self, cell, k):
        if k < K_MIN:
            v_w = 3.3                                    # strongly off: masked slot (h far above w)
        else:
            v_w = W_REF - NUT_P * math.log(k)            # h = w - nU_T,p ln k
        self.wr(Q01, 0xFF)
        self.wr(Q23, 0xFF)                               # write reference: all columns at code 15
        self.wr(WSEL, WSEL_EN | (cell & 0x1F))
        self.hw.vw_set(v_w)
        self.hw.sleep_us(20)                             # C_W charge through the transmission gate
        self.wr(WSEL, cell & 0x1F)                       # open the switch
        return v_w

    def write_keys(self, k16):
        for i in range(16):
            self.write_key(i, k16[i])

    def load_query(self, q):
        self.wr(Q01, (q[0] & 15) | ((q[1] & 15) << 4))
        self.wr(Q23, (q[2] & 15) | ((q[3] & 15) << 4))

    # ---------------------------------------------------------------- passes
    def _wait_idle(self, timeout_us=200000):
        t = 0
        while self.rd(STATUS) & STATUS_BUSY:
            self.hw.sleep_us(10)
            t += 10
            if t > timeout_us:
                raise RuntimeError("pass timeout")

    def run_pass(self, cal=False):
        self.wr(CTRL, CTRL_GATE | CTRL_VBPROBE | (CTRL_CAL if cal else CTRL_START))
        lse = self._read_lse()                           # V_B is valid during the settle window
        self._wait_idle()
        codes = [self.rd(RES0 + j) for j in range(4)]
        return codes, lse

    def _read_lse(self):
        self.hw.sleep_us(self._vb_sample_us())           # sample near the end of the window
        v = self.hw.vb_read()
        if v is None:
            return float("nan")
        return math.log(4.0) + (v - self.vb0) / self.vb_slope

    def calibrate_pass(self, targets):
        for j in range(4):
            self.wr(TGT0 + j, targets[j])
        codes, _ = self.run_pass(cal=True)
        return codes, self.rd(LASTUPD)

    def vb_calibrate(self):
        """Two known patterns: all keys 0 (LSE = ln 4) and one key at 1 with q = 15s (LSE = ln(e^18 + 3))."""
        pts = []
        for top in (0.0, 1.0):
            self.write_keys([top] * 4 + [0.0] * 12)
            self.load_query([15, 15, 15, 15])
            self.wr(CTRL, CTRL_GATE | CTRL_VBPROBE | CTRL_START)
            self.hw.sleep_us(self._vb_sample_us())
            v = self.hw.vb_read()
            self._wait_idle()
            if v is None:
                return None
            pts.append(v)
        lse_hi = math.log(math.exp(18.0) + 3.0)
        slope = (pts[1] - pts[0]) / (lse_hi - math.log(4.0))
        if not (0.01 < slope < 0.08):          # expected ~0.034-0.040 V/e-fold; reject a dead or saturated probe
            raise RuntimeError("VBCAL slope %.4f V/e-fold out of range; keeping %.4f" % (slope, self.vb_slope))
        self.vb_slope, self.vb0 = slope, pts[0]
        return self.vb0, self.vb_slope


def _hx(s):
    return int(s, 16)


class Protocol:
    def __init__(self, fw):
        self.fw = fw

    def handle(self, line):
        p = line.strip().split()
        if not p:
            return "ERR empty"
        cmd, a = p[0].upper(), p[1:]
        fw = self.fw
        try:
            if cmd == "ID":
                return "OK %02x %s" % (fw.init(), FW_VERSION)
            if cmd == "W":
                fw.wr(_hx(a[0]), _hx(a[1]))
                return "OK"
            if cmd == "R":
                return "OK %02x" % fw.rd(_hx(a[0]))
            if cmd == "WIN":
                fw.set_window(int(a[0]))
                return "OK"
            if cmd == "WAKE":
                fw.set_wake(int(a[0]))
                return "OK"
            if cmd == "KEY":
                return "OK %.5f" % fw.write_key(int(a[0]), float(a[1]))
            if cmd == "KEYS":
                fw.write_keys([float(v) for v in a[:16]])
                return "OK"
            if cmd == "Q":
                fw.load_query([int(v) for v in a[:4]])
                return "OK"
            if cmd == "PASS":
                c, lse = fw.run_pass()
                return "OK %d %d %d %d %s" % (c[0], c[1], c[2], c[3], ("%.4f" % lse) if lse == lse else "nan")
            if cmd == "CAL":
                c, u = fw.calibrate_pass([int(v) for v in a[:4]])
                return "OK %d %d %d %d %02x" % (c[0], c[1], c[2], c[3], u)
            if cmd == "VBCAL":
                r = fw.vb_calibrate()
                return "ERR no V_B ADC" if r is None else "OK %.5f %.6f" % r
            return "ERR unknown command"
        except Exception as e:  # noqa: BLE001  (firmware must never die on a bad line)
            return "ERR " + str(e)
