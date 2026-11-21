"""V_B buffer vs the model's probe (rt5w/analog_model.py: v_b is read directly): ua[1] = V_B within 2 mV over the
V_B range 1.2..2.3 V into a 1 MOhm || 10 pF probe, settling < 20 us; disabled leakage < 100 pA."""
import numpy as np

import sim
import tech

VB_RANGE = (1.1, 1.5, 1.9, 2.35)  # V_B over the softmax tb vectors and corners (sky130: 1.13..2.35 V)


def run(corner="tt", temp=27.0):
    L = ["Vdd vdd 0 3.3", "Vss vss 0 0", f"Vvbn vbn 0 {tech.measure(corner, temp)['vbn']:.4f}", "Ven en 0 PWL(0 0 1u 0 1.01u 3.3)",
         "Vvb vb 0 1.3", "Rp pad 0 1Meg", "Cp pad 0 10p",
         sim.inst("Xb", "rt5w_vbbuf", **{p: p for p in sim.ports("rt5w_vbbuf")})]
    ctl = ["tran 50n 40u", "wrdata __DATA__ v(pad)"]
    _, tab, _ = sim.run("\n".join(L), "\n".join(ctl), corner, temp, blocks=["rt5w_vbbuf"])
    t, v = tab[:, 0], tab[:, 1]
    bad = np.where(np.abs(v - v[-1]) > 2e-3)[0]
    t_settle = (t[bad[-1]] - 1.01e-6) * 1e6 if len(bad) else 0.0
    errs = []
    for vb in VB_RANGE:
        L2 = [l.replace("Vvb vb 0 1.3", f"Vvb vb 0 {vb}").replace("Ven en 0 PWL(0 0 1u 0 1.01u 3.3)", "Ven en 0 3.3")
              for l in L]
        vals, _, _ = sim.run("\n".join(L2), "op\nprint v(pad)", corner, temp, blocks=["rt5w_vbbuf"])
        errs.append(vals["v(pad)"] - vb)
    L3 = [l.replace("Ven en 0 PWL(0 0 1u 0 1.01u 3.3)", "Ven en 0 0").replace("Rp pad 0 1Meg", "Vpad pad 0 2.0")
          for l in L]
    vals, _, _ = sim.run("\n".join(L3), "op\nprint i(Vpad)", corner, temp, blocks=["rt5w_vbbuf"])
    e = 1e3 * np.array(errs)
    fit = np.polyfit(VB_RANGE, e, 1)
    return dict(err_mV=e, resid_mV=float(np.abs(e - np.polyval(fit, VB_RANGE)).max()), t_settle_us=t_settle, leak=abs(vals["i(vpad)"]))


if __name__ == "__main__":
    for c, T in (("tt", 27), ("ss", -40), ("ff", 125)):
        r = run(c, T)
        print(f"{c:8s} {T:5.0f} C: ua[1] - V_B at {VB_RANGE} V = {np.round(r['err_mV'], 2)} mV (after VBCAL slope/offset {r['resid_mV']:.2f} mV) | settle (2 mV) "
              f"{r['t_settle_us']:.1f} us | disabled leakage {r['leak']*1e12:.1f} pA")
