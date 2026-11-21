"""Column IDAC: 4-bit current sink, 15 matched unit sinks mirrored from a diode fed with I_LSB (I_u/15, PTAT/R).
The units are grouped binary (1, 2, 4, 8 units behind switches b0..b3), so the controller drives 4 lines per column
instead of 15 thermometer lines; every unit is still the same device, so matching is unchanged.
Textbook layout: reference diode on the left, unit sinks in one row, unit switches above them, output bus on top."""
from schem import Schematic
from units import IDAC_U, SW, SWL

GROUP = [0] + [1] * 2 + [2] * 4 + [3] * 8         # unit i -> bit


def idac4():
    s = Schematic("rt5w_idac4", ports=["nd", "b0", "b1", "b2", "b3", "col", "vss"])
    s.text("4-bit column IDAC (sink): I_col = q * I_LSB, q = b3..b0; 15 unit sinks in binary groups", -120, -330, 0.5)
    s.nmos("Md", 0, 0, D="nd", G="nd", S="vss", **IDAC_U)
    s.port("nd", "in", -80, 0)
    for i in range(15):
        x = 200 + 180 * i
        s.nmos(f"Mu{i}", x, 0, D=f"s{i}", G="nd", S="vss", **IDAC_U)
        s.nmos(f"Ms{i}", x, -110, D="col", G=f"b{GROUP[i]}", S=f"s{i}", **SWL)
    for b, x in ((0, 150), (1, 330), (2, 690), (3, 1410)):
        s.port(f"b{b}", "in", x, -250)
    s.labels_only |= {"b0", "b1", "b2", "b3"}
    s.port("col", "inout", 200 + 180 * 15, -180)
    s.bus("col", "h", -180)
    s.bus("nd", "h", 0)
    return s
