"""DEF (+ tech/cell LEF) -> GDS with the sky130_fd_sc_hd cell layouts merged in (KLayout Python API)."""
import os
import sys

try:
    import pya
except ImportError:
    import klayout.db as pya

PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/ext/pdk")
SC = os.path.join(PDK_ROOT, "sky130A", "libs.ref", "sky130_fd_sc_hd")
MAP = os.path.join(PDK_ROOT, "sky130A", "libs.tech", "klayout", "tech", "sky130A.map")


def main(def_path, gds_out):
    opt = pya.LoadLayoutOptions()
    lef = opt.lefdef_config
    lef.lef_files = [os.path.join(SC, "techlef", "sky130_fd_sc_hd__min.tlef"),
                     os.path.join(SC, "lef", "sky130_fd_sc_hd.lef")]
    if os.path.exists(MAP):
        lef.map_file = MAP
    lef.read_lef_with_def = False
    lef.macro_resolution_mode = 1          # LEF macros become empty cells we fill from the GDS below
    ly = pya.Layout()
    ly.read(def_path, opt)
    top = ly.top_cell()
    cells = pya.Layout()
    cells.read(os.path.join(SC, "gds", "sky130_fd_sc_hd.gds"))
    for c in list(ly.each_cell()):
        src = cells.cell(c.name)
        if src is not None and c.cell_index() != top.cell_index():
            c.clear()
            c.copy_tree(src)
    top.name = "rt5w_digital"            # = the module and the top-level netlist cell
    # supply pins for the top level: label the right ends of the met3 core-ring sides (PDN ring, pnr.tcl) and run them
    # out to the die edge (lefgen takes the labelled polygon inside its 2.5 um edge band)
    import re
    txt = open(def_path).read()
    units = int(re.search(r"UNITS DISTANCE MICRONS (\d+)", txt).group(1))
    die = [int(v) for v in re.search(r"DIEAREA \( (\d+) (\d+) \) \( (\d+) (\d+) \)", txt).groups()]
    sc = 1000 / units
    sn = txt[txt.index("SPECIALNETS"):txt.index("END SPECIALNETS")]
    m3 = ly.layer(70, 20)
    m3l = ly.layer(70, 5)
    for net in ("VPWR", "VGND"):
        body = sn[sn.index(f"- {net} "):]
        body = body[:body.index(";")]
        for w, x0, y0, x1, y1 in re.findall(r"met3 (\d+) \+ SHAPE STRIPE \( (\d+) (\d+) \) \( (\d+) (\d+) \)", body):
            if y0 == y1 and int(x1) - int(x0) > 0.8 * (die[2] - die[0]):
                hw, y, xe = int(w) * sc / 2, int(y0) * sc, int(x1) * sc
                top.shapes(m3).insert(pya.Box(int(xe - hw), int(y - hw), int(die[2] * sc), int(y + hw)))
                top.shapes(m3l).insert(pya.Text(net, pya.Trans(int(die[2] * sc - 600), int(y))))
    ly.write(gds_out)


if __name__ == "__main__":
    main(*sys.argv[1:3])
