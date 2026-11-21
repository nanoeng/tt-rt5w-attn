"""SPICE side of the RTL + analog co-simulation on the sky130 macro (TTSKY26e). Task: sky130 co-simulation, 2026-11-21.

Same interface as rt5w/cosim.py (gf180 version of 19 Nov): netlist / simulate / operating_point / Cosim. Selected in
test/cosim_driver.py and test/test_cosim.py by COSIM_PDK=sky130 (default).

Transistor level (sky130 schematics, netlist/rt5w_analog.spice): rt5w_bias (with its real gating: bias_en is a
drawn input now, so the start-up after a gated-off interval is simulated, not parameterised) -> 4 x rt5w_idac4 and the
4x4 key array (rt5w_array) -> 4 x rt5w_kscale (per-key scale ks) -> rt5w_softmax; outputs held at V_O = 2.2 V
(the readout's cascode-source level, tb_softmax). Shares = I_out,j / sum I_out.

IDEAL here (stated on the deck): key storage -- the storage nodes h_ji and the row trim lines w_j are forced by
voltage sources with the firmware key mapping h = w - nU_T,p ln(k (1 + gamma_j)) + nU_T,p ln G0 (as tb_chain), and
w_j = W_REF + V_trim,j (the behavioural pump's trim voltage); the readout (the SAR DAC + comparator are verified
separately at transistor level by tb_chain in continuous mode; here the comparator is the ideal decision
255 * share + 0.5 > dac in test/rt5w_analog_cosim.v); the V_B probe buffer (V_B is the softmax node itself).
"""
import math
import os
import re
import sys
import tempfile
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "design"), os.path.join(ROOT, "design", "tb"), os.path.join(ROOT, "design", "blocks")):
    if p not in sys.path:
        sys.path.insert(0, p)

import sim      # noqa: E402
import tech     # noqa: E402

T_ON = 0.1e-6
# A from-off event starts from the converged bias-ON operating point: bias_en drops at 1 us, stays off for OFF_US
# (the gated interval between passes), then rises with the new inputs. An operating point computed with bias_en = 0
# does not converge to a physical state (taps at -0.3..-0.9 V, 2 mA from vdd), so it is never used.
OFF_US = float(os.environ.get("COSIM_OFF_US", "100"))
T_HORIZON = 130e-6
T_STEP = 20e-9
V_O = 2.2
OPTIONS = "rshunt=1e12 itl1=1000"
OFF = None      # interface compatibility with rt5w/cosim.py (the sky130 bias gating is drawn)


def _src(name, a, b, v0, v1, t_on):
    if abs(v1 - v0) < 1e-12:
        return f"{name} {a} {b} {v1:.6e}"
    return f"{name} {a} {b} PWL(0 {v0:.6e} {t_on:.4e} {v0:.6e} {t_on + 5e-9:.4e} {v1:.6e})"


def _storage(state, corner):
    """h[j][i], w[j] (V) for a state, firmware key mapping (tb_chain)."""
    T = state["temp"]
    t = tech.measure(corner, T)
    nu = t.get("nUT_p_cell", t["nUT_p"])
    g0 = t["cell_gain0"]
    w_ref = t["dcol"]
    w = [w_ref + state["trim_mv"][j] * 1e-3 for j in range(4)]
    h = [[3.3] * 4 for _ in range(4)]
    for j in range(4):
        for i in range(4):
            k = state["k"][j][i] / 255.0 * (1.0 + state["gamma"][j])
            if k > 1e-6:
                h[j][i] = w_ref - nu * math.log(k) + nu * math.log(g0)
    return h, w


def t_event(bias_from_off):
    return (OFF_US + 1.0) * 1e-6 if bias_from_off else T_ON


def body(new, old, bias_from_off, corner="tt"):
    T = new["temp"]
    te = t_event(bias_from_off)
    h1, w1 = _storage(new, corner)
    h0, w0 = _storage(old, corner)
    L = ["Vdd vdd 0 3.3", "Vss vss 0 0", (f"Ven bias_en 0 PWL(0 3.3 1e-6 3.3 1.005e-6 0 {te:.4e} 0 {te + 5e-9:.4e} 3.3)" if bias_from_off
          else "Ven bias_en 0 3.3"),
         "Vua0 ua0 0 1.0", "Vndac ndac 0 0.6", "Vua2 ua2 0 2.0"]
    L += [f"Vws{n} wsel{n} 0 0" for n in range(20)]
    L += [f"Vpu{j} pump_up{j} 0 0" for j in (1, 2, 3)] + [f"Vpd{j} pump_dn{j} 0 0" for j in (1, 2, 3)]
    for i in range(4):
        for b in range(4):
            L.append(_src(f"Vq{i}_{b}", f"q{i}_{b}", "0", 3.3 * ((old["q"][i] >> b) & 1), 3.3 * ((new["q"][i] >> b) & 1), te))
            L.append(_src(f"Vk{i}_{b}", f"k{i}_{b}", "0", 3.3 * ((old["ks"][i] >> b) & 1), 3.3 * ((new["ks"][i] >> b) & 1), te))
    L.append("xbias bias_en nbias kbias nd0 nd1 nd2 nd3 ndac vbn pg ng vcas vr vmid ua0 vdd vss rt5w_bias")
    L.append("xarr q0_0 q0_1 q0_2 q0_3 q1_0 q1_1 q1_2 q1_3 q2_0 q2_1 q2_2 q2_3 q3_0 q3_1 q3_2 q3_3 nd0 nd1 nd2 nd3 vbn ua2 "
             + " ".join(f"wsel{n}" for n in range(20))
             + " pump_up1 pump_up2 pump_up3 pump_dn1 pump_dn2 pump_dn3 pg ng vmid row0 row1 row2 row3 vdd vss rt5w_array")
    L.append("xsm g0 g1 g2 g3 nbias kbias vr vcas vb out0 out1 out2 out3 vdd vss rt5w_softmax")
    for j in range(4):
        L.append(f"xk{j} row{j} k{j}_0 k{j}_1 k{j}_2 k{j}_3 g{j} vdd vss rt5w_kscale")
        L.append(f"Vo{j} out{j} 0 {V_O}")
        L.append(_src(f"Vw{j}", f"xarr.w{j}", "0", w0[j], w1[j], te))
        for i in range(4):
            L.append(_src(f"Vh{j}{i}", f"xarr.xc{j}{i}.h", "0", h0[j][i], h1[j][i], te))
    return "\n".join(L)


