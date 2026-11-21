# SPDX-License-Identifier: Apache-2.0
"""Instrumented RTL + SPICE co-simulation of the Illustrated-Transformer examples (E1-E7) through the HIL firmware.

Records, for every chip pass: the example, the encoding (q codes, keys, expected scores, golden codes), the protocol
lines, every SPI transaction, every key-cell write, the pass FSM timeline, the bias, every SAR trial (channel, DAC,
comparator), the V_B samples, and each SPICE transient (state, solve time, shares and V_B every 0.5 us).
Output: test/cosim_trace.json (see examples/cosim_report.py).

  make cosim-trace                          # Icarus + PySpice, WAKE 255, bias off 1e-6 (as make cosim)
  make cosim-trace SIM=verilator COSIM_ENGINE=ngspice
"""
import json
import os
import sys

import cocotb
import numpy as np
from cocotb.task import bridge
from cocotb.triggers import FallingEdge
from cocotb.utils import get_sim_time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cosim_driver import AnalogCosimDriver                     # noqa: E402
from test_cosim import CosimBackend, CosimHW, WAKE, _setup     # noqa: E402
from rt5w import cosim as C                                    # noqa: E402
from rt5w.illustrated import EXAMPLES, e1_thinking_machines    # noqa: E402

ST_NAMES = {0: "IDLE", 1: "WAKE", 2: "SETTLE", 3: "CONV", 4: "UPD", 5: "DONE"}
REGS = {0x00: "CTRL", 0x01: "Q01", 0x02: "Q23", 0x03: "K01", 0x04: "K23", 0x05: "WIN_L", 0x06: "WIN_H", 0x07: "WAKE",
        0x08: "ADCT", 0x09: "WSEL", 0x0A: "PULSE", 0x0B: "OUT_SEL", 0x0C: "TGT0", 0x0D: "TGT1", 0x0E: "TGT2",
        0x0F: "TGT3", 0x10: "RES0", 0x11: "RES1", 0x12: "RES2", 0x13: "RES3", 0x14: "STATUS", 0x15: "NPASS",
        0x16: "LASTUPD", 0x7F: "ID"}


def now_us():
    return get_sim_time("ns") * 1e-3


def _clean(v):
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, np.ndarray):
        return [_clean(x) for x in v.tolist()]
    if isinstance(v, (list, tuple)):
        return [_clean(x) for x in v]
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    return v


class Recorder:
    def __init__(self):
        self.example = "setup"
        self.passes = []
        self.cur = None
        self.loose = []          # transactions outside a backend pass (setup, VBCAL, WAKE)

    def sink(self):
        return self.cur if self.cur is not None else None

    def log(self, kind, item):
        tgt = self.cur if self.cur is not None else None
        if tgt is None:
            self.loose.append(dict(example=self.example, kind=kind, **item))
        else:
            tgt.setdefault(kind, []).append(item)


REC = Recorder()


class TraceHW(CosimHW):
    def xfer16(self, w):
        rd = super().xfer16(w)
        wr = bool(w & 0x8000)
        addr = (w >> 8) & 0x7F
        REC.log("spi", dict(t_us=round(now_us(), 3), op="W" if wr else "R", reg=REGS.get(addr, hex(addr)),
                            data=(w & 0xFF) if wr else rd))
        return rd

    def vw_set(self, v):
        super().vw_set(v)
        if int(self.ana.wsel_en.value):
            cell = int(self.ana.wsel_i.value)
            if cell < 16:
                code = (self.ana.kflat.value.to_unsigned() >> (8 * cell)) & 0xFF
                REC.log("keys", dict(t_us=round(now_us(), 3), cell=cell, volts=round(v, 5), code=code))

    def vb_read(self):
        v = super().vb_read()
        REC.log("vb", dict(t_us=round(now_us(), 3), volts=None if v is None else round(v, 6)))
        return v


class TraceBackend(CosimBackend):
    def __init__(self, dut, drv):
        import rt5w_fw
        self.proto = rt5w_fw.Protocol(rt5w_fw.Rt5wFirmware(TraceHW(dut, drv)))

    def _cmd(self, line):
        r = super()._cmd(line)
        REC.log("proto", dict(t_us=round(now_us(), 3), line=line if len(line) < 60 else line[:57] + "...", reply=r))
        return r

    def run(self, enc):
        REC.cur = dict(example=REC.example, index=len(REC.passes), t0_us=round(now_us(), 3),
                       q_codes=_clean(enc.q_codes), k=_clean(np.round(np.asarray(enc.k), 6)), n=int(enc.n_real), alpha=float(enc.alpha), beta=float(enc.beta), b=float(enc.b),
                       x_expected=_clean(np.round(np.asarray(enc.x_expected), 4)), golden_codes=_clean(enc.golden_codes()))
        codes, lse = super().run(enc)
        REC.cur.update(codes=codes, lse=round(lse, 5), t1_us=round(now_us(), 3))
        REC.passes.append(REC.cur)
        REC.cur = None
        return codes, lse


