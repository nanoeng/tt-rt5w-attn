"""Translinear array cell (gf180mcuD, weak inversion): I_out = I_Q * I_K / I_ref * exp(V_w / nU_T).
Stacked loop: Q1 (diode, I_Q, source 0) + Q2 (diode, I_K, source on g1) = Q3 (follower, I_ref sink) + Q4 (output).
Q2 and Q3 have floating sources -> each in its own DNWELL pocket with p-well tied to source (no body effect).
V_w enters as a gate offset on Q4 (the C_W cell sits in series with Q4's gate).
Variants: 'iso' (Q2/Q3 bulk = source) vs 'sub' (all bulks at 0) reproduces the shared-substrate failure."""
import json, itertools, sys
import numpy as np
from multiprocessing import Pool
from rt5w_ng import MODELS, run, parse_print, AVT_N

CELL = dict(W=20.0, L=2.0, m=4)     # unit NMOS (all four devices equal); sizes checked by gm/ID audit below


def netlist(IQ, IK, Iref, Vw, corner="tt", T=27, iso=True, mm=None, vdd=3.3):
    mm = mm or {}
    b2 = "g1" if iso else "0"
    b3 = "y" if iso else "0"
    W, L, m = CELL["W"], CELL["L"], CELL["m"]
    lib = {"tt": "typical"}.get(corner, corner)
    return "\n".join([
        f"* tl cell", f".include {MODELS}/design.ngspice", f".lib {MODELS}/sm141064.ngspice {lib}", f".temp {T}",
        f"Vdd vdd 0 {vdd}",
        f"Iq vdd g1 {IQ:.6e}", f"Vm1 g1 g1m {mm.get('q1',0):.6e}", f"Mq1 g1 g1m 0 0 nmos_3p3 w={W}u l={L}u m={m}",
        f"Ik vdd g2 {IK:.6e}", f"Vm2 g2 g2m {mm.get('q2',0):.6e}", f"Mq2 g2 g2m g1 {b2} nmos_3p3 w={W}u l={L}u m={m}",
        f"Vm3 g2 g3m {mm.get('q3',0):.6e}", f"Mq3 vdd g3m y {b3} nmos_3p3 w={W}u l={L}u m={m}",
        f"Ir y 0 {Iref:.6e}",
        f"Vw g4 y {Vw + mm.get('q4',0):.6e}", f"Mq4 out g4 0 0 nmos_3p3 w={W}u l={L}u m={m}",
        f"Vo vdd out 0",   # row line held near VDD-? -> output measured into a 2.0 V node below
        ".control", "op",
        "print i(vo) v(g1) v(g2) v(y) @mq1[gm] @mq1[id] @mq2[gm] @mq2[id] @mq3[gm] @mq3[id] @mq4[gm] @mq4[id] @mq4[vds]",
        ".endc", ".end"]).replace("Vo vdd out 0", "Vo vrow out 0\nVrow vrow 0 2.0")


def cell(IQ, IK, Iref, Vw, **kw):
    v = parse_print(run(netlist(IQ, IK, Iref, Vw, **kw))[0])
    return -v["i(vo)"], v


NUT = 37.5e-3
LSB_Q = 50e-9          # proposed: 0.5 uA LSB of record scaled 10x down
IREF = 0.5e-6


def sweep(args):
    corner, T, iso = args
    ptat = (T + 273.15) / 300.15
    errs = []
    for cq, ck, vw in itertools.product([1, 4, 8, 15], [1, 4, 8, 15], [-0.06, 0.0, 0.06]):
        IQ, IK, Ir = cq * LSB_Q * ptat, ck * LSB_Q * ptat, IREF * ptat
        I, _ = cell(IQ, IK, Ir, vw * ptat, corner=corner, T=T, iso=iso)
        ideal = IQ * IK / Ir * np.exp(vw * ptat / (NUT * ptat))
        errs.append(I / ideal - 1)
    e = np.array(errs)
    return dict(corner=corner, T=T, iso=iso, max_err_pct=float(np.abs(e).max() * 100), mean_err_pct=float(e.mean() * 100),
                spread_pct=float((e.max() - e.min()) * 100))


if __name__ == "__main__":
    # gm/ID audit at the largest product
    I, v = cell(15 * LSB_Q, 15 * LSB_Q, IREF, 0.06)
    audit = {d: v[f"@m{d}[gm]"] / abs(v[f"@m{d}[id]"]) for d in ("q1", "q2", "q3", "q4")}
    print("gm/ID at full scale:", {k: round(x, 1) for k, x in audit.items()}, "I_out uA", round(I * 1e6, 3))
    jobs = [(c, T, iso) for iso in (True, False) for c, T in (("tt", 27), ("ss", -40), ("ff", 125), ("sf", 27), ("fs", 27))]
    with Pool(2) as p:
        R = p.map(sweep, jobs)
    # Monte Carlo (iso) at TT: per-cell gain error sigma
    rng = np.random.default_rng(3)
    sig = AVT_N / np.sqrt(CELL["W"] * CELL["L"] * CELL["m"])
    g = []
    for _ in range(40):
        mm = {k: rng.normal(0, sig) for k in ("q1", "q2", "q3", "q4")}
        I, _ = cell(8 * LSB_Q, 8 * LSB_Q, IREF, 0.0, mm=mm)
        g.append(I / (8 * LSB_Q * 8 * LSB_Q / IREF) - 1)
    out = dict(cell=CELL, LSB_Q=LSB_Q, I_ref=IREF, gmid_full_scale=audit, pvt=R,
               mc_gain_sigma_pct=float(np.std(g) * 100), mc_gain_mean_pct=float(np.mean(g) * 100))
    json.dump(out, open("results/tl_cell.json", "w"), indent=1)
    for r in R:
        print(r)
    print("MC per-cell gain sigma %.2f %%, mean %.2f %%" % (out["mc_gain_sigma_pct"], out["mc_gain_mean_pct"]))
