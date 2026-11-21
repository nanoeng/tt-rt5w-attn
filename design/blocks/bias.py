"""Bias generator and references (sky130A, 3.3 V g5v0d10v5 devices; sizes from sizing.dev / units.py).

Core: cascoded weak-inversion beta multiplier, K = 8 (M1 = 4 units, M2 = 32 units of the NMOS I_u unit), R_b of
res_xhigh_po_0p35, the SAME resistor type as the softmax R_c, so I_ref = nU_T ln K / R_b tracks R_c and the score
scale x = I R_c / nU_T has no resistor tempco. I_ref = 4 I_u = 0.5 uA. The PMOS mirror M3/M4 is 4 units of the
PMOS distribution unit, so every PMOS copy of I_u downstream is one unit (one geometry everywhere = ratio by count).
Cascode gates come from self-biased stacks fed by copies of the core current (no ideal sources).
Start-up: Mi1 (gate n1, a mirror of M1) against a weak always-on pull-up Mi2a-d; Ms3 pulls p2 down while the
core is off; the vcp stack is fed from vcn so the cascode gates come up as soon as p2 is pulled down.

Gating with keep-alive: the core always runs; its output copy feeds the distribution through a switch (bias_en)
with an always-on leg in parallel (~1 %), so every downstream current drops to ~1 % when gated.
Distribution (unit I_u = I_ref / 4 = 125 nA):
  nbias   softmax AGC unit        I_u
  kbias   keep-alive unit         I_u / 25 = 5 nA
  nd0..3  IDAC LSB feeds          I_u / 15 = 8.33 nA each
  ndac    DAC unit feed           I_u (the DAC divides by 16)
  vbn     key-cell DDA tails      gate voltage, I_u per tail
  pg, ng  trim pump gates         I_u / 34 = 3.7 nA
  vcas    tail / DAC cascode      diode at I_u (strong inversion, long L: headroom for the cascoded sinks)
  vr      softmax / readout reference   PMOS source follower from the divider tap vrg
  vmid    trim steering dump, ~ the key-write level W_REF (divider tap)
"""
from schem import Schematic
from units import NU, PU, CASN, CASP, HEAD_N, HEAD_P, SW, SWP
from sizing import dev

RB_L = 24.5         # um of res_xhigh_po_0p35 (tuned in tb_bias so that I_u = 125 nA at tt 27 C)
R_UNIT_L = 8.75     # um: 50 kOhm divider unit (res_xhigh_po_0p35, ~2 kOhm/sq)
DIV_UNITS = 30      # 1.5 MOhm, 2.2 uA
TAP_VMID = 9        # units from the top: vmid = 3.3 (1 - 9/30) = 2.31 V
TAP_VRG = 24        # units from the top: vrg = 3.3 * 6/30 = 0.66 V -> vr = vrg + |V_GS,p| ~ 1.65 V
FOLLOW = dev("p", 1.5e-6, ("gmid", 18), L=1, tag="vr follower @ 1.5 uA (sinks the four R_c currents)")
WEAK = dict(W=0.42, L=20)   # start-up pull-up: deliberately weak (4 in series, far below I_ref)
PD = dev("p", 125e-9, ("gmid", 16), L=2, tag="vcp stack diodes @ I_u")
VCD = dev("n", 125e-9, ("gmid", 4), L=20, tag="vcas diode @ I_u (strong inv., V_GS ~1.2 V)")
CC = dev("n", 500e-9, ("gmid", 17), L=1, tag="core NMOS cascode @ I_ref (weak inv.: low V_GS)")


