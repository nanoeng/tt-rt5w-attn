"""STL falsification of the sky130 RT5W (TTSKY26e) analog macro with PSY-TaLiRo (staliro 3.2) and RTAMT.
Task: sky130 falsification, 2026-11-21.

Two systems under test, both on the captured sky130 netlists (netlist/, or netlist_pex/ with RT5W_NETLIST):

1. Softmax core + bias (campaign 'softmax'): rt5w_bias (real I_u, vr, vcas, kbias at temperature T) driving
   rt5w_softmax; score currents I_j = x_j nU_T,n(T) / R_c are stepped x_a -> x_b at T_STEP. Signals as in
   rt5w/falsify.py (gf180 campaign of 19 Nov), with the sky130 scaling: the outputs are a x4 mirror of the tail,
   so a_j = I_out,j / (4 I_tail). I_tail is sensed by a 0 V source on the tail source inside a copy of the subckt;
   the AGC reference is the bias block's nbias current (sensed): agc_err = |I_tail / (4 I_nbias) - 1|.
   nU_T,n(T) = nU_T,n(27 C, corner; tech.py) x (T + 273.15) / 300.15 (kT/q scaling of the measured slope);
   R_c = RC_L x R_per_um (res_xhigh_po_0p35, flat in temperature in this model release).
   Search: x_a, x_b in [0, 18]^4, T in [-40, 125] C, one process corner per campaign. Requirements R1..R7, R1t, R2t
   with the limits of record (rt5w/falsify.py; never relaxed).

2. Full chain (campaign 'chain'): rt5w_analog (bias -> IDACs -> 4x4 key array -> k-scale -> softmax -> readout).
   Search: query codes q in {0..15}^4, keys k in [0.05, 1]^16, per-key scales ks in {1..15}^4, at the corner's
   sign-off temperature. Stage 1 (falsification search): DC operating point of the chain, shares quantised ideally
   (round(255 a)), against the model codes (design/tb/tb_chain.model_codes). Stage 2 (confirmation): the worst
   samples re-run with the SAR as one continuous transient (RT5W_SAR=cont, tb_chain.run), i.e. as on silicon.
   Requirements: C1 max_j |code_j - model_j| <= 7.65 LSB (R3's 3 % at the chain output); C2 a clear model winner
   (lead >= 0.05) stays the top code.
   Engines: 'ngspice' (CLI, design/sim.py) or 'pyspice' (libngspice via PySpice) for stage 1 and the softmax SUT.
"""
import math
import os
import re
import sys
import tempfile
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "design"), os.path.join(ROOT, "design", "tb"), os.path.join(ROOT, "design", "blocks")):
    if p not in sys.path:
        sys.path.insert(0, p)

import sim          # noqa: E402
import tech         # noqa: E402
from softmax import RC_L   # noqa: E402

from . import falsify as gf   # requirement table, RTAMT evaluation  # noqa: E402

REQUIREMENTS = gf.REQUIREMENTS
T_STEP_US, T_END_US, DT_US, X_MAX, MARGIN_GAP = gf.T_STEP_US, gf.T_END_US, gf.DT_US, gf.X_MAX, gf.MARGIN_GAP
V_O = 2.2                       # outputs held at the readout cascode-source level (tb_softmax)
LOADS = {"iref": 1.0, "ndac": 0.6, "nd0": 0.6, "nd1": 0.6, "nd2": 0.6, "nd3": 0.6}   # unused bias outputs (tb_bias)
SIGN_OFF_T = {"tt": 27.0, "ss": -40.0, "ff": 125.0}


def golden(x):
    e = np.exp(np.asarray(x, float) - np.max(x))
    return e / e.sum()


# ----------------------------------------------------------------------------- softmax core + bias
def _softmax_sense():
    """rt5w_softmax with a 0 V source in the tail source (I_tail), as subckt rt5w_softmax_s."""
    txt = open(os.path.join(sim.NETLIST_DIR, "rt5w_softmax.spice")).read()
    body = re.search(r"^\.subckt rt5w_softmax .*?^\.ends", txt, re.M | re.S | re.I).group(0)
    body = body.replace(".subckt rt5w_softmax ", ".subckt rt5w_softmax_s ", 1)
    lines = body.splitlines()
    out, k = [], 0
    while k < len(lines):
        ln = lines[k]
        if re.match(r"^XMtail\s", ln, re.I) or re.match(r"^XMtail\b", ln.split()[0] if ln.split() else "", re.I):
            w = ln.split()
            assert w[3].lower() == "vss", "tail source not on vss"
            w[3] = "tsn"
            ln = " ".join(w)
            out.append(ln)
            k += 1
            while k < len(lines) and lines[k].startswith("+"):
                out.append(lines[k]); k += 1
            out.append("Vtsn tsn vss 0")
            continue
        out.append(ln)
        k += 1
    s = "\n".join(out)
    assert "Vtsn tsn vss 0" in s, "tail device not found in rt5w_softmax"
    return s


