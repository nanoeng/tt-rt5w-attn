"""SPICE side of the RTL + analog co-simulation (cocotb drives the RTL; this module solves the analog macro).

The analog macro's array + softmax core is simulated at transistor level (gf180mcuD) as a transient, with the same
netlist as the ngspice/PySpice backends (rt5w/backends/spice.py: 4-bit thermometer column IDACs -> PMOS diode/cell
array -> rt5w_softmax from analog/rt5w_core.spice). One transient per *analog event*: the bias turning on (the pass
FSM's WAKE state) or an input change while biased. Engines: PySpice (libngspice, in-process) or the ngspice CLI.

IDEAL here, as in the backend netlist, and stated on the deck: V_R, V_cas, the bias and IDAC unit feeds, key storage
(series gate offset in place of the floating C_W, open item O1), and the readout (share = I_j / sum I; the SAR
current DAC + comparator are not drawn yet, so the comparator decision 255*share + 0.5 > dac is ideal).
Not in rt5w_core.spice and therefore modelled as extra series gate offsets on row j's cells (same mechanism as keys):
the per-key scale IDAC k_code (factor ks_j/15), the row trim V_w,j from the charge pump (factor exp(V_w,j/nU_T,p)),
and the backdoor row-gain mismatch gamma_j (factor 1+gamma_j). The pump step itself stays behavioural (Verilog,
characterised in sim/results/weight_cell.json).
"""
import math
import os
import re
import subprocess
import tempfile

import numpy as np

from .backends.spice import CORE, CORNER_LIB, IQ_LSB, MODELS, NUT_P, shared_ngspice

T_ON = 0.1e-6          # event time inside each transient
T_HORIZON = 130e-6     # record length after the event: max WAKE (1021 clk = 51 us) + window 50 us + SAR 13 us + margin
T_STEP = 20e-9
OFF = 1e-6             # bias feeds while gated off, as a fraction of nominal. The gating switch is not drawn yet;
                       # start-up time depends strongly on this (sim: 45 us at 0.1, 90 us at 1e-6), so it is a parameter


def cell_offsets(state):
    """Series gate offset (V) per cell [row][col] from keys, per-key scale, trim and row mismatch."""
    T = state["temp"]
    ptat = (T + 273.15) / 300.15
    vw = np.zeros((4, 4))
    for r in range(4):
        g = (state["ks"][r] / 15.0) * math.exp(state["trim_mv"][r] * 1e-3 / (NUT_P * ptat)) * (1.0 + state["gamma"][r])
        for c in range(4):
            k = state["k"][r][c] / 255.0 * g
            vw[r, c] = 1.0 if k < 1e-6 else -NUT_P * ptat * math.log(k)
    return vw


def _src(name, a, b, v0, v1, t_on):
    if abs(v1 - v0) < 1e-15:
        return f"{name} {a} {b} {v1:.6e}"
    return f"{name} {a} {b} PWL(0 {v0:.6e} {t_on:.4e} {v0:.6e} {t_on + 5e-9:.4e} {v1:.6e})"


def netlist(new, old, bias_from_off, corner="tt", off=None):
    """Transient: inputs `old` (bias off if bias_from_off) -> `new` at T_ON. States are dicts (see Cosim.state)."""
    T = new["temp"]
    ptat = (T + 273.15) / 300.15
    f0 = (OFF if off is None else off) if bias_from_off else 1.0
    vw_new, vw_old = cell_offsets(new), cell_offsets(old)
    L = ["* rt5w array + softmax, co-simulation event", f".include {MODELS}/design.ngspice",
         f".lib {MODELS}/sm141064.ngspice {CORNER_LIB[corner]}", f".include {CORE}", f".temp {T}",
         ".subckt cell_ideal vdd dcol row fg", "Mc row fg vdd vdd pmos_3p3 w=20u l=4u m=8", ".ends",
         "Vdd vdd 0 3.3", "Vr vr 0 1.65", "Vcas vcas 0 1.05",
         _src("Ib", "vdd", "nbias", 125e-9 * ptat * f0, 125e-9 * ptat, T_ON),
         _src("Ik", "vdd", "kbias", 5e-9 * ptat * f0, 5e-9 * ptat, T_ON)]
    for c in range(4):
        L.append(_src(f"Ilsb{c}", "vdd", f"nd{c}", IQ_LSB * ptat * f0, IQ_LSB * ptat, T_ON))
        th = []
        for u in range(15):
            a, b = (3.3 if u < old["q"][c] else 0.0), (3.3 if u < new["q"][c] else 0.0)
            L.append(_src(f"Vt{c}_{u}", f"t{c}_{u}", "0", a, b, T_ON))
            th.append(f"t{c}_{u}")
        L += [f"Xi{c} dcol{c} nd{c} 0 {' '.join(th)} rt5w_idac4", f"Xd{c} vdd dcol{c} rt5w_coldiode"]
        for r in range(4):
            L.append(_src(f"Vw{r}{c}", f"fg{r}{c}", f"dcol{c}", vw_old[r, c], vw_new[r, c], T_ON))
            L.append(f"Xc{r}{c} vdd dcol{c} g{r} fg{r}{c} cell_ideal")
    L += ["Xsm vdd 0 g0 g1 g2 g3 vb o0 o1 o2 o3 nbias kbias vr vcas rt5w_softmax"]
    L += [f"Vo{j} o{j} 0 2.78" for j in range(4)]
    L += [".options method=gear maxord=2"]       # trapezoidal rings on alternate samples (known pitfall)
    return "\n".join(L)


