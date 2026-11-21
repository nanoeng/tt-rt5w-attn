"""Array blocks: column diode, key cell (buffered gate offset via a differential-difference amplifier), trim cell.

Key cell (open item O1, owner decision 19 Nov 2026: buffered gate offset):
  h   key voltage stored on a GROUNDED NMOS capacitor (no coupling path from dcol), written from vw (ua[2]) through a
      transmission gate while wsel is high;
  DDA two NMOS pairs on one PMOS mirror: (+dcol, -g) and (+h, -w)  =>  g = dcol + (h - w);
  Both pairs run at the same common mode: w (row trim) and h are written near the column-line level (~2.3 V on sky130), so the
  two pairs see the same V_GS, V_DS and body bias and have the same tanh transfer; then g - dcol = h - w holds even
  when V_w drives the pairs towards saturation. (With w at 1.65 V the pairs differed by ~1 V in V_DS and the key law
  bent above V_w ~ 0.1 V; isolating the bulks did not cure it and added hot leakage.)
  Mc  array PMOS, gate g:  I_cell = I_Q,c * exp(-(h - w) / nU_T,p)   (key k = exp(-(h - w)/nU_T,p), row trim w).
"""
from schem import Schematic
from units import MC, DDA_N, DDA_P, NU, SW, SWP, CAP
from bias import PUMP_P, PUMP_N


def coldiode():
    s = Schematic("rt5w_coldiode", ports=["dcol", "vdd"])
    s.text("Column diode: carries I_Q,c, sets the column line dcol", -100, -170, 0.4)
    s.pmos("Md", 0, 0, D="dcol", G="dcol", S="vdd", **MC)
    s.port("dcol", "inout", 60, 60)
    s.bus("dcol", "v", 60) if False else None
    return s


def keycell():
    s = Schematic("rt5w_keycell", ports=["dcol", "w", "vw", "wsel", "vbn", "row", "vdd", "vss"])
    s.text("Key cell: g = dcol + (h - w);  I_cell = I_Q * exp(-(h - w)/nU_T,p)", -260, -430, 0.45)
    # PMOS mirror load of the DDA
    s.pmos("Mp1", 0, -250, D="nl", G="nl", S="vdd", **DDA_P, m=2, flip=1)
    s.pmos("Mp2", 200, -250, D="g", G="nl", S="vdd", **DDA_P, m=2)
    # input pairs: + inputs drain into nl (diode side), - inputs into g (output side)
    s.nmos("M1", -120, -120, D="nl", G="dcol", S="ta", **DDA_N, flip=1)
    s.nmos("M2", 120, -120, D="g", G="g", S="ta", **DDA_N)
    s.nmos("M3", -320, -120, D="nl", G="h", S="tb", **DDA_N, flip=1)
    s.nmos("M4", 320, -120, D="g", G="w", S="tb", **DDA_N)
    s.nmos("Mt1", 0, 20, D="ta", G="vbn", S="vss", **NU)
    s.nmos("Mt2", 400, 20, D="tb", G="vbn", S="vss", **NU)
    # array transistor
    s.pmos("Mc", 600, -250, D="row", G="g", S="vdd", **MC)
    # key storage + write gate
    s.moscap("Cw", -520, 40, G="h", B="vss", **CAP)
    s.nmos("Mwn", -560, -180, D="h", G="wsel", S="vw", **SW)
    s.pmos("Mwp", -720, -180, D="h", G="wselb", S="vw", **SW)
    s.pmos("Mip", -820, -360, D="wselb", G="wsel", S="vdd", **SW)
    s.nmos("Min", -820, -260, D="wselb", G="wsel", S="vss", **SW)
    for net, d, x, y in [("dcol", "inout", -200, 60), ("w", "in", 440, 60), ("vw", "inout", -900, -100),
                         ("wsel", "in", -960, -310), ("vbn", "in", -120, 140), ("row", "inout", 700, -400)]:
        s.port(net, d, x, y)
    return s


def trimcell():
    """Row trim: storage node w (grounded NMOS cap), written from vw like a key, then nudged by the steered
    charge pump (rev 3: I_P = 3.7 nA for one 50 ns clock).  vmid is the steering dump node (= vr)."""
    s = Schematic("rt5w_trimcell", ports=["vw", "wsel", "up_b", "up", "dn", "dn_b", "pg", "ng", "vmid", "w", "vdd", "vss"])
    s.text("Row trim cell: w written from vw, then +/- one pump step per clock", -360, -420, 0.45)
    s.pmos("Mpu", 0, -260, D="pu", G="pg", S="vdd", **PUMP_P)
    s.pmos("Msu", 0, -140, D="w", G="up_b", S="pu", **SW)
    s.pmos("Msub", 200, -140, D="vmid", G="up", S="pu", **SW)
    s.nmos("Msd", 0, 40, D="w", G="dn", S="nd", **SW)
    s.nmos("Msdb", 200, 40, D="vmid", G="dn_b", S="nd", **SW)
    s.nmos("Mnd", 0, 160, D="nd", G="ng", S="vss", **PUMP_N)
    s.moscap("Cw", -160, 100, G="w", B="vss", **CAP)
    s.nmos("Mwn", -320, -60, D="w", G="wsel", S="vw", **SW)
    s.pmos("Mwp", -480, -60, D="w", G="wselb", S="vw", **SW)
    s.pmos("Mip", -620, -260, D="wselb", G="wsel", S="vdd", **SW)
    s.nmos("Min", -620, -160, D="wselb", G="wsel", S="vss", **SW)
    for net, d, x, y in [("vw", "inout", -680, 20), ("wsel", "in", -760, -210), ("pg", "in", -100, -300),
                         ("ng", "in", -100, 200), ("up_b", "in", -80, -180), ("up", "in", 120, -180),
                         ("dn", "in", -80, 0), ("dn_b", "in", 120, 0), ("vmid", "inout", 320, -60),
                         ("w", "out", 120, -60)]:
        s.port(net, d, x, y)
    return s


