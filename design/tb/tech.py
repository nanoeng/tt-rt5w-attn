"""Per-corner technology / bias constants for the testbenches, MEASURED on the sky130 schematics (no gf180 numbers):
  bias block op  -> I_u, vr, vcas, vbn, vmid           (rt5w_bias, the real generator)
  Me slope       -> nU_T,n of the exponentiator at I_u (d ln I / d V_GS of the softmax Me geometry)
  Mc slope       -> nU_T,p of the array PMOS at I_u    (the key law exp(-V_w / nU_T,p))
  R_sq           -> res_xhigh_po_0p35 ohm per um of length
  dcol           -> column-line voltage at I_u (sets the key-write level W_REF)
Cached in tech_<corner>_<T>.json; delete to re-measure."""
import json
import math

import numpy as np
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.dirname(HERE), os.path.join(os.path.dirname(HERE), "blocks")]
import sim  # noqa: E402
import units  # noqa: E402

CORNERS = (("tt", 27.0), ("ss", -40.0), ("ff", 125.0))


def _slope(kind, geo, i_d, corner, temp):
    """nU_T = I / g_m of a diode-connected device at i_d (gm from the model's op point)."""
    m = "nfet" if kind == "n" else "pfet"
    if kind == "n":
        L = ["Vdd vdd 0 3.3", f"Ii vdd d {i_d:.4e}",
             f"XM d d 0 0 sky130_fd_pr__{m}_g5v0d10v5 L={geo['L']} W={geo['W']} nf=1 m=1"]
    else:
        L = ["Vdd vdd 0 3.3", f"Ii d 0 {i_d:.4e}",
             f"XM d d vdd vdd sky130_fd_pr__{m}_g5v0d10v5 L={geo['L']} W={geo['W']} nf=1 m=1"]
    ctl = f"op\nprint @m.xm.msky130_fd_pr__{m}_g5v0d10v5[gm]\nprint v(d)"
    v, _, _ = sim.run("\n".join(L), ctl, corner, temp)
    gm = v[f"@m.xm.msky130_fd_pr__{m}_g5v0d10v5[gm]"]
    return i_d / gm, v["v(d)"]


def _rsq(corner, temp):
    L = ["V1 a 0 1.0", "XR 0 a 0 sky130_fd_pr__res_xhigh_po_0p35 L=100 mult=1 m=1"]
    v, _, _ = sim.run("\n".join(L), "op\nprint i(V1)", corner, temp)
    return 1.0 / abs(v["i(v1)"]) / 100.0           # ohm per um


def measure(corner="tt", temp=27.0, force=False):
    path = os.path.join(HERE, f"tech_{corner}_{int(temp)}.json")
    if os.path.exists(path) and not force:
        return json.load(open(path))
    if force or not os.path.exists(path):
        _base(corner, temp, path)
    return json.load(open(path))


def _base(corner, temp, path):
    import tb_bias
    b = tb_bias.run(corner, temp, 1)
    iu = b["nbias"]
    nut_n, vgs_e = _slope("n", units.SM_E, iu, corner, temp)
    nut_p, vdcol = _slope("p", units.MC, iu, corner, temp)
    # key-write calibration: the cell gain I_cell / I_Q at V_w = 0 (DDA systematic offset, ~9 mV); the firmware
    # writes h with + nU_T,p ln(gain0) (per-cell calibration on silicon; one value per corner here)
    out = dict(corner=corner, temp=temp, I_u=iu, cell_gain0=1.0, vr=b["vr"], vcas=b["vcas"], vbn=b["vbn"], vmid=b["vmid"],
               nUT_n=nut_n, nUT_p=nut_p, vgs_e=vgs_e, dcol=vdcol, R_per_um=_rsq(corner, temp))
    json.dump(out, open(path, "w"), indent=1)
    import tb_keycell                                # needs dcol from the file just written
    kc = tb_keycell.run(corner, temp)
    out["cell_gain0"] = float(np.mean(kc["gain0"]))
    out["nUT_p_cell"] = float(np.mean(kc["nUT_fit"]))       # in-cell slope of the key law (fit over V_w)
    json.dump(out, open(path, "w"), indent=1)


if __name__ == "__main__":
    for c, T in CORNERS:
        m = measure(c, T, force=True)
        print(f"{c} {T:5.0f} C: I_u {m['I_u']*1e9:6.1f} nA  vr {m['vr']:.3f}  vcas {m['vcas']:.3f}  vbn {m['vbn']:.3f}  "
              f"vmid {m['vmid']:.3f}  nU_T,n {m['nUT_n']*1e3:.1f} mV  nU_T,p {m['nUT_p']*1e3:.1f} mV  "
              f"dcol {m['dcol']:.3f} V  cell gain {m['cell_gain0']:.3f}  R {m['R_per_um']/1e3:.2f} kOhm/um")
