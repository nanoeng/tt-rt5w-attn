"""Bias block: outputs against their design targets, gating with keep-alive, and start-up from a supply ramp.
Targets (rt5w model constants): I_u = 125 nA (I_ref/4), nbias = ndac = I_u, nd = I_u/15, kbias = I_u/25,
gated outputs ~1 % of nominal; vr ~ 1.65 V, vmid ~ 2.64 V, vcas ~ 1.05 V. The score scale needs I_u ~ PTAT / R."""
import numpy as np

import sim

LOADS = {"iref": 1.0, "nbias": 0.6, "ndac": 0.6, "nd0": 0.6, "nd1": 0.6, "nd2": 0.6, "nd3": 0.6, "kbias": 0.6}


def run(corner="tt", temp=27.0, bias_en=1):
    L = ["Vdd vdd 0 3.3", "Vss vss 0 0", f"Ven bias_en 0 {3.3 * bias_en}"]
    L += [f"V_{n} {n} 0 {v}" for n, v in LOADS.items()]
    L += ["Cv vbn 0 1p", "Cr vr 0 1p"]
    L.append(sim.inst("Xb", "rt5w_bias", **{p: p for p in sim.ports("rt5w_bias")}))
    ctl = "op\n" + "\n".join(f"print -i(V_{n})" for n in LOADS) + "\n" + \
          "\n".join(f"print {v}" for v in ("v(vbn)", "v(vcas)", "v(vr)", "v(vmid)", "v(pg)", "v(ng)", "-i(Vdd)"))
    vals, _, _ = sim.run("\n".join(L), ctl, corner, temp, blocks=["rt5w_bias"])
    out = {n: -vals[f"-i(v_{n})"] for n in LOADS}
    out.update({k: vals[f"v({k})"] for k in ("vbn", "vcas", "vr", "vmid", "pg", "ng")})
    out["i_vdd"] = vals["-i(vdd)"]
    return out


def startup(corner="tt", temp=27.0):
    L = ["Vdd vdd 0 PWL(0 0 10u 3.3)", "Vss vss 0 0", "Ven bias_en 0 PWL(0 0 10u 3.3)"]
    L += [f"V_{n} {n} 0 0.6" for n in LOADS]
    L.append(sim.inst("Xb", "rt5w_bias", **{p: p for p in sim.ports("rt5w_bias")}))
    ctl = "tran 50n 200u\nwrdata __DATA__ -i(V_nbias)"
    _, tab, _ = sim.run("\n".join(L), ctl, corner, temp, blocks=["rt5w_bias"])
    t, i = tab[:, 0], tab[:, 1]
    i = np.abs(i)
    final = i[-1]
    ok = np.where(np.abs(i - final) > 0.02 * abs(final))[0]
    return dict(final=final, t_settle_us=(t[ok[-1]] * 1e6 if len(ok) else 0.0))


if __name__ == "__main__":
    for c, T in (("tt", 27), ("ss", -40), ("ff", 125)):
        on, off = run(c, T, 1), run(c, T, 0)
        iu = on["nbias"]
        ratios = {k: on[k] / iu for k in ("ndac", "nd0", "nd3", "kbias")}
        print(f"{c:8s} {T:5.0f} C: I_u {iu*1e9:6.1f} nA | ndac/I_u {ratios['ndac']:.3f}  nd/I_u {ratios['nd0']:.4f} (1/15 = 0.0667)"
              f"  kbias/I_u {ratios['kbias']:.4f} (0.04) | gated: nbias {100*off['nbias']/iu:.2f} %  nd0 {100*off['nd0']/on['nd0']:.2f} %"
              f" | vr {on['vr']:.3f} vmid {on['vmid']:.3f} vcas {on['vcas']:.3f} vbn {on['vbn']:.3f} | I_DD {on['i_vdd']*1e6:.2f} uA "
              f"(gated {off['i_vdd']*1e6:.2f})")
    s = startup()
    print(f"start-up (supply ramp 0->3.3 V in 10 us): I_u settles to 2 % at {s['t_settle_us']:.1f} us, final {s['final']*1e9:.1f} nA")
