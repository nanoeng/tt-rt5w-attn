"""Per-key (row) scale: I_g = (ks / 15) I_row, ks = k3..k0 (k_code nibble). The row line ends in an NMOS diode of 15
unit devices; 15 matching output units grouped 1/2/4/8 behind switches sink (ks/15) I_row from a PMOS diode of 15
units, whose 1:1 PMOS copy sources the scaled current into the softmax input g. unit = KS_U (gm/ID LUT, sigma(I)/I = 3 %)."""
from schem import Schematic
from units import KS_U, SW, SWL

GROUP = [0] + [1] * 2 + [2] * 4 + [3] * 8
U = KS_U


def kscale():
    s = Schematic("rt5w_kscale", ports=["row", "k0", "k1", "k2", "k3", "g", "vdd", "vss"])
    s.text("Key scale: I_g = (ks/15) I_row  (15-unit NMOS diode -> binary-grouped units -> 15-unit PMOS mirror)",
           -200, -560, 0.45)
    s.nmos("Mdn", 0, 0, D="row", G="row", S="vss", m=15, **U)
    for i in range(15):
        x = 200 + 160 * i
        s.nmos(f"Mu{i}", x, 0, D=f"s{i}", G="row", S="vss", **U)
        s.nmos(f"Ms{i}", x, -120, D="kp", G=f"k{GROUP[i]}", S=f"s{i}", **SWL)
    s.pmos("Mpd", 2700, -380, D="kp", G="kp", S="vdd", m=15, **U, flip=1)
    s.pmos("Mpo", 2900, -380, D="g", G="kp", S="vdd", m=15, **U)
    s.bus("kp", "h", -240)
    s.bus("row", "h", 80)
    for b, x in ((0, 150), (1, 310), (2, 630), (3, 1270)):
        s.port(f"k{b}", "in", x, -200)
    s.labels_only |= {"k0", "k1", "k2", "k3"}
    s.port("row", "inout", -100, 80)
    s.port("g", "out", 3000, -300)
    return s
