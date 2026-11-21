"""Bias reference (cascoded weak-inversion beta multiplier with start-up) and 4-bit thermometer column IDAC.
Reference: M1 (W/L) diode, M2 (K*W/L) with source resistor R; cascoded PMOS mirror (1:1) and NMOS cascodes.
  I_ref = n U_T ln K / R   (PTAT).  Target I_ref = 0.5 uA (I_sum); K = 8.
IDAC: 15 unit NMOS sinks (I_LSB = I_ref/50 = 10 nA) mirrored from a diode, thermometer switches."""
import json
import numpy as np
from rt5w_ng import MODELS, run, parse_print, AVT_N

R_REF = 170e3      # sets I_ref = 0.5 uA at TT 27 C (n U_T ln 8 / R)
K = 8


def ref_netlist(corner="tt", T=27, vdd=3.3, extra=""):
    lib = {"tt": "typical"}.get(corner, corner)
    return "\n".join([
        "* beta multiplier", f".include {MODELS}/design.ngspice", f".lib {MODELS}/sm141064.ngspice {lib}", f".temp {T}",
        f"Vdd vdd 0 {vdd}",
        # NMOS core (M2 in a DNWELL pocket: bulk tied to its source -> ln K exact, no body effect)
        "M1 n1 n1 0 0 nmos_3p3 w=40u l=2u m=1",
        f"M2 n2c n1 s2 s2 nmos_3p3 w=40u l=2u m={K}",
        f"R1 s2 0 {R_REF}",
        # NMOS cascodes
        "M1c p1 vcn n1 0 nmos_3p3 w=20u l=4u",
        f"M2c p2 vcn n2c 0 nmos_3p3 w=20u l=4u m={K}",
        # PMOS cascoded mirror (p2 diode-side)
        "M3 a3 p2c vdd vdd pmos_3p3 w=40u l=4u",
        "M4 a4 p2c vdd vdd pmos_3p3 w=40u l=4u",
        "M3c p1 vcp a3 vdd pmos_3p3 w=40u l=4u",
        "M4c p2 vcp a4 vdd pmos_3p3 w=40u l=4u",
        "Vlnk p2 p2c 0",
        # cascode bias from self-biased stacks (low-voltage diodes)
        "M5 x5 x5 vdd vdd pmos_3p3 w=4u l=16u", "M5b vcp vcp x5 vdd pmos_3p3 w=4u l=16u",
        "Ib5 vcp 0 0.1u", "M6 vcn vcn x6 0 nmos_3p3 w=4u l=16u", "M6b x6 x6 0 0 nmos_3p3 w=4u l=16u", "Ib6 vdd vcn 0.1u",
        # output copy (to IDAC / tail): cascoded PMOS
        "M7 a7 p2c vdd vdd pmos_3p3 w=40u l=4u", "M7c out vcp a7 vdd pmos_3p3 w=40u l=4u", "Vout out 0 1.0",
        # start-up: pulls n1 up while the core is off (I_su -> 0 once p2 is low)
        # start-up: a = core-current copy against a 0.1 uA sink (high when running, low when off);
        # skewed inverter -> b high only when the core is off -> Ms3 pulls the PMOS gate line low.
        "M8 a p2c vdd vdd pmos_3p3 w=40u l=4u", "Mld a x6 0 0 nmos_3p3 w=4u l=16u",    # 0.1 uA sink (copy of M6b)
        "Mi1 b a 0 0 nmos_3p3 w=1u l=4u", "Mi2 b 0 vdd vdd pmos_3p3 w=0.5u l=50u",
        "Ms3 p2 b 0 0 nmos_3p3 w=1u l=2u",
        extra,
        ".control", "op", "print i(vout) v(n1) v(s2) v(p2) v(b) i(vdd) @m1[gm] @m1[id] @m2[gm] @m2[id]", ".endc", ".end"])


def ref_point(corner="tt", T=27, vdd=3.3):
    v = parse_print(run(ref_netlist(corner, T, vdd))[0])
    return abs(v["i(vout)"]), v


