"""Device sizing for the sky130 schematics: every analog device's W and L come from here, i.e. from the gm/ID
look-up tables (gmid/techsweep.py -> lut_*.npz; Jespers & Murmann 2017) and the PDK mismatch model (gmid/mismatch.py
-> A_VT), never from a guess.  A block calls

    dev("n", i_d, ("sigma_i", 0.03))     ratio device (mirror / DAC / IDAC unit): sigma(I)/I target
    dev("p", i_d, ("vos", 0.010))        pair / comparator device: input-offset target (sigma)
    dev("n", i_d, ("gmid", 12), L=1)     explicit gm/ID (e.g. a cascode in moderate inversion for headroom)
    dev("n", i_d, ("vt", 0.0023))        single device whose V_T error matters directly (exponentiator)
    dev("n", 0, ("min",))                switch / logic: minimum 3.3 V device (W = 2 W_min, L = L_min)

and gets dict(W, L) in um.  Policy (owner rule, 19 Nov 2026): every ratio / pair device in weak inversion, i.e.
gm/ID = 0.9 x gm/ID(1 nA/um) at its L (wi_target).  For each candidate L in L_TRY the width follows from the
LUT current density at that gm/ID; the Pelgrom area W L >= (gm/ID A_VT / sigma)^2 then widens the device (deeper weak
inversion; gm/ID re-read at the final density); the smallest gate area wins.  Every call is logged; report() prints the table that goes into
the design report (device, current, spec, gm/ID, W, L, V_GS)."""
import functools
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "gmid"))
from lookup import Lut  # noqa: E402

AVT = {"n": 8.70e-3, "p": 12.5e-3}          # V.um: gmid/mismatch.py (PDK MC_MM_SWITCH=1)
W_MIN, L_MIN = 0.42, 0.5
L_TRY = (0.5, 1.0, 2.0, 4.0, 8.0)
LOG = []
POLICY = os.environ.get("RT5W_POLICY", "wi")    # wi: every ratio/pair device in weak inversion (stored rule)


@functools.lru_cache(maxsize=None)
def _lut(kind):
    return Lut(kind, "tt", 27)


@functools.lru_cache(maxsize=None)
def _size(kind, i_d, spec, L_fix, vds):
    if spec[0] == "min":
        return dict(W=2 * W_MIN, L=L_MIN, gm_id=None, vgs=None)
    lut = _lut(kind)
    best = None
    for L in ((L_fix,) if L_fix else L_TRY):
        gm_id = spec[1] if spec[0] == "gmid" else lut.wi_target(L, vds)
        if POLICY == "mi" and spec[0] == "sigma_i":     # ratio devices in moderate inversion (owner decision pending)
            gm_id = min(gm_id, 11.0)
        try:
            op = lut.at(gm_id, L, vds)
        except ValueError:
            continue
        if spec[0] == "sigma_i":
            wl = (gm_id * AVT[kind] / spec[1]) ** 2
        elif spec[0] == "vt":
            wl = (AVT[kind] / spec[1]) ** 2           # single device: sigma(V_T) = A_VT / sqrt(WL)
        elif spec[0] == "vos":
            wl = 2 * (AVT[kind] / spec[1]) ** 2       # pair: sigma(V_os) = sqrt(2) A_VT / sqrt(WL)
        else:
            wl = 0.0
        w_cur = i_d / op["id_w"] if i_d > 0 else W_MIN
        W, g = max(W_MIN, w_cur), gm_id
        for _ in range(4):                            # W beyond w_cur runs the device deeper in weak inversion:
            wl_g = wl * (g / gm_id) ** 2 if spec[0] == "sigma_i" else wl   # re-evaluate gm/ID at the real density
            W = max(W_MIN, w_cur, wl_g / L)
            g = lut.gm_id_at_density(i_d / W, L, vds) if i_d > 0 else gm_id
        Lf = L
        gm_id = g
        cand = dict(W=round(W, 2), L=round(Lf, 2), gm_id=round(gm_id, 1), vgs=round(op["vgs"], 3), wl=W * Lf,
                    fp=(W + 1.6) * (Lf + 0.8))   # finger height incl. gate contact; finger pitch incl. strip
        # pick the L with the smallest drawn footprint (gate area plus the source/drain strips and gate
        # extensions), not the smallest W L: long thin devices waste row height and router stubs
        if best is None or cand["fp"] < best["fp"]:
            best = cand
    if best is None:
        raise ValueError(f"no L meets {spec} for {kind} at {i_d:.3g} A")
    return best


def dev(kind, i_d, spec, L=None, vds=1.0, tag=""):
    r = dict(_size(kind, float(i_d), tuple(spec), L, vds))
    LOG.append((tag, kind, i_d, spec, r))
    return dict(W=r["W"], L=r["L"])


def report():
    seen, out = set(), []
    for tag, kind, i_d, spec, r in LOG:
        key = (tag, kind, i_d, spec)
        if key in seen:
            continue
        seen.add(key)
        gi = f"{r['gm_id']:5.1f}" if r["gm_id"] else "  -  "
        out.append(f"{tag:28s} {kind}  I_D {i_d * 1e9:8.2f} nA  {str(spec):24s} gm/ID {gi}  W {r['W']:6.2f}  "
                   f"L {r['L']:5.2f}  V_GS {r['vgs'] if r['vgs'] is not None else '-'}")
    return "\n".join(out)


if __name__ == "__main__":
    print(dev("n", 125e-9 / 15, ("sigma_i", 0.03), tag="idac unit"))
    print(dev("p", 125e-9, ("sigma_i", 0.03), tag="pmos dist"))
    print(dev("n", 31e-9, ("vos", 0.01), tag="dda pair"))
    print(report())
