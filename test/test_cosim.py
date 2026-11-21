# SPDX-License-Identifier: Apache-2.0
"""RTL + SPICE co-simulation tests: the real controller (Icarus / Verilator) with the analog macro solved at transistor
level in ngspice / PySpice through cocotb (test/cosim_driver.py, rt5w/cosim.py).

What each test checks
  cs01  'Thinking Machines' pass: SAR codes within 1 LSB of the settled SPICE operating point of the same inputs
        (closes the loop RTL -> SPICE -> comparator -> SAR), and the same winner as the ideal softmax. The distance to
        the ideal softmax is reported (uncalibrated array chain; R3's 3 % applies to the softmax core over PVT).
  cs02  random rows: the same checks.
  cs03  start-up timing: the same row at WAKE = 30 (reset default), 128 and 255; reports how far each is from the
        settled SPICE answer (the analog chain starts from a gated-off bias at every pass). Must reach 1 LSB at 255.
  cs04  firmware-in-the-loop: the unchanged HIL firmware runs VBCAL and the Illustrated-Transformer examples E1-E7
        on RTL + SPICE; same tolerance as the ngspice backend (0.03), argmax correct.
  cs05  (COSIM_FULL=1) SS-SGD calibration on a mismatched die.
Environment: COSIM_WAKE (default 255 for cs01/cs02/cs04), COSIM_N (random rows, default 3), see cosim_driver.py."""
import json
import os
import random
import sys

import cocotb
from cocotb.task import bridge

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cosim_driver import AnalogCosimDriver  # noqa: E402
from test_rt5w import codes, load_keys, load_qk, rd, reset, run_pass, scores, wr  # noqa: E402
from test_illustrated import CocotbHW, RtlBackend  # noqa: E402
from rt5w.cosim import operating_point  # noqa: E402
from rt5w.illustrated import EXAMPLES, calibrate  # noqa: E402

WAKE = int(os.environ.get("COSIM_WAKE", "255"))
N_RANDOM = int(os.environ.get("COSIM_N", "3"))
FULL = os.environ.get("COSIM_FULL", "0") == "1"
R3_LSB = 0.03 * 255
RESULTS = os.path.join(HERE, f"results_cosim_{os.environ.get('SIM', 'icarus')}.json")


def _save(name, obj):
    try:
        allr = json.load(open(RESULTS))
    except (OSError, ValueError):
        allr = {}
    allr[name] = obj
    json.dump(allr, open(RESULTS, "w"), indent=1)


async def _setup(dut, wake=WAKE):
    await reset(dut)
    drv = AnalogCosimDriver(dut).start()
    await wr(dut, 0x07, wake)
    return drv


async def _one_row(dut, drv, q, k, ks):
    load_keys(dut, k)
    await load_qk(dut, q, ks)
    st = drv.state()
    got = await run_pass(dut, timeout_us=400)
    sh, _ = operating_point(st, drv.cs.corner)
    op = [max(0, min(255, int(round(255 * v)))) for v in sh]
    gold = codes(scores(q, k, ks))
    return dict(q=q, ks=ks, k=k, codes=got, op=op, golden=gold,
                err_op=max(abs(a - b) for a, b in zip(got, op)), err_golden=max(abs(a - b) for a, b in zip(got, gold)))


TM = dict(q=[15] * 4, k=[[255] * 4, [227, 227, 226, 226], [0] * 4, [0] * 4], ks=[15] * 4)


@cocotb.test()
async def cs01_thinking_machines(dut):
    drv = await _setup(dut)
    r = await _one_row(dut, drv, **TM)
    dut._log.info(f"RTL+SPICE codes {r['codes']}  SPICE op {r['op']}  ideal softmax {r['golden']}  "
                  f"({drv.cs.n_sim} transients, {drv.cs.sim_seconds:.1f} s in SPICE)")
    _save("cs01", r)
    assert r["err_op"] <= 1, r
    assert _argmax(r["codes"]) == _argmax(r["golden"]), r


def _argmax(c):
    return max(range(4), key=lambda j: c[j])


