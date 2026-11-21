"""Softmax core (rev 2b design of record), on the release models: scores arrive as row currents into g0..g3,
R_c of res_xhigh_po_0p35 (the bias R_b type) to vr, sized so that the full chain meets x = 0.3 q k (tb_chain); exponentiators Me0..3 with body on vss (no deep n-well on sky130: the common source V_B multiplies every Me current by the same exp(-V_B/U_T), so the shares stay softmax(V_g / nU_T); V_B/LSE slope is absorbed by VBCAL); AGC tail = 4 x nbias;
keep-alive I_K at each PMOS diode, given back at the outputs. Change for the readout: each output mirror is x4
(Mo m=16, give-back Mr m=4), so the SAR sees 4 x share x I_sum.
Textbook layout: row resistors on top, exponentiators in a row on the V_B line, PMOS diodes/outputs above, tail below."""
from schem import Schematic
from units import SM_P, SM_E, NU, CASN
from sizing import dev

RC_L = 244.0      # um of res_xhigh_po_0p35: R_c = 18 nU_T,n / (4 I_u) = 1.96 MOhm (x = 18 at the full row current)
KA = dev("n", 125e-9 / 25, ("sigma_i", 0.10), tag="softmax keep-alive @ I_u/25")
CB = dict(W=15, L=15)


def softmax():
    s = Schematic("rt5w_softmax", ports=["g0", "g1", "g2", "g3", "nbias", "kbias", "vr", "vcas",
                                          "vb", "out0", "out1", "out2", "out3", "vdd", "vss"])
    s.text("Softmax core: I_out,j = 4 I_sum exp(x_j)/sum exp(x_k),  V_B = log-sum-exp", -200, -720, 0.5)
    for j in range(4):
        x = 300 * j
        s.pmos(f"Mp{j}", x, -480, D=f"dp{j}", G=f"dp{j}", S="vdd", **SM_P, m=4, flip=1)
        s.pmos(f"Mo{j}", x + 160, -480, D=f"out{j}", G=f"dp{j}", S="vdd", **SM_P, m=16)
        s.nmos(f"Mk{j}", x - 60, -320, D=f"dp{j}", G="kbias", S="vss", **KA)
        s.nmos(f"Mr{j}", x + 220, -320, D=f"out{j}", G="kbias", S="vss", **KA, m=4)
        s.nmos(f"Me{j}", x, -180, D=f"dp{j}", G=f"g{j}", S="vb", B="vss", **SM_E, m=4)
        s.res(f"Rc{j}", x - 120, -40, P="vr", M=f"g{j}", B="vss", L=RC_L)
        s.port(f"g{j}", "in", x - 60, -120)
        s.port(f"out{j}", "out", x + 240, -560)
    s.bus("vb", "h", -130)
    s.nmos("Mcas", 300, 40, D="vb", G="vcas", S="tc", **CASN)
    s.nmos("Mtail", 300, 160, D="tc", G="nbias", S="vss", **NU, m=16)
    s.nmos("Mbc", 0, 40, D="nbias", G="vcas", S="nbm", **CASN, flip=1)
    s.nmos("Mbias", 0, 160, D="nbm", G="nbias", S="vss", **NU, m=4, flip=1)
    s.nmos("Mkb", 600, 160, D="kbias", G="kbias", S="vss", **KA)
    s.moscap("Cb", 760, 40, G="vb", B="vss", **CB)
    for net, d, x, y in [("nbias", "in", -120, 0), ("vcas", "in", 160, 100), ("kbias", "in", 640, 100),
                         ("vr", "in", -240, 40), ("vb", "out", 1000, -130)]:
        s.port(net, d, x, y)
    s.bus("vr", "h", 20)
    return s
