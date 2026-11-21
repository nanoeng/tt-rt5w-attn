"""Full analog chain at transistor level (rt5w_analog: bias -> IDACs -> array -> softmax -> readout) against the
Python model (rt5w/analog_model.py with the schematic calibration, design/calibration.json if present).

Keys are 'written' ideally: the storage nodes h_ji (and the row trims w_j) are forced by voltage sources to
h = w - nU_T,p ln k (the firmware key mapping), w = W_REF. The controller's SAR (rt5w_ctrl.v) runs in the ngspice
control loop on every channel: adc_rst 1 clock, integrate ADCT-2 clocks, adc_lat 1 clock, keep the trial bit if
cmp = 1. Codes are compared with the model's codes."""
import json
import math
import os
import sys

import numpy as np

import sim
import tech

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rt5w.regmap import X_PER_QK  # noqa: E402

W_REF = None          # per corner: the column-line level at I_u (tech dcol); on silicon: firmware calibration
T_CLK = 50e-9
# rshunt: 1 pA/V per node for the nA-biased diodes; itl1 (Newton iterations of the operating point, default 100): with the extracted netlist at ss / -40 C the
# transient operating point otherwise ended in a non-converged state (vr = -0.48 V, int - intr = 0.2 V during reset)
OPTIONS = os.environ.get("RT5W_CHAIN_OPTIONS", "rshunt=1e12 itl1=1000")
CAL = os.path.join(os.path.dirname(__file__), "..", "calibration.json")
BLOCKS = ["rt5w_analog"]        # the hierarchical netlist carries every child subckt
VECTORS = [  # (q codes per column, keys k[j][i], per-key scale ks_j)
    ([15, 15, 15, 15], [[1, 1, 1, 1], [0.5, 0.5, 0.5, 0.5], [0.25, 0.25, 0.25, 0.25], [0.1, 0.1, 0.1, 0.1]], [15] * 4),
    ([15, 8, 4, 0], [[1, 0.2, 0.2, 1], [0.2, 1, 0.2, 1], [0.2, 0.2, 1, 1], [0.6, 0.6, 0.6, 1]], [15] * 4),
    ([7, 7, 7, 7], [[1, 1, 1, 1]] * 4, [15] * 4),
    ([15, 8, 4, 0], [[1, 0.2, 0.2, 1], [0.2, 1, 0.2, 1], [0.2, 0.2, 1, 1], [0.6, 0.6, 0.6, 1]], [9, 15, 12, 6]),
]


PEX = os.environ.get("RT5W_NETLIST", "netlist") != "netlist"
_NODES = None


def node_h(j, i):
    """storage node of key cell (row j, column i): schematic hierarchy, or the flat extracted array (pex.py)"""
    global _NODES
    if not PEX:
        return f"xa.xarr.xc{j}{i}.h"
    _NODES = _NODES or json.load(open(os.path.join(os.path.dirname(__file__), "..", "..", "layout", "pex", "array_nodes.json")))
    return "xa.xarr.xp." + _NODES["h"][f"{j}{i}"]


def node_w(j):
    global _NODES
    if not PEX:
        return f"xa.xarr.w{j}"
    _NODES = _NODES or json.load(open(os.path.join(os.path.dirname(__file__), "..", "..", "layout", "pex", "array_nodes.json")))
    return "xa.xarr.xp." + _NODES["w"][str(j)]


def G0(corner, temp):
    """Calibrated key write: cell gain at V_w = 0 (tech.py), removed by the firmware's key mapping."""
    return tech.measure(corner, temp)["cell_gain0"]


def nut_p(corner, temp):
    """nU_T,p of the key law at this corner: the in-cell fit of tb_keycell (tech.py), i.e. what the firmware's key
    calibration would measure."""
    t = tech.measure(corner, temp)
    return t.get("nUT_p_cell", t["nUT_p"])


def model_codes(q, k, ks=(15, 15, 15, 15), beta=1.0):
    x = np.clip(X_PER_QK * np.array(ks) / 15.0 * (np.array(k) @ np.array(q, float)) * beta, 0, 18.0)
    e = np.exp(x - x.max())
    a = e / e.sum()
    return [int(min(255, math.floor(255 * v + 0.5))) for v in a], x


def _sar(adct):
    t_end = adct * T_CLK
    L = []
    for ch in range(4):
        for j in range(4):
            L.append(f"alter Vch{j} dc = {3.3 if j == ch else 0}")
        L.append("let code = 0")
        for b in range(7, -1, -1):
            L.append(f"let trial = code + {2 ** b}")
            for kk in range(8):
                L += [f"let d{kk} = 3.3*(floor(trial/{2 ** kk}) - 2*floor(trial/{2 ** (kk + 1)}))",
                      f"alter Vd{kk} dc = d{kk}"]
            L += [f"tran 10n {t_end:.3e}", "let c = v(cmp)[length(v(cmp))-1]", "if c > 1.65", "let code = trial",
                  "end", "destroy all"]
        L.append(f"let code_{ch} = code\nprint code_{ch}")
    return "\n".join(L)


