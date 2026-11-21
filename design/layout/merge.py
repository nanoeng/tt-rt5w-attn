"""Final GDS of tt_um_rt5w_attn: the routed top-level DEF (OpenROAD) read by KLayout with every macro taken from its
own GDS (LEF FOREIGN, macro_resolution_mode 2), plus the analog-pin stubs (template ua pin -> met3 landing pad of
the routed net) and the prBoundary rectangle the TT precheck wants.

    pixi run -e layout python design/layout/merge.py        -> layout/gds/tt_um_rt5w_attn.gds
"""
import os
import sys

import klayout.db as pya

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [HERE]
import topflow as T  # noqa: E402

PDK_ROOT = T.PDK_ROOT
MAP = os.path.join(PDK_ROOT, "sky130A", "libs.tech", "klayout", "tech", "sky130A.map")
TLEF = os.path.join(PDK_ROOT, "sky130A", "libs.ref", "sky130_fd_sc_hd", "techlef", "sky130_fd_sc_hd__min.tlef")
GDS_OF = {c: os.path.join(T.GDS, c + ".gds") for c, x, y in T.FP.values()}
M3, V3, M4 = (70, 20), (70, 44), (71, 20)
M4_PIN, M4_LABEL = (71, 16), (71, 5)


def marker_fixes(ly, top):
    """Implant / high-voltage marker clean-up for the KLayout FEOL deck of the precheck (magic's deck does not check
    these across cells): every nwell touching hvi is fully covered by hvi (MR_nwell.CON.1), and gaps narrower than
    the minimum spacing are filled (closing) on hvi (0.7 um, hvi.2a), hvntm (0.7 um, hvntm.2) and psdm (0.38 um,
    MR_psdm.SP.1; never over nsdm). Flat shapes in the top cell, no new area beyond the gaps."""
    def flat(ld):
        li = ly.find_layer(*ld)
        return pya.Region(top.begin_shapes_rec(li)).merged() if li is not None else pya.Region()
    nwell, hvi, hvntm, psdm, nsdm = (flat(x) for x in ((64, 20), (75, 20), (125, 20), (94, 20), (93, 44)))
    add = {}
    hv_nw = nwell.interacting(nwell & hvi)
    hvi2 = (hvi + (hv_nw - hvi)).merged()
    hvi2 = hvi2.sized(350).sized(-350)
    add[(75, 20)] = hvi2 - hvi
    add[(125, 20)] = hvntm.sized(350).sized(-350) - hvntm
    add[(94, 20)] = (psdm.sized(190).sized(-190) - psdm) - nsdm
    for ld, r in add.items():
        top.shapes(ly.layer(*ld)).insert(r)
    return {ld: r.count() for ld, r in add.items()}


