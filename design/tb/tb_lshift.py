"""Level shifters (design/blocks/lshift.py) at corners: static levels and 50 %-crossing delays for a 1 MHz input,
vddl 1.62 / 1.98 V, vddh 3.0 / 3.6 V, 50 fF load (about 300 um of met3 plus a gate)."""
import numpy as np

import sim


def run_up(corner, temp, vddl, vddh):
    body = [f"Vl vddl 0 {vddl}", f"Vh vdd 0 {vddh}", "Vs vss 0 0",
            f"Vin in 0 PULSE(0 {vddl} 100n 1n 1n 499n 1u)", "Cl out 0 50f",
            sim.inst("X1", "rt5w_lsup", **{"in": "in", "out": "out", "vddl": "vddl", "vdd": "vdd", "vss": "vss"})]
    ctl = (f"tran 1n 1.2u\nmeas tran tr when v(out)={vddh / 2} rise=1\nmeas tran tf when v(out)={vddh / 2} fall=1\n"
           f"meas tran vhi find v(out) at=500n\nmeas tran vlo find v(out) at=1.1u\n"
           f"meas tran iq avg i(Vh) from=300n to=550n\n"
           "print tr tf vhi vlo iq")
    v, _, _ = sim.run("\n".join(body), ctl, corner, temp, blocks=["rt5w_lsup"])
    return dict(t_rise=v["tr"] - 100e-9, t_fall=v["tf"] - 600e-9, vhi=v["vhi"], vlo=v["vlo"], iq=-v["iq"])


def run_dn(corner, temp, vddl, vddh):
    body = [f"Vl vddl 0 {vddl}", "Vs vss 0 0", f"Vin in 0 PULSE(0 {vddh} 100n 1n 1n 499n 1u)", "Cl out 0 20f",
            sim.inst("X1", "rt5w_lsdn", **{"in": "in", "out": "out", "vddl": "vddl", "vss": "vss"})]
    ctl = (f"tran 1n 1.2u\nmeas tran tr when v(out)={vddl / 2} rise=1\nmeas tran tf when v(out)={vddl / 2} fall=1\n"
           "meas tran vhi find v(out) at=500n\nmeas tran vlo find v(out) at=1.1u\nprint tr tf vhi vlo")
    v, _, _ = sim.run("\n".join(body), ctl, corner, temp, blocks=["rt5w_lsdn"])
    return dict(t_rise=v["tr"] - 100e-9, t_fall=v["tf"] - 600e-9, vhi=v["vhi"], vlo=v["vlo"])


if __name__ == "__main__":
    for c in ("tt", "ss", "ff", "sf", "fs"):
        for T in (-40, 27, 125):
            for vl, vh in ((1.62, 3.6), (1.98, 3.0)):
                u, d = run_up(c, T, vl, vh), run_dn(c, T, vl, vh)
                print(f"{c} {T:4d} vddl {vl} vddh {vh} | up: tr {u['t_rise']*1e9:5.2f} tf {u['t_fall']*1e9:5.2f} ns "
                      f"hi {u['vhi']:.3f} lo {u['vlo']:.3f} | dn: tr {d['t_rise']*1e9:5.2f} tf {d['t_fall']*1e9:5.2f} ns "
                      f"hi {d['vhi']:.3f} lo {d['vlo']:.3f}", flush=True)


def run_lib(cell, corner, temp, vddl, vddh, load=50e-15):
    """sky130_fd_sc_hvl level shifters (ports A LVPWR VGND VNB VPB VPWR X): lsbuflv2hv_1 (up), lsbufhv2lv_1 (down)."""
    up = cell.endswith("lsbuflv2hv_1")
    vin, vout = (vddl, vddh) if up else (vddh, vddl)
    body = [f"Vl lv 0 {vddl}", f"Vh hv 0 {vddh}", f"Vin a 0 PULSE(0 {vin} 100n 1n 1n 499n 1u)", f"Cl x 0 {load}",
            f"X1 a lv 0 0 hv hv x {cell}"]    # VPB = VPWR (HV) in both cells
    ctl = (f"tran 0.1n 1.2u\nmeas tran tr when v(x)={vout / 2} rise=1\nmeas tran tf when v(x)={vout / 2} fall=1\n"
           "meas tran vhi find v(x) at=500n\nmeas tran vlo find v(x) at=1.1u\n"
           "meas tran ih avg i(Vh) from=300n to=550n\nprint tr tf vhi vlo ih")
    v, _, _ = sim.run("\n".join(body), ctl, corner, temp, blocks=[cell])
    return dict(t_rise=v["tr"] - 100e-9, t_fall=v["tf"] - 600e-9, vhi=v["vhi"], vlo=v["vlo"], i_hv=-v["ih"])