SAR_MODE = os.environ.get("RT5W_SAR", "trial")   # "cont": one continuous transient (realistic; see results 2026-11-21)


def _sar_cont(adct):
    """The SAR as one continuous transient (as on silicon): adc_rst / adc_lat are periodic pulses (1 clock each per
    trial of ADCT clocks), the transient stops 2 ns into every trial's reset clock, reads cmp (held by the SR latch),
    sets the next trial's DAC code / channel and resumes. One operating point per vector instead of one per trial."""
    P = adct * T_CLK
    L = []
    def set_trial(ch, trial):
        out = [f"alter Vch{j} dc = {3.3 if j == ch else 0}" for j in range(4)]
        for kk in range(8):
            out += [f"let d{kk} = 3.3*(floor({trial}/{2 ** kk}) - 2*floor({trial}/{2 ** (kk + 1)}))", f"alter Vd{kk} dc = d{kk}"]
        return out
    # operating point with every channel off and the DAC at 0 (with the extracted netlist the op with a channel and
    # DAC code applied could converge to a spurious state); trial 0's code is applied 2 ns into its reset clock
    L += ["let code = 0", "let trial = 128"]
    L.append("stop when time = 2e-9")
    for n in range(1, 33):
        L.append(f"stop when time = {n * P + 2e-9:.4e}")
    L.append(f"tran 2n {32 * P + 4e-9:.4e}")
    L += set_trial(0, "trial") + ["resume"]
    for n in range(32):
        ch, b = n // 8, 7 - n % 8
        L += ["let c = v(cmp)[length(v(cmp))-1]", "if c > 1.65", "let code = trial", "end"]
        if b == 0:
            L += [f"let code_{ch} = code", f"print code_{ch}", "let code = 0"]
        if n < 31:
            nch, nb = (n + 1) // 8, 7 - (n + 1) % 8
            L += [f"let trial = code + {2 ** nb}"] + set_trial(nch, "trial") + ["resume"]
    return "\n".join(L)


def run(q, k, ks=(15, 15, 15, 15), corner="tt", temp=27.0, adct=16):
    nu = nut_p(corner, temp)
    w_ref = tech.measure(corner, temp)["dcol"]
    L = ["Vdd vdd 0 3.3", "Vss vss 0 0", "Vben bias_en 0 3.3", "Vvbp vb_probe_en 0 0", "Vua2 ua2 0 2.0",
         "Vua0 ua0 0 1.0", f"Vrst adc_rst 0 PWL(0 3.3 {T_CLK:.3e} 3.3 {T_CLK + 1e-9:.3e} 0)",
         f"Vlat adc_lat 0 PWL(0 0 {(adct - 1) * T_CLK:.3e} 0 {(adct - 1) * T_CLK + 1e-9:.3e} 3.3)"]
    if SAR_MODE == "cont":
        P = adct * T_CLK
        L[6] = f"Vrst adc_rst 0 PULSE(3.3 0 {T_CLK:.4e} 1n 1n {P - T_CLK - 1e-9:.4e} {P:.4e})"
        L[7] = f"Vlat adc_lat 0 PULSE(0 3.3 {(adct - 1) * T_CLK:.4e} 1n 1n {T_CLK - 2e-9:.4e} {P:.4e})"
    conn = {p: p for p in sim.ports("rt5w_analog")}
    for i in range(4):
        for b in range(4):
            L.append(f"Vq{i}_{b} q{i}_{b} 0 {3.3 * ((q[i] >> b) & 1)}")
            L.append(f"Vk{i}_{b} k{i}_{b} 0 {3.3 * ((ks[i] >> b) & 1)}")
    L += [f"Vws{n} wsel{n} 0 0" for n in range(20)]
    L += [f"Vpu{j} pump_up{j} 0 0" for j in (1, 2, 3)] + [f"Vpd{j} pump_dn{j} 0 0" for j in (1, 2, 3)]
    L += [f"Vch{j} adc_ch{j} 0 0" for j in range(4)] + [f"Vd{kk} dac{kk} 0 0" for kk in range(8)]
    L.append(sim.inst("Xa", "rt5w_analog", **conn))
    for j in range(4):
        L.append(f"Vw{j} {node_w(j)} 0 {w_ref:.4f}")
        for i in range(4):
            h = (w_ref - nu * math.log(k[j][i]) + nu * math.log(G0(corner, temp))) if k[j][i] > 0 else 0.0
            L.append(f"Vh{j}{i} {node_h(j, i)} 0 {h:.5f}")
    vals, _, out = sim.run("\n".join(L), (_sar_cont if SAR_MODE == "cont" else _sar)(adct), corner, temp, blocks=BLOCKS, timeout=7200, options=OPTIONS)
    got = [int(round(vals[f"code_{ch}"])) for ch in range(4)]
    want, x = model_codes(q, k, ks)
    return dict(q=q, k=k, ks=ks, x=x, spice=got, model=want, err=max(abs(a - b) for a, b in zip(got, want)))