def bias():
    s = Schematic("rt5w_bias", ports=["bias_en", "nbias", "kbias", "nd0", "nd1", "nd2", "nd3", "ndac", "vbn",
                                       "pg", "ng", "vcas", "vr", "vmid", "iref", "vdd", "vss"])
    s.text("Bias: beta multiplier (R_b = res_xhigh_po, tracks R_c), 1 % keep-alive gate, distribution", -300, -760, 0.5)
    # ---- beta multiplier core
    s.nmos("M1", 0, 0, D="n1", G="n1", S="vss", **NU, m=4, flip=1)
    s.nmos("M2", 200, 0, D="n2c", G="n1", S="s2", **NU, m=32)
    s.res("Rb", 220, 140, P="s2", M="vss", B="vss", L=RB_L)
    s.nmos("M1c", 0, -120, D="p1", G="vcn", S="n1", **CC, flip=1)
    s.nmos("M2c", 200, -120, D="p2", G="vcn", S="n2c", **CC, m=8)
    s.pmos("M3c", 0, -260, D="p1", G="vcp", S="a3", **CASP, flip=1)
    s.pmos("M4c", 200, -260, D="p2", G="vcp", S="a4", **CASP)
    s.pmos("M3", 0, -380, D="a3", G="p2", S="vdd", **PU, m=4, flip=1)
    s.pmos("M4", 200, -380, D="a4", G="p2", S="vdd", **PU, m=4)
    # cascode gate stacks, fed by I_u copies of the core current.  vcn = two stacked weak-inversion diodes (NU):
    # M1c's source sits on the diode n1, so vcn = V_GS(M1) + V_GS(M1c) (~1.7 V) puts n2c at n1 (V_DS match M1/M2).
    # vcp = vdd - two PMOS diodes (~1.2 V); its sink Mcpi mirrors the bottom vcn diode (x8), so vcp comes up with vcn.
    s.pmos("Mcp1", 560, -380, D="x7", G="x7", S="vdd", **PD)
    s.pmos("Mcp2", 560, -260, D="vcp", G="vcp", S="x7", **PD)
    s.nmos("Mcpi", 560, 0, D="vcp", G="x8", S="vss", **NU)
    s.pmos("Mcn1", 720, -380, D="vcn", G="p2", S="vdd", **PU)
    s.nmos("Mcn2", 720, -120, D="vcn", G="vcn", S="x8", **NU)
    s.nmos("Mcn3", 720, 0, D="x8", G="x8", S="vss", **NU)
    # start-up: Mi1 mirrors the core current against a weak always-on pull-up; Ms3 pulls p2 down while it is off
    s.nmos("Mi1", -200, 0, D="b8", G="n1", S="vss", **NU, m=12, flip=1)   # 3 I_ref vs ~0.1 uA pull-up
    for k, (d, src) in enumerate([("b8", "u1"), ("u1", "u2"), ("u2", "u3"), ("u3", "vdd")]):
        s.pmos(f"Mi2{'abcd'[k]}", -360, -20 - 120 * k, D=d, G="vss", S=src, B="vdd", **WEAK, flip=1)
    s.nmos("Ms3", -520, -200, D="p2", G="b8", S="vss", W=0.84, L=2, flip=1)   # longer L: no leakage from p2 when off
    # ---- core output copy (4 I_u), gate with keep-alive leg
    s.pmos("M7", 900, -380, D="a7", G="p2", S="vdd", **PU, m=4)
    s.pmos("M7c", 900, -260, D="a7c", G="vcp", S="a7", **CASP)
    s.pmos("Msw", 900, -140, D="root", G="bias_enb", S="a7c", **SWP)
    s.pmos("M7k", 1080, -380, D="root", G="p2", S="vdd", W=1.0, L=20)   # ~1 % of 4 I_u (narrow-width current excess measured in tb_bias)
    s.pmos("Mib1", 1080, -140, D="bias_enb", G="bias_en", S="vdd", **SWP)
    s.nmos("Mib2", 1080, 0, D="bias_enb", G="bias_en", S="vss", **SW)
    # root: NMOS diode carrying I_ref (4 units of I_u)
    s.nmos("Mr", 1240, 0, D="root", G="root", S="vss", **NU, m=4)
    # ---- PMOS distribution diode: an NMOS copy of I_u sinks from the PMOS diode 'pu'
    s.nmos("Mpu_n", 1560, 0, D="pu", G="root", S="vss", **NU)
    s.pmos("Mpu", 1560, -380, D="pu", G="pu", S="vdd", **PU)
    s.pmos("Mo_nb", 1720, -380, D="nbias", G="pu", S="vdd", **PU)            # I_u
    s.pmos("Mo_dac", 1880, -380, D="ndac", G="pu", S="vdd", **PU)            # I_u
    s.pmos("Mo_ir", 1400, -380, D="iref", G="pu", S="vdd", **PU)             # I_u monitor to ua[0]
    s.pmos("Mo_vbn", 2040, -380, D="vbn", G="pu", S="vdd", **PU)
    s.nmos("Mvbn_d", 2040, 0, D="vbn", G="vbn", S="vss", **NU)               # DDA tail geometry
    # IDAC LSB feeds: PMOS diode of 15 units fed by I_u -> I_u/15 per unit copy
    s.nmos("Ml_n", 2200, 0, D="pl", G="root", S="vss", **NU)
    s.pmos("Ml", 2200, -380, D="pl", G="pl", S="vdd", **PU, m=15)
    for c in range(4):
        s.pmos(f"Mo_nd{c}", 2360 + 160 * c, -380, D=f"nd{c}", G="pl", S="vdd", **PU)
    # keep-alive unit I_u/25 for kbias
    s.nmos("Mk_n", 3040, 0, D="pk", G="root", S="vss", **NU)
    s.pmos("Mk", 3040, -380, D="pk", G="pk", S="vdd", **PU, m=25)
    s.pmos("Mo_kb", 3200, -380, D="kbias", G="pk", S="vdd", **PU)
    # pump gates: I_u/34 in a PMOS diode (pg) and an NMOS diode (ng) of the pump device geometry
    s.nmos("Mp_n", 3360, 0, D="pp", G="root", S="vss", **NU)
    s.pmos("Mpp", 3360, -380, D="pp", G="pp", S="vdd", **PU, m=34)
    s.pmos("Mpg", 3520, -380, D="pg", G="pg", S="vdd", **PUMP_P)
    s.pmos("Mo_ng", 3680, -380, D="ng", G="pp", S="vdd", **PU)
    s.nmos("Mng", 3680, 0, D="ng", G="ng", S="vss", **PUMP_N)
    s.nmos("Mpg_n", 3520, 0, D="pg", G="ng", S="vss", **PUMP_N)
    # vcas: diode at I_u in strong inversion (long L)
    s.pmos("Mo_vc", 3840, -380, D="vcas", G="pu", S="vdd", **PU)
    s.nmos("Mvc", 3840, 0, D="vcas", G="vcas", S="vss", **VCD)
    # ---- references: divider of res_xhigh_po units + PMOS follower for vr
    taps = {TAP_VMID: "vmid", TAP_VRG: "vrg"}
    for k in range(DIV_UNITS):
        top = "vdd" if k == 0 else taps.get(k, f"rd{k}")
        bot = "vss" if k == DIV_UNITS - 1 else taps.get(k + 1, f"rd{k + 1}")
        s.res(f"Rd{k}", 4040, -380 + 60 * k, P=top, M=bot, B="vss", L=R_UNIT_L)
    s.pmos("Mvr", 4240, -40, D="vss", G="vrg", S="vr", B="vr", **FOLLOW)
    s.pmos("Mvrb", 4240, -380, D="vr", G="pu", S="vdd", **PU)
    for net, d, x, y in [("bias_en", "in", 1000, 60), ("nbias", "out", 1760, -300), ("ndac", "out", 1920, -300),
                         ("vbn", "out", 2080, -300), ("kbias", "out", 3240, -300), ("pg", "out", 3560, -300),
                         ("ng", "out", 3720, -300), ("vcas", "out", 3880, -300), ("vr", "out", 4320, -200),
                         ("vmid", "out", 4320, -260), ("iref", "out", 1440, -300)] + [(f"nd{c}", "out", 2400 + 160 * c, -300) for c in range(4)]:
        s.port(net, d, x, y)
    s.labels_only |= {"p2", "vcp", "vcn", "root", "pu", "pl", "pk", "pp", "n1", "bias_enb"}
    return s


PUMP_P = dev("p", 125e-9 / 34, ("sigma_i", 0.10), tag="trim pump PMOS @ I_u/34")
PUMP_N = dev("n", 125e-9 / 34, ("sigma_i", 0.10), tag="trim pump NMOS @ I_u/34")
