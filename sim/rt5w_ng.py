"""RT5W analog netlist generator + ngspice runner (gf180mcuD, 3.3 V).

Softmax core (rev 2b): score current I_s,j -> R_c from V_R -> gate of exponentiator M_j.
All M_j share source node V_B; a tail sink fixes sum(I_j) = I_sum (KCL normalisation).
I_j = I_sum * exp(x_j) / sum exp(x_k),  x_j = I_s,j R_c / (n U_T).
Each drain feeds a PMOS diode with keep-alive sink I_K (bounds the slowest node);
a matched PMOS mirror copies (I_j + I_K) and a replica sink removes I_K at the output.
"""
import os, subprocess, tempfile, re, json, math
import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.environ.get("GF180_MODELS", os.path.join(_ROOT, ".pdk", "gf180mcu_fd_pr", "models", "ngspice"))
AVT_N, AVT_P = 7.148e-3, 6.66e-3   # Pelgrom A_VT (V*um), PDK statistical params (provenance doc)
K_B, Q_E = 1.380649e-23, 1.602176634e-19

# ---- design of record for this rebuild (all sizes: um) ----
D = dict(
    VDD=3.3,
    I_sum=0.5e-6,        # tail (AGC) current
    kappa=0.01,          # keep-alive fraction
    R_c=1.376e6,         # score resistor: 4 x the record (344 k) so the array runs at 1/4 current in weak inversion
    V_R=1.65,            # gate reference for x = 0  (set so V_B ~ 0.95 V at all-zero scores)
    We=200.0, Le=1.0,    # exponentiator NMOS, gm/ID >= 25 S/A at full share (weak-inversion rule)
    Wt=48.0, Lt=1.0, mt=4,# tail sink: 4 units of I_sum/4
    Wp=240.0, Lp=1.0,    # PMOS diode + output mirror (weak-inversion rule)
    Wk=4.0, Lk=2.0,      # keep-alive / replica sink unit (I_K)
    C_B=1e-12,           # explicit cap on V_B (spec of record)
    X_MAX=18.0,
    Be="vb",             # exponentiator bulk: '0' (p-sub) or 'vb' (DNWELL pocket, p-well tied to V_B)
    V_O=2.78,
    V_cas=1.05,          # tail cascode gate (bias generator output; ideal here)            # ADC input node voltage (matches PMOS diode node -> mirror V_DS match)
)


def corner_lib(c):
    return {"tt": "typical", "ss": "ss", "ff": "ff", "sf": "sf", "fs": "fs"}[c]


def nUT_nom(T=27.0, n=1.39):
    return n * K_B * (T + 273.15) / Q_E


