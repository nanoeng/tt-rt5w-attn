# SPDX-License-Identifier: Apache-2.0
"""Firmware-in-the-loop on the RTL: the unchanged HIL firmware (hil/firmware/rt5w_fw.py) and the unchanged
Illustrated-Transformer examples (rt5w/illustrated.py) drive tt_um_rt5w_attn in Icarus or Verilator.

  blocking firmware code ----cocotb.task.bridge----> runs in a thread
  hw.xfer16 / sleep_us / vw_set ----cocotb.task.resume----> await on the simulator (SPI bit-bang on ui_in/uio_out)

Analog pins: ua[2] key writes are applied to the behavioural model's key memory for the selected cell
(the Verilog model has no real-valued pins); V_B (ua[1]) is computed from the model's score reals."""
import math
import os
import sys

import cocotb
from cocotb.task import bridge, resume
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "hil", "firmware"))
import rt5w_fw                                           # noqa: E402
from rt5w.backends import ProtocolBackend                # noqa: E402
from rt5w.illustrated import EXAMPLES, calibrate         # noqa: E402

CLK_NS, SCK_HALF_NS = 50, 500
VB0, VB_SLOPE = 1.298, 0.0342


class CocotbHW:
    """Board adapter for the simulator: same interface as hil/firmware/board_tt.py."""

    def __init__(self, dut):
        self.dut = dut
        self.ana = dut.user_project.u_ana

    async def _xfer(self, word):
        dut = self.dut
        base = dut.ui_in.value.to_unsigned() & ~0x07
        dut.ui_in.value = base
        await Timer(SCK_HALF_NS, "ns")
        rd = 0
        for b in range(15, -1, -1):
            m = ((word >> b) & 1) << 1
            dut.ui_in.value = base | m
            await Timer(SCK_HALF_NS, "ns")
            dut.ui_in.value = base | m | 1
            if b < 8:
                rd = (rd << 1) | (dut.uio_out.value.to_unsigned() & 1)
            await Timer(SCK_HALF_NS, "ns")
        dut.ui_in.value = base | 0x04
        await Timer(SCK_HALF_NS, "ns")
        return rd

    async def _sleep(self, us):
        await Timer(max(int(us * 1000), 1), "ns")

    async def _vw(self, volts):
        if int(self.ana.wsel_en.value):
            cell = int(self.ana.wsel_i.value)
            if cell < 16:
                dh = volts - rt5w_fw.W_REF                       # h - w (buffered gate offset key cell)
                k = math.exp(-dh / rt5w_fw.NUT_P) if dh < 0.6 else 0.0
                code = max(0, min(255, int(round(255 * min(k, 1.0)))))
                flat = self.ana.kflat.value.to_unsigned()
                flat = (flat & ~(0xFF << (8 * cell))) | (code << (8 * cell))
                self.ana.kflat.value = flat
        await Timer(1, "ns")

    async def _vb(self):
        xs = [float(getattr(self.ana, f"x{j}").value) for j in range(4)]
        m = max(xs)
        lse = m + math.log(sum(math.exp(x - m) for x in xs))
        return VB0 + VB_SLOPE * (lse - math.log(4.0))

    # blocking API used by the firmware (called from a cocotb.bridge thread)
    def xfer16(self, w):
        return resume(self._xfer)(w)

    def start(self, level):
        pass

    def sleep_us(self, us):
        resume(self._sleep)(us)

    def vw_set(self, v):
        resume(self._vw)(v)

    def vb_read(self):
        return resume(self._vb)()


class RtlBackend(ProtocolBackend):
    name = "rtl"

    def __init__(self, dut):
        self.proto = rt5w_fw.Protocol(rt5w_fw.Rt5wFirmware(CocotbHW(dut)))

    def _cmd(self, line):
        return self.proto.handle(line)


async def reset(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.ena.value = 1
    dut.ui_in.value = 0x04
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)


def _make_test(fn, tol):
    async def _t(dut):
        await reset(dut)
        be = RtlBackend(dut)
        await bridge(be.setup)()
        r = await bridge(fn)(be)
        dut._log.info(f"{r['example']}: max|err| {r['max_abs_err']} argmax_ok {r['argmax_ok']} "
                      + str({k: v for k, v in r.items() if k in ('codes', 'golden_codes', 'top_word', 'word', 'pivot')}))
        assert r["argmax_ok"] and r["max_abs_err"] <= tol, r
        if "codes" in r:      # keys are 8-bit codes in the Verilog model -> +-1 LSB vs the float golden
            assert max(abs(a - b) for a, b in zip(r["codes"], r["golden_codes"])) <= 1, r
    _t.__name__ = _t.__qualname__ = "it_" + fn.__name__
    return _t


for _f in EXAMPLES:
    globals()["it_" + _f.__name__] = cocotb.test(_make_test(_f, 0.02))


@cocotb.test()
async def it_ss_sgd_on_mismatched_die(dut):
    """Row-gain mismatch injected in the analog model; the firmware's CAL passes must cut the code error."""
    await reset(dut)
    ana = dut.user_project.u_ana
    ana.gam_ppm1.value, ana.gam_ppm2.value, ana.gam_ppm3.value = 30000, -25000, 20000
    be = RtlBackend(dut)
    await bridge(be.setup)()
    await bridge(be._ok)("W 0a 04")          # 4-clock pulses
    hist = await bridge(calibrate)(be, 4)
    dut._log.info("SS-SGD median code MAE per epoch: " + " ".join(f"{v:.2f}" for v in hist))
    assert hist[-1] < 0.5 * hist[0], hist