def main(out=None):
    macros = []
    for cell, path in GDS_OF.items():
        m = pya.Layout()
        m.read(path)
        if m.cell(cell) is None:
            raise ValueError(f"{path}: no cell {cell}")
        macros.append(m)
    opt = pya.LoadLayoutOptions()
    c = opt.lefdef_config
    c.lef_files = [TLEF] + [os.path.join(T.LEF, cell + ".lef") for cell in GDS_OF]
    c.map_file = MAP
    c.read_lef_with_def = False
    c.macro_resolution_mode = 2            # never LEF geometry: the FOREIGN cells come from macro_layouts
    c.macro_layouts = macros
    c.produce_labels = True
    c.produce_pins = True
    ly = pya.Layout()
    ly.read(os.path.join(T.TOPD, "tt_um_rt5w_attn.def"), opt)
    top = ly.top_cell()
    top.name = "tt_um_rt5w_attn"
    # macro placement: KLayout puts the GDS cell origin at the DEF location and ignores the LEF ORIGIN; the abstract
    # (lefgen) has its lower-left at the DEF location, i.e. the GDS origin belongs at location + ORIGIN (all N)
    import re
    org = {}
    for cell in GDS_OF:
        m = re.search(r"ORIGIN\s+(-?[\d.]+)\s+(-?[\d.]+)", open(os.path.join(T.LEF, cell + ".lef")).read())
        org[cell] = (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)
    loc = {cell: [] for cell in GDS_OF}
    for inst, (cell, x, y) in T.FP.items():
        loc[cell].append((x, y))
    for inst in list(top.each_inst()):
        cell = inst.cell.name
        if cell in org:
            d = inst.trans.disp
            x, y = min(loc[cell], key=lambda p: abs(p[0] * 1000 - d.x) + abs(p[1] * 1000 - d.y))
            assert abs(x * 1000 - d.x) < 2 and abs(y * 1000 - d.y) < 2 and inst.trans.rot == 0, (cell, d)
            inst.trans = pya.Trans(int(round((x + org[cell][0]) * 1000)), int(round((y + org[cell][1]) * 1000)))
    # analog pins: met4 stub from the template pin (y 0 .. 1 um, 0.9 um wide) to the routed met3 landing pad
    for name, x, y in T.tt_pins():
        if name in ("ua[0]", "ua[1]", "ua[2]"):
            xi, yp = int(x * 1000), int(T.UA_PAD_Y * 1000)
            top.shapes(ly.layer(*M4)).insert(pya.Box(xi - 450, 0, xi + 450, yp + 300))
            top.shapes(ly.layer(*V3)).insert(pya.Box(xi - 100, yp - 100, xi + 100, yp + 100))
            top.shapes(ly.layer(*M3)).insert(pya.Box(xi - 250, yp - 250, xi + 250, yp + 250))
            # the port is the template's met4 pin (0.9 x 1 um at the bottom edge), not the routed met3 pseudo-pin
            for lay in (M4_PIN,):
                top.shapes(ly.layer(*lay)).insert(pya.Box(xi - 450, 0, xi + 450, 1000))
            top.shapes(ly.layer(*M4_LABEL)).insert(pya.Text(name, pya.Trans(xi, 500)))
    # digital TT pins: template met4 pin (y 224.76 .. 225.76, 0.3 um) -> 0.5 um met4 below it -> via3 -> met3 ->
    # via2 -> met2 down to the digital macro's met2 top pin (macro top = 224.76 - DIG_GAP)
    M2, V2 = (69, 20), (69, 44)
    ytop = int((T.FP["xdig"][2] + T.DIG["h"]) * 1000)
    for name, x, y in T.tt_pins():
        if y > 100:
            xi = int(x * 1000)
            yv = 224760 - 260                      # via stack under the template pin, 0.4 um clear of the digital
            #                                        macro's top-edge met3 (routes up to 0.09 um above its die)
            top.shapes(ly.layer(*M4)).insert(pya.Box(xi - 250, yv - 250, xi + 250, 224760 + 10))
            # the template pin itself (met4 drawing + pin + label): the routed DEF dropped these (disconnected
            # bterms), and the precheck compares the GDS pins with the template DEF
            for lay in (M4, M4_PIN):
                top.shapes(ly.layer(*lay)).insert(pya.Box(xi - 150, 224760, xi + 150, 225760))
            top.shapes(ly.layer(*M4_LABEL)).insert(pya.Text(name, pya.Trans(xi, 225260)))
            top.shapes(ly.layer(*V3)).insert(pya.Box(xi - 100, yv - 100, xi + 100, yv + 100))
            top.shapes(ly.layer(*M3)).insert(pya.Box(xi - 250, yv - 250, xi + 250, yv + 250))
            top.shapes(ly.layer(*V2)).insert(pya.Box(xi - 100, yv - 100, xi + 100, yv + 100))
            top.shapes(ly.layer(*M2)).insert(pya.Box(xi - 100, ytop - 300, xi + 100, yv - 185))   # = macro pin width
            top.shapes(ly.layer(*M2)).insert(pya.Box(xi - 140, yv - 185, xi + 140, yv + 185))     # via2.4a: 0.085
    # drop the met3 pseudo-pins of ua[0..2] that the DEF reader made (pin + label purposes only; the metal stays)
    for lay in ((70, 16), (70, 5)):
        li = ly.find_layer(*lay)
        if li is None:
            continue
        for sh in list(top.shapes(li).each()):
            if (sh.is_text() and sh.text.string in ("ua[0]", "ua[1]", "ua[2]")) or \
                    (not sh.is_text() and sh.bbox().top < int((T.UA_PAD_Y + 1) * 1000)):
                top.shapes(li).erase(sh)
    marker_fixes(ly, top)
    # prBoundary = the project area
    top.shapes(ly.layer(235, 4)).insert(pya.Box(0, 0, int(T.DIE[0] * 1000), int(T.DIE[1] * 1000)))
    out = out or os.path.join(T.GDS, "tt_um_rt5w_attn.gds")
    ly.write(out)
    return out, top.bbox()


if __name__ == "__main__":
    print(main())
