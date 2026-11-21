"""Analog macro top (rt5w_analog): bias -> array -> key scale -> softmax -> readout, V_B buffer, and the three analog pins.
Interface to the hardened controller (all 3.3 V CMOS levels): bias_en, q{i}_{b} (column codes), wsel0..19 (one-hot
cell select, 16 keys + 4 row trims), k{j}_{b} (per-key scale ks_j), pump_up/dn{1..3}, adc_ch0..3 (one-hot), adc_rst, adc_lat, dac0..7, cmp (out),
vb_probe_en.  Analog pins: ua0 = I_u monitor, ua1 = V_B probe, ua2 = cell write voltage vw."""
from schem import Schematic

DIG_IN = (["bias_en"] + [f"q{i}_{b}" for i in range(4) for b in range(4)] +
          [f"k{j}_{b}" for j in range(4) for b in range(4)] + [f"wsel{k}" for k in range(20)] +
          [f"pump_up{j}" for j in (1, 2, 3)] + [f"pump_dn{j}" for j in (1, 2, 3)] + [f"adc_ch{j}" for j in range(4)] +
          ["adc_rst", "adc_lat"] + [f"dac{k}" for k in range(8)] + ["vb_probe_en"])


def analog_top():
    ports = DIG_IN + ["cmp", "ua0", "ua1", "ua2", "vdd", "vss"]
    s = Schematic("rt5w_analog", ports=ports)
    s.text("rt5w_analog: bias -> 4x4 array -> softmax -> readout;  V_B buffer;  ua0 I_u monitor, ua1 V_B, ua2 vw",
           -400, -1100, 0.6)
    s.block("xbias", "rt5w_bias.sym", 0, -400,
            dict(bias_en="bias_en", nbias="nbias", kbias="kbias", nd0="nd0", nd1="nd1", nd2="nd2", nd3="nd3",
                 ndac="ndac", vbn="vbn", pg="pg", ng="ng", vcas="vcas", vr="vr", vmid="vmid", iref="ua0",
                 vdd="vdd", vss="vss"))
    arr = dict(vbn="vbn", vw="ua2", pg="pg", ng="ng", vmid="vmid", vdd="vdd", vss="vss",
               **{f"nd{i}": f"nd{i}" for i in range(4)}, **{f"row{j}": f"row{j}" for j in range(4)},
               **{f"q{i}_{b}": f"q{i}_{b}" for i in range(4) for b in range(4)},
               **{f"wsel{k}": f"wsel{k}" for k in range(20)},
               **{f"pump_up{j}": f"pump_up{j}" for j in (1, 2, 3)}, **{f"pump_dn{j}": f"pump_dn{j}" for j in (1, 2, 3)})
    s.block("xarr", "rt5w_array.sym", 600, -400, arr)
    s.block("xsm", "rt5w_softmax.sym", 1300, -400,
            dict(nbias="nbias", kbias="kbias", vr="vr", vcas="vcas", vb="vb", vdd="vdd", vss="vss",
                 **{f"g{j}": f"g{j}" for j in range(4)}, **{f"out{j}": f"out{j}" for j in range(4)}))
    for j in range(4):
        s.block(f"xk{j}", "rt5w_kscale.sym", 900, -800 + 200 * j,
                dict(row=f"row{j}", g=f"g{j}", vdd="vdd", vss="vss", **{f"k{b}": f"k{j}_{b}" for b in range(4)}))
    s.block("xro", "rt5w_readout.sym", 1800, -400,
            dict(ndac="ndac", vcas="vcas", vr="vr", adc_rst="adc_rst", adc_lat="adc_lat", cmp="cmp",
                 vdd="vdd", vss="vss", **{f"out{j}": f"out{j}" for j in range(4)},
                 **{f"adc_ch{j}": f"adc_ch{j}" for j in range(4)}, **{f"dac{k}": f"dac{k}" for k in range(8)}))
    s.block("xvb", "rt5w_vbbuf.sym", 1200, 100, dict(vb="vb", vbn="vbn", en="vb_probe_en", pad="ua1",
                                                     vdd="vdd", vss="vss"))
    for k, p in enumerate(DIG_IN):
        s.port(p, "in", -700 + 200 * (k // 25), -900 + 40 * (k % 25))
    for k, (p, d) in enumerate((("cmp", "out"), ("ua0", "inout"), ("ua1", "inout"), ("ua2", "inout"))):
        s.port(p, d, 2300, -900 + 40 * k)
    s.labels_only |= set(DIG_IN) | {"cmp", "ua0", "ua1", "ua2", "nbias", "kbias", "ndac", "vbn", "pg", "ng", "vcas",
                                     "vr", "vmid", "vb"} | {f"nd{i}" for i in range(4)} | \
        {f"row{j}" for j in range(4)} | {f"out{j}" for j in range(4)} | {f"g{j}" for j in range(4)}
    return s
