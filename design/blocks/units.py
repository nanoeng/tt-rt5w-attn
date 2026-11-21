"""Shared device sizes for the sky130 port, all from sizing.dev() (gm/ID LUT + PDK A_VT). Currents from the
architecture: I_u = 125 nA (bias unit), I_LSB = I_u / 15 (IDAC), I_u / 16 (readout DAC unit)."""
from sizing import dev

I_U = 125e-9

NU = dev("n", I_U, ("sigma_i", 0.05), tag="n mirror unit @ I_u")                 # bias core / root / tails
PU = dev("p", I_U, ("sigma_i", 0.05), tag="p distribution unit @ I_u")   # 5 % (owner 19 Nov: relax where calibrated)         # every PMOS copy of I_u
IDAC_U = dev("n", I_U / 15, ("sigma_i", 0.03), tag="IDAC unit @ I_u/15")
DAC_U = dev("n", I_U / 16, ("sigma_i", 0.05), tag="DAC unit @ I_u/16")
KS_U = dev("n", 4 * I_U / 15, ("sigma_i", 0.05), tag="k-scale unit @ 4I_u/15")   # 5 %: row gain trimmed by SS-SGD
MC = dev("p", I_U, ("sigma_i", 0.05), tag="array PMOS / column diode @ I_u")
DDA_N = dev("n", I_U / 2, ("vos", 0.010), L=4, tag="DDA pair device @ I_u/2 (L 4: gain + CMRR)")
DDA_P = dev("p", I_U / 2, ("vos", 0.010), L=4, tag="DDA PMOS load @ I_u/2 (L 4)")
SM_P = dev("p", I_U, ("sigma_i", 0.03), tag="softmax PMOS unit @ I_u")   # 3 %: share error ~1.5 LSB
SM_E = dev("n", I_U, ("vt", 0.0023), tag="exponentiator Me @ I_u")
SA_IN = dev("n", 2e-6, ("vos", 0.006), tag="StrongARM input @ 2 uA")
BUF_IN = dev("n", 2 * I_U, ("vos", 0.005), tag="V_B buffer pair @ 2I_u")
BUF_P = dev("p", 2 * I_U, ("sigma_i", 0.03), tag="V_B buffer load @ 2I_u")
CASN = dev("n", 4 * I_U, ("gmid", 14), L=1, tag="NMOS cascode @ 4I_u")
CASP = dev("p", 4 * I_U, ("gmid", 14), L=1, tag="PMOS cascode @ 4I_u")
HEAD_N = dev("n", I_U, ("gmid", 6), L=8, tag="headroom diode @ I_u (strong inv.)")
HEAD_P = dev("p", I_U, ("gmid", 6), L=8, tag="headroom diode p @ I_u (strong inv.)")
SW = dev("n", 0, ("min",), tag="switch / logic n")
SWP = dev("p", 0, ("min",), tag="switch / logic p")
SWP2 = dict(W=2 * SWP["W"], L=SWP["L"])
# switch in series with a current-sink unit (IDAC, k-scale): long L against subthreshold leakage when off.
# nfet_g5v0d10v5 at V_GS = 0, V_DS = 1.5 V, ff / 125 C: W0.84/L0.5 0.52 nA (5 % of an I_u/15 unit), W0.42/L1 ~29 pA
SWL = dict(W=0.42, L=1.0)        # logic PMOS at 2x (rise/fall balance), same rule
CAP = dict(W=10.4, L=10.4)                      # 0.5 pF grounded MOS cap (C_ox 4.6 fF/um2, LUT cgg/WL)