def simulate(new, old, bias_from_off, corner="tt", engine="pyspice", off=None):
    """Return t (s, from the event), shares (n x 4), V_B (n)."""
    nl = netlist(new, old, bias_from_off, corner, off)
    tstop = T_ON + T_HORIZON
    if engine == "pyspice":
        from .falsify import _Mute
        ng = shared_ngspice()
        with _Mute():
            ng.destroy()
            ng.load_circuit(nl + "\n.end\n")
            ng._ngspice_shared.ngSpice_Command(f"tran {T_STEP:.3e} {tstop:.4e}".encode())
        p = ng.plot(None, ng.last_plot)
        g = lambda n: np.real(np.asarray(p[n]._data, dtype=complex))   # noqa: E731
        t, I, vb = g("time"), np.stack([g(f"vo{j}#branch") for j in range(4)], 1), g("vb")
    elif engine == "ngspice":
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "o.dat")
            body = nl + f"\n.control\nset filetype=ascii\ntran {T_STEP:.3e} {tstop:.4e}\n" \
                        f"wrdata {out} i(vo0) i(vo1) i(vo2) i(vo3) v(vb)\n.endc\n.end\n"
            path = os.path.join(td, "n.sp")
            open(path, "w").write(body)
            r = subprocess.run(["ngspice", "-b", path], capture_output=True, text=True, timeout=900)
            if not os.path.exists(out):
                raise RuntimeError("ngspice: no data\n" + (r.stdout + r.stderr)[-2000:])
            d = np.loadtxt(out)
        t, I, vb = d[:, 0], np.stack([d[:, 1 + 2 * j] for j in range(4)], 1), d[:, 9]
    else:
        raise ValueError(engine)
    k = t >= T_ON - 1e-12
    t, I, vb = t[k] - T_ON, I[k], vb[k]
    s = I.sum(1)
    shares = np.where(s[:, None] > 0, I / np.where(s > 0, s, 1)[:, None], 0.25)
    return t, shares, vb


def operating_point(state, corner="tt"):
    """DC reference for a state (bias on, settled): shares and V_B from an ngspice .op of the same netlist."""
    nl = netlist(state, state, False, corner)
    body = nl + "\n.control\nop\nprint i(vo0) i(vo1) i(vo2) i(vo3) v(vb)\n.endc\n.end\n"
    with tempfile.NamedTemporaryFile("w", suffix=".sp", delete=False) as f:
        f.write(body)
    r = subprocess.run(["ngspice", "-b", f.name], capture_output=True, text=True, timeout=300)
    os.unlink(f.name)
    v = {m.group(1).lower(): float(m.group(2)) for m in re.finditer(r"^\s*([\w\(\)#\.]+)\s*=\s*([-+0-9.eE]+)", r.stdout, re.M)}
    I = np.array([v[f"i(vo{j})"] for j in range(4)])
    return list(I / I.sum()), v["v(vb)"]


class Trajectory:
    """Shares and V_B after one analog event, as functions of time since the event (held after the horizon)."""

    def __init__(self, t, shares, vb):
        self.t, self.shares, self.vb = t, shares, vb

    def at(self, dt):
        dt = min(max(dt, 0.0), self.t[-1])
        return [float(np.interp(dt, self.t, self.shares[:, j])) for j in range(4)], float(np.interp(dt, self.t, self.vb))


class Cosim:
    """Event-driven analog solver. The cocotb side calls update(state, bias_en, now_s) on every input change and
    sample(now_s) when it needs the shares; transients are cached by (old, new, bias_from_off)."""

    def __init__(self, corner="tt", temp=27.0, engine="pyspice", off=None):
        self.corner, self.temp, self.engine, self.off = corner, temp, engine, (OFF if off is None else off)
        self.cache, self.n_sim, self.sim_seconds = {}, 0, 0.0
        self.settled = None          # state the circuit was last left settled in (None: never biased)
        self.traj, self.t_event = None, 0.0
        self.pending = None          # (old, new, from_off, t_event) awaiting simulation

    def blank_state(self):
        return dict(q=[0] * 4, ks=[0] * 4, k=[[0] * 4 for _ in range(4)], trim_mv=[0.0] * 4, gamma=[0.0] * 4,
                    temp=self.temp)

    @staticmethod
    def _key(st):
        return (tuple(st["q"]), tuple(st["ks"]), tuple(tuple(r) for r in st["k"]),
                tuple(round(v, 4) for v in st["trim_mv"]), tuple(round(v, 7) for v in st["gamma"]), st["temp"])

    def event(self, state, bias_en, now_s, was_biased):
        """Record an analog event: bias turned on, or inputs changed while biased."""
        if not bias_en:
            self.traj, self.pending = None, None
            return
        from_off = not was_biased
        old = state if from_off else (self.pending[1] if self.pending else (self.settled or state))
        self.pending = (dict(old), dict(state), from_off, now_s)

    def _solve(self):
        old, new, from_off, t_ev = self.pending
        key = (self._key(old), self._key(new), from_off)
        if key not in self.cache:
            import time
            t0 = time.time()
            self.cache[key] = Trajectory(*simulate(new, old, from_off, self.corner, self.engine, self.off))
            self.n_sim += 1
            self.sim_seconds += time.time() - t0
        self.traj, self.t_event, self.settled, self.pending = self.cache[key], t_ev, new, None

    def sample(self, now_s):
        """Shares and V_B now; None if the macro is unbiased."""
        if self.pending:
            self._solve()
        if self.traj is None:
            return None
        return self.traj.at(now_s - self.t_event)