def netlist(new, old, bias_from_off, corner="tt", control=""):
    return (f"* rt5w sky130 co-simulation event\n{sim.header(corner, new['temp'], ['rt5w_analog'], OPTIONS)}\n"
            f"{body(new, old, bias_from_off, corner)}\n" + (f".control\nset filetype=ascii\n{control}\n.endc\n" if control else "")
            + ".end\n")


_NG = None


def _shared():
    global _NG
    if _NG is None:
        from .backends.spice import shared_ngspice
        _NG = shared_ngspice()
        for c in sim.SPICEINIT.strip().splitlines():
            if c.startswith("set "):
                _NG.exec_command(c)
    return _NG


def simulate(new, old, bias_from_off, corner="tt", engine="pyspice", off=None):
    """t (s, from the event), shares (n x 4), V_B (n)."""
    te = t_event(bias_from_off)
    tstop = te + T_HORIZON
    tran = f"tran {T_STEP:.3e} {tstop:.4e}"
    if engine == "pyspice":
        from .falsify import _Mute
        ng = _shared()
        # save only what is used: a full-macro transient keeps every node otherwise, and libngspice holds the
        # plots and circuits in-process (the first Icarus run was OOM-killed at 6.3 GB during cs04)
        net = netlist(new, old, bias_from_off, corner).replace(".end\n", ".save i(vo0) i(vo1) i(vo2) i(vo3) v(vb)\n.end\n")
        with _Mute():
            ng.load_circuit(net)
            ng._ngspice_shared.ngSpice_Command(tran.encode())
        p = ng.plot(None, ng.last_plot)
        g = lambda n: np.real(np.asarray(p[n]._data, dtype=complex)).copy()   # noqa: E731
        t, I, vb = g("time"), np.stack([g(f"vo{j}#branch") for j in range(4)], 1), g("vb")
        with _Mute():
            ng.destroy()                                   # all plots
            ng._ngspice_shared.ngSpice_Command(b"remcirc")
    elif engine == "ngspice":
        _, d, out = sim.run(body(new, old, bias_from_off, corner), f"{tran}\nwrdata __DATA__ i(vo0) i(vo1) i(vo2) i(vo3) v(vb)",
                            corner, new["temp"], blocks=["rt5w_analog"], timeout=3600, options=OPTIONS)
        if d is None:
            raise RuntimeError(out[-2000:])
        t, I, vb = d[:, 0], np.stack([d[:, 1 + 2 * j] for j in range(4)], 1), d[:, 9]
    else:
        raise ValueError(engine)
    k = t >= te - 1e-12
    t, I, vb = t[k] - te, I[k], vb[k]
    s = I.sum(1)
    shares = np.where(s[:, None] > 0, I / np.where(s > 0, s, 1)[:, None], 0.25)
    return t, shares, vb


def operating_point(state, corner="tt"):
    vals, _, _ = sim.run(body(state, state, False, corner), "op\nprint i(vo0) i(vo1) i(vo2) i(vo3) v(vb)", corner,
                         state["temp"], blocks=["rt5w_analog"], options=OPTIONS)
    I = np.array([vals[f"i(vo{j})"] for j in range(4)])
    return list(I / I.sum()), vals["v(vb)"]


class Trajectory:
    def __init__(self, t, shares, vb):
        self.t, self.shares, self.vb = t, shares, vb

    def at(self, dt):
        dt = min(max(dt, 0.0), self.t[-1])
        return [float(np.interp(dt, self.t, self.shares[:, j])) for j in range(4)], float(np.interp(dt, self.t, self.vb))


class Cosim:
    """Event-driven analog solver (same protocol as rt5w/cosim.Cosim)."""

    def __init__(self, corner="tt", temp=27.0, engine="pyspice", off=None):
        self.corner, self.temp, self.engine, self.off = corner, temp, engine, off
        self.cache, self.n_sim, self.sim_seconds = {}, 0, 0.0
        self.settled = None
        self.traj, self.t_event = None, 0.0
        self.pending = None

    def blank_state(self):
        return dict(q=[0] * 4, ks=[0] * 4, k=[[0] * 4 for _ in range(4)], trim_mv=[0.0] * 4, gamma=[0.0] * 4,
                    temp=self.temp)

    @staticmethod
    def _key(st):
        return (tuple(st["q"]), tuple(st["ks"]), tuple(tuple(r) for r in st["k"]),
                tuple(round(v, 4) for v in st["trim_mv"]), tuple(round(v, 7) for v in st["gamma"]), st["temp"])

    def event(self, state, bias_en, now_s, was_biased):
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
            t0 = time.time()
            self.cache[key] = Trajectory(*simulate(new, old, from_off, self.corner, self.engine))
            self.n_sim += 1
            self.sim_seconds += time.time() - t0
        self.traj, self.t_event, self.settled, self.pending = self.cache[key], t_ev, new, None

    def sample(self, now_s):
        if self.pending:
            self._solve()
        if self.traj is None:
            return None
        return self.traj.at(now_s - self.t_event)
