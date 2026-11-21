"""STL falsification of the RT5W softmax core with PSY-TaLiRo (psy-taliro 3.2, imports as `staliro`) and RTAMT.

System under test: the transistor-level softmax core (sim/rt5w_ng.softmax_netlist, gf180mcuD, Gear integration),
simulated as a step transient x_a -> x_b at T_STEP, by ngspice (CLI) or PySpice (libngspice, shared library).
One PSY-TaLiRo sample = one transient. Search space: x_a, x_b in [0, 18]^4 (scores in e-folds) and T in [-40, 125] C,
one process corner per campaign. Signals are resampled on a uniform DT grid (time unit: us) and every requirement is
evaluated by RTAMT (discrete-time STL) through staliro.specifications.rtamt.

Requirements: the nine STL requirements of the rev-2 campaign (R1-R7 at readout, R1t/R2t during the step), with the
limits of record. T0 = T_STEP + the FSM settle window (1000 cycles at 20 MHz = 50 us in this tree), Tend = end of record.
Cost = min_i rho_i / s_i (each robustness over its own scale); negative = counterexample. Limits are never relaxed here.

Definitions (all in fractions of the measured tail current I_tail, which the host's renormalisation tracks):
  a_j       = I_out,j / I_tail                    share of token j
  sum_err   = |sum_j I_out,j / I_tail - 1|        output KCL (outputs give back the keep-alive, so sum = tail)
  min_share = min_j a_j
  gold_err  = max_j |a_j - softmax(x_b)_j|
  drift     = max_j |a_j(t) - a_j(t_end)|          settled to within 1 LSB (1/255 ~ 0.004) of the final value
  margin    = a_win - max_{j != win} a_j  if the golden top-1 leads by >= MARGIN_GAP, else +1 (vacuous)
  agc_err   = |I_tail / (I_sum * T/300.15) - 1|   AGC against the PTAT reference
  vb        = V_B (log-sum-exp node)
MARGIN_GAP (what counts as a 'clear winner') is not recorded with the original requirement; 0.05 is used here and is a
parameter.
"""
import math
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(ROOT, "sim"))
import rt5w_ng  # noqa: E402  (sim/ is a script folder, not a package)

T_STEP_US = 1.0          # step time
WINDOW_US = 50.0         # FSM settle window (1000 cycles at 20 MHz, rt5w_ctrl default)
T_END_US = 60.0          # end of record
DT_US = 0.05             # resampling grid for RTAMT (discrete time needs uniform samples)
X_MAX = 18.0
MARGIN_GAP = 0.05
LSB = 1.0 / 255

T0 = T_STEP_US + WINDOW_US
REQUIREMENTS = {   # name: (RTAMT formula, scale s_i, plain wording)
    "R1":  (f"always[{T0}:{T_END_US}] (sum_err <= 0.001)", 0.001, "outputs sum to I_tail within 0.1 % at readout"),
    "R1t": ("always (sum_err <= 0.1)", 0.1, "during a step, sum within 10 %"),
    "R2":  (f"always[{T0}:{T_END_US}] (min_share >= -0.0004)", LSB, "no share below -0.1 LSB at readout"),
    "R2t": ("always (min_share >= -0.004)", LSB, "during a step, no share below -1 LSB"),
    "R3":  (f"always[{T0}:{T_END_US}] (gold_err <= 0.03)", 0.03, "every share within 3 % of softmax"),
    "R4":  (f"always[{T0}:{T_END_US}] (drift <= 0.004)", LSB, "within 1 LSB of the final value"),
    "R5":  (f"always[{T0}:{T_END_US}] (margin >= 0.0)", LSB, "a clear winner stays the winner"),
    "R6":  (f"always[{T0}:{T_END_US}] (agc_err <= 0.02)", 0.02, "AGC holds the tail within 2 % of the PTAT reference"),
    "R7":  ("always ((vb >= 0.05) and (vb <= 1.3))", 0.05, "V_B inside the amplifier range"),
}
SIGNALS = ["sum_err", "min_share", "gold_err", "drift", "margin", "agc_err", "vb"]