def softmax_netlist(x, d=None, corner="tt", T=27.0, vdd=None, mm=None, tran=None, x_prev=None, nUT=None):
    """x: 4 scores in e-folds (nominal n*U_T at 27 C). PTAT reference -> score current scales with T.
    mm: dict of mismatch offsets (V) per device name. tran: (tstep, tstop) for a step x_prev -> x."""
    d = dict(D, **(d or {}))
    vdd = vdd or d["VDD"]
    nUT = nUT or nUT_nom()
    mm = mm or {}
    ptat = (T + 273.15) / 300.15
    I_unit = d["I_sum"] / 4
    L = [f"* rt5w softmax core corner={corner} T={T} VDD={vdd}",
         f".include {MODELS}/design.ngspice",
         f".lib {MODELS}/sm141064.ngspice {corner_lib(corner)}",
         f".temp {T}",
         f"Vdd vdd 0 {vdd}",
         f"Vr vr 0 {d['V_R']}",
         f"Ibias vdd nbias {I_unit*ptat:.6e}",
         # wide-swing cascode mirror: bias branch cascoded too, so V_DS(Mbias) = V_DS(Mtail) at every corner
         f"Mbc nbias vcas nbm 0 nmos_3p3 w={d['Wt']}u l={d['Lt']}u",
         f"Mbias nbm nbias 0 0 nmos_3p3 w={d['Wt']}u l={d['Lt']}u",
         f"Vmt nbias gt_t {mm.get('Mt',0):.6e}",
         f"Mtail tc gt_t 0 0 nmos_3p3 w={d['Wt']}u l={d['Lt']}u m={d['mt']}",
         f"Vcas vcas 0 {d['V_cas']}",
         f"Mcas vb vcas tc 0 nmos_3p3 w={d['Wt']}u l={d['Lt']}u m={d['mt']}",   # tail cascode (V_DS(tail) ~ V_DS(bias diode))
         f"Cb vb 0 {d['C_B']}",
         # keep-alive unit current I_K = kappa*I_sum (mirror from its own bias)
         f"Ikb vdd kbias {d['kappa']*d['I_sum']*ptat:.6e}",
         f"Mkb kbias kbias 0 0 nmos_3p3 w={d['Wk']}u l={d['Lk']}u"]
    for j in range(4):
        Is = x[j] * nUT / d["R_c"] * ptat
        if tran and x_prev is not None:
            Ip = x_prev[j] * nUT / d["R_c"] * ptat
            src = f"PWL(0 {Ip:.6e} {tran[2]:.6e} {Ip:.6e} {tran[2]+5e-9:.6e} {Is:.6e})"
            L.append(f"Is{j} 0 g{j} {src}")
        else:
            L.append(f"Is{j} 0 g{j} {Is:.6e}")
        L += [f"Rc{j} vr g{j} {d['R_c']}",
              f"Vme{j} g{j} ge{j} {mm.get(f'Me{j}',0):.6e}",
              f"Me{j} dp{j} ge{j} vb {d['Be']} nmos_3p3 w={d['We']/4}u l={d['Le']}u m=4",
              f"Mp{j} dp{j} dp{j} vdd vdd pmos_3p3 w={d['Wp']/4}u l={d['Lp']}u m=4",
              f"Vmp{j} dp{j} gpo{j} {-mm.get(f'Mo{j}',0):.6e}",
              f"Mo{j} out{j} gpo{j} vdd vdd pmos_3p3 w={d['Wp']/4}u l={d['Lp']}u m=4",
              f"Vmk{j} kbias gk{j} {mm.get(f'Mk{j}',0):.6e}",
              f"Mk{j} dp{j} gk{j} 0 0 nmos_3p3 w={d['Wk']}u l={d['Lk']}u",
              f"Vmr{j} kbias gr{j} {mm.get(f'Mr{j}',0):.6e}",
              f"Mr{j} out{j} gr{j} 0 0 nmos_3p3 w={d['Wk']}u l={d['Lk']}u",
              f"Vo{j} out{j} 0 {d['V_O']}"]   # ADC input node held at V_O (ideal current-input ADC)
    L.append(".control")
    L.append("set filetype=ascii")
    if tran:
        L.insert(-1, "option method=gear maxord=2")   # trapezoidal rings on alternate samples (known pitfall)
        L.append(f"tran {tran[0]:.3e} {tran[1]:.3e}")
        L.append("wrdata __OUT__ i(vo0) i(vo1) i(vo2) i(vo3) v(vb) i(vdd)")
    else:
        L.append("op")
        L.append("print i(vo0) i(vo1) i(vo2) i(vo3) v(vb) i(vdd) v(g0) v(dp0) v(dp1) v(dp2) v(dp3)")
        devs = ["mbias", "mbc", "mtail", "mcas", "mkb"] + [f"{p}{j}" for j in range(4) for p in ("me", "mp", "mo", "mk", "mr")]
        for dv in devs:
            L.append(f"print @{dv}[gm] @{dv}[id] @{dv}[vds] @{dv}[vdsat]")
    L += [".endc", ".end"]
    return "\n".join(L)


def run(netlist, timeout=600):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "o.dat")
        p = os.path.join(td, "n.sp")
        open(p, "w").write(netlist.replace("__OUT__", out))
        r = subprocess.run(["ngspice", "-b", p], capture_output=True, text=True, timeout=timeout)
        txt = r.stdout + r.stderr
        data = np.loadtxt(out) if os.path.exists(out) else None
    return txt, data


def parse_print(txt):
    vals = {}
    for m in re.finditer(r"^\s*([@\w\(\)\[\]\.#]+)\s*=\s*([-+0-9.eE]+)", txt, re.M):
        vals[m.group(1)] = float(m.group(2))
    return vals


def softmax_op(x, **kw):
    txt, _ = run(softmax_netlist(x, **kw))
    v = parse_print(txt)
    try:
        I = np.array([v[f"i(vo{j})"] for j in range(4)])  # current INTO node from source = -(out)
    except KeyError:
        raise RuntimeError(txt[-3000:])
    # Vo forces 1.2 V; mirror sources current into out node, ngspice i(vo) is current through source (+ to -)
    I = I  # flows out0 -> 0 through Vo: positive when mirror delivers net current
    return dict(I=I, vb=v["v(vb)"], idd=-v["i(vdd)"], raw=v)


def golden(x):
    e = np.exp(np.asarray(x) - np.max(x))
    return e / e.sum()


def codes(a):
    return np.clip(np.round(255 * np.asarray(a)), 0, 255).astype(int)