def idac_netlist(code, mm=None, corner="tt", T=27):
    mm = mm or {}
    lib = {"tt": "typical"}.get(corner, corner)
    L = ["* idac", f".include {MODELS}/design.ngspice", f".lib {MODELS}/sm141064.ngspice {lib}", f".temp {T}",
         "Vdd vdd 0 3.3", "Iin vdd nd 10n", "Md nd nd 0 0 nmos_3p3 w=2u l=16u"]
    for u in range(15):
        on = 3.3 if u < code else 0.0
        L += [f"Vm{u} nd g{u} {mm.get(u,0):.6e}", f"Mu{u} s{u} g{u} 0 0 nmos_3p3 w=2u l=16u",
              f"Ms{u} col s{u} sw{u} 0 nmos_3p3 w=1u l=0.5u", f"Vsw{u} sw{u} 0 {on}"]   # switch drain-side
    L = [l.replace(f"Ms{u} col s{u} sw{u} 0", f"Ms{u} col sw{u} s{u} 0") for u in range(15) for l in [l]] if False else L
    L2 = []
    for l in L:
        if l.startswith("Ms"):
            u = int(l.split()[0][2:])
            l = f"Ms{u} col sw{u} s{u} 0 nmos_3p3 w=1u l=0.5u"
        L2.append(l)
    L2 += ["Vcol vcolsrc col 0", "Vcs vcolsrc 0 2.3", ".control", "op", "print i(vcol)", ".endc", ".end"]
    return "\n".join(L2)


if __name__ == "__main__":
    out = {}
    I0, v = ref_point()
    out["ref_tt"] = dict(I_uA=I0 * 1e6, gmid_M1=v["@m1[gm]"] / v["@m1[id]"], gmid_M2=v["@m2[gm]"] / v["@m2[id]"])
    sup = [ref_point(vdd=vd)[0] for vd in (3.0, 3.3, 3.6)]
    out["ref_supply_pct_per_V"] = float((sup[2] - sup[0]) / 0.6 / sup[1] * 100)
    temps = [-40, 27, 125]
    It = [ref_point(T=T)[0] for T in temps]
    out["ref_vs_T_uA"] = dict(zip(map(str, temps), [i * 1e6 for i in It]))
    out["ref_tc_ppm_per_K"] = float(np.polyfit(np.array(temps) + 273.15, It, 1)[0] / It[1] * 1e6)
    out["ref_corners_uA"] = {c: ref_point(corner=c)[0] * 1e6 for c in ("tt", "ss", "ff", "sf", "fs")}
    # start-up from 0 V supply ramp
    tr = ref_netlist(extra="").replace("Vdd vdd 0 3.3", "Vdd vdd 0 PWL(0 0 2u 3.3)").replace(
        ".control\nop\nprint i(vout) v(n1) v(s2) v(p2) v(b) i(vdd) @m1[gm] @m1[id] @m2[gm] @m2[id]",
        ".control\noption method=gear\ntran 10n 30u\nmeas tran ifin find i(vout) at=29u\nmeas tran tsu when i(vout)=-0.45u cross=1")
    t = run(tr)[0]
    m = parse_print(t)
    out["ref_startup"] = dict(final_uA=m.get("ifin", 0) * 1e6, t_90pct_us=(m.get("tsu", float("nan")) - 2e-6) * 1e6)
    # IDAC transfer (TT) and MC INL/DNL
    codes = list(range(16))
    I = np.array([abs(parse_print(run(idac_netlist(c))[0])["i(vcol)"]) for c in codes])
    lsb = (I[15] - I[0]) / 15
    out["idac_tt"] = dict(lsb_nA=float(lsb * 1e9), gain_err_pct=float((lsb / 10e-9 - 1) * 100),
                          inl_lsb=float(np.abs((I - I[0]) / lsb - np.arange(16)).max()))
    rng = np.random.default_rng(4)
    sig = AVT_N / np.sqrt(2 * 16)
    inl, dnl = [], []
    for _ in range(20):
        mm = {u: rng.normal(0, sig) for u in range(15)}
        Im = np.array([abs(parse_print(run(idac_netlist(c, mm))[0])["i(vcol)"]) for c in codes])
        l = (Im[15] - Im[0]) / 15
        inl.append(np.abs((Im - Im[0]) / l - np.arange(16)).max()); dnl.append(np.abs(np.diff(Im) / l - 1).max())
    out["idac_mc"] = dict(inl_max_lsb=float(max(inl)), dnl_max_lsb=float(max(dnl)), monotonic=bool(max(dnl) < 1))
    json.dump(out, open("results/bias_idac.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
