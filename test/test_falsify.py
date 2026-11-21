# SPDX-License-Identifier: Apache-2.0
"""PSY-TaLiRo falsification on the RTL (controller + behavioural analog macro), in Icarus or Verilator under cocotb.

  PSY-TaLiRo optimiser (blocking) ----cocotb.task.bridge----> runs in a thread
  one sample = one pass on the DUT  ----cocotb.task.resume----> SPI writes, START, BUSY sampled every 1 us, 4 reads

Each sample sets q (4 x 4 bit), per-key scale ks (4 x 4 bit), keys k_j (8 bit, one value per key row) and, in the
window-search test, the settle window WIN (cycles) and bias wake-up WAKE. The trace (time in us from START, 1 us grid,
0..HORIZON) carries:
  busy     BUSY pin (uio_out[2])
  err      max_j |code_j - golden_j| in LSB once the pass is done (VALID), 0 before: outputs are only defined
           after VALID, so the requirement is 'VALID -> phi', written by masking
  sum_dev  |sum_j code_j - 255| once done, 0 before
Requirements (RTAMT discrete-time STL, evaluated through staliro.specifications.rtamt):
  D1  always (err <= 1.0)            every code within 1 LSB of the golden softmax code
  D2  always (sum_dev <= 3.0)        codes sum to 255 +- 3
  D3  eventually[0:90] (busy <= 0.5) the pass finishes within 90 us of START
Environment: FALSIFY_BUDGET (samples per test, default 24), FALSIFY_SEED (default 1, must be > 0)."""
import json
import os
import sys

import cocotb
from cocotb.task import bridge, resume
from cocotb.triggers import ClockCycles

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_rt5w import codes, load_keys, load_qk, rd, reset, scores, wr   # noqa: E402

HORIZON_US = 100
REQ = {"D1": ("always (err <= 1.0)", 1.0), "D2": ("always (sum_dev <= 3.0)", 1.0),
       "D3": ("eventually[0:90] (busy <= 0.5)", 0.5)}
BUDGET = int(os.environ.get("FALSIFY_BUDGET", "24"))
SEED = int(os.environ.get("FALSIFY_SEED", "1"))
SIM = os.environ.get("SIM", "icarus")


def _rho(times, states):
    from staliro import Trace
    from staliro.specifications import rtamt as st_rtamt
    tr = Trace(times=times, states=states)
    return {k: float(st_rtamt.parse_discrete(f).evaluate(tr).value) for k, (f, _) in REQ.items()}


async def one_pass(dut, q, ks, kv, win, wake):
    k = [[kv[j]] * 4 for j in range(4)]
    load_keys(dut, k)
    await load_qk(dut, q, ks)
    await wr(dut, 0x05, win & 0xFF); await wr(dut, 0x06, win >> 8); await wr(dut, 0x07, wake)
    await wr(dut, 0x00, 0x02 | 0x04)                       # GATE | START
    busy, t_done = [], None
    for i in range(HORIZON_US + 1):
        b = (dut.uio_out.value.to_unsigned() >> 2) & 1
        busy.append(float(b))
        if not b and t_done is None:
            t_done = i
        await ClockCycles(dut.clk, 20)                      # 1 us at 20 MHz
    got = [await rd(dut, 0x10 + j) for j in range(4)] if t_done is not None else [0, 0, 0, 0]
    exp = codes(scores(q, k, ks))
    err = max(abs(a - b) for a, b in zip(got, exp))
    sdev = abs(sum(got) - 255)
    times = [float(i) for i in range(HORIZON_US + 1)]
    states = [{"busy": busy[i],
               "err": float(err) if (t_done is not None and i >= t_done) else 0.0,
               "sum_dev": float(sdev) if (t_done is not None and i >= t_done) else 0.0} for i in range(len(times))]
    return dict(q=q, ks=ks, k=kv, win=win, wake=wake, codes=got, golden=exp, t_done_us=t_done,
                rho=_rho(times, states))


def _campaign(dut, search_timing):
    """Blocking: runs in a bridge thread; each sample resumes one_pass on the simulator."""
    import staliro
    from staliro import optimizers
    static = {f"q{j}": (0.0, 15.0) for j in range(4)}
    static.update({f"ks{j}": (1.0, 15.0) for j in range(4)})
    static.update({f"k{j}": (0.0, 255.0) for j in range(4)})
    if search_timing:
        static["win"] = (20.0, 1000.0)
        static["wake"] = (1.0, 30.0)
    samples = []

    @staliro.costfunc
    def cost(inputs):
        s = inputs.static
        q = [int(round(s[f"q{j}"])) for j in range(4)]
        ks = [int(round(s[f"ks{j}"])) for j in range(4)]
        kv = [int(round(s[f"k{j}"])) for j in range(4)]
        win = int(round(s["win"])) if search_timing else 1000
        wake = int(round(s["wake"])) if search_timing else 30
        r = resume(one_pass)(dut, q, ks, kv, win, wake)
        r["cost"] = min(r["rho"][k] / REQ[k][1] for k in REQ)
        samples.append(r)
        return staliro.Result(r["cost"], None)

    staliro.test(cost, optimizers.UniformRandom(), staliro.TestOptions(runs=1, iterations=BUDGET,
                                                                       static_inputs=static, seed=SEED))
    return samples


def _report(dut, name, samples):
    rho_min = {k: min(s["rho"][k] for s in samples) for k in REQ}
    bad = {k: min(samples, key=lambda s: s["rho"][k]) for k in REQ if rho_min[k] < 0}
    dut._log.info(f"{name}: {len(samples)} passes; rho_min " + str({k: round(v, 3) for k, v in rho_min.items()}))
    for k, s in bad.items():
        dut._log.info(f"  {k} FALSIFIED by q={s['q']} ks={s['ks']} k={s['k']} win={s['win']} wake={s['wake']}: "
                      f"codes {s['codes']} golden {s['golden']}")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"results_falsify_{SIM}.json")
    try:
        allr = json.load(open(path))
    except (OSError, ValueError):
        allr = {}
    allr[name] = dict(n=len(samples), rho_min=rho_min, falsified=sorted(bad), samples=samples)
    json.dump(allr, open(path, "w"), indent=1)
    return rho_min, bad


@cocotb.test()
async def fz_default_timing(dut):
    """Default window (1000 cycles) and wake (30): search q, ks, k. Every requirement is expected to hold."""
    await reset(dut)
    samples = await bridge(_campaign)(dut, False)
    rho_min, bad = _report(dut, "default_timing", samples)
    assert len(samples) == BUDGET
    assert not bad, f"falsified at the default timing: {sorted(bad)} (see results_falsify_{SIM}.json)"


@cocotb.test()
async def fz_window_search(dut):
    """Window and wake searched too: falsification must find the known short-window failure (cf. t06), and every
    counterexample must use a window shorter than the default."""
    await reset(dut)
    samples = await bridge(_campaign)(dut, True)
    rho_min, bad = _report(dut, "window_search", samples)
    fails = [s for s in samples if min(s["rho"].values()) < 0]
    passes = [s for s in samples if min(s["rho"].values()) >= 0]
    if fails:
        dut._log.info(f"  failing windows (cycles): {sorted(s['win'] for s in fails)}; "
                      f"shortest passing window: {min((s['win'] for s in passes), default=None)}")
    assert fails, "no counterexample found: falsifier did not reproduce the short-window failure"
    assert all(s["win"] < 1000 for s in fails), "a counterexample at the default window"
