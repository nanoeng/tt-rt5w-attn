"""gm/ID characterisation of the sky130 3.3 V-class devices (Jespers & Murmann look-up tables, as in H. Pretl's
JKU course "Analog Circuit Design", ch. 3 "Transistor sizing using the gm/ID methodology": a MOSFET
characterisation testbench sweeps V_GS, V_DS and L at fixed W and stores the small-signal parameters).

    pixi run -e pd python gmid/techsweep.py        -> gmid/lut_<dev>_<corner>_<T>.npz
Device: sky130_fd_pr__nfet_g5v0d10v5 / pfet_g5v0d10v5 (gate oxide for 5 V, used at 3.3 V: the RT5W analog supply).
Stored per (L, VDS, VGS): id, gm, gds, gmb, cgg, cgs, cgd, vth (W = 10 um, VSB = 0, |values| for the PMOS)."""
import os
import subprocess
import sys
import tempfile

import numpy as np

PDK = os.environ.get("PDK_ROOT", "/home/claude/ext/pdk") + "/sky130A"
LIB = PDK + "/libs.tech/combined/sky130.lib.spice"
HERE = os.path.dirname(os.path.abspath(__file__))
W = 10.0
LS = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]
VGS = np.round(np.arange(0.0, 3.3001, 0.01), 3)
VDS = np.round(np.arange(0.05, 3.3001, 0.05), 3)
PARAMS = ["id", "gm", "gds", "gmbs", "cgg", "cgs", "cgd", "vth"]
DEV = {"n": "sky130_fd_pr__nfet_g5v0d10v5", "p": "sky130_fd_pr__pfet_g5v0d10v5"}


def sweep(kind, L, corner="tt", temp=27.0, vsb=0.0):
    s = 1 if kind == "n" else -1
    dev = DEV[kind]
    path = f"@m.xm1.m{dev}"
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "o.txt")
        net = f"""* techsweep {dev} L={L}
.lib {LIB} {corner}
.temp {temp}
.option gmin=1e-15
Vg g 0 0
Vd d 0 0
Vb b 0 {-s * vsb}
XM1 d g 0 b {dev} W={W} L={L} nf=1
.control
save {' '.join(f'{path}[{p}]' for p in PARAMS)}
dc Vg 0 {s * 3.3} {s * 0.01} Vd {s * 0.05} {s * 3.3} {s * 0.05}
wrdata {out} {' '.join(f'{path}[{p}]' for p in PARAMS)}
.endc
.end
"""
        sp = os.path.join(td, "t.sp")
        open(sp, "w").write(net)
        r = subprocess.run(["ngspice", "-b", sp], capture_output=True, text=True)
        d = np.loadtxt(out)
    vals = d[:, 1::2]                                   # wrdata: (x, y) pairs
    nv, ng = len(VDS), len(VGS)
    vals = vals.reshape(nv, ng, len(PARAMS))
    return {p: np.abs(vals[:, :, k]) if p in ("id", "gm", "gmbs", "cgg", "cgs", "cgd") else
            (vals[:, :, k] if p != "vth" else np.abs(vals[:, :, k])) for k, p in enumerate(PARAMS)}


def build(kind, corner="tt", temp=27.0):
    tabs = {p: [] for p in PARAMS}
    for L in LS:
        r = sweep(kind, L, corner, temp)
        for p in PARAMS:
            tabs[p].append(r[p])
    out = os.path.join(HERE, f"lut_{kind}_{corner}_{int(temp)}.npz")
    np.savez_compressed(out, L=np.array(LS), VGS=VGS, VDS=VDS, W=W, device=DEV[kind], corner=corner, temp=temp,
                        **{p: np.array(v) for p, v in tabs.items()})
    return out


if __name__ == "__main__":
    for kind in sys.argv[1:] or ["n", "p"]:
        for corner, T in (("tt", 27), ("ss", -40), ("ff", 125)):
            print(build(kind, corner, T), flush=True)