# ----------------------------------------------------------------------------- system under test
def netlist(xa, xb, corner="tt", temp=27.0):
    """Softmax-core step transient, with a 0 V sense source on the tail so that I_tail is measured."""
    nl = rt5w_ng.softmax_netlist(list(xb), x_prev=list(xa), corner=corner, T=temp,
                                 tran=(20e-9, (T_END_US + 1) * 1e-6, T_STEP_US * 1e-6))
    old = "Mtail tc gt_t 0 0 "
    assert old in nl, "tail device line changed in sim/rt5w_ng.py"
    nl = nl.replace(old, "Mtail tc gt_t tsn 0 ") .replace(".control", "Vtsn tsn 0 0\n.control", 1)
    return nl


class _Mute:
    """libngspice writes gmin-stepping notes straight to fd 1/2 (not through PySpice's callbacks)."""
    def __enter__(self):
        sys.stdout.flush(); sys.stderr.flush()
        self._null = os.open(os.devnull, os.O_WRONLY)
        self._saved = [os.dup(1), os.dup(2)]
        os.dup2(self._null, 1); os.dup2(self._null, 2)

    def __exit__(self, *a):
        os.dup2(self._saved[0], 1); os.dup2(self._saved[1], 2)
        for f in self._saved + [self._null]:
            os.close(f)


def _pyspice():
    from .backends.spice import shared_ngspice
    return shared_ngspice()


def simulate(xa, xb, temp=27.0, corner="tt", engine="ngspice"):
    """Return t (s), I_out (n x 4), V_B, I_tail from one transient."""
    nl = netlist(xa, xb, corner, temp)
    if engine == "ngspice":
        nl = nl.replace("wrdata __OUT__ i(vo0) i(vo1) i(vo2) i(vo3) v(vb) i(vdd)",
                        "wrdata __OUT__ i(vo0) i(vo1) i(vo2) i(vo3) v(vb) i(vtsn)")
        txt, d = rt5w_ng.run(nl, timeout=600)
        if d is None:
            raise RuntimeError("ngspice produced no data:\n" + txt[-2000:])
        t = d[:, 0]
        cols = [d[:, 1 + 2 * k] for k in range(6)]          # wrdata writes (t, value) pairs
        return t, np.stack(cols[:4], 1), cols[4], cols[5]
    if engine == "pyspice":
        body, ctl = nl.split(".control", 1)
        opts = [ln for ln in ctl.splitlines() if ln.startswith("option")]
        tran = [ln for ln in ctl.splitlines() if ln.startswith("tran")][0]
        ng = _pyspice()
        with _Mute():
            ng.destroy()
            ng.load_circuit(body + "\n" + "\n".join("." + o for o in opts) + "\n.end\n")
            ng._ngspice_shared.ngSpice_Command(tran.encode())   # PySpice 1.5 misreads newer ngspice 'run' status
        p = ng.plot(None, ng.last_plot)
        g = lambda n: np.real(np.asarray(p[n]._data, dtype=complex))   # noqa: E731
        t = g("time")
        return t, np.stack([g(f"vo{j}#branch") for j in range(4)], 1), g("vb"), g("vtsn#branch")
    raise ValueError(engine)


def signals(t, I, vb, it, xb, temp):
    """Requirement signals on a uniform DT_US grid (time in us)."""
    tu = np.arange(0.0, T_END_US + DT_US / 2, DT_US)
    ts = t * 1e6
    I = np.stack([np.interp(tu, ts, I[:, j]) for j in range(4)], 1)
    vb = np.interp(tu, ts, vb)
    it = np.abs(np.interp(tu, ts, it))
    a = I / it[:, None]
    g = rt5w_ng.golden(xb)
    order = np.argsort(g)[::-1]
    win, second = order[0], order[1]
    if g[win] - g[second] >= MARGIN_GAP:
        margin = a[:, win] - np.max(np.delete(a, win, axis=1), axis=1)
    else:
        margin = np.ones_like(tu)
    iref = rt5w_ng.D["I_sum"] * (temp + 273.15) / 300.15
    return tu, dict(sum_err=np.abs(I.sum(1) / it - 1), min_share=a.min(1), gold_err=np.abs(a - g).max(1),
                    drift=np.abs(a - a[-1]).max(1), margin=margin, agc_err=np.abs(it / iref - 1), vb=vb)


