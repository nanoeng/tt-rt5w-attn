"""Level shifters between the 1.8 V controller (VDPWR) and the 3.3 V analog macro (VAPWR); thick-oxide devices only
(nfet/pfet_g5v0d10v5), because sky130_fd_sc_hvl cannot be fetched in this environment.

Up-shifter (rt5w_lsup): input inverter on vddl (1.8 V) makes inb; cross-coupled pair and output inverter on vdd (3.3 V).
Sizing reference: PDK-model on-currents (design/tb/tb_lshift.py ion table, 20 Nov 2026). Worst corner fs: per um,
I_n(V_GS 1.62 V, L 0.5) / I_p(V_SG 3.63 V, L 1.0) = 0.60 at -40 C. Pull-down margin >= 3 needs W_n / W_p >= 5:
W_p 0.42 (minimum) / L 1.0, W_n 2.5 / L 0.5 -> 3.6 at fs -40 C.
Down-shifter (rt5w_lsdn): two thick-oxide inverters on vddl (= VDPWR, 1.8 V); the first gate takes the 3.3 V comparator output.
"""
from schem import Schematic

LS_N = dict(W=2.5, L=0.5)          # input pull-downs (V_GS = vddl)
LS_P = dict(W=0.42, L=1.0)         # cross-coupled loads
INV_N = dict(W=0.84, L=0.5)        # inverters (min-length thick oxide)
INV_P = dict(W=1.68, L=0.5)


def lsup():
    s = Schematic("rt5w_lsup", ports=["in", "out", "vddl", "vdd", "vss"])
    s.text("1.8 V -> 3.3 V level shifter", -100, -400, 0.4)
    s.pmos("Mip", 0, -200, D="inb", G="in", S="vddl", B="vddl", **INV_P)
    s.nmos("Min", 0, -40, D="inb", G="in", S="vss", **INV_N)
    s.pmos("Mpa", 200, -200, D="xa", G="xb", S="vdd", B="vdd", **LS_P)
    s.pmos("Mpb", 400, -200, D="xb", G="xa", S="vdd", B="vdd", **LS_P)
    s.nmos("Mna", 200, -40, D="xa", G="in", S="vss", **LS_N)
    s.nmos("Mnb", 400, -40, D="xb", G="inb", S="vss", **LS_N)
    s.pmos("Mop", 600, -200, D="out", G="xa", S="vdd", B="vdd", **INV_P)      # xa high when in low -> out = in
    s.nmos("Mon", 600, -40, D="out", G="xa", S="vss", **INV_N)
    for net, d, x, y in [("in", "in", -80, -120), ("out", "out", 680, -120), ("vddl", "inout", -80, -320)]:
        s.port(net, d, x, y)
    s.labels_only |= {"in", "out", "inb", "xa", "xb", "vddl"}
    return s


def lsdn():
    s = Schematic("rt5w_lsdn", ports=["in", "out", "vddl", "vss"])
    s.text("3.3 V -> 1.8 V level shifter", -100, -400, 0.4)
    s.pmos("Map", 0, -200, D="mid", G="in", S="vddl", B="vddl", **INV_P)
    s.nmos("Man", 0, -40, D="mid", G="in", S="vss", **INV_N)
    s.pmos("Mbp", 200, -200, D="out", G="mid", S="vddl", B="vddl", **INV_P)
    s.nmos("Mbn", 200, -40, D="out", G="mid", S="vss", **INV_N)
    for net, d, x, y in [("in", "in", -80, -120), ("out", "out", 280, -120), ("vddl", "inout", -80, -320)]:
        s.port(net, d, x, y)
    s.labels_only |= {"in", "out", "mid", "vddl"}
    return s


def lsbank(n=8, name=None):
    """n up-shifters in one block: the vddl n-wells and the vdd n-wells merge, rails and taps are shared."""
    name = name or f"rt5w_lsbank{n}"
    s = Schematic(name, ports=[f"in{k}" for k in range(n)] + [f"out{k}" for k in range(n)] + ["vddl", "vdd", "vss"])
    s.text(f"{n} x 1.8 V -> 3.3 V level shifters", -100, -300, 0.4)
    for k in range(n):
        s.block(f"xl{k}", "rt5w_lsup.sym", 500 * k, 0, {"in": f"in{k}", "out": f"out{k}", "vddl": "vddl",
                                                       "vdd": "vdd", "vss": "vss"})
        s.port(f"in{k}", "in", -400, 600 + 40 * k)
        s.port(f"out{k}", "out", 4400, 600 + 40 * k)
    s.port("vddl", "inout", -400, 1200)
    s.labels_only |= {f"in{k}" for k in range(n)} | {f"out{k}" for k in range(n)} | {"vddl"}
    return s
