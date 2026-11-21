"""Static conformance of the softmax core over the full PVT grid (5 corners x 3 T x 3 VDD)
and a Pelgrom Monte Carlo at TT. Spec: rms share error <= 3 % per die (spec of record),
code error reported in LSB of the 8-bit readout. Encoding uses the TT-27C calibrated nU_T."""
import json, itertools, sys
import numpy as np
from multiprocessing import Pool
from rt5w_ng import softmax_op, golden, D, AVT_N, AVT_P

NUT_CAL = None   # fitted at TT 27 C 3.3 V in the share domain (calibrate())
rng = np.random.default_rng(7)
VEC = rng.uniform(0, 18, size=(40, 4))
VEC[:4] = [[18, 16, 0, 0], [3, 2, 0, 0], [18, 0, 0, 0], [9, 9, 9, 9]]


def calibrate():
    from scipy.optimize import minimize_scalar
    R = [softmax_op(list(x), nUT=37e-3)["I"] for x in VEC]
    f = lambda b: sum(((I / I.sum() - golden(x * b)) ** 2).sum() for x, I in zip(VEC, R))
    b = minimize_scalar(f, bounds=(0.8, 1.25), method="bounded").x
    return 37e-3 / b


def point(args):
    corner, T, vdd, mm, nut = args
    ptat = (T + 273.15) / 300.15
    out = []
    for x in VEC:
        r = softmax_op(list(x), corner=corner, T=T, vdd=vdd, mm=mm, nUT=nut)
        out.append(((r["I"] / ptat).tolist(), r["vb"], r["idd"]))   # ratio to PTAT reference (ratiometric ADC)
    return out


def metrics(res):
    I = np.array([o[0] for o in res])
    a = I / D["I_sum"]                      # ratiometric to nominal I_sum (ADC full scale)
    an = I / I.sum(1, keepdims=True)        # shares (common gain removed)
    g = np.array([golden(x) for x in VEC])
    e = an - g
    code_err = np.round(255 * an) - np.round(255 * g)
    # gain (beta) fit: x_eff = beta * x  (least squares on log-ratios of shares > 1 LSB)
    num = den = 0.0
    for x, s in zip(VEC, an):
        m = s > 1 / 255
        if m.sum() >= 2:
            lx = x[m] - x[m].mean(); ls = np.log(s[m]) - np.log(s[m]).mean()
            num += (lx * ls).sum(); den += (lx * lx).sum()
    return dict(max_err_pct=float(np.abs(e).max() * 100), rms_err_pct=float(np.sqrt((e ** 2).mean()) * 100),
                max_code_err_lsb=int(np.abs(code_err).max()), exact_codes_pct=float((code_err == 0).mean() * 100),
                sum_err_pct=float((a.sum(1).mean() - 1) * 100), beta=float(num / den),
                vb_min=float(min(o[1] for o in res)), vb_max=float(max(o[1] for o in res)),
                idd_uA=float(np.mean([o[2] for o in res]) * 1e6))


def mc_die(seed):
    r = np.random.default_rng(1000 + seed)
    mm = {}
    for j in range(4):
        mm[f"Me{j}"] = r.normal(0, AVT_N / np.sqrt(D["We"] * D["Le"]))
        mm[f"Mo{j}"] = r.normal(0, AVT_P / np.sqrt(D["Wp"] * D["Lp"]) * np.sqrt(2))   # diode vs mirror pair
        mm[f"Mk{j}"] = r.normal(0, AVT_N / np.sqrt(D["Wk"] * D["Lk"]))
        mm[f"Mr{j}"] = r.normal(0, AVT_N / np.sqrt(D["Wk"] * D["Lk"]))
    mm["Mt"] = r.normal(0, AVT_N / np.sqrt(D["Wt"] * D["Lt"] * D["mt"]))
    return mm


if __name__ == "__main__":
    NUT_CAL = calibrate()
    print("calibrated nUT (mV):", NUT_CAL * 1e3)
    pts = [(c, T, v, None, NUT_CAL) for c, T, v in itertools.product(["tt", "ss", "ff", "sf", "fs"], [-40, 27, 125], [3.0, 3.3, 3.6])]
    with Pool(2) as p:
        R = p.map(point, pts)
    pvt = [dict(corner=c, T=T, vdd=v, **metrics(r)) for (c, T, v, _, _n), r in zip(pts, R)]
    mcs = [("tt", 27, 3.3, mc_die(s), NUT_CAL) for s in range(20)]
    with Pool(2) as p:
        RM = p.map(point, mcs)
    mc = [dict(die=i, **metrics(r)) for i, r in enumerate(RM)]
    out = dict(nUT_cal=NUT_CAL, design=D, n_vectors=len(VEC), pvt=pvt, mc=mc)
    json.dump(out, open("results/softmax_static.json", "w"), indent=1)
    def summ(L, k): return (min(p[k] for p in L), max(p[k] for p in L))
    for name, L in (("PVT (45 points)", pvt), ("MC (20 dies, TT 27C)", mc)):
        print(name)
        for k in ("max_err_pct", "rms_err_pct", "max_code_err_lsb", "exact_codes_pct", "sum_err_pct", "beta", "vb_min", "vb_max", "idd_uA"):
            print(f"  {k:18s} {summ(L,k)}")
    tt = [p for p in pvt if p["corner"] == "tt" and p["T"] == 27 and p["vdd"] == 3.3][0]
    print("TT nominal", tt)