def robustness(tu, sig, reqs=None):
    """rho_i for each requirement, evaluated by RTAMT (discrete-time STL) via staliro."""
    from staliro import Trace
    from staliro.specifications import rtamt as st_rtamt
    states = [{k: float(sig[k][i]) for k in SIGNALS} for i in range(len(tu))]
    trace = Trace(times=[float(x) for x in tu], states=states)
    out = {}
    for name in (reqs or REQUIREMENTS):
        formula = REQUIREMENTS[name][0]
        out[name] = float(st_rtamt.parse_discrete(formula).evaluate(trace).value)
    return out


def evaluate(xa, xb, temp=27.0, corner="tt", engine="ngspice", reqs=None):
    t, I, vb, it = simulate(xa, xb, temp, corner, engine)
    tu, sig = signals(t, I, vb, it, xb, temp)
    rho = robustness(tu, sig, reqs)
    norm = {k: v / REQUIREMENTS[k][1] for k, v in rho.items()}
    return dict(xa=[float(v) for v in xa], xb=[float(v) for v in xb], temp=float(temp), corner=corner,
                rho=rho, cost=min(norm.values()), worst=min(norm, key=norm.get),
                final_codes=[int(round(255 * v)) for v in (I[-1] / abs(it[-1]))],
                golden_codes=[int(round(255 * v)) for v in rt5w_ng.golden(xb)])


# ----------------------------------------------------------------------------- PSY-TaLiRo campaign
def campaign(corner="tt", engine="ngspice", budget=40, anneal=0, seed=1, reqs=None, temp_range=(-40.0, 125.0),
             log=print):
    """UniformRandom(budget) [+ DualAnnealing(anneal)] over x_a, x_b, T. Returns per-requirement minima and samples."""
    import staliro
    from staliro import optimizers
    names = list(reqs or REQUIREMENTS)
    static = {f"xa{j}": (0.0, X_MAX) for j in range(4)}
    static.update({f"xb{j}": (0.0, X_MAX) for j in range(4)})
    static["temp"] = tuple(temp_range)
    samples = []

    @staliro.costfunc
    def cost(inputs):
        s = inputs.static
        r = evaluate([s[f"xa{j}"] for j in range(4)], [s[f"xb{j}"] for j in range(4)], s["temp"],
                     corner, engine, names)
        samples.append(r)
        if len(samples) % 10 == 0:
            log(f"  {corner} {engine}: {len(samples)} transients, min cost so far "
                f"{min(x['cost'] for x in samples):+.3f}")
        return staliro.Result(r["cost"], r)

    t0 = time.time()
    phases = [("UniformRandom", optimizers.UniformRandom(), budget)]
    if anneal:
        phases.append(("DualAnnealing", optimizers.DualAnnealing(), anneal))
    for _, opt, n in phases:
        opts = staliro.TestOptions(runs=1, iterations=n, static_inputs=static, seed=seed)
        staliro.test(cost, opt, opts)
    rho_min = {k: min(s["rho"][k] for s in samples) for k in names}
    worst = {k: min(samples, key=lambda s: s["rho"][k]) for k in names}
    return dict(corner=corner, engine=engine, n=len(samples), seconds=round(time.time() - t0, 1),
                rho_min=rho_min, falsified=[k for k in names if rho_min[k] < 0],
                held=[k for k in names if rho_min[k] >= 0],
                counterexamples={k: dict(xa=worst[k]["xa"], xb=worst[k]["xb"], temp=worst[k]["temp"],
                                         rho=worst[k]["rho"][k]) for k in names if rho_min[k] < 0},
                samples=samples)