def softmax_netlist(xa, xb, corner="tt", temp=27.0):
    t27 = tech.measure(corner, SIGN_OFF_T[corner])          # nU_T,n and R per um of this corner (tech.py)
    nut = t27["nUT_n"] * (temp + 273.15) / (SIGN_OFF_T[corner] + 273.15)
    R_C = RC_L * t27["R_per_um"]
    ts = T_STEP_US * 1e-6
    L = ["Vdd vdd 0 3.3", "Vss vss 0 0", "Ven bias_en 0 3.3", "Cv vbn 0 1p", "Cr vr 0 1p"]
    L += [f"V_{n} {n} 0 {v}" for n, v in LOADS.items()]
    conn = {p: p for p in sim.ports("rt5w_bias")}
    conn["nbias"] = "nbs"
    L.append(sim.inst("Xb", "rt5w_bias", **conn))
    L.append("Vnb nbs nbias 0")                               # nbias current sense (AGC reference)
    for j in range(4):
        ia, ib = xa[j] * nut / R_C, xb[j] * nut / R_C
        L.append(f"Ig{j} vdd g{j} PWL(0 {ia:.6e} {ts:.6e} {ia:.6e} {ts + 5e-9:.6e} {ib:.6e})")
        L.append(f"Vo{j} o{j} 0 {V_O}")
    L.append("Xs g0 g1 g2 g3 nbias kbias vr vcas vb o0 o1 o2 o3 vdd vss rt5w_softmax_s")
    return "\n".join(L)


def _full_netlist(body, corner, temp, blocks, options, control):
    return (f"* tb\n{sim.header(corner, temp, blocks, options)}\n{_softmax_sense()}\n{body}\n"
            f".control\nset filetype=ascii\n{control}\n.endc\n.end\n")


_NG = None


def _shared():
    global _NG
    if _NG is None:
        sys.path.insert(0, ROOT)
        from rt5w.backends.spice import shared_ngspice
        _NG = shared_ngspice()
        for c in sim.SPICEINIT.strip().splitlines():
            if c.startswith("set "):          # 'option noinit' is a netlist option, not a shared-library command
                _NG.exec_command(c)
    return _NG


def simulate_softmax(xa, xb, temp=27.0, corner="tt", engine="ngspice"):
    """t (s), I_out (n x 4), V_B, I_tail, I_nbias."""
    body = softmax_netlist(xa, xb, corner, temp)
    tran = f"tran 20n {(T_END_US + 1) * 1e-6:.4e}"
    vecs = "i(vo0) i(vo1) i(vo2) i(vo3) v(vb) i(v.xs.vtsn) i(vnb)"
    if engine == "ngspice":
        ctl = f"{tran}\nwrdata __DATA__ {vecs}"
        _, d, out = sim.run(_softmax_sense() + "\n" + body, ctl, corner, temp, blocks=["rt5w_bias"],
                            timeout=1800, options="rshunt=1e12 itl1=1000")
        if d is None:
            raise RuntimeError(out[-2000:])
        t = d[:, 0]
        cols = [d[:, 1 + 2 * k] for k in range(7)]
        return t, np.stack(cols[:4], 1), cols[4], cols[5], cols[6]
    if engine == "pyspice":
        ng = _shared()
        net = (f"* tb\n{sim.header(corner, temp, ['rt5w_bias'], 'rshunt=1e12 itl1=1000')}\n{_softmax_sense()}\n"
               f"{body}\n.end\n")
        with gf._Mute():
            ng.destroy()
            ng.load_circuit(net)
            ng._ngspice_shared.ngSpice_Command(tran.encode())
        p = ng.plot(None, ng.last_plot)
        g = lambda n: np.real(np.asarray(p[n]._data, dtype=complex))   # noqa: E731
        return (g("time"), np.stack([g(f"vo{j}#branch") for j in range(4)], 1), g("vb"),
                g("v.xs.vtsn#branch"), g("vnb#branch"))
    raise ValueError(engine)


