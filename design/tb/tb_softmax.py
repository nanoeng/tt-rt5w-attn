"""Softmax core vs the Python golden model (sim/rt5w_ng.golden): shares a_j = I_out,j / sum I_out against
softmax(x); total output = 4 I_sum (x4 readout mirrors); V_B against log-sum-exp (slope and offset, as VBCAL fits).
Score currents: I_j = x_j nU_T,n / R_c, with nU_T,n the measured slope of the Me geometry and R_c the drawn
res_xhigh_po length (tech.py); vr, vcas and the AGC unit I_u are the bias block's values at each corner."""
import numpy as np

import sim
import tech
from softmax import RC_L

KAPPA, V_O = 0.04, 2.2        # keep-alive I_u/25 per diode; output held at the readout cascode-source level
VECTORS = [[0, 0, 0, 0], [18, 16, 0, 0], [18, 0, 0, 0], [5.05, 8.04, 4.35, 4.65], [10, 10, 10, 10],
           [3, 6, 9, 12], [16.8, 14.93, 0, 0], [12, 11.5, 11, 10.5]]


def golden(x):
    e = np.exp(np.asarray(x, float) - np.max(x))
    return e / e.sum()


def lse(x):
    m = max(x)
    return m + np.log(np.sum(np.exp(np.asarray(x, float) - m)))


def r_track(temp):
    """R(T)/R(27 C) of res_xhigh_po_0p35: flat in this model release (tech.py measures 7.37 kOhm/um at every
    corner), so I_u = PTAT/R and R_c track trivially."""
    return 1.0


def run(corner="tt", temp=27.0, vectors=VECTORS, track_r=True):
    """track_r: score currents ~ PTAT / R(T), as from a beta multiplier whose resistor is the same ppolyf_u_3k type
    (so the score x = I R_c / nU_T keeps its scale); False = ideal PTAT current into a real R_c."""
    t = tech.measure(corner, temp)
    R_C = RC_L * t["R_per_um"]
    V_R, V_CAS, I_SUM = t["vr"], t["vcas"], 4 * t["I_u"]
    ptat, pt0 = 1.0, 1.0                 # the measured values already carry the corner / temperature
    nut = t["nUT_n"]
    L = ["Vdd vdd 0 3.3", "Vss vss 0 0"]
    for k, x in enumerate(vectors):
        L += [f"Vr{k} vr{k} 0 {V_R}", f"Vc{k} vcas{k} 0 {V_CAS}",
              f"Ib{k} vdd nb{k} {I_SUM / 4 * pt0:.5e}", f"Ik{k} vdd kb{k} {KAPPA * I_SUM * pt0:.5e}"]
        L += [f"Ig{k}_{j} vdd g{k}_{j} {x[j] * nut / R_C * ptat:.5e}" for j in range(4)]
        L += [f"Vo{k}_{j} o{k}_{j} 0 {V_O}" for j in range(4)]
        L.append(sim.inst(f"Xs{k}", "rt5w_softmax", vdd="vdd", vss="vss", vr=f"vr{k}", vcas=f"vcas{k}",
                          nbias=f"nb{k}", kbias=f"kb{k}", vb=f"vb{k}",
                          **{f"g{j}": f"g{k}_{j}" for j in range(4)}, **{f"out{j}": f"o{k}_{j}" for j in range(4)}))
    ctl = "op\n" + "\n".join(f"print -i(Vo{k}_{j})" for k in range(len(vectors)) for j in range(4)) + "\n" + \
          "\n".join(f"print v(vb{k})" for k in range(len(vectors)))
    vals, _, _ = sim.run("\n".join(L), ctl, corner, temp, blocks=["rt5w_softmax"])
    rows = []
    for k, x in enumerate(vectors):
        I = np.array([-vals[f"-i(vo{k}_{j})"] for j in range(4)])
        rows.append(dict(x=x, I=I, a=I / I.sum(), g=golden(x), vb=vals[f"v(vb{k})"], lse=lse(x)))
    vb = np.array([r["vb"] for r in rows]); ls = np.array([r["lse"] for r in rows])
    slope, off = np.polyfit(ls, vb, 1)
    for r in rows:
        r["err_lsb"] = float(np.abs(255 * (r["a"] - r["g"])).max())
        r["vb_fit_err_mV"] = 1e3 * (r["vb"] - (slope * r["lse"] + off))
    # effective score scale: Me runs with body = source (V_B), so its in-circuit slope differs from the diode's;
    # the chain calibration (R_c / X_PER_QK fit) absorbs one scale factor -- report the residual after it
    best = min(((max(float(np.abs(255 * (r["a"] - golden(np.array(r["x"]) * sc))).max()) for r in rows), sc)
                for sc in np.arange(0.70, 1.40, 0.0025)))
    return dict(rows=rows, vb_slope=slope, vb_off=off, x_scale=best[1], err_cal=best[0], i_sum_out=[float(r["I"].sum()) for r in rows],
                ptat=pt0)


if __name__ == "__main__":
    for c, T in (("tt", 27), ("ss", -40), ("ff", 125)):
        r = run(c, T)
        e = max(x["err_lsb"] for x in r["rows"])
        tot = np.array(r["i_sum_out"]) / (4 * 4 * tech.measure(c, T)["I_u"])
        print(f"{c:8s} {T:5.0f} C: max share error {e:.2f} LSB raw, {r['err_cal']:.2f} LSB at x scale {r['x_scale']:.3f};  sum I_out / (4 I_sum) {tot.min():.3f}..{tot.max():.3f};  "
              f"V_B = {r['vb_off']:.3f} + {r['vb_slope']*1e3:.2f} mV x LSE (fit residual "
              f"{max(abs(x['vb_fit_err_mV']) for x in r['rows']):.1f} mV)")
        for x in r["rows"]:
            print(f"      x {x['x']}: codes {np.round(255*x['a']).astype(int)} golden {np.round(255*x['g']).astype(int)}  V_B {x['vb']:.4f}")
