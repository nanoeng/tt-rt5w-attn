"""Top level of tt_um_rt5w_attn on tt_analog_6x2_3v3 (1014.76 x 225.76 um): floorplan, macro LEF abstracts (magic),
structural netlist, digital pin plan and the OpenROAD script that routes between the hard macros on met1..met4.

Floorplan (20 Nov 2026):
  left stack (x 2..538): array (535.9 x 128.1) at the bottom, top-edge pins up; channel ch1; level-shifter bank
  (A pins up into the digital macro's bottom pins, X pins down into ch1); digital macro (525 x 52) under the TT pins
  (its met4 top pins abut the template pins).
  power stripes VAPWR / VGND / VDPWR (met4) in the gap x 539..547.
  right (x 548..1009): bias + 2 k-scales | readout + vbbuf + 2 k-scales | softmax; down-shifter beside the readout.

    pixi run -e layout python design/layout/topflow.py lef|netlist|order|tcl
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "design"), os.path.join(ROOT, "design", "blocks")]
GDS = os.path.join(ROOT, "layout", "gds")
LEF = os.path.join(ROOT, "layout", "lef")
TOPD = os.path.join(ROOT, "layout", "top")
PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/ext/pdk")
TT_DEF = "/home/claude/ext/tt/tt-support-tools/tech/sky130A/def/analog/tt_analog_6x2_3v3.def"
DIE = (1014.76, 225.76)
DIG = dict(cell="rt5w_digital", w=330.0, h=82.0)
DIG_GAP = 1.0                  # um between the digital macro top and the TT pins (met4 -> met2 via stacks)

# instance -> (cell, lower-left x, lower-left y)  [tile coordinates, um]
# band above the array: digital (under the TT pins, x 2..322), then the 3.3 V interface (hvif) with the 30-cell
# up-shifter bank above it; right region: bias, k-scales, readout, V_B buffer, softmax, down-shifter
FP = {
    "xarr": ("rt5w_array", 1.84, 6.0),           # x = 0 mod 0.46: array lanes on met4 tracks; top at 135.3
    "xdig": (DIG["cell"], 2.0, 225.76 - 1.0 - DIG_GAP - DIG["h"]),
    "xhvif": ("rt5w_hvif", 336.26, 147.0),
    "xbank": ("rt5w_lsbank", 342.0, 192.0),
    "xbias": ("rt5w_bias", 556.76, 3.0),          # 21 Nov: right region +2.76 um (array 545.3 wide, wider IDACs)
    "xk0": ("rt5w_kscale", 556.76, 177.0),
    "xk1": ("rt5w_kscale", 624.76, 177.0),
    "xro": ("rt5w_readout", 689.3, 3.0),         # 178.9 x 116.1 (steering DAC, clamps, int/intr guard tracks, 21 Nov)
    "xvb": ("rt5w_vbbuf", 689.3, 131.0),
    "xk2": ("rt5w_kscale", 696.76, 177.0),
    "xk3": ("rt5w_kscale", 766.76, 177.0),
    "xsm": ("rt5w_softmax", 907.76, 4.0),
    "xlsdn": ("rt5w_lsdn", 880.0, 140.0),
}
# 1.8 V -> 3.3 V crossings (30): the static q/k codes now cross serially (cfg_sdat/cfg_sclk into the hvif chain), the
# one-hot wsel[19:0] as a 5-bit address + enable decoded in hvif
LS_IN = (["bias_en", "vb_probe_en"] + [f"pump_up{j}" for j in (1, 2, 3)] + [f"pump_dn{j}" for j in (1, 2, 3)] +
         [f"adc_ch{j}" for j in range(4)] + ["adc_rst", "adc_lat"] + [f"dac{k}" for k in range(8)] +
         ["cfg_sdat", "cfg_sclk"] + [f"wsel_a{k}" for k in range(5)] + ["wsel_e"])
HVIF_IN = ["cfg_sdat", "cfg_sclk"] + [f"wsel_a{k}" for k in range(5)] + ["wsel_e"]
HVIF_OUT = ([f"q{i}_{b}" for i in range(4) for b in range(4)] + [f"k{j}_{b}" for j in range(4) for b in range(4)] +
            [f"wsel{k}" for k in range(20)])
UA_PAD_Y = 3.0                 # um: met3 landing pad of the analog pins ua0..2 (met4 stub from the template pin)
STRIPES = {"VAPWR": 548.26, "VGND": 551.26, "VDPWR": 554.26}     # met4 stripe left edges, 2.0 um wide


def block_info(cell):
    return json.load(open(os.path.join(GDS, cell + ".json")))


def gds_bbox(cell):
    import klayout.db as pya
    ly = pya.Layout()
    ly.read(os.path.join(GDS, cell + ".gds"))
    c = ly.cell(cell) or ly.top_cell()
    b = c.bbox()
    return b.left / 1000, b.bottom / 1000, b.right / 1000, b.top / 1000


# ------------------------------------------------------------------------------------------------ connectivity
def analog_conn():
    """instance -> {block port: top net} from design/blocks/top.py (the captured rt5w_analog) + digital side."""
    conn = {
        "xbias": dict(bias_en="bias_en", nbias="nbias", kbias="kbias", nd0="nd0", nd1="nd1", nd2="nd2", nd3="nd3",
                      ndac="ndac", vbn="vbn", pg="pg", ng="ng", vcas="vcas", vr="vr", vmid="vmid", iref="ua0",
                      vdd="VAPWR", vss="VGND"),
        "xarr": dict(vbn="vbn", vw="ua2", pg="pg", ng="ng", vmid="vmid", vdd="VAPWR", vss="VGND",
                     **{f"nd{i}": f"nd{i}" for i in range(4)}, **{f"row{j}": f"row{j}" for j in range(4)},
                     **{f"q{i}_{b}": f"q{i}_{b}" for i in range(4) for b in range(4)},
                     **{f"wsel{k}": f"wsel{k}" for k in range(20)},
                     **{f"pump_up{j}": f"pump_up{j}" for j in (1, 2, 3)},
                     **{f"pump_dn{j}": f"pump_dn{j}" for j in (1, 2, 3)}),
        "xsm": dict(nbias="nbias", kbias="kbias", vr="vr", vcas="vcas", vb="vb", vdd="VAPWR", vss="VGND",
                    **{f"g{j}": f"g{j}" for j in range(4)}, **{f"out{j}": f"out{j}" for j in range(4)}),
        "xro": dict(ndac="ndac", vcas="vcas", vr="vr", adc_rst="adc_rst", adc_lat="adc_lat", cmp="cmp",
                    vdd="VAPWR", vss="VGND", **{f"out{j}": f"out{j}" for j in range(4)},
                    **{f"adc_ch{j}": f"adc_ch{j}" for j in range(4)}, **{f"dac{k}": f"dac{k}" for k in range(8)}),
        "xvb": dict(vb="vb", vbn="vbn", en="vb_probe_en", pad="ua1", vdd="VAPWR", vss="VGND"),
        "xlsdn": {"in": "cmp", "out": "cmp_lv", "vddl": "VDPWR", "vss": "VGND"},
        "xbank": dict(vdd="VAPWR", vss="VGND", vddl="VDPWR", **{f"{s}_lv": f"{s}_lv" for s in LS_IN},
                      **{s: s for s in LS_IN}),
        "xhvif": dict(vdd="VAPWR", vss="VGND", **{s: s for s in HVIF_IN + HVIF_OUT}),
    }
    for j in range(4):
        conn[f"xk{j}"] = dict(row=f"row{j}", g=f"g{j}", vdd="VAPWR", vss="VGND", **{f"k{b}": f"k{j}_{b}" for b in range(4)})
    return conn


def digital_bits():
    """rt5w_digital output bit -> level-shifter input net (1.8 V side)."""
    m = {"bias_en": "bias_en_lv", "adc_rst": "adc_rst_lv", "adc_lat": "adc_lat_lv", "vb_probe_en": "vb_probe_en_lv",
         "cfg_sdat": "cfg_sdat_lv", "cfg_sclk": "cfg_sclk_lv", "wsel_e": "wsel_e_lv"}
    for k in range(5):
        m[f"wsel_a[{k}]"] = f"wsel_a{k}_lv"
    for j in (1, 2, 3):
        m[f"pump_up[{j}]"] = f"pump_up{j}_lv"
        m[f"pump_dn[{j}]"] = f"pump_dn{j}_lv"
    for j in range(4):
        m[f"adc_ch[{j}]"] = f"adc_ch{j}_lv"
    for k in range(8):
        m[f"adc_dac[{k}]"] = f"dac{k}_lv"
    return m


def array_dest():
    """array top-pin net -> tile x"""
    arr = block_info("rt5w_array")
    ax0 = FP["xarr"][1] - arr.get("origin", [0.0, 0.0])[0]        # array GDS bbox starts at x = 0
    return {p["net"]: ax0 + p["x"] for p in arr["pins"] if p["side"] == "T"}


def hvif_pin_order():
    """hvif outputs (bottom edge) sorted by destination x; inputs (top edge) in the fixed order of HVIF_IN"""
    dest = array_dest()
    for j, x in enumerate((554.0, 627.0, 703.0, 776.0)):
        for b in range(4):
            dest[f"k{j}_{b}"] = 1000.0 + x + b
    return sorted(HVIF_OUT, key=lambda s: (dest[s], s)), list(HVIF_IN)


def hvif_pin_x(name):
    """tile x of an hvif pin (evenly spread over the macro edge, 8 um margins, met2 track grid 0.46 / 0.23)"""
    from hvif import W, pin_x
    outs, ins = hvif_pin_order()
    outs = [n for n in outs if not n.startswith("k")]        # k codes leave through the right edge
    return FP["xhvif"][1] + pin_x(name, outs, ins)


# ------------------------------------------------------------------------------------------------ bank order
def bank_order():
    """Slot order of the 30 up-shifters by destination x (tile coordinates): array top pins (pumps), the hvif inputs
    below the bank, then the right region."""
    dest = array_dest()
    xs = {}
    for s in LS_IN:
        if s in dest:
            xs[s] = dest[s]
        elif s in HVIF_IN:
            xs[s] = hvif_pin_x(s)
    right = {"bias_en": 560.0, "vb_probe_en": 700.0}
    for k, s in enumerate(["adc_rst", "adc_lat"] + [f"adc_ch{j}" for j in range(4)] + [f"dac{k}" for k in range(8)]):
        right[s] = 697.0 + k
    for s in LS_IN:
        xs.setdefault(s, right.get(s))
    missing = [s for s, x in xs.items() if x is None]
    if missing:
        raise ValueError(f"no destination for {missing}")
    return sorted(LS_IN, key=lambda s: (xs[s], s))


# ------------------------------------------------------------------------------------------------ LEF abstracts
MAGIC_LEF = """
gds readonly true
gds rescale false
gds read {gds}
load {cell}
select top cell
port makeall
lef write {out} -hide
quit -noprompt
"""


def make_lef(cell):
    os.makedirs(LEF, exist_ok=True)
    out = os.path.join(LEF, cell + ".lef")
    tcl = os.path.join(LEF, cell + ".tcl")
    open(tcl, "w").write(MAGIC_LEF.format(gds=os.path.join(GDS, cell + ".gds"), cell=cell, out=out))
    rc = f"{PDK_ROOT}/sky130A/libs.tech/magic/sky130A.magicrc"
    r = subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", rc, tcl], capture_output=True, text=True,
                       cwd=LEF, timeout=1800)
    if not os.path.exists(out):
        raise RuntimeError(r.stdout[-2000:] + r.stderr[-2000:])
    return out


def digital_lef():
    """Placeholder abstract of the digital macro with the planned pins (the hardened macro must reproduce them)."""
    plan = digital_pin_plan()
    L = ["VERSION 5.7 ;", "BUSBITCHARS \"[]\" ;", "DIVIDERCHAR \"/\" ;", f"MACRO {DIG['cell']}", "  CLASS BLOCK ;", f"  FOREIGN {DIG['cell']} ;",
         "  ORIGIN 0 0 ;", f"  SIZE {DIG['w']:.3f} BY {DIG['h']:.3f} ;"]
    for p in plan:
        x, y, layer, w, h = p["x"], p["y"], p["layer"], p["w"], p["h"]
        L += [f"  PIN {p['name']}", f"    DIRECTION {p['dir']} ;", "    USE SIGNAL ;", "    PORT", f"      LAYER {layer} ;",   # supplies: wide signal nets
              f"        RECT {x - w / 2:.3f} {y - h / 2:.3f} {x + w / 2:.3f} {y + h / 2:.3f} ;", "    END",
              f"  END {p['name']}"]
    L += ["  OBS"]
    for layer in ("li1", "met1", "met2", "met3", "met4"):
        L += [f"    LAYER {layer} ;", f"      RECT 0.5 1.0 {DIG['w'] - 0.5:.3f} {DIG['h'] - 1.0:.3f} ;"]
    L += ["  END", f"END {DIG['cell']}", "END LIBRARY"]
    os.makedirs(LEF, exist_ok=True)
    open(os.path.join(LEF, DIG["cell"] + ".lef"), "w").write("\n".join(L) + "\n")


def tt_pins():
    txt = open(TT_DEF).read().split("PINS")[1].split("END PINS")[0]
    out, cur = [], None
    for line in txt.splitlines():
        m = re.match(r"\s*- (\S+) \+ NET", line)
        if m:
            cur = m.group(1)
        m = re.search(r"PLACED \( (-?\d+) (-?\d+) \)", line)
        if m and cur:
            out.append((cur, int(m.group(1)) / 1000, int(m.group(2)) / 1000))
            cur = None
    return out


def digital_pin_plan():
    """Top pins (met2, under the TT pins: joined by via stacks in merge.py). The remaining (analog-side) pins are
    placed by the harden on the right edge (PIN_REST_RIGHT); the abstract comes from the hardened GDS (lefgen)."""
    x0, y0 = FP["xdig"][1], FP["xdig"][2]
    plan = []
    for name, x, y in tt_pins():
        if name.startswith("ua") or y < 100:
            continue
        plan.append(dict(name=name, dir="INPUT" if name.startswith(("ui_in", "uio_in", "clk", "ena", "rst_n"))
                         else "OUTPUT", layer="met2", x=x - x0, y=DIG["h"] - 0.5, w=0.2, h=1.0))
    return plan


# ------------------------------------------------------------------------------------------------ netlist
def ports_of(cell):
    if cell == DIG["cell"]:
        return None
    info = block_info(cell)
    return info.get("ports") or sorted({p["net"] for p in info["pins"]})


def top_verilog():
    conn = analog_conn()
    L = ["// tt_um_rt5w_attn: structural top for the 6x2_3v3 layout (generated by design/layout/topflow.py)",
         "module tt_um_rt5w_attn (input wire [7:0] ui_in, output wire [7:0] uo_out, input wire [7:0] uio_in,",
         "  output wire [7:0] uio_out, output wire [7:0] uio_oe, inout wire [7:0] ua, input wire ena,",
         "  input wire clk, input wire rst_n, inout wire VAPWR, inout wire VDPWR, inout wire VGND);"]
    nets = set()
    for inst, c in conn.items():
        nets |= set(c.values())
    nets |= set(digital_bits().values()) | {"cmp_lv"}
    nets -= {"VAPWR", "VDPWR", "VGND", "ua0", "ua1", "ua2"}
    L += [f"  wire {n};" for n in sorted(nets)]
    alias = {"ua0": "ua[0]", "ua1": "ua[1]", "ua2": "ua[2]"}
    for inst, c in conn.items():
        cell = FP[inst][0]
        L.append(f"  {cell} {inst} (" + ", ".join(f".{p}({alias.get(n, n)})" for p, n in sorted(c.items())) + ");")
    dig = {k: v for k, v in digital_bits().items()}
    dconn = {"ui_in": "ui_in", "uo_out": "uo_out", "uio_in": "uio_in", "uio_out": "uio_out", "uio_oe": "uio_oe",
             "ena": "ena", "clk": "clk", "rst_n": "rst_n", "adc_cmp": "cmp_lv", "VPWR": "VDPWR", "VGND": "VGND"}
    buses = {}
    for bit, net in dig.items():
        m = re.match(r"(\w+)\[(\d+)\]", bit)
        if m:
            buses.setdefault(m.group(1), {})[int(m.group(2))] = net
        else:
            dconn[bit] = net
    for b, bits in buses.items():
        width = {"wsel_a": 5, "pump_up": 4, "pump_dn": 4, "adc_ch": 4, "adc_dac": 8}[b]
        for i in range(width):
            if i not in bits:
                bits[i] = f"nc_{b}_{i}"            # unused controller output (pump_up/dn[0]: row 0 is pinned)
                L.insert(4, f"  wire nc_{b}_{i};")
        dconn[b] = "{" + ", ".join(bits[i] for i in range(width - 1, -1, -1)) + "}"
    L.append(f"  {DIG['cell']} xdig (" + ", ".join(f".{p}({n})" for p, n in dconn.items()) + ");")
    L.append("endmodule")
    return "\n".join(L) + "\n"


def digital_pin_tcl():
    """place_pin commands for design/digital/pnr.tcl (PIN_TCL): the hardened macro reproduces the planned abstract."""
    L = []
    for p in digital_pin_plan():
        if p["name"] in ("VPWR", "VGND"):
            continue
        L.append(f"place_pin -pin_name {{{p['name']}}} -layer {p['layer']} -location {{{p['x']:.3f} {p['y']:.3f}}} "
                 f"-pin_size {{{p['w']:.3f} {p['h']:.3f}}}")
    os.makedirs(TOPD, exist_ok=True)
    open(os.path.join(TOPD, "digital_pins.tcl"), "w").write("\n".join(L) + "\n")


def route_tcl():
    """OpenROAD: macros FIRM at FP, power stripes as top-level met4 pins, supplies with a wide-wire rule,
    global + detailed route on met1..met4 (met5 is forbidden in TT analog tiles)."""
    tlef = f"{PDK_ROOT}/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__min.tlef"
    L = ["set_thread_count [exec nproc]", f"read_lef {tlef}",
         f"read_liberty {PDK_ROOT}/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"]
    for cell in sorted({c for c, x, y in FP.values()}):
        L.append(f"read_lef {os.path.join(LEF, cell + '.lef')}")
    L += [f"read_verilog {os.path.join(TOPD, 'tt_um_rt5w_attn.v')}", "link_design tt_um_rt5w_attn",
          f"read_def -floorplan_initialize {TT_DEF}",
          "set block [ord::get_db_block]", "set tech [ord::get_db_tech]",
          # the template declares VGND / VPWR as SPECIALNETS: route our supplies as ordinary (wide) nets
          "foreach n {VGND VAPWR VDPWR} { set net [$block findNet $n]; if {$net ne \"NULL\"} { $net clearSpecial; $net setSigType SIGNAL } }"]
    # half-pitch tracks on met2..met4: the macro pins are not on one grid; every 0.3 um pin then has a track
    # through or next to it (detailed routing still enforces the real spacing)
    for layer, xo, xp, yo, yp in (("li1", 0.23, 0.46, 0.17, 0.34), ("met1", 0.17, 0.34, 0.17, 0.34),
                                  ("met2", 0.115, 0.23, 0.115, 0.23), ("met3", 0.17, 0.34, 0.17, 0.34),
                                  ("met4", 0.23, 0.46, 0.23, 0.46)):   # no met5 tracks (forbidden in TT analog tiles); pin_access below is limited to met4
        L.append(f"make_tracks {layer} -x_offset {xo} -x_pitch {xp} -y_offset {yo} -y_pitch {yp}")
    for inst, (cell, x, y) in FP.items():
        L.append(f"set i [$block findInst {inst}]")
        L.append(f"$i setLocation [expr int({x} * 1000)] [expr int({y} * 1000)]")
        L.append("$i setPlacementStatus FIRM")
    # TT pins: the digital-side pins (top edge) connect by abutment with the digital macro's met4 top pins -> not
    # routed; ua0..ua2 (met4-only, bottom edge) are routed to a met3 landing pad UA_PAD_Y above the pin (the met4
    # stub + via3 + pad are drawn into the final GDS by merge.py)
    L.append("set m3 [$tech findLayer met3]")
    for name, x, y in tt_pins():
        bus = name.replace("[", "\\[").replace("]", "\\]")
        if y > 100:
            L += [f"set bt [$block findBTerm {{{name}}}]", "if {$bt ne \"NULL\"} { $bt disconnect }"]
        elif name in ("ua[0]", "ua[1]", "ua[2]"):
            L += [f"set bt [$block findBTerm {{{name}}}]",
                  "foreach bp [$bt getBPins] { odb::dbBPin_destroy $bp }", "set bp [odb::dbBPin_create $bt]",
                  f"odb::dbBox_create $bp $m3 [expr int(({x} - 0.25) * 1000)] [expr int(({UA_PAD_Y} - 0.25) * 1000)] "
                  f"[expr int(({x} + 0.25) * 1000)] [expr int(({UA_PAD_Y} + 0.25) * 1000)]",
                  "$bp setPlacementStatus FIRM"]
    # power stripes: top-level pins (met4, 2 um wide, y 5 .. 220.76 as the TT power-pin rule)
    L.append("set m4 [$tech findLayer met4]")
    for net, x in STRIPES.items():
        L += [f"set bt [$block findBTerm {net}]",
              "if {$bt eq \"NULL\"} { set n [$block findNet " + net + "]; set bt [odb::dbBTerm_create $n " + net + "] }",
              "set bp [odb::dbBPin_create $bt]",
              f"odb::dbBox_create $bp $m4 [expr int({x} * 1000)] 5000 [expr int(({x} + 2.0) * 1000)] 220760",
              "$bp setPlacementStatus FIRM"]
    L += ["create_ndr -name PWR -spacing {met1 0.14 met2 0.14 met3 0.3 met4 0.3} "
          "-width {met1 0.5 met2 0.5 met3 0.6 met4 0.6}",
          "foreach n {VAPWR VGND VDPWR} { assign_ndr -ndr PWR -net $n }",
          "set_routing_layers -signal met1-met4",
          "pin_access -bottom_routing_layer met1 -top_routing_layer met4 -verbose 1",
          "set_global_routing_layer_adjustment met1-met4 0.3", "set_global_routing_layer_adjustment met5 1.0",
          "set_routing_layers -signal met1-met4 -clock met1-met4",
          f"global_route -guide_file {os.path.join(TOPD, 'route.guide')} "
          "-allow_congestion -verbose",
          f"detailed_route -output_drc {os.path.join(TOPD, 'route_drc.rpt')} -bottom_routing_layer met1 "
          "-top_routing_layer met4 -droute_end_iter 30 -verbose 1",
          f"write_def {os.path.join(TOPD, 'tt_um_rt5w_attn.def')}"]
    open(os.path.join(TOPD, "route.tcl"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "order"
    if cmd == "order":
        print(bank_order())
    elif cmd == "lef":
        for cell in sorted({c for c, x, y in FP.values()} - {DIG["cell"]}):
            print(make_lef(cell))
        digital_lef()
    elif cmd == "tcl":
        route_tcl()
        digital_pin_tcl()
    elif cmd == "netlist":
        os.makedirs(TOPD, exist_ok=True)
        open(os.path.join(TOPD, "tt_um_rt5w_attn.v"), "w").write(top_verilog())
