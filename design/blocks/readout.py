"""Readout: one-hot channel mux, 8-bit binary current DAC, integrating comparator (StrongARM + NAND SR latch),
pseudo-differential against a replica node intr.

Per SAR bit (ADCT clocks): adc_rst resets the integration node 'int' to vr; the selected softmax output (sourced,
4 x share x I_sum = 16 I_u x a_j) and the DAC (sunk, code x I_u/16) integrate on int; adc_lat fires the StrongARM
latch, and the SR latch holds cmp = 1 when I_share > I_dac (int rose above vr) until the next adc_lat.
Each output feeds a PMOS common-gate cascode to int (selected) or to the vr dump, so the outputs never move and
their drain capacitance stays off the integration node.
DAC switch cascodes at L = 2 um and a leak-free replica dummy (source at vr): no off cascode leaks charge at 125 C.
Textbook layout: mux on the left, integration node and reset in the middle, DAC bank below, comparator on the right."""
from schem import Schematic
from units import DAC_U, SA_IN, SW, SWP, CASP, PU
from sizing import dev

UNIT = DAC_U                   # DAC unit sink: I_u/16 against the m=16 diode fed by ndac (= I_u)
DIODE_T = dict(UNIT, W=round(UNIT["W"] * 1.013 / 0.005) * 0.005)     # = 4.74 um (see Mdd)
MUXP = dev("p", 16 * 125e-9, ("gmid", 15), L=0.5, tag="mux cascode @ 16 I_u")
PCAS = dev("p", 125e-9, ("gmid", 10), L=0.5, tag="pcas diodes @ I_u")
DCAS = dev("n", 125e-9 / 16, ("gmid", 15), L=0.5, tag="DAC unit cascode @ I_u/16")
# DAC switch cascodes at L = 1 um (same W): an off cascode (gate at vss, source sk ~ 0) leaks ~10x less than at
# L = 0.5 (nfet_g5v0d10v5, ff / 125 C, V_GS = 0, per 0.84 um of W: 57 pA vs 0.52 nA). With 255 units at L = 0.5
# the off-bit leakage was up to ~100 nA (~10 LSB at ff); still weak inversion at I_u/16, V_DS,sat ~ 0.1 V.
DCASL = dict(W=DCAS["W"], L=1.0)
SWU = DCASL                    # steering-switch unit (W0.42 / L1)
SA_X = dev("n", 2e-6, ("gmid", 12), L=0.5, tag="StrongARM cross / tail @ 2 uA")
# swing clamps on int / intr (21 Nov): without them int ran to the rails on the coarse SAR bits (+-1.1..1.7 V), the
# input cascodes / DAC cascodes left saturation and kicked the softmax output mirrors and ndac through C_gd, so
# every SAR trial depended on the previous one (continuous-transient chain error 59..64 LSB). A clamp is a single
# NMOS (pull-up when int < vr) or PMOS (pull-down when int > vr) between int and vr, gate biased by a diode replica
# 8x wider carrying one DAC unit (I_u/16): the clamp carries ~I_u/128 at |int - vr| = 0 V_GS excess and grows
# exponentially beyond, so it holds |int - vr| to n U_T ln(I_max / (I_u/128)) ~ 0.3..0.5 V. A clamp only pulls int
# toward vr, so it can never flip the comparator's sign; intr carries identical clamps (no current at intr = vr).
CLAMP = dict(W=0.42, L=0.5)
# local static gate bias of the DAC cascodes (vcl): their drains swing ~1 V at a bit switch and couple into the gate
# line through C_gd; on the shared vcas (nA bias, also the softmax's) that kick would recover slowly. vcl = NMOS
# diode at 16 I_u (1/g_m ~ 25 kOhm) recovers in a few ns. (Gate-switched cascodes charged from vcas pulled it from
# 1.15 V to 0.5..0.9 V at every trial start.)
# W0.58/L2 at 2 uA: 1.16 / 1.23 / 1.07 V (tt / ss / ff), = the bias block's vcas (1.15 / 1.20 / 1.12 V).
VCL = dict(W=0.58, L=2.0)


