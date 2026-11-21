"""Rev-3b array: 1T + C_W PMOS cells, query on column diodes, keys as floating gate offsets.
  column c : PMOS diode (source = bulk = VDD) carrying I_Q,c (sunk by the column IDAC)
  cell r,c : PMOS, gate = V_Dc + V_w,rc (floating C_W offset; V_w > 0 lowers |V_SG| -> k < 1)
             I_rc = I_Q,c * exp(-V_w,rc / nU_T,p) = I_Q,c * k_rc
  row r    : KCL sum S_r = sum_c I_rc, sourced directly into R_c of the softmax core (rt5w_ng.py)
Checks: (1) product law over PVT, (2) Pelgrom MC per-cell gain, (3) full chain QK^T -> softmax codes."""
import json, itertools
import numpy as np
from multiprocessing import Pool
from rt5w_ng import MODELS, run, parse_print, softmax_netlist, D, AVT_P, golden

AW = dict(W=20.0, L=4.0, m=8)       # column diode and cell (equal); gm/ID audited below
CASC = None                          # per-row cascode gate (V); tested, no benefit -> disabled
IQ_LSB = 8.25e-9                     # column IDAC LSB (record: 0.5 uA) -> I_Q max 124 nA, x_max ~ 18 with R_c = 1.376 M
NUT_P = None                         # calibrated PMOS n*U_T (fitted below)


def array_netlist(IQ, Vw, corner="tt", T=27, vdd=3.3, row_v=2.0, mm=None, to_softmax=None, nUT_s=37.517e-3):
    """IQ: 4 column currents; Vw: 4x4 offsets (V). If to_softmax is None rows go to fixed row_v."""
    mm = mm or {}
    W, L, m = AW["W"], AW["L"], AW["m"]
    lib = {"tt": "typical"}.get(corner, corner)
    if to_softmax is None:
        L_ = [f"* array", f".include {MODELS}/design.ngspice", f".lib {MODELS}/sm141064.ngspice {lib}", f".temp {T}",
              f"Vdd vdd 0 {vdd}"]
        tail = [".control", "op", "print " + " ".join(f"i(vrow{r})" for r in range(4)) + " " +
                " ".join(f"@md{c}[gm] @md{c}[id]" for c in range(4)), ".endc", ".end"]
    else:
        base = softmax_netlist([0, 0, 0, 0], corner=corner, T=T, vdd=vdd, nUT=nUT_s).splitlines()
        # drop the ideal score sources: rows of the array drive g0..g3 instead
        base = [l for l in base if not l.startswith("Is")]
        cut = base.index(".control")
        L_, tail = base[:cut], base[cut:]
    for c in range(4):
        L_ += [f"Iq{c} dcol{c} 0 {IQ[c]:.6e}",
               f"Vmd{c} dcol{c} dg{c} {mm.get(f'd{c}',0):.6e}",
               f"Md{c} dcol{c} dg{c} vdd vdd pmos_3p3 w={W}u l={L}u m={m}"]
        for r in range(4):
            off = Vw[r][c] + mm.get(f"c{r}{c}", 0)
            row = f"rw{r}" if to_softmax is None else (f"rs{r}" if CASC else f"g{r}")
            L_ += [f"Vw{r}{c} cg{r}{c} dcol{c} {off:.6e}",
                   f"Mc{r}{c} {row} cg{r}{c} vdd vdd pmos_3p3 w={W}u l={L}u m={m}"]
    if to_softmax is None:
        L_ += [f"Vrow{r} rw{r} 0 {row_v}" for r in range(4)]
    elif CASC:   # per-row PMOS cascode: every cell sees the same V_SD whatever the softmax gate voltage
        L_ += [f"Vcr vcr 0 {CASC}"] + [f"Mrc{r} g{r} vcr rs{r} vdd pmos_3p3 w=20u l=1u m=20" for r in range(4)]
    return "\n".join(L_ + tail)


def rows(IQ, Vw, **kw):
    v = parse_print(run(array_netlist(IQ, Vw, **kw))[0])
    return np.array([v[f"i(vrow{r})"] for r in range(4)]), v


def calibrate():
    # one cell column: fit nU_T,p from I(Vw)/I(0)
    vws = np.linspace(0, 0.12, 7)
    I = [rows([100e-9, 0, 0, 0], [[w, 0, 0, 0]] + [[0] * 4] * 3)[0][0] for w in vws]
    slope = np.polyfit(vws, np.log(np.array(I) / I[0]), 1)[0]
    return -1 / slope


def law(args):
    corner, T, vdd, nut = args
    ptat = (T + 273.15) / 300.15
    rng = np.random.default_rng(5)
    errs = []
    for _ in range(12):
        q = rng.integers(1, 16, 4)
        k = rng.uniform(0.05, 1.0, (4, 4))
        Vw = (-nut * ptat * np.log(k)).tolist()      # PTAT write voltage keeps k fixed over T
        IQ = (q * IQ_LSB * ptat).tolist()
        I, _ = rows(IQ, Vw, corner=corner, T=T, vdd=vdd)
        ideal = (k * np.array(IQ)[None, :]).sum(1)
        errs += list(I / ideal - 1)
    e = np.array(errs)
    return dict(corner=corner, T=T, vdd=vdd, max_err_pct=float(np.abs(e).max() * 100), mean_err_pct=float(e.mean() * 100),
                rms_err_pct=float(np.sqrt((e ** 2).mean()) * 100))


