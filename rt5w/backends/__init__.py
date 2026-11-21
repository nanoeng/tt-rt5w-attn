"""Execution backends for one RT5W pass. All share: run(enc) -> (codes[4], lse or nan).

  ideal     exact chip arithmetic (golden codes)
  behav     Python behavioural model (analog_model.py), optional Monte-Carlo die (seed)
  hil-sim   HIL firmware protocol (hil/firmware/rt5w_fw.py) running on the host against the virtual chip
  hil       HIL firmware on the TT demo board over USB serial (pyserial)
  ngspice   transistor-level array + softmax core (analog/rt5w_core.spice), ngspice CLI
  pyspice   same netlist through PySpice / libngspice (shared library)
The cocotb RTL path (Icarus / Verilator) lives in test/test_illustrated.py and uses the same firmware."""
import math
import os
import sys

import numpy as np

from ..golden import softmax

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "hil", "firmware"))


class Backend:
    name = "base"

    def run(self, enc):
        raise NotImplementedError

    def close(self):
        pass


class IdealBackend(Backend):
    name = "ideal"

    def run(self, enc):
        x = enc.x_expected
        return enc.golden_codes(), float(np.log(np.exp(x - x.max()).sum()) + x.max())


class BehavBackend(Backend):
    name = "behav"

    def __init__(self, seed=None):
        from ..analog_model import AnalogModel
        self.m = AnalogModel(seed=seed)

    def run(self, enc):
        self.m.k = np.asarray(enc.k, float).copy()
        codes, v_b, _ = self.m.evaluate(enc.q_codes)
        lse = math.log(4.0) + (v_b - self.m.p["vb0"]) / self.m.p["vb_slope"]
        return codes, lse


class ProtocolBackend(Backend):
    """Talks the HIL line protocol; subclasses provide _cmd(line) -> reply."""

    def _ok(self, line):
        r = self._cmd(line).strip()
        if not r.startswith("OK"):
            raise RuntimeError(f"{line!r} -> {r!r}")
        return r.split()[1:]

    def setup(self):
        ident = self._ok("ID")
        assert int(ident[0], 16) == 0x5A, ident
        return ident

    def run(self, enc):
        self._ok("KEYS " + " ".join(f"{v:.6f}" for v in np.asarray(enc.k).ravel()))
        self._ok("Q " + " ".join(str(int(v)) for v in enc.q_codes))
        r = self._ok("PASS")
        return [int(v) for v in r[:4]], float(r[4])

    def calibrate(self, enc):
        """One on-chip sign-sign pass: load the vector, targets = golden codes, firmware issues CAL."""
        self._ok("KEYS " + " ".join(f"{v:.6f}" for v in np.asarray(enc.k).ravel()))
        self._ok("Q " + " ".join(str(int(v)) for v in enc.q_codes))
        r = self._ok("CAL " + " ".join(str(int(t)) for t in enc.golden_codes()))
        return [int(v) for v in r[:4]], int(r[4], 16)


class HilSimBackend(ProtocolBackend):
    name = "hil-sim"

    def __init__(self, seed=None):
        from rt5w_fw import Rt5wFirmware, Protocol
        from ..vchip import VirtualChip

        class _HW:
            def __init__(s, chip):
                s.chip = chip

            def xfer16(s, w):
                return s.chip.xfer16(w)

            def start(s, level):
                pass

            def sleep_us(s, us):
                pass

            def vw_set(s, v):
                s.chip.vw_set(v)

            def vb_read(s):
                return s.chip.vb_read()

        self.chip = VirtualChip(seed=seed)
        self.proto = Protocol(Rt5wFirmware(_HW(self.chip)))
        self.setup()

    def _cmd(self, line):
        return self.proto.handle(line)


class HilBackend(ProtocolBackend):
    """HIL over any pyserial URL:
         /dev/ttyACM0, COM5            local USB serial (board plugged into this machine)
         rfc2217://host:4000           board on another machine / the container host (hil/tools/rfc2217_bridge.py)
         socket://host:4000            raw TCP (e.g. ser2net in raw mode)
         loop://                       loopback (transport self-test only)"""
    name = "hil"

    def __init__(self, port, baud=115200, timeout=5.0):
        import serial
        self.s = serial.serial_for_url(port, baudrate=baud, timeout=timeout)
        self.s.reset_input_buffer()
        self.setup()

    def _cmd(self, line):
        self.s.write((line + "\n").encode())
        while True:                                   # skip echo / banner lines
            r = self.s.readline().decode(errors="replace").strip()
            if not r:
                raise TimeoutError(line)
            if r.startswith(("OK", "ERR")):
                return r

    def close(self):
        self.s.close()


def get_backend(name, **kw):
    if name == "ideal":
        return IdealBackend()
    if name == "behav":
        return BehavBackend(seed=kw.get("seed"))
    if name == "hil-sim":
        return HilSimBackend(seed=kw.get("seed"))
    if name == "hil":
        return HilBackend(kw["port"])
    if name in ("ngspice", "pyspice"):
        from .spice import SpiceBackend
        return SpiceBackend(engine=name, corner=kw.get("corner", "tt"), temp=kw.get("temp", 27))
    raise ValueError(name)