def pumpinv():
    """Complements of a row's pump strobes for the steered pump (up_b drives the PMOS switch, dn_b the dump)."""
    s = Schematic("rt5w_pumpinv", ports=["up", "dn", "upb", "dnb", "vdd", "vss"])
    s.text("Pump strobe inverters", -100, -260, 0.4)
    s.pmos("Mupp", 0, -120, D="upb", G="up", S="vdd", **SWP)
    s.nmos("Mupn", 0, 40, D="upb", G="up", S="vss", **SW)
    s.pmos("Mdnp", 200, -120, D="dnb", G="dn", S="vdd", **SWP)
    s.nmos("Mdnn", 200, 40, D="dnb", G="dn", S="vss", **SW)
    for net, d, x, y in [("up", "in", -80, -40), ("dn", "in", 120, -40), ("upb", "out", 60, -40),
                         ("dnb", "out", 260, -40)]:
        s.port(net, d, x, y)
    s.labels_only |= {"up", "dn", "upb", "dnb"}
    return s


def array_top():
    """4 x 4 array: column IDACs -> column diodes (dcol_i), key cells (row_j = sum_i I_cell,ji), row trims w_j.
    Row 0's trim cell has its pump tied off (pinned row); rows 1..3 get local up/dn complements."""
    ports = ([f"q{i}_{b}" for i in range(4) for b in range(4)] + [f"nd{i}" for i in range(4)] +
             ["vbn", "vw"] + [f"wsel{k}" for k in range(20)] +
             [f"pump_up{j}" for j in (1, 2, 3)] + [f"pump_dn{j}" for j in (1, 2, 3)] +
             ["pg", "ng", "vmid"] + [f"row{j}" for j in range(4)] + ["vdd", "vss"])
    s = Schematic("rt5w_array", ports=ports)
    s.text("4 x 4 key array: IDAC(q_i) -> dcol_i;  row_j = sum_i I_Q exp(-(h_ji - w_j)/nU_T,p);  trims w_j", 0, -900, 0.6)
    for i in range(4):
        x = 600 * i
        s.block(f"xq{i}", "rt5w_idac4.sym", x, -700, dict(nd=f"nd{i}", b0=f"q{i}_0", b1=f"q{i}_1", b2=f"q{i}_2",
                                                         b3=f"q{i}_3", col=f"dcol{i}", vss="vss"))
        s.block(f"xd{i}", "rt5w_coldiode.sym", x + 260, -560, dict(dcol=f"dcol{i}", vdd="vdd"))
        for j in range(4):
            s.block(f"xc{j}{i}", "rt5w_keycell.sym", x, -300 + 300 * j,
                    dict(dcol=f"dcol{i}", w=f"w{j}", vw="vw", wsel=f"wsel{4 * j + i}", vbn="vbn", row=f"row{j}",
                         vdd="vdd", vss="vss"))
    for j in range(4):
        y = -300 + 300 * j
        if j == 0:
            pump = dict(up_b="vdd", up="vss", dn="vss", dn_b="vdd")
        else:
            pump = dict(up_b=f"upb{j}", up=f"pump_up{j}", dn=f"pump_dn{j}", dn_b=f"dnb{j}")
            s.block(f"xpi{j}", "rt5w_pumpinv.sym", 2900, y,
                    dict(up=f"pump_up{j}", dn=f"pump_dn{j}", upb=f"upb{j}", dnb=f"dnb{j}", vdd="vdd", vss="vss"))
        s.block(f"xt{j}", "rt5w_trimcell.sym", 2500, y,
                dict(vw="vw", wsel=f"wsel{16 + j}", pg="pg", ng="ng", vmid="vmid", w=f"w{j}", vdd="vdd", vss="vss",
                     **pump))
    s.labels_only |= set(p for p in ports if p not in ("vdd", "vss")) | {f"dcol{i}" for i in range(4)} | \
        {f"w{j}" for j in range(4)} | {f"upb{j}" for j in (1, 2, 3)} | {f"dnb{j}" for j in (1, 2, 3)}
    for k, p in enumerate(p for p in ports if p not in ("vdd", "vss")):
        d = "out" if p.startswith("row") else ("inout" if p == "vw" else "in")
        s.port(p, d, -600 + 160 * (k // 20), -800 + 40 * (k % 20) + 1400 * 0)
    return s
