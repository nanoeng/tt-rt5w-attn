"""rt5w_hvif: the 3.3 V interface macro behind the level shifters (sky130_fd_sc_hvl, skywater-pdk-libs 4fd4f85).
Gate netlist of src/rt5w_hvif.v:
  chain:   32 x dfxtp_1, flop i = chain[i], D0 = cfg_sdat, D_i = Q_{i-1}; CLK from buf_8(cfg_sclk)
           q{i}_{b} = chain[4i+b], k{j}_{b} = chain[16+4j+b]
  decoder: na_k = inv(a_k); lo_i = and3(e, a1|na1, a0|na0) (i = 0..3); hi_j = and3(a4|na4, a3|na3, a2|na2)
           (j = 0..4); wsel_{4j+i} = and2(hi_j, lo_i), 20 outputs (addresses >= 20 select nothing)
OpenROAD places and routes the signals on unithv rows; the row rails (VGND / VPWR inset, VNB / VPB at the row edges)
are tied by power columns at both row ends (met1 extensions, met2 straps, via stacks to met4 pins), as in the
level-shifter bank.

    pixi run -e openroad python design/layout/hvif.py pnr      (OpenROAD)
    pixi run -e layout   python design/layout/hvif.py gds      (KLayout: GDS + power columns + LEF + LVS netlist)
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
HVL = "/home/claude/ext/sky130_fd_sc_hvl_4fd4f85"
B = os.path.join(ROOT, "layout", "hvif")
CELL = "rt5w_hvif"
NROWS = 6
W, H = 196.0, 8.0 + NROWS * 4.07     # die; core = 6 unithv rows + 4 um top/bottom, 6 um power columns (~60 % util)
CORE = (6.0, 4.0, W - 6.0, 4.0 + NROWS * 4.07)
USED = ["dfxtp_1", "inv_1", "and2_1", "and3_1", "buf_8", "fill_1", "fill_2", "fill_4", "fill_8"]
INPUTS = ["cfg_sdat", "cfg_sclk"] + [f"wsel_a{k}" for k in range(5)] + ["wsel_e"]
OUTPUTS = ([f"q{i}_{b}" for i in range(4) for b in range(4)] + [f"k{j}_{b}" for j in range(4) for b in range(4)] +
           [f"wsel{k}" for k in range(20)])


def pin_x(name, outs, ins):
    """macro x of a pin: outputs spread over the bottom edge, inputs over the top edge, in the given orders, 8 um
    margins, snapped to the met2 track grid (0.23 + 0.46 k)"""
    seq = outs if name in outs else ins
    k = seq.index(name)
    x = 8.0 + (W - 16.0) * (k + 0.5) / len(seq)
    return round((x - 0.23) / 0.46) * 0.46 + 0.23


def pin_orders():
    """(outputs, inputs) from the top-level floorplan (destination order); fallback: declaration order"""
    try:
        from topflow import hvif_pin_order
        return hvif_pin_order()
    except Exception as e:                                       # noqa: BLE001
        print("hvif: no floorplan pin order:", e)
        return list(OUTPUTS), list(INPUTS)


def chname(i):
    """chain bit i is an output port: q{i//4}_{i%4} for i < 16, k{(i-16)//4}_{i%4} above"""
    return f"q{i // 4}_{i % 4}" if i < 16 else f"k{(i - 16) // 4}_{i % 4}"


def gates():
    """(instance, cell, {pin: net})"""
    g = [("xck", "buf_8", dict(A="cfg_sclk", X="sclk_b"))]
    for i in range(32):
        g.append((f"xff{i}", "dfxtp_1", dict(D="cfg_sdat" if i == 0 else chname(i - 1), CLK="sclk_b", Q=chname(i))))
    for k in range(5):
        g.append((f"xinv{k}", "inv_1", dict(A=f"wsel_a{k}", Y=f"na{k}")))
    bit = lambda k, v: f"wsel_a{k}" if v else f"na{k}"          # noqa: E731
    for i in range(4):
        g.append((f"xlo{i}", "and3_1", dict(A="wsel_e", B=bit(1, i >> 1 & 1), C=bit(0, i & 1), X=f"lo{i}")))
    for j in range(5):
        g.append((f"xhi{j}", "and3_1", dict(A=bit(4, j >> 2 & 1), B=bit(3, j >> 1 & 1), C=bit(2, j & 1), X=f"hi{j}")))
    for k in range(20):
        g.append((f"xw{k}", "and2_1", dict(A=f"hi{k // 4}", B=f"lo{k % 4}", X=f"wsel{k}")))
    return g


def verilog():
    L = [f"module {CELL} (" + ", ".join(INPUTS + OUTPUTS) + ");"]
    L += [f"  input {p};" for p in INPUTS] + [f"  output {p};" for p in OUTPUTS]
    nets = {n for _, _, c in gates() for n in c.values()} - set(INPUTS) - set(OUTPUTS)
    L += [f"  wire {n};" for n in sorted(nets)]
    for inst, cell, conn in gates():
        L.append(f"  sky130_fd_sc_hvl__{cell} {inst} (" + ", ".join(f".{p}({n})" for p, n in conn.items()) + ");")
    L.append("endmodule")
    return "\n".join(L) + "\n"


def pnr_tcl():
    tracks = (("li1", 0.23, 0.46, 0.17, 0.34), ("met1", 0.17, 0.34, 0.17, 0.34), ("met2", 0.23, 0.46, 0.23, 0.46),
              ("met3", 0.34, 0.68, 0.34, 0.68), ("met4", 0.46, 0.92, 0.46, 0.92))
    L = ["set_thread_count [exec nproc]", f"read_lef {HVL}/sky130_fd_sc_hvl.tlef"]
    L += [f"read_lef {HVL}/sky130_fd_sc_hvl__{c}.lef" for c in USED]
    L += ["read_liberty /home/claude/ext/pdk/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib",   # units only
          f"read_verilog {B}/{CELL}.v", f"link_design {CELL}",
          f"initialize_floorplan -die_area {{0 0 {W} {H}}} -core_area {{{' '.join(str(v) for v in CORE)}}} -site unithv"]
    L += [f"make_tracks {l} -x_offset {a} -x_pitch {b} -y_offset {c} -y_pitch {d}" for l, a, b, c, d in tracks]
    # inputs from the shifter bank on the top edge, outputs to the analog blocks on the bottom edge (met2), in
    # destination order (topflow.hvif_pin_order)
    outs, ins = pin_orders()
    right = [n for n in outs if n.startswith("k")]        # k codes go right (k-scales): met3 on the right edge,
    outs = [n for n in outs if n not in right]             # k0 on top (turns up first), between the strap via pads
    for n in outs:
        L.append(f"place_pin -pin_name {n} -layer met2 -location {{{pin_x(n, outs, ins):.3f} 0.5}} -pin_size {{0.28 1.0}}")
    for k, n in enumerate(sorted(right, reverse=True)):
        y = 0.34 + 0.68 * (15 + k)               # met3 tracks, clear of the strap via pads (y 5.75..6.25, 26.17..26.67)
        L.append(f"place_pin -pin_name {n} -layer met3 -location {{{W - 0.5:.3f} {y:.3f}}} -pin_size {{1.0 0.3}}")
    for n in ins:
        L.append(f"place_pin -pin_name {n} -layer met2 -location {{{pin_x(n, outs, ins):.3f} {H - 0.5:.3f}}} "
                 "-pin_size {0.28 1.0}")
    L += [
          "set_placement_padding -global -left 1 -right 1",          # fill between cells: magic hvntm slivers at some abutments
          "global_placement -skip_initial_place -density 0.75", "detailed_placement",
          "filler_placement [list sky130_fd_sc_hvl__fill_8 sky130_fd_sc_hvl__fill_4 sky130_fd_sc_hvl__fill_2 "
          "sky130_fd_sc_hvl__fill_1]", "check_placement",
          "set_routing_layers -signal met1-met4",
          "pin_access -bottom_routing_layer met1 -top_routing_layer met4",
          "global_route -allow_congestion",
          f"detailed_route -bottom_routing_layer met1 -top_routing_layer met4 -output_drc {B}/route_drc.rpt "
          "-droute_end_iter 30 -verbose 1",
          f"write_def {B}/{CELL}.def", "exit"]
    return "\n".join(L) + "\n"


def pnr():
    os.makedirs(B, exist_ok=True)
    open(os.path.join(B, CELL + ".v"), "w").write(verilog())
    open(os.path.join(B, "pnr.tcl"), "w").write(pnr_tcl())
    r = subprocess.run(["openroad", "-exit", "-no_init", os.path.join(B, "pnr.tcl")], capture_output=True, text=True,
                       cwd=B, timeout=3600)
    open(os.path.join(B, "pnr.log"), "w").write(r.stdout + r.stderr)
    v = re.findall(r"Number of violations = (\d+)", r.stdout)
    print("hvif pnr rc", r.returncode, "violations", v[-1] if v else "?")


# --------------------------------------------------------------------------------------- GDS, power, LEF, LVS
def gds():
    import klayout.db as pya
    sys.path[:0] = [HERE]
    import pdkcells as P
    from blockgen import Canvas
    opt = pya.LoadLayoutOptions()
    c = opt.lefdef_config
    c.lef_files = [f"{HVL}/sky130_fd_sc_hvl.tlef"] + [f"{HVL}/sky130_fd_sc_hvl__{x}.lef" for x in USED]
    c.map_file = os.path.join("/home/claude/ext/pdk", "sky130A", "libs.tech", "klayout", "tech", "sky130A.map")
    c.read_lef_with_def = False
    c.macro_resolution_mode = 2
    libs = []
    for x in USED:
        m = pya.Layout()
        m.read(f"{HVL}/sky130_fd_sc_hvl__{x}.gds")
        libs.append(m)
    c.macro_layouts = libs
    ly = pya.Layout()
    ly.read(os.path.join(B, CELL + ".def"), opt)
    top = ly.top_cell()
    top.name = CELL
    cv = Canvas(ly, top)
    UM = 1000
    x0, y0, x1, y1 = (int(v * UM) for v in CORE)
    rails = pya.Region(top.begin_shapes_rec(ly.layer(*P.L_M1))) & pya.Region(pya.Box(x0 - 1000, y0, x1 + 1000, y1))
    rx0, rx1 = rails.bbox().left, rails.bbox().right           # where the placed rows (and their rails) end
    # rails per row r (row 0 N, row 1 FS, ...): (net, y_lo, y_hi) in row-local coordinates of an N row
    rails_n = [("vss", -115, 625), ("vdd", 3445, 4185)]          # VNB+VGND merged, VPWR+VPB merged (+ above)
    straps = {"vdd": (x0 - 3800, x1 + 3800), "vss": (x0 - 5000, x1 + 5000)}   # inside the 2.5 um LEF pin band
    for r in range(NROWS):
        base = y0 + r * 4070
        for net, a, b in rails_n:
            if r % 2:                                              # FS row: mirrored about the row centre
                a, b = 4070 - b, 4070 - a
            ya, yb = base + a, base + b
            for xs in straps[net]:
                left = xs < x0
                cv.box(P.L_M1, xs - 300 if left else rx1, ya, rx0 if left else xs + 300, yb, net)
                cv.via(P.L_V1, [P.L_M1, P.L_M2], xs, (ya + yb) // 2, net=net, vertical=False)
    for net, xs_pair in straps.items():
        for xs in xs_pair:
            cv.box(P.L_M2, xs - 300, y0 - 600, xs + 300, y1 + 600, net)
            for yy in (y0 + 2000, y1 - 2000):
                cv.via(P.L_V2, [P.L_M2, P.L_M3], xs, yy, net=net, big=True)
                cv.via(P.L_V3, [P.L_M3, P.L_M4], xs, yy, net=net, big=True)
            cv.box(P.L_M4, xs - 300, y0 - 600, xs + 300, y1 + 600, net)
            cv.label(P.L_M4, net, xs, (y0 + y1) // 2)
            cv.label(P.L_M3, net, xs, y0 + 2000)       # met3 landing pad in the pin too (macro met4-only pins
            #                                            found no access point at the top level, as in the bank)
    # magic's hierarchical check sees each cell's HVNTM separately inside the interaction window of a routed via at
    # some abutments (e.g. dfxtp_1 | and2_1: overlapping by 70 nm, flagged as hvntm.1 < 0.7 um). A top-level copy of
    # the merged HVNTM (no new area) makes the window see the continuous band.
    hl = ly.layer(125, 20)
    top.shapes(hl).insert(pya.Region(top.begin_shapes_rec(hl)).merged())
    out = os.path.join(ROOT, "layout", "gds", CELL + ".gds")
    ly.write(out)
    # LVS reference: the hvl cells from their CDL (sky130_fd_pr device names), the gate netlist with supplies
    cdl = []
    for x in sorted({g[1] for g in gates()}):
        t = open(f"{HVL}/sky130_fd_sc_hvl__{x}.cdl").read().replace("\n+", " ")
        for line in t.splitlines():
            if line.startswith("*") or not line.strip():
                continue
            if line[0] in "Mm":
                tk = line.split()
                p = dict(kv.split("=") for kv in tk[6:] if "=" in kv)
                line = f"X{tk[0]} {tk[1]} {tk[2]} {tk[3]} {tk[4]} sky130_fd_pr__{tk[5]} W={p['w']} L={p['l']} m={p.get('m', '1')}"
            cdl.append(line)
    port = lambda n: n                                    # noqa: E731
    L = cdl + [f".subckt {CELL} " + " ".join(INPUTS + OUTPUTS) + " vdd vss"]
    for inst, cell, conn in gates():
        order = re.search(rf"\.SUBCKT sky130_fd_sc_hvl__{cell} (.*)", "\n".join(cdl), re.I).group(1).split()
        pins = {**{p: port(n) for p, n in conn.items()}, "VPWR": "vdd", "VPB": "vdd", "VGND": "vss", "VNB": "vss"}
        L.append(f"X{inst} " + " ".join(pins[p] for p in order) + f" sky130_fd_sc_hvl__{cell}")
    L.append(".ends")
    open(os.path.join(ROOT, "netlist", CELL + ".spice"), "w").write("\n".join(L) + "\n")
    info = dict(block=CELL, width=W, height=H, cells=len(gates()))
    json.dump(info, open(os.path.join(ROOT, "layout", "gds", CELL + ".json"), "w"), indent=1)
    print(out, top.bbox())


if __name__ == "__main__":
    {"pnr": pnr, "gds": gds}[sys.argv[1]]()