def signals_softmax(t, I, vb, it, inb, xb):
    tu = np.arange(0.0, T_END_US + DT_US / 2, DT_US)
    ts = t * 1e6
    I = np.stack([np.interp(tu, ts, I[:, j]) for j in range(4)], 1)
    vb = np.interp(tu, ts, vb)
    it = np.abs(np.interp(tu, ts, it))
    inb = np.abs(np.interp(tu, ts, inb))
    a = I / (4 * it[:, None])
    g = golden(xb)
    order = np.argsort(g)[::-1]
    win, second = order[0], order[1]
    margin = (a[:, win] - np.max(np.delete(a, win, axis=1), axis=1)) if g[win] - g[second] >= MARGIN_GAP \
        else np.ones_like(tu)
    return tu, dict(sum_err=np.abs(I.sum(1) / (4 * it) - 1), min_share=a.min(1), gold_err=np.abs(a - g).max(1),
                    drift=np.abs(a - a[-1]).max(1), margin=margin, agc_err=np.abs(it / (4 * inb) - 1), vb=vb)


def evaluate_softmax(xa, xb, temp=27.0, corner="tt", engine="ngspice", reqs=None):
    t, I, vb, it, inb = simulate_softmax(xa, xb, temp, corner, engine)
    tu, sig = signals_softmax(t, I, vb, it, inb, xb)
    rho = gf.robustness(tu, sig, reqs)
    norm = {k: v / REQUIREMENTS[k][1] for k, v in rho.items()}
    a_end = I[-1] / (4 * abs(it[-1]))
    return dict(xa=[float(v) for v in xa], xb=[float(v) for v in xb], temp=float(temp), corner=corner,
                rho=rho, cost=min(norm.values()), worst=min(norm, key=norm.get),
                final_codes=[int(round(255 * v)) for v in a_end],
                golden_codes=[int(round(255 * v)) for v in golden(xb)],
                sum_end=float(I[-1].sum() / (4 * abs(it[-1]))), vb_end=float(vb[-1]))


# ----------------------------------------------------------------------------- full chain
C1_LSB = 0.03 * 255          # R3's 3 % at the chain output
CHAIN_REQ = {"C1": (f"max_j |code - model| <= {C1_LSB:.2f} LSB", C1_LSB),
             "C2": ("a clear model winner (lead >= 0.05) stays the top code", 1.0)}


def _chain_rho(codes, model, a_model):
    codes, model = np.asarray(codes), np.asarray(model)
    rho = {"C1": float(C1_LSB - np.abs(codes - model).max())}
    order = np.argsort(a_model)[::-1]
    if a_model[order[0]] - a_model[order[1]] >= MARGIN_GAP:
        w = order[0]
        rho["C2"] = float(codes[w] - np.max(np.delete(codes, w)))      # in LSB; < 0: another channel wins
        if rho["C2"] == 0:
            rho["C2"] = -0.5                                             # a tie loses the winner
    else:
        rho["C2"] = 255.0
    return rho


def evaluate_chain_dc(q, k, ks, corner="tt", engine="ngspice"):
    import tb_chain
    temp = SIGN_OFF_T[corner]
    d = tb_chain.dc_shares(q, k, ks, corner, temp)
    codes = [int(min(255, math.floor(255 * v + 0.5))) for v in d["a"]]
    model, x = tb_chain.model_codes(q, k, ks)
    a_model = golden(x)
    rho = _chain_rho(codes, model, a_model)
    norm = {n: rho[n] / CHAIN_REQ[n][1] for n in rho}
    return dict(q=[int(v) for v in q], k=[[float(v) for v in r] for r in k], ks=[int(v) for v in ks],
                corner=corner, temp=temp, codes=codes, model=model, rho=rho, cost=min(norm.values()),
                worst=min(norm, key=norm.get), stage="dc")


def evaluate_chain_cont(q, k, ks, corner="tt"):
    import tb_chain
    os.environ["RT5W_SAR"] = "cont"
    tb_chain.SAR_MODE = "cont"
    temp = SIGN_OFF_T[corner]
    r = tb_chain.run(q, k, ks, corner, temp)
    a_model = golden(r["x"])
    rho = _chain_rho(r["spice"], r["model"], a_model)
    norm = {n: rho[n] / CHAIN_REQ[n][1] for n in rho}
    return dict(q=[int(v) for v in q], k=[[float(v) for v in rr] for rr in k], ks=[int(v) for v in ks],
                corner=corner, temp=temp, codes=r["spice"], model=r["model"], rho=rho, cost=min(norm.values()),
                worst=min(norm, key=norm.get), stage="continuous SAR")