def chain(args):
    """QK^T on the array -> softmax core -> shares, vs golden of the ideal scores."""
    q, k, corner, T, nut, nUT_s = args[:6]
    g = args[6] if len(args) > 6 else 1.0
    Vw = (-nut * np.log(k)).tolist()
    IQ = (np.array(q) * IQ_LSB).tolist()
    S = (k * np.array(IQ)[None, :]).sum(1)
    x = g * S * D["R_c"] / nUT_s                       # ideal scores in e-folds (g: host-calibrated common gain)
    nl = array_netlist(IQ, Vw, corner=corner, T=T, to_softmax=True, nUT_s=nUT_s)
    v = parse_print(run(nl)[0])
    I = np.array([v[f"i(vo{j})"] for j in range(4)])
    return dict(x=x.tolist(), shares=(I / I.sum()).tolist(), golden=golden(x).tolist(),
                codes=np.round(255 * I / I.sum()).astype(int).tolist(), golden_codes=np.round(255 * golden(x)).astype(int).tolist())


if __name__ == "__main__":
    nut = calibrate()
    I, v = rows([124e-9] * 4, [[0] * 4] * 4)
    audit = {f"d{c}": v[f"@md{c}[gm]"] / abs(v[f"@md{c}[id]"]) for c in range(4)}
    print(f"nU_T,p = {nut*1e3:.2f} mV; column diode gm/ID at 124 nA: {audit['d0']:.1f} S/A")
    jobs = [(c, T, vd, nut) for c, T in (("tt", 27), ("ss", -40), ("ss", 125), ("ff", -40), ("ff", 125), ("sf", 27), ("fs", 27))
            for vd in (3.0, 3.6)] + [("tt", 27, 3.3, nut)]
    with Pool(2) as p:
        R = p.map(law, jobs)
    for r in R:
        print(r)
    # MC: per-cell gain error (column diode vs cell mismatch, both PMOS)
    sig = AVT_P / np.sqrt(AW["W"] * AW["L"] * AW["m"])
    rng = np.random.default_rng(9)
    g = []
    for _ in range(30):
        mm = {f"d{c}": rng.normal(0, sig) for c in range(4)}
        mm.update({f"c{r}{c}": rng.normal(0, sig) for r in range(4) for c in range(4)})
        I, _ = rows([100e-9] * 4, [[0] * 4] * 4, mm=mm)
        g += list(I / 400e-9 - 1)
    mc = dict(sigma_row_gain_pct=float(np.std(g) * 100), sigma_VT_mV=float(sig * 1e3), nUT_p_mV=float(nut * 1e3))
    print("MC row-gain sigma %.2f %% (sigma_VT %.2f mV per device)" % (mc["sigma_row_gain_pct"], mc["sigma_VT_mV"]))
    # chain: calibrate the common array gain g on 8 random vectors, then test on held-out vectors + the
    # Illustrated-Transformer 'Thinking Machines' row (x ~ [18, 16, 0, 0] -> 0.88 / 0.12)
    from scipy.optimize import minimize_scalar
    rng = np.random.default_rng(21)
    calv = [(rng.integers(1, 16, 4).tolist(), rng.uniform(0.05, 1.0, (4, 4))) for _ in range(8)]
    raw = [chain((q, k, "tt", 27, nut, 37.517e-3)) for q, k in calv]
    def loss(g):
        return sum(((np.array(r["shares"]) - golden(g * np.array(r["x"]))) ** 2).sum() for r in raw)
    g_cal = float(minimize_scalar(loss, bounds=(0.7, 1.3), method="bounded").x)
    test = [([15, 15, 15, 15], np.array([[0.97] * 4, [0.862] * 4, [0.002] * 4, [0.002] * 4]))]
    test += [(rng.integers(1, 16, 4).tolist(), rng.uniform(0.05, 1.0, (4, 4))) for _ in range(12)]
    CH = []
    for q, k in test:
        S = (k * (np.array(q) * IQ_LSB)[None, :]).sum(1)
        CH.append(chain((q, k, "tt", 27, nut, 37.517e-3, g_cal)))
    for c in CH[:4]:
        print("x", np.round(c["x"], 2), "codes", c["codes"], "golden", c["golden_codes"])
    err = np.array([np.abs(np.array(c["shares"]) - np.array(c["golden"])).max() for c in CH]) * 100
    cerr = np.array([np.abs(np.array(c["codes"]) - np.array(c["golden_codes"])).max() for c in CH])
    print("common array gain g = %.3f; held-out chain max share error %%: %.2f (median %.2f); max code error %d LSB"
          % (g_cal, err.max(), np.median(err), cerr.max()))
    json.dump(dict(cell=AW, IQ_LSB=IQ_LSB, nUT_p=nut, gmid_col_diode_124nA=audit, law_pvt=R, mc=mc, chain=CH, g_cal=g_cal,
                   chain_max_share_err_pct=float(err.max()), chain_max_code_err=int(cerr.max())), open("results/array_chain.json", "w"), indent=1)
