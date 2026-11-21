"""Settling of the softmax core: step x_a -> x_b at t = 1 us, measure time until every output is
within 0.5 LSB (I_sum/510) of its final value. Steps include the falsifier pattern (one dominant +
small tokens) and the masking pattern. Window of record: 50 us (1000 cycles at 20 MHz)."""
import json, itertools
import numpy as np
from multiprocessing import Pool
from rt5w_ng import softmax_netlist, run, D

NUT = 37.517e-3
STEPS = [([0, 0, 0, 0], [18, 16, 0, 0]), ([18, 0, 0, 0], [0, 18, 0, 0]), ([18, 0, 0, 0], [18, 0, 0, 12]),
         ([18, 16, 0, 0], [0, 0, 0, 0]), ([18, 9, 6, 3], [3, 6, 9, 18]), ([0, 0, 0, 18], [18, 0, 0, 0]),
         ([18, 0, 0, 0], [18, 1, 1, 1]), ([5, 5, 5, 5], [18, 13, 12, 11])]
T_STEP = 1e-6


def one(args):
    (xa, xb), corner, T = args
    nl = softmax_netlist(xb, x_prev=xa, corner=corner, T=T, nUT=NUT, tran=(20e-9, 101e-6, T_STEP))
    _, data = run(nl, timeout=1200)
    t = data[:, 0]
    I = np.stack([data[:, 1 + 2 * j] for j in range(4)], 1)       # wrdata: t, val pairs
    ptat = (T + 273.15) / 300.15
    lsb = D["I_sum"] * ptat / 255
    fin = I[-1]
    bad = np.any(np.abs(I - fin) > 0.5 * lsb, axis=1)
    idx = np.where(bad)[0]
    t_settle = (t[idx[-1]] - T_STEP) if len(idx) else 0.0
    return dict(xa=xa, xb=xb, corner=corner, T=T, settle_us=float(t_settle * 1e6),
                final_codes=[float(v) for v in np.round(fin / lsb, 2)])


if __name__ == "__main__":
    jobs = [(s, c, T) for s in STEPS for c, T in (("tt", 27), ("ss", -40), ("ss", 27), ("ff", 125), ("sf", -40), ("fs", 125))]
    with Pool(2) as p:
        R = p.map(one, jobs)
    json.dump(R, open("results/softmax_tran.json", "w"), indent=1)
    worst = max(R, key=lambda r: r["settle_us"])
    print(f"runs {len(R)}; worst settle {worst['settle_us']:.1f} us at {worst['corner']} {worst['T']} C step {worst['xa']}->{worst['xb']}")
    print(f"over 50 us window: {sum(r['settle_us'] > 50 for r in R)}; median {np.median([r['settle_us'] for r in R]):.1f} us")
    for c, T in sorted(set((r['corner'], r['T']) for r in R)):
        print(f"  {c} {T:4d} C: max {max(r['settle_us'] for r in R if r['corner']==c and r['T']==T):.1f} us")
