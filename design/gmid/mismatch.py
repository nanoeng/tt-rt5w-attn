"""Pelgrom coefficient A_VT of the sky130 5 V-class devices from the PDK's own mismatch model
(MC_MM_SWITCH = 1): N diode-connected copies biased at the same weak-inversion current density, one .op,
sigma(V_GS) across the copies; A_VT = sigma * sqrt(W L). This is the matching reference used for sizing."""
import os
import subprocess
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from techsweep import DEV, LIB  # noqa: E402

N = 300


def sigma_vgs(kind, W, L, j=1e-9, seed=1):
    """sigma(V_GS) of N copies at I = j * W/L (weak inversion for j ~ 1 nA)."""
    dev = DEV[kind]
    i = j * W / L
    L_ = [f"* mm", f".lib {LIB} tt", ".param MC_MM_SWITCH=1", ".option gmin=1e-15 seed=%d" % seed, ".temp 27"]
    for k in range(N):
        if kind == "n":
            L_ += [f"I{k} 0 g{k} {i:.4e}", f"XM{k} g{k} g{k} 0 0 {dev} W={W} L={L} nf=1"]
        else:
            L_ += [f"I{k} g{k} 0 {i:.4e}", f"XM{k} g{k} g{k} vdd vdd {dev} W={W} L={L} nf=1"]
    L_ += ["Vdd vdd 0 3.3", ".control", "op"] + [f"print v(g{k})" for k in range(N)] + [".endc", ".end"]
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "m.sp")
        open(p, "w").write("\n".join(L_))
        r = subprocess.run(["ngspice", "-b", p], capture_output=True, text=True)
    v = np.array([float(l.split("=")[1]) for l in r.stdout.splitlines() if l.strip().startswith("v(g")])
    return float(np.std(v)), len(v)


if __name__ == "__main__":
    rows = []
    for kind in ("n", "p"):
        for W, L in ((1, 1), (2, 2), (4, 4), (2, 8), (8, 2)):
            s, n = sigma_vgs(kind, W, L)
            rows.append((kind, W, L, s, s * np.sqrt(W * L)))
            print(f"{kind}fet W={W} L={L}: sigma(VGS) {s*1e3:.2f} mV (N={n})  A_VT = {s*np.sqrt(W*L)*1e3:.2f} mV.um", flush=True)
    np.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "avt.npy"), np.array(rows, dtype=object))