@cocotb.test()
async def cs02_random_rows(dut):
    drv = await _setup(dut)
    rnd = random.Random(5)
    out = []
    for _ in range(N_RANDOM):
        q = [rnd.randrange(4, 16) for _ in range(4)]
        ks = [rnd.randrange(8, 16) for _ in range(4)]
        k = [[rnd.randrange(256) for _ in range(4)] for _ in range(4)]
        r = await _one_row(dut, drv, q, k, ks)
        dut._log.info(f"q={q} ks={ks}: RTL+SPICE {r['codes']}  op {r['op']}  ideal {r['golden']}")
        out.append(r)
    _save("cs02", out)
    dut._log.info(f"max distance to the ideal softmax: {max(r['err_golden'] for r in out)} LSB "
                  f"(R3-scale reference {R3_LSB:.2f} LSB, not gated: uncalibrated chain)")
    for r in out:
        assert r["err_op"] <= 1, r
        assert _argmax(r["codes"]) == _argmax(r["golden"]), r


@cocotb.test()
async def cs03_startup_timing(dut):
    drv = await _setup(dut, wake=30)
    res = []
    for wake in (30, 128, 255):
        await wr(dut, 0x07, wake)
        r = await _one_row(dut, drv, **TM)
        r["wake"] = wake
        r["readout_us"] = (4 * wake + 1 + 1000) / 20.0
        res.append(r)
        dut._log.info(f"WAKE {wake:3d} (readout {r['readout_us']:.1f} us after START): codes {r['codes']} "
                      f"vs settled {r['op']}  -> {r['err_op']} LSB")
    _save("cs03", dict(bias_off=drv.cs.off, corner=drv.cs.corner, temp=drv.cs.temp, runs=res))
    assert res[-1]["err_op"] <= 1, res[-1]


class CosimHW(CocotbHW):
    """Firmware board adapter with V_B from SPICE (the behavioural adapter computes it from Verilog reals)."""

    def __init__(self, dut, drv):
        super().__init__(dut)
        self.drv = drv

    async def _vb(self):
        return self.drv.vb_now()


class CosimBackend(RtlBackend):
    name = "rtl+spice"

    def __init__(self, dut, drv):
        import rt5w_fw
        self.proto = rt5w_fw.Protocol(rt5w_fw.Rt5wFirmware(CosimHW(dut, drv)))


@cocotb.test()
async def cs04_illustrated_firmware_in_the_loop(dut):
    drv = await _setup(dut)
    be = CosimBackend(dut, drv)
    await bridge(be.setup)()
    await bridge(be._ok)(f"WAKE {WAKE}")
    vb = await bridge(be._ok)("VBCAL")
    dut._log.info(f"VBCAL on SPICE: V_B0 {vb[0]} V, slope {vb[1]} V/e-fold")
    out = []
    for fn in EXAMPLES:
        r = await bridge(fn)(be)
        out.append({k: v for k, v in r.items() if isinstance(v, (int, float, str, list, bool))})
        dut._log.info(f"{r['example']}: max|err| {r['max_abs_err']:.4f} argmax_ok {r['argmax_ok']}"
                      + (f" codes {r['codes']} golden {r['golden_codes']}" if "codes" in r else ""))
    dut._log.info(f"{drv.cs.n_sim} SPICE transients, {drv.cs.sim_seconds:.0f} s in SPICE")
    _save("cs04", dict(vbcal=vb, examples=out, transients=drv.cs.n_sim))
    for r in out:
        assert r["argmax_ok"] and r["max_abs_err"] <= 0.03, r


@cocotb.test(skip=not FULL)
async def cs05_ss_sgd_on_mismatched_die(dut):
    drv = await _setup(dut)
    ana = dut.user_project.u_ana
    ana.gam_ppm1.value, ana.gam_ppm2.value, ana.gam_ppm3.value = 30000, -25000, 20000
    be = CosimBackend(dut, drv)
    await bridge(be.setup)()
    await bridge(be._ok)(f"WAKE {WAKE}")
    await bridge(be._ok)("W 0a 04")
    hist = await bridge(calibrate)(be, 4)
    dut._log.info("SS-SGD median code MAE per epoch (RTL+SPICE): " + " ".join(f"{v:.2f}" for v in hist))
    _save("cs05", dict(hist=hist))
    assert hist[-1] < hist[0], hist
