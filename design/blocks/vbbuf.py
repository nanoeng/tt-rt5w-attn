"""V_B probe buffer: two-stage Miller op amp in unity gain -- NMOS pair (4 I_u, input range to ~3 V), PMOS
common-source output (32 I_u sink) so ua[1] follows V_B over 1.2..2.4 V; biased from vbn; output to ua[1]
through a transmission gate. Disabled: tail gate pulled to vss, output TG open (ua[1] high-Z)."""
from schem import Schematic
from units import BUF_IN, BUF_P, NU, SW, SWP
from sizing import dev

MO = dev("p", 32 * 125e-9, ("gmid", 12), L=0.5, tag="V_B buffer output PMOS @ 32 I_u")
TGN, TGP = dict(W=4, L=0.5), dict(W=8, L=0.5)   # output TG: sized for on-resistance (~10 kOhm), not by gm/ID


def vbbuf():
    s = Schematic("rt5w_vbbuf", ports=["vb", "vbn", "en", "pad", "vdd", "vss"])
    s.text("V_B buffer: unity-gain two-stage Miller op amp, TG to ua[1]", -200, -620, 0.5)
    s.pmos("Ml1", 0, -440, D="d1", G="d1", S="vdd", **BUF_P, flip=1)
    s.pmos("Ml2", 240, -440, D="o1", G="d1", S="vdd", **BUF_P)
    s.nmos("Mi1", 0, -260, D="d1", G="bo", S="tl", **BUF_IN, flip=1)
    s.nmos("Mi2", 240, -260, D="o1", G="vb", S="tl", **BUF_IN)
    s.nmos("Mt", 120, -80, D="tl", G="tg", S="vss", **NU, m=4)
    # second stage: PMOS common source (rail-to-rail output for V_B up to ~2.4 V), 32 I_u sink, Miller cap = PMOS
    # in its own n-well (channel and well on o1, gate on the output)
    s.pmos("Mo", 560, -440, D="bo", G="o1", S="vdd", **MO)
    s.nmos("Mos", 560, -80, D="bo", G="tg", S="vss", **NU, m=32)
    s.moscap("Cc", 400, -300, G="bo", B="o1", W=20, L=20, kind="pmos")
    s.pmos("Moff", 400, -560, D="o1", G="en", S="vdd", **SW)      # disabled: o1 high, Mo off
    # enable: tail gate = vbn (en) or vss (enb)
    s.nmos("Men1", -200, -80, D="vbn", G="en", S="tg", **SW, flip=1)
    s.nmos("Men2", -200, 60, D="tg", G="enb", S="vss", **SW, flip=1)
    s.pmos("Minp", -400, -200, D="enb", G="en", S="vdd", **SWP)
    s.nmos("Minn", -400, -60, D="enb", G="en", S="vss", **SW)
    # output TG to the pad
    s.nmos("Mtgn", 800, -260, D="bo", G="en", S="pad", **TGN)
    s.pmos("Mtgp", 800, -440, D="bo", G="enb", S="pad", **TGP)
    for net, d, x, y in [("vb", "in", -80, -260), ("vbn", "in", -280, -140), ("en", "in", -480, -130),
                         ("pad", "out", 920, -340)]:
        s.port(net, d, x, y)
    s.labels_only |= {"enb", "en", "bo", "tg", "tl", "o1"}
    return s
