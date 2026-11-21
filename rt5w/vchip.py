"""Virtual chip: register-accurate Python model of tt_um_rt5w_attn (rt5w_ctrl.v + analog model).
Implements the same SPI frame semantics as the RTL, so the HIL firmware (hil/firmware/rt5w_fw.py) can run
against it unchanged ("hil-sim"). Timing is not cycle-accurate: a pass completes within the xfer that starts it."""
import math

from . import regmap as R
from .analog_model import AnalogModel


class VirtualChip:
    def __init__(self, seed=None, ideal=False, params=None):
        self.ana = AnalogModel(seed=seed, ideal=ideal, params=params)
        self.reg = [0] * 128
        self.reg[R.CTRL] = R.CTRL_GATE
        self.reg[R.WIN_L], self.reg[R.WIN_H], self.reg[R.WAKE], self.reg[R.ADCT] = 1000 & 0xFF, 1000 >> 8, 30, 8
        self.reg[R.PULSE] = 1
        self.reg[R.ID] = R.ID_VALUE
        self.vw = 0.0
        self.vb = None
        self.log = []

    # ---- pins
    def vw_set(self, volts):
        self.vw = volts
        if self.reg[R.WSEL] & R.WSEL_EN:
            self.ana.write_cell_voltage(self.reg[R.WSEL] & 0x1F, volts)

    def vb_read(self):
        return self.vb

    # ---- SPI
    def xfer16(self, word):
        addr, data = (word >> 8) & 0x7F, word & 0xFF
        if word & 0x8000:
            self._write(addr, data)
            return 0
        return self.reg[addr] if addr < 0x7F else R.ID_VALUE

    def _write(self, addr, data):
        if addr in (R.RES0, R.RES0 + 1, R.RES0 + 2, R.RES0 + 3, R.STATUS, R.NPASS, R.LASTUPD, R.ID):
            return                                   # read-only
        if addr == R.CTRL:
            self.reg[R.CTRL] = data & ~(R.CTRL_START | R.CTRL_CAL) & 0xFF
            if data & (R.CTRL_START | R.CTRL_CAL):
                self._pass(cal=bool(data & R.CTRL_CAL))
            return
        if addr == R.WSEL:
            self.reg[R.WSEL] = data & 0x3F
            if data & R.WSEL_EN:
                self.ana.write_cell_voltage(data & 0x1F, self.vw)
            return
        self.reg[addr] = data

    def _pass(self, cal):
        q = [self.reg[R.Q01] & 15, self.reg[R.Q01] >> 4, self.reg[R.Q23] & 15, self.reg[R.Q23] >> 4]
        win = self.reg[R.WIN_L] | (self.reg[R.WIN_H] << 8)
        codes, vb, x = self.ana.evaluate(q, window_us=win / R.CLK_HZ * 1e6)
        self.vb = vb if (self.reg[R.CTRL] & R.CTRL_VBPROBE) else None
        for j in range(4):
            self.reg[R.RES0 + j] = codes[j]
        self.reg[R.NPASS] = (self.reg[R.NPASS] + 1) & 0xFF
        upd = 0
        if cal:
            up = dn = 0
            for r in range(1, 4):                      # row 0 pinned; equal codes -> no pulse
                t = self.reg[R.TGT0 + r]
                if codes[r] < t:
                    up |= 1 << r
                elif codes[r] > t:
                    dn |= 1 << r
            self.ana.pump(up, dn, clocks=max(1, self.reg[R.PULSE] & 15))
            upd = (dn << 4) | up
            self.reg[R.LASTUPD] = upd
        self.reg[R.STATUS] = R.STATUS_VALID | (R.STATUS_CAL if cal else 0)
        self.log.append(dict(q=q, codes=codes, x=list(x), cal=cal, upd=upd))
