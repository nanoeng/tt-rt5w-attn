"""gm/ID sizing of every RT5W device group for sky130 (3.3 V devices) and the resulting area budget.

Method (Jespers & Murmann 2017; Pretl, JKU Analog Circuit Design, ch. 3):
  1. the operating current of each group comes from the architecture (I_u = 125 nA, I_LSB = I_u / 15, ...);
  2. its role sets the governing spec: a ratio device (mirror, DAC unit) is sized for sigma(I)/I, a pair for its
     offset, an exponential device for the error it adds to the score x, a switch for nothing but minimum size;
  3. gm/ID is read from the look-up table at the chosen L (the weak-inversion plateau, or a lower value where the
     policy allows moderate inversion for ratio devices), the mismatch gives the gate area
     W L >= (gm/ID * A_VT / sigma_target)^2 (Pelgrom; A_VT from mismatch.py, i.e. the PDK mismatch model),
     and the LUT current density at that gm/ID gives W/L, from which W and L follow;
  4. the device footprint (diffusion ends, contacts) and a layout utilisation turn gate area into block area.
Every number printed is traceable to: the LUT (techsweep.py), A_VT (mismatch.py) or the spec column below."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lookup import Lut  # noqa: E402

AVT = {"n": 8.70e-3, "p": 12.5e-3}          # V.um, mismatch.py (PDK MC_MM_SWITCH=1, 300 copies, 5 sizes)
I_U = 125e-9
W_MIN, L_MIN = 0.42, 0.5                     # 5 V devices (g5v0d10v5)
UTIL = 0.33                                  # device footprint / block area (this flow's layouts: 0.10..0.38)

# role, kind, current per device (A), count, spec: ('sigma_i', x) | ('vos', V) | ('min',) ; note
GROUPS = [
    ("bias", "beta-multiplier core + mirrors", "n", 4 * I_U, 12, ("sigma_i", 0.05), "absolute I_u is trimmed by PTAT/R tracking, 5 % copies"),
    ("bias", "PMOS distribution", "p", I_U, 14, ("sigma_i", 0.03), "copies of I_u to IDACs, DAC, softmax"),
    ("bias", "cascode/start-up/switches", "n", I_U, 10, ("min",), "not ratio-critical"),
    ("idac", "column IDAC units (4 x 15)", "n", I_U / 15, 60, ("sigma_i", 0.03), "unit error < 0.5 LSB of 4 bit at 3 sigma ~ 1 unit"),
    ("idac", "IDAC switches", "n", I_U, 64, ("min",), ""),
    ("array", "column diodes (4)", "p", 15 * I_U / 15, 4, ("sigma_i", 0.05), "cell gains are calibrated per cell by the key write"),
    ("array", "array PMOS Mc (16)", "p", I_U, 16, ("sigma_i", 0.05), "per-cell gain error is absorbed by the calibrated key write"),
    ("array", "key-cell DDA pairs (16 x 4)", "n", I_U / 4, 64, ("vos", 0.010), "offset calibrated per cell; 10 mV keeps k in range"),
    ("array", "key-cell DDA loads/tails (16 x 4)", "p", I_U / 4, 64, ("vos", 0.010), ""),
    ("array", "key storage caps (16 + 4)", "cap", 0, 20, ("cap", 0.5e-12), "droop < 1 LSB over a pass (hold leakage)"),
    ("array", "write TGs, inverters, pumps", "n", 0, 120, ("min",), ""),
    ("kscale", "key-scale mirrors (4 x 32)", "n", I_U / 4, 128, ("sigma_i", 0.03), "row gain error is trimmed by SS-SGD"),
    ("softmax", "exponentiators Me (4)", "n", I_U, 4, ("vos", 0.0023), "dx = sigma/nU_T <= 0.05 e-fold"),
    ("softmax", "PMOS diodes + x4 outputs (4 x 20 units)", "p", 0.1e-6, 80, ("sigma_ratio", 0.02, 4), "share error <= 2 % (~2.5 LSB at a = 1)"),
    ("softmax", "tail, cascodes, keep-alive", "n", 4 * I_U, 12, ("sigma_i", 0.05), ""),
    ("readout", "DAC units (271)", "n", I_U / 16, 271, ("sigma_i", 0.05), "binary DAC: MSB/LSB ratio error < 0.5 LSB needs ~5 % per unit"),
    ("readout", "DAC cascodes / switches / mux", "n", I_U / 16, 300, ("min",), ""),
    ("readout", "StrongARM + SR latch", "n", 0, 20, ("vos", 0.006), "half-LSB integrated signal ~13 mV, 2 sigma"),
    ("vbbuf", "V_B buffer", "n", 4 * I_U, 15, ("vos", 0.005), "absorbed by VBCAL; 5 mV"),
]


def size_group(kind, i_d, spec, policy):
    if kind == "cap":
        c = spec[1]
        area = c / 4.6e-15 * 1.0                     # MOS cap, C_ox(5 V oxide, ~12 nm) ~ 4.6 fF/um2 (LUT cgg/WL at L = 8)
        return dict(W=math.sqrt(area), L=math.sqrt(area), gm_id=None, wl=area)
    if spec[0] == "min" or i_d == 0 and spec[0] != "vos":
        return dict(W=W_MIN * 2, L=L_MIN, gm_id=None, wl=W_MIN * 2 * L_MIN)
    lut = LUTS[kind]
    L_try = [1.0, 2.0, 4.0, 8.0]
    best = None
    for L in L_try:
        plateau = lut.gm_id_at_density(1e-9, L, 1.0)
        gm_id = lut.wi_target(L) if (policy == "wi" or spec[0] == "vos") else min(lut.wi_target(L), 11.0)
        try:
            op = lut.at(gm_id, L, 1.0)
        except ValueError:
            continue
        if spec[0] == "sigma_i":
            wl = (gm_id * AVT[kind] / spec[1]) ** 2
        elif spec[0] == "sigma_ratio":                  # n_out units vs 1 diode unit set: sigma^2 = s_u^2 (1/n + 1)
            n = spec[2]
            wl = (gm_id * AVT[kind] / spec[1]) ** 2 * (1 + 1.0 / n) / n * 1.0
        else:                                           # pair offset: sqrt(2) A_VT / sqrt(WL)
            wl = 2 * (AVT[kind] / spec[1]) ** 2
        if i_d > 0:
            w_cur = i_d / op["id_w"]                    # width that puts i_d at this gm/ID
        else:
            w_cur = W_MIN
        W = max(W_MIN, w_cur, wl / L)
        Lf = max(L, wl / W)
        # W > w_cur means the device runs deeper in weak inversion than gm_id (fine: gm/ID only rises)
        cand = dict(W=round(W, 2), L=round(Lf, 2), gm_id=round(gm_id, 1), wl=W * Lf, plateau=round(plateau, 1),
                    inversion="weak" if gm_id >= 0.85 * plateau else "moderate")
        cand["vgs"] = round(op["vgs"], 3)
        if best is None or cand["wl"] < best["wl"]:
            best = cand
    return best


def footprint(W, L):
    return (W + 0.9) * (L + 1.1)             # 5 V device: diffusion/contacts both sides, poly end caps (estimate)


def budget(policy):
    rows, tot = [], 0.0
    for blk, name, kind, i_d, cnt, spec, note in GROUPS:
        s = size_group(kind, i_d, spec, policy)
        fp = footprint(s["W"], s["L"]) * cnt
        tot += fp
        rows.append((blk, name, kind, cnt, s, fp, note))
    return rows, tot


LUTS = {"n": Lut("n"), "p": Lut("p")}

if __name__ == "__main__":
    tiles = {"sky130 2x2 (3v3)": 319.24 * 225.76, "sky130 4x2 (3v3)": 667.0 * 225.76}
    digital = 12663 / 0.6                         # yosys sky130_fd_sc_hd, 1175 cells, 60 % utilisation
    shifters = 70 * 30.0                          # ~70 lv->hv level shifters (sky130_fd_sc_hvl lsbuflv2hv), est.
    for policy, label in (("wi", "all devices at the weak-inversion plateau (stored rule)"),
                          ("mixed", "ratio devices allowed gm/ID = 11 (moderate inversion)")):
        rows, tot = budget(policy)
        print(f"\n=== policy: {label}")
        for blk, name, kind, cnt, s, fp, note in rows:
            gi = f"gm/ID {s['gm_id']}" if s.get("gm_id") else "min/cap"
            print(f"  {blk:8s} {name:42s} {cnt:4d} x {kind} W {s['W']:6.2f} L {s['L']:6.2f}  {gi:12s} "
                  f"{s.get('inversion',''):9s} footprint {fp:8.0f} um2")
        analog = tot / UTIL
        print(f"  device footprint {tot:.0f} um2 -> analog blocks at {UTIL:.0%} utilisation {analog:.0f} um2")
        for t, a in tiles.items():
            need = analog + digital + shifters
            print(f"  {t}: tile {a:.0f} um2; analog {analog:.0f} + digital {digital:.0f} + shifters {shifters:.0f} "
                  f"= {need:.0f} um2 -> {need / a:.2f} x the tile")