# ----------------------------------------------------------------------------- PSY-TaLiRo campaigns
def campaign_softmax(corner="tt", engine="ngspice", budget=30, anneal=10, seed=1, reqs=None,
                     temp_range=(-40.0, 125.0), log=print):
    import staliro
    from staliro import optimizers
    names = list(reqs or REQUIREMENTS)
    static = {f"xa{j}": (0.0, X_MAX) for j in range(4)}
    static.update({f"xb{j}": (0.0, X_MAX) for j in range(4)})
    static["temp"] = tuple(temp_range)
    samples = []

    @staliro.costfunc
    def cost(inputs):
        s = inputs.static
        r = evaluate_softmax([s[f"xa{j}"] for j in range(4)], [s[f"xb{j}"] for j in range(4)], s["temp"],
                             corner, engine, names)
        samples.append(r)
        log(f"  softmax {corner} {engine} #{len(samples)}: T {r['temp']:6.1f} C worst {r['worst']} "
            f"cost {r['cost']:+.3f} codes {r['final_codes']} golden {r['golden_codes']}")
        return staliro.Result(r["cost"], r)

    t0 = time.time()
    phases = [optimizers.UniformRandom()] + ([optimizers.DualAnnealing()] if anneal else [])
    for opt, n in zip(phases, [budget, anneal]):
        staliro.test(cost, opt, staliro.TestOptions(runs=1, iterations=n, static_inputs=static, seed=seed))
    rho_min = {k: min(s["rho"][k] for s in samples) for k in names}
    worst = {k: min(samples, key=lambda s: s["rho"][k]) for k in names}
    return dict(sut="softmax+bias", corner=corner, engine=engine, n=len(samples), seconds=round(time.time() - t0, 1),
                rho_min=rho_min, rho_norm={k: rho_min[k] / REQUIREMENTS[k][1] for k in names},
                falsified=[k for k in names if rho_min[k] < 0], held=[k for k in names if rho_min[k] >= 0],
                counterexamples={k: dict(xa=worst[k]["xa"], xb=worst[k]["xb"], temp=worst[k]["temp"],
                                         rho=worst[k]["rho"][k], codes=worst[k]["final_codes"],
                                         golden=worst[k]["golden_codes"]) for k in names if rho_min[k] < 0},
                samples=samples)


def campaign_chain(corner="tt", engine="ngspice", budget=24, anneal=8, seed=1, confirm=2, log=print):
    import staliro
    from staliro import optimizers
    static = {f"q{i}": (0.0, 15.999) for i in range(4)}
    static.update({f"k{j}{i}": (0.05, 1.0) for j in range(4) for i in range(4)})
    static.update({f"ks{j}": (1.0, 15.999) for j in range(4)})
    samples = []

    @staliro.costfunc
    def cost(inputs):
        s = inputs.static
        q = [int(s[f"q{i}"]) for i in range(4)]
        k = [[round(s[f"k{j}{i}"], 3) for i in range(4)] for j in range(4)]
        ks = [int(s[f"ks{j}"]) for j in range(4)]
        r = evaluate_chain_dc(q, k, ks, corner, engine)
        samples.append(r)
        log(f"  chain {corner} DC #{len(samples)}: q {q} ks {ks} codes {r['codes']} model {r['model']} "
            f"cost {r['cost']:+.3f} ({r['worst']})")
        return staliro.Result(r["cost"], r)

    t0 = time.time()
    phases = [optimizers.UniformRandom()] + ([optimizers.DualAnnealing()] if anneal else [])
    for opt, n in zip(phases, [budget, anneal]):
        staliro.test(cost, opt, staliro.TestOptions(runs=1, iterations=n, static_inputs=static, seed=seed))
    worst_dc = sorted(samples, key=lambda s: s["cost"])[:confirm]
    confirmed = []
    for w in worst_dc:
        log(f"  chain {corner}: confirming q {w['q']} ks {w['ks']} with the continuous SAR ...")
        c = evaluate_chain_cont(w["q"], w["k"], w["ks"], corner)
        c["dc_codes"] = w["codes"]
        confirmed.append(c)
        log(f"    continuous SAR codes {c['codes']} model {c['model']} rho {c['rho']}")
    names = list(CHAIN_REQ)
    rho_min = {n: min(s["rho"][n] for s in samples) for n in names}
    rho_cont = {n: min(c["rho"][n] for c in confirmed) for n in names} if confirmed else {}
    return dict(sut="chain", corner=corner, engine=engine, n=len(samples), seconds=round(time.time() - t0, 1),
                rho_min_dc=rho_min, rho_min_cont=rho_cont,
                falsified_dc=[n for n in names if rho_min[n] < 0],
                falsified_cont=[n for n in names if rho_cont.get(n, 1) < 0],
                confirmed=confirmed, samples=samples)
