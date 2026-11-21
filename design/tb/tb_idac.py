"""IDAC vs the Python model: I_col(q) = q * I_LSB (rt5w/analog_model.py, I_LSB = I_u/15, PTAT).
16 copies of the captured schematic, one per code, column held at the array's column voltage (tech dcol)."""
import numpy as np

import sim
import tech

I_LSB = tech.measure("tt", 27.0)["I_u"] / 15     # 27 C value, scaled PTAT below


def run(corner="tt", temp=27.0, v_col=None):
    v_col = v_col if v_col is not None else tech.measure(corner, temp)["dcol"]
    ptat = (temp + 273.15) / 300.15
    L = ["Vdd vdd 0 3.3", "Vss vss 0 0"]
    for q in range(16):
        L += [f"Iref{q} vdd nd{q} {I_LSB * ptat:.6e}",
              f"Vc{q} c{q} 0 {v_col}",
              sim.inst(f"Xi{q}", "rt5w_idac4", nd=f"nd{q}", col=f"c{q}", vss="vss",
                       **{f"b{b}": ("vdd" if (q >> b) & 1 else "vss") for b in range(4)})]
    ctl = "op\n" + "\n".join(f"print -i(Vc{q})" for q in range(16))
    vals, _, out = sim.run("\n".join(L), ctl, corner, temp, blocks=["rt5w_idac4"])
    I = np.array([vals[f"-i(vc{q})"] for q in range(16)])
    lsb = I[15] / 15                       # end-point LSB
    model = np.arange(16) * I_LSB * ptat
    inl = (I - np.arange(16) * lsb) / lsb
    dnl = np.diff(I) / lsb - 1
    return dict(corner=corner, temp=temp, I=I, gain_err=I[15] / model[15] - 1,
                inl_max=float(np.abs(inl).max()), dnl_max=float(np.abs(dnl).max()),
                monotonic=bool(np.all(np.diff(I) > 0)))


if __name__ == "__main__":
    for c, T in (("tt", 27), ("ss", -40), ("ff", 125)):
        r = run(c, T)
        print(f"{c:8s} {T:5.0f} C: I(15) {r['I'][15]*1e9:7.2f} nA  gain vs model {r['gain_err']*100:+.2f} %  "
              f"INL {r['inl_max']:.3f} LSB  DNL {r['dnl_max']:.3f} LSB  monotonic {r['monotonic']}")