if __name__ == "__main__":
    for c, T in (("tt", 27), ("ss", -40), ("ff", 125)):
        for q, k, ks in VECTORS:
            r = run(q, k, ks, c, T)
            print(f"{c} {T} C  q={q} ks={ks}  x={np.round(r['x'], 2)}  model {r['model']}  SPICE {r['spice']}  "
                  f"max |err| {r['err']} LSB")


def dc_shares(q, k, ks=(15, 15, 15, 15), corner="tt", temp=27.0):
    """Fast DC check of the analog chain (no SAR): softmax output currents from the operating point, as shares,
    plus the fitted score scale (x_spice / x_model) -- used to set R_c (softmax.RC_L)."""
    nu = nut_p(corner, temp)
    w_ref = tech.measure(corner, temp)["dcol"]
    L = ["Vdd vdd 0 3.3", "Vss vss 0 0", "Vben bias_en 0 3.3", "Vvbp vb_probe_en 0 0", "Vua2 ua2 0 2.0",
         "Vua0 ua0 0 1.0", "Vrst adc_rst 0 3.3", "Vlat adc_lat 0 0"]
    for i in range(4):
        for b in range(4):
            L.append(f"Vq{i}_{b} q{i}_{b} 0 {3.3 * ((q[i] >> b) & 1)}")
            L.append(f"Vk{i}_{b} k{i}_{b} 0 {3.3 * ((ks[i] >> b) & 1)}")
    L += [f"Vws{n} wsel{n} 0 0" for n in range(20)]
    L += [f"Vpu{j} pump_up{j} 0 0" for j in (1, 2, 3)] + [f"Vpd{j} pump_dn{j} 0 0" for j in (1, 2, 3)]
    L += [f"Vch{j} adc_ch{j} 0 0" for j in range(4)] + [f"Vd{kk} dac{kk} 0 0" for kk in range(8)]
    L.append(sim.inst("Xa", "rt5w_analog", **{p: p for p in sim.ports("rt5w_analog")}))
    for j in range(4):
        L.append(f"Vw{j} {node_w(j)} 0 {w_ref:.4f}")
        for i in range(4):
            h = (w_ref - nu * math.log(k[j][i]) + nu * math.log(G0(corner, temp))) if k[j][i] > 0 else 0.0
            L.append(f"Vh{j}{i} {node_h(j, i)} 0 {h:.5f}")
    ctl = "op\n" + "\n".join(f"print @m.xa.xsm.xmo{j}.msky130_fd_pr__pfet_g5v0d10v5[id]" for j in range(4)) + "\n" + \
        "\n".join(f"print @m.xa.xsm.xmr{j}.msky130_fd_pr__nfet_g5v0d10v5[id]" for j in range(4)) + \
        "\nprint v(xa.vb)\n" + "\n".join(f"print v(xa.g{j})" for j in range(4))
    vals, _, out = sim.run("\n".join(L), ctl, corner, temp, blocks=BLOCKS, options="rshunt=1e12")
    # net output = PMOS output mirror minus the keep-alive give-back (what the readout sees)
    I = np.array([abs(vals[f"@m.xa.xsm.xmo{j}.msky130_fd_pr__pfet_g5v0d10v5[id]"]) -
                  abs(vals[f"@m.xa.xsm.xmr{j}.msky130_fd_pr__nfet_g5v0d10v5[id]"]) for j in range(4)])
    a = I / I.sum()
    xm = X_PER_QK * np.array(ks) / 15.0 * (np.array(k) @ np.array(q, float))
    best = min((float(np.abs(a - np.exp(sc * xm - (sc * xm).max()) / np.exp(sc * xm - (sc * xm).max()).sum()).max()), sc)
               for sc in np.arange(0.5, 1.6, 0.005))
    return dict(a=a, I=I, x_model=xm, scale=best[1], err_lsb=255 * best[0], vb=vals["v(xa.vb)"],
                g=[vals[f"v(xa.g{j})"] for j in range(4)])
