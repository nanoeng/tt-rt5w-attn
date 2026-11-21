"""Key cell vs the Python model (rt5w/analog_model.py): I_cell = I_Q,c * exp(-V_w / nU_T,p), V_w = h - w.
The O1 check: at fixed V_w the ratio I_cell/I_Q must not depend on the column current (coupling ratio alpha = 1)."""
import numpy as np

import sim
import tech
from units import NU

T27 = tech.measure("tt", 27.0)
I_LSB = T27["I_u"] / 15
NUT_P_MODEL = T27["nUT_p"]   # Mc diode slope at I_u (tech.py)
NUT_FIT_27 = T27["nUT_p"]    # refined below by the per-q fit; goes into the model calibration
QS = (1, 3, 7, 15)
VWS = (0.0, 0.02, 0.05, 0.1, 0.15, 0.2)


def run(corner="tt", temp=27.0, w=None, i_tail=None, v_row=0.85):
    t = tech.measure(corner, temp)
    w = w if w is not None else t["dcol"]
    i_tail = i_tail if i_tail is not None else T27["I_u"]
    ptat = (temp + 273.15) / 300.15
    L = ["Vdd vdd 0 3.3", "Vss vss 0 0", f"Ib vdd vbn {i_tail * ptat:.4e}",
         f"Xbn vbn vbn vss vss sky130_fd_pr__nfet_g5v0d10v5 L={NU['L']} W={NU['W']} nf=1 m=1", f"Vw w 0 {w}", "Vsel wsel 0 3.3"]
    for q in QS:
        for k, vw in enumerate(VWS):
            n = f"{q}_{k}"
            L += [f"Iq{n} dcol{n} 0 {q * I_LSB * ptat:.6e}",
                  sim.inst(f"Xd{n}", "rt5w_coldiode", dcol=f"dcol{n}", vdd="vdd"),
                  f"Vh{n} vw{n} 0 {w + vw}",
                  f"Vr{n} row{n} 0 {v_row}",
                  sim.inst(f"Xc{n}", "rt5w_keycell", dcol=f"dcol{n}", w="w", vw=f"vw{n}", wsel="wsel", vbn="vbn",
                           row=f"row{n}", vdd="vdd", vss="vss")]
    ctl = "op\n" + "\n".join(f"print i(Vr{q}_{k})" for q in QS for k in range(len(VWS)))
    vals, _, _ = sim.run("\n".join(L), ctl, corner, temp, blocks=["rt5w_coldiode", "rt5w_keycell"])
    ratio = np.array([[vals[f"i(vr{q}_{k})"] / (q * I_LSB * ptat) for k in range(len(VWS))] for q in QS])
    vws = np.array(VWS)
    # fitted slope per q (log-linear), and gain at V_w = 0
    slopes = [-1 / np.polyfit(vws, np.log(r), 1)[0] for r in ratio]
    nut_T = t.get("nUT_p_cell", t["nUT_p"])           # model law with the in-cell slope at this corner (tech.py)
    model = np.exp(-vws / nut_T)
    big = ratio * (np.arange(len(QS))[:, None] * 0 + np.array(QS)[:, None]) * I_LSB > 200e-12   # ignore < 200 pA
    err = np.where(big, ratio / ratio[:, :1] / model - 1, 0.0)
    return dict(ratio=ratio, gain0=ratio[:, 0], nUT_fit=np.array(slopes), shape_err=err, nut_T=nut_T)


if __name__ == "__main__":
    for c, T in (("tt", 27), ("ss", -40), ("ff", 125)):
        r = run(c, T)
        g = r["gain0"]
        print(f"{c:8s} {T:5.0f} C: I_cell/I_Q at V_w=0 for q={QS}: {np.round(g, 4)}  "
              f"(spread {100 * (g.max() / g.min() - 1):.2f} %)")
        print(f"          fitted nU_T,p per q (mV): {np.round(r['nUT_fit'] * 1e3, 2)}  (model {NUT_P_MODEL*1e3} at 27 C);"
              f"  max |error| vs exp(-V_w/{r['nut_T']*1e3:.1f} mV) {100 * np.abs(r['shape_err']).max():.1f} % (cells > 200 pA)")