def readout():
    ports = (["out0", "out1", "out2", "out3", "ndac", "vcas", "vr"] + [f"adc_ch{j}" for j in range(4)] +
             ["adc_rst", "adc_lat"] + [f"dac{k}" for k in range(8)] + ["cmp", "vdd", "vss"])
    s = Schematic("rt5w_readout", ports=ports)
    s.text("Readout: one-hot mux -> int, 8-bit binary current DAC (unit I_u/16), integrating StrongARM comparator",
           -1000, -1150, 0.5)
    # ---- mux: PMOS common-gate cascodes. Each softmax output sees a cascode source at all times (to int when
    # selected, to the vr dump otherwise), so the output node never moves and its large drain capacitance is kept
    # off int. Gate drivers swing between vdd (off) and pcas (on).
    for j in range(4):
        y = -900 + 260 * j
        s.pmos(f"Mcs{j}", -200, y, D="int", G=f"gs{j}", S=f"out{j}", **MUXP)
        s.pmos(f"Mcd{j}", -360, y, D="vr", G=f"gd{j}", S=f"out{j}", **MUXP, flip=1)
        s.pmos(f"Mib{j}p", -560, y - 60, D=f"chb{j}", G=f"adc_ch{j}", S="vdd", **SWP)
        s.nmos(f"Mib{j}n", -560, y + 60, D=f"chb{j}", G=f"adc_ch{j}", S="vss", **SW)
        s.pmos(f"Mgs{j}p", -720, y - 60, D=f"gs{j}", G=f"adc_ch{j}", S="vdd", **SWP)
        s.nmos(f"Mgs{j}n", -720, y + 60, D=f"gs{j}", G=f"adc_ch{j}", S="pcas", **SWP)
        s.pmos(f"Mgd{j}p", -880, y - 60, D=f"gd{j}", G=f"chb{j}", S="vdd", **SWP)
        s.nmos(f"Mgd{j}n", -880, y + 60, D=f"gd{j}", G=f"chb{j}", S="pcas", **SWP)
        s.port(f"out{j}", "in", -280, y - 80)
        s.port(f"adc_ch{j}", "in", -1000, y)
    # pcas = vdd - 2 |V_GS| at I_u (two stacked PMOS diodes, sunk by an I_u copy of the DAC diode)
    s.pmos("Mpb1", -1100, -620, D="pb1", G="pb1", S="vdd", **PCAS)
    s.pmos("Mpb2", -1100, -480, D="pcas", G="pcas", S="pb1", **PCAS)
    s.nmos("Mpbn", -1100, -320, D="pcas", G="ndac", S="vss", **UNIT, m=16)
    s.moscap("Cpc", -1260, -320, G="pcas", B="vss", W=6, L=6)
    s.pmos("Mvp", -1420, -620, D="vcl", G="pb1", S="vdd", **PCAS, m=16)
    s.nmos("Mvl", -1420, -320, D="vcl", G="vcl", S="vss", **VCL)
    s.moscap("Cvc", -1580, -320, G="vcas", B="vss", W=6, L=6)        # vcas now only decoupled here (softmax bias)
    # ---- integration node and its replica 'intr' (pseudo-differential): both reset to vr by identical switches,
    # (no explicit caps: C = parasitics ~0.2 pF), and intr carries dummy copies of every device hanging on int, so reset charge injection and
    # StrongARM kickback are common-mode; only the integrated (I_share - I_dac) T / C is differential.
    s.nmos("Mrst", 100, -620, D="int", G="adc_rst", S="vr", **SWP)
    # ---- swing clamps (see CLAMP): upper = PMOS int -> vr, gate cgp = vr - V_SG(I_u/16, 8x); lower = NMOS
    # vr -> int, gate cgn = vr + V_GS(I_u/16, 8x)
    s.pmos("Mcu", 100, -1050, D="vr", G="cgp", S="int", **CLAMP)
    s.nmos("Mcl", 260, -1050, D="vr", G="cgn", S="int", **CLAMP)
    s.pmos("Mcur", 420, -1050, D="vr", G="cgp", S="intr", **CLAMP)
    s.nmos("Mclr", 580, -1050, D="vr", G="cgn", S="intr", **CLAMP)
    s.pmos("Mru", 740, -1050, D="cgp", G="cgp", S="vr", **CLAMP, m=8)
    s.nmos("Mku", 900, -1050, D="cgp", G="ndac", S="vss", **UNIT)
    s.nmos("Mrl", 1060, -1050, D="cgn", G="cgn", S="vr", **CLAMP, m=8)
    s.pmos("Mpm", 1220, -1050, D="pm", G="pm", S="vdd", **PCAS)
    s.nmos("Mku2", 1380, -1050, D="pm", G="ndac", S="vss", **UNIT)
    s.pmos("Mpm2", 1540, -1050, D="cgn", G="pm", S="vdd", **PCAS)
    
    s.nmos("Mrstr", 2340, -620, D="intr", G="adc_rst", S="vr", **SWP)
    s.pmos("Mdcs", 2500, -620, D="intr", G="vdd", S="vr", **MUXP, m=4)      # = 4 x Mcs drains
    # = the DAC switch drains on int (Mon, 34 SWU units in all); source at vr, gate at vss: no current (a vss-sourced
    # dummy leaked ~100 nA off intr at ff/125 C)
    s.nmos("Mdsw", 2660, -620, D="intr", G="vss", S="vr", **SWU, m=34)
    
    # ---- DAC: cascoded binary sinks (unit I_u/16) steered at the cascode drain (see below); the m=16 diode is
    # cascoded the same way, so the units run at the diode's V_DS.
    s.nmos("Mdc", 200, -40, D="ndac", G="vcas", S="nd2", **SWU, m=2, flip=1)   # = a conducting switch at 8 units / SWU; steady gate
    # DAC reference trim (21 Nov): measured with int forced to vr (scripts/dac_gain_check.py), the DAC sinks
    # +0.55 % (tt; +0.8 % ff) over 255 I_u/16 (units at V_DS = sk vs the diode at nd2) and the softmax-type output
    # mirror delivers -1.0 % at full scale through the mux cascode (finite r_o): SAR gain -1.6 % (255 -> 251).
    # The m=16 diode is 1.3 % wider (4.74 vs 4.68 um), so every unit carries 1.3 % less (systematic ratio trim).
    s.nmos("Mdd", 200, 200, D="nd2", G="ndac", S="vss", **DIODE_T, m=16, flip=1)
    for k in range(8):
        x = 400 + 240 * k
        s.pmos(f"Mdi{k}p", x, -720, D=f"dacb{k}", G=f"dac{k}", S="vdd", **SWP)
        s.nmos(f"Mdi{k}n", x, -580, D=f"dacb{k}", G=f"dac{k}", S="vss", **SW)
        # current-steering cell (21 Nov): the units' drain sk is steered to int (Mon) or dumped to vdd (Mof) by two
        # equal cascoded switches whose gates toggle between vss and vcl; the conducting one sets sk = vcl - V_GS in
        # both states, so the units and ndac never see a bit switch, int sees the same switch drains at every code
        # (constant C_int, matched by the dummy on intr), and an off switch has V_GS = -sk (no 125 C leakage).
        # Switch size: m_k = max(1, 2^k / 8) units of SWU (up to 8 DAC units per switch unit).
        mk = max(1, 2 ** k // 8)
        s.nmos(f"Mon{k}", x, -40, D="int", G=f"gon{k}", S=f"sk{k}", **SWU, m=mk)
        s.nmos(f"Mof{k}", x + 120, -40, D="vdd", G=f"gof{k}", S=f"sk{k}", **SWU, m=mk)
        s.nmos(f"Mgn{k}p", x, -400, D="vcl", G=f"dac{k}", S=f"gon{k}", **SWP)
        s.nmos(f"Mgn{k}n", x, -240, D=f"gon{k}", G=f"dacb{k}", S="vss", **SW)
        s.nmos(f"Mgf{k}p", x + 120, -400, D="vcl", G=f"dacb{k}", S=f"gof{k}", **SWP)
        s.nmos(f"Mgf{k}n", x + 120, -240, D=f"gof{k}", G=f"dac{k}", S="vss", **SW)
        s.nmos(f"Mu{k}", x, 200, D=f"sk{k}", G="ndac", S="vss", **UNIT, m=2 ** k)
        s.port(f"dac{k}", "in", x - 100, -650)
    s.bus("ndac", "h", 300)
    # ---- StrongARM latch: int vs vr, clocked by adc_lat
    X = 2600
    s.nmos("Mtl", X + 100, 200, D="tl", G="adc_lat", S="vss", **SA_X, m=2)
    s.nmos("M1a", X, 60, D="xa", G="int", S="tl", **SA_IN, flip=1)
    s.nmos("M1b", X + 200, 60, D="xb", G="intr", S="tl", **SA_IN)
    s.nmos("M2a", X, -80, D="oa", G="ob", S="xa", **SA_X, flip=1)
    s.nmos("M2b", X + 200, -80, D="ob", G="oa", S="xb", **SA_X)
    s.pmos("M3a", X, -240, D="oa", G="ob", S="vdd", **SA_X, flip=1)
    s.pmos("M3b", X + 200, -240, D="ob", G="oa", S="vdd", **SA_X)
    s.pmos("Mra", X - 160, -240, D="oa", G="adc_lat", S="vdd", **SWP, flip=1)
    s.pmos("Mrb", X + 360, -240, D="ob", G="adc_lat", S="vdd", **SWP)
    s.pmos("Mrxa", X - 160, -80, D="xa", G="adc_lat", S="vdd", **SWP, flip=1)
    s.pmos("Mrxb", X + 360, -80, D="xb", G="adc_lat", S="vdd", **SWP)
    # ---- NAND SR latch: cmp = NAND(oa, cmpb), cmpb = NAND(ob, cmp)
    Y = 3300
    for q, a, qb, x in (("cmp", "oa", "cmpb", Y), ("cmpb", "ob", "cmp", Y + 300)):
        s.pmos(f"Mp_{q}a", x, -240, D=q, G=a, S="vdd", **SWP)
        s.pmos(f"Mp_{q}b", x + 120, -240, D=q, G=qb, S="vdd", **SWP)
        s.nmos(f"Mn_{q}a", x, -80, D=q, G=a, S=f"n_{q}", **SWP)
        s.nmos(f"Mn_{q}b", x, 60, D=f"n_{q}", G=qb, S="vss", **SWP)
    for net, d, x, y in [("ndac", "in", 40, 120), ("vcas", "in", 120, -60), ("vr", "in", -440, -660), ("adc_rst", "in", 20, -480),
                         ("adc_lat", "in", X - 20, 260), ("cmp", "out", Y + 40, -360)]:
        s.port(net, d, x, y)
    s.labels_only |= {"vcl", "cgp", "cgn", "pm", "vr", "int", "intr", "pcas", "ndac", "vcas", "adc_rst", "adc_lat", "oa", "ob", "cmp", "cmpb", "xa", "xb"}
    return s
