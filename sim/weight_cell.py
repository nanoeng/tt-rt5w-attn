"""Rev-3 weight (C_W) cell at the 20 MHz clock: pump I_P = 0.37 nA for one 50 ns clock -> 0.184 mV on 100 fF.
UP: PMOS source (mirror, I_P) + PMOS switch; DN: NMOS switch + NMOS sink (I_P). Write switch to ua[2] (V_W pin) open.
Measures: mean UP / DN step, asymmetry, droop with the switches off (gmin 1e-15, BSIM leakage)."""
import json
import numpy as np
from rt5w_ng import MODELS, run

IP = 3.7e-9      # one 50 ns clock -> 185 fC -> 0.185 mV on 1 pF
CW = 1e-12       # 1 pF (MOS cap ~230 um^2 if MIM is unavailable on TT GF)


def netlist(corner="tt", T=27, n_up=20, n_dn=20, tper=1e-6):
    lib = {"tt": "typical"}.get(corner, corner)
    L = ["* weight cell", f".include {MODELS}/design.ngspice", f".lib {MODELS}/sm141064.ngspice {lib}", f".temp {T}",
         "Vdd vdd 0 3.3",
         # UP source: PMOS mirror of I_P (reference diode fed by ideal I_P), switch PMOS, all minimum-ish
         f"Ipr pg 0 {IP:.4e}", "Mpr pg pg vdd vdd pmos_3p3 w=1u l=4u", "Mpu pu pg vdd vdd pmos_3p3 w=1u l=4u",
         "Msu w upb pu vdd pmos_3p3 w=0.5u l=0.5u",
         "Msub vmid up pu vdd pmos_3p3 w=0.5u l=0.5u",        # steering: off-current goes to V_mid (cell-voltage replica)
         f"Inr vdd ng {IP:.4e}", "Mnr ng ng 0 0 nmos_3p3 w=1u l=4u", "Mnd nd ng 0 0 nmos_3p3 w=1u l=4u",
         "Msd w dn nd 0 nmos_3p3 w=0.5u l=0.5u",
         "Msdb vmid dnb nd 0 nmos_3p3 w=0.5u l=0.5u",
         "Vmid vmid 0 1.65",
         # dummy-free write switch to the V_W pin (off: gate 0), transmission gate
         "Mwn w 0 vwpin 0 nmos_3p3 w=0.5u l=0.5u", "Mwp w vdd vwpin vdd pmos_3p3 w=0.5u l=0.5u", "Vwpin vwpin 0 1.65",
         f"Cw w 0 {CW}", ".ic v(w)=1.65",
         # cell transistor gate load (PMOS cell gate of the array, 16u/4u x2)
         "Mcell 0 w vdd vdd pmos_3p3 w=16u l=4u m=2"]
    t0 = 2e-6
    pu, pd = [], []
    for i in range(n_up):
        t = t0 + i * tper
        pu += [f"{t:.4e} 3.3 {t+1e-9:.4e} 0 {t+51e-9:.4e} 0 {t+52e-9:.4e} 3.3"]
    for i in range(n_dn):
        t = t0 + (n_up + i) * tper
        pd += [f"{t:.4e} 0 {t+1e-9:.4e} 3.3 {t+51e-9:.4e} 3.3 {t+52e-9:.4e} 0"]
    inv = lambda pts: " ".join(" ".join(f"{a} {3.3-float(b):g}" if j % 2 else a for j, a in enumerate([]) ) for _ in [])
    L += ["Vup upb 0 PWL(0 3.3 " + " ".join(pu) + ")", "Vdn dn 0 PWL(0 0 " + " ".join(pd) + ")",
          "Bup up 0 V=3.3-v(upb)", "Bdnb dnb 0 V=3.3-v(dn)"]
    tend = t0 + (n_up + n_dn) * tper + 1e-6
    L += [".control", "option gmin=1e-15 method=gear maxord=2", f"tran 2n {tend:.4e}",
          "wrdata __OUT__ v(w)", ".endc", ".end"]
    return "\n".join(L), t0, tper, n_up, n_dn


def steps(corner="tt", T=27):
    nl, t0, tp, nu, nd = netlist(corner, T)
    _, d = run(nl, timeout=1200)
    t, v = d[:, 0], d[:, 1]
    samp = np.array([np.interp(t0 + i * tp - 0.1e-6, t, v) for i in range(nu + nd + 1)])
    s = np.diff(samp) * 1e3
    return float(s[:nu].mean()), float(s[nu:].mean()), s


def droop(corner="tt", T=27, vw=(1.2, 1.65, 2.1)):
    out = []
    for v0 in vw:
        nl = "\n".join(["* droop", f".include {MODELS}/design.ngspice", f".lib {MODELS}/sm141064.ngspice {'typical' if corner=='tt' else corner}",
                        f".temp {T}", "Vdd vdd 0 3.3", "Vupb upb 0 3.3", "Vdn dn 0 0",
                        f"Ipr pg 0 {IP:.4e}", "Mpr pg pg vdd vdd pmos_3p3 w=1u l=4u", "Mpu pu pg vdd vdd pmos_3p3 w=1u l=4u",
                        "Msu w upb pu vdd pmos_3p3 w=0.5u l=0.5u",
                        f"Inr vdd ng {IP:.4e}", "Mnr ng ng 0 0 nmos_3p3 w=1u l=4u", "Mnd nd ng 0 0 nmos_3p3 w=1u l=4u",
                        "Msd w dn nd 0 nmos_3p3 w=0.5u l=0.5u",
                        "Mwn w 0 vwpin 0 nmos_3p3 w=0.5u l=0.5u", "Mwp w vdd vwpin vdd pmos_3p3 w=0.5u l=0.5u", "Vwpin vwpin 0 1.65",
                        f"Cw w 0 {CW}", f".ic v(w)={v0}", "Mcell 0 w vdd vdd pmos_3p3 w=16u l=4u m=2",
                        ".control", "option gmin=1e-15 method=gear maxord=2", "tran 10u 10m uic",
                        "meas tran v1 find v(w) at=1m", "meas tran v2 find v(w) at=10m", ".endc", ".end"])
        txt, _ = run(nl, timeout=1200)
        import re
        v1 = float(re.search(r"v1\s*=\s*([-+0-9.eE]+)", txt).group(1)); v2 = float(re.search(r"v2\s*=\s*([-+0-9.eE]+)", txt).group(1))
        out.append(dict(v0=v0, droop_uV_per_ms=(v2 - v1) / 9e-3 * 1e-3 * 1e6))
    return out


if __name__ == "__main__":
    R = {}
    for c, T in (("tt", 27), ("ss", -40), ("ff", 125), ("sf", 27), ("fs", 27)):
        up, dn, s = steps(c, T)
        R[f"{c}_{T}"] = dict(up_mV=up, dn_mV=dn, asym_pct=float((abs(up) - abs(dn)) / ((abs(up) + abs(dn)) / 2) * 100))
        print(c, T, R[f"{c}_{T}"])
    D_ = {f"{c}_{T}": droop(c, T) for c, T in (("tt", 27), ("ff", 125))}
    print(json.dumps(D_, indent=1))
    json.dump(dict(I_pump_nA=IP * 1e9, C_W_fF=CW * 1e15, pulse_ns=50, steps=R, droop=D_), open("results/weight_cell.json", "w"), indent=1)