async def monitor_fsm(dut):
    ctrl, ana = dut.user_project.u_dig.u_ctrl, dut.user_project.u_ana
    last = None
    while True:
        await ctrl.st.value_change
        s = int(ctrl.st.value)
        if s != last:
            REC.log("fsm", dict(t_us=round(now_us(), 3), state=ST_NAMES.get(s, str(s)), bias=int(ana.bias_en.value)))
            last = s


async def monitor_sar(dut):
    ana = dut.user_project.u_ana
    prev = None
    while True:
        await FallingEdge(dut.clk)
        if not int(ana.adc_en.value):
            if prev is not None:
                REC.log("sar", prev)
                prev = None
            continue
        cur = dict(t_us=round(now_us(), 3), ch=int(ana.adc_sel.value), dac=int(ana.adc_dac.value),
                   cmp=int(ana.adc_cmp.value), share_mlsb=int(getattr(ana, f"sh_mlsb{int(ana.adc_sel.value)}").value))
        if prev is not None and (cur["ch"], cur["dac"]) != (prev["ch"], prev["dac"]):
            REC.log("sar", prev)                 # the last sample of a trial is the decision the SAR latched
        prev = cur


def instrument_spice(cs):
    orig = cs._solve

    def _solve():
        old, new, from_off, t_ev = cs.pending
        n0, s0 = cs.n_sim, cs.sim_seconds
        orig()
        tr = cs.traj
        grid = np.arange(0.0, C.T_HORIZON + 1e-9, 0.5e-6)
        sh = np.array([tr.at(t)[0] for t in grid])
        vb = np.array([tr.at(t)[1] for t in grid])
        REC.log("spice", dict(t_event_us=round(t_ev * 1e6, 3), from_off=from_off, cached=cs.n_sim == n0,
                              solve_s=round(cs.sim_seconds - s0, 2),
                              state=dict(q=new["q"], ks=new["ks"], k=new["k"], trim_mv=[round(v, 3) for v in new["trim_mv"]]),
                              t_us=_clean(np.round(grid * 1e6, 2)), shares=_clean(np.round(sh, 5)),
                              vb=_clean(np.round(vb, 5))))
    cs._solve = _solve


@cocotb.test()
async def trace_illustrated(dut):
    drv = await _setup(dut)
    instrument_spice(drv.cs)
    cocotb.start_soon(monitor_fsm(dut))
    cocotb.start_soon(monitor_sar(dut))
    be = TraceBackend(dut, drv)
    REC.example = "setup"
    await bridge(be.setup)()
    await bridge(be._ok)(f"WAKE {WAKE}")
    REC.example = "VBCAL"
    vb = await bridge(be._ok)("VBCAL")
    results = []
    for fn in EXAMPLES:
        REC.example = fn.__name__
        r = await bridge(fn)(be)
        results.append(_clean(r))
        dut._log.info(f"{r['example']}: max|err| {r['max_abs_err']} argmax_ok {r['argmax_ok']}")
    REC.example = "e1_at_wake30"
    await bridge(be._ok)("WAKE 30")
    r30 = _clean(await bridge(e1_thinking_machines)(be))
    meta = dict(sim=os.environ.get("SIM", "icarus"), engine=drv.cs.engine, corner=drv.cs.corner, temp=drv.cs.temp,
                bias_off=drv.cs.off, wake=WAKE, transients=drv.cs.n_sim, spice_seconds=round(drv.cs.sim_seconds, 1),
                sim_time_ms=round(now_us() / 1000, 3), vbcal=vb)
    out = dict(meta=meta, results=results, e1_at_wake30=r30, passes=REC.passes, loose=REC.loose)
    json.dump(out, open(os.path.join(HERE, "cosim_trace.json"), "w"))
    dut._log.info(f"trace: {len(REC.passes)} passes, {drv.cs.n_sim} transients, {drv.cs.sim_seconds:.0f} s in SPICE")
    for r in results:
        assert r["argmax_ok"] and r["max_abs_err"] <= 0.03, r
