"""LEF abstracts of the hard macros for top-level routing (KLayout): SIZE = the cell's bounding box; each pin = the
merged polygon on its layer under the pin label (full strap / trunk / lane, not just magic's label tile); OBS = the
whole bounding box on li1..met4 minus the pins and an access corridor from each pin to the nearest cell edge (when the
pin lies within EDGE_REACH of it), both grown by the layer's minimum spacing.

    pixi run -e layout python design/layout/lefgen.py <cell> [...]      -> layout/lef/<cell>.lef
"""
import os
import sys

import klayout.db as pya

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GDS = os.path.join(ROOT, "layout", "gds")
LEF = os.path.join(ROOT, "layout", "lef")
LAYERS = {"li1": ((67, 20), (67, 5), 170), "met1": ((68, 20), (68, 5), 140), "met2": ((69, 20), (69, 5), 140),
          "met3": ((70, 20), (70, 5), 300), "met4": ((71, 20), (71, 5), 300)}
EDGE_REACH = 3000               # nm: pins closer than this to an edge get a corridor to it
BAND = int(os.environ.get("LEF_BAND", 2500))   # nm: edge band where the obstruction is the real metal (pin access room)
SUPPLY = {"vdd", "vss", "vddl", "VPWR", "VGND", "VDPWR", "VAPWR"}


def _rects(region, clean=20):
    """Rectangles of a region, after an opening by `clean` nm (removes the 15 nm slivers that via-pad overhangs
    leave next to 0.30 um trunks)."""
    out = []
    region = region.merged().sized(-clean).sized(clean).merged() if clean else region.merged()
    for p in region.decompose_trapezoids_to_region(1).each():   # 1 = horizontal trapezoids -> rectangles
        b = p.bbox()
        out.append(b)
    return out


def extend_pins(cell, reach=EDGE_REACH):
    """Extend every top-level pin's metal (merged polygon under its label) straight to the cell edge it is closest
    to, when that edge is within `reach`: TritonRoute only builds planar access to macro pins on the boundary.
    The extension is the pin's own net in an empty margin (DRC / LVS re-run after this)."""
    path = os.path.join(GDS, cell + ".gds")
    ly = pya.Layout()
    ly.read(path)
    top = ly.cell(cell) or ly.top_cell()
    bb = top.bbox()
    added = 0
    for lname, (dl, ll, sp) in LAYERS.items():
        if ly.find_layer(*dl) is None or ly.find_layer(*ll) is None or lname == "li1":
            continue
        li = ly.layer(*dl)
        metal = pya.Region(top.begin_shapes_rec(li)).merged()
        for sh in top.shapes(ly.layer(*ll)).each():
            if not sh.is_text():
                continue
            t = sh.text
            hit = metal.interacting(pya.Region(pya.Box(t.x - 1, t.y - 1, t.x + 1, t.y + 1)))
            for p in hit.each():
                b = p.bbox()
                d = {"L": b.left - bb.left, "R": bb.right - b.right, "B": b.bottom - bb.bottom, "T": bb.top - b.top}
                side = min(d, key=d.get)
                if 0 < d[side] < reach:
                    # extension with the width of the pin's end (the trunk / lane width)
                    if side in "LR":
                        x = b.left if side == "L" else b.right
                        edge = pya.Region(pya.Box(x - 2, b.bottom, x + 2, b.top)) & pya.Region(p)
                        e = edge.bbox()
                        ext = pya.Box(bb.left, e.bottom, x, e.top) if side == "L" else pya.Box(x, e.bottom, bb.right, e.top)
                    else:
                        y = b.bottom if side == "B" else b.top
                        edge = pya.Region(pya.Box(b.left, y - 2, b.right, y + 2)) & pya.Region(p)
                        e = edge.bbox()
                        ext = pya.Box(e.left, bb.bottom, e.right, y) if side == "B" else pya.Box(e.left, y, e.right, bb.top)
                    if ext.width() > 0 and ext.height() > 0:
                        top.shapes(li).insert(ext)
                        added += 1
    ly.write(path)
    return added


def make(cell, gds=None, out=None, use=None):
    ly = pya.Layout()
    ly.read(gds or os.path.join(GDS, cell + ".gds"))
    top = ly.cell(cell) or ly.top_cell()
    bb = top.bbox()
    pins = {}                                   # net -> {layer: Region}
    for lname, (dl, ll, sp) in LAYERS.items():
        if ly.find_layer(*dl) is None:
            continue
        metal = pya.Region(top.begin_shapes_rec(ly.layer(*dl))).merged()
        if ly.find_layer(*ll) is None:
            continue
        for sh in top.shapes(ly.layer(*ll)).each():          # top-level labels only (leaf pins are internal)
            if not sh.is_text():
                continue
            t = sh.text
            hit = metal.interacting(pya.Region(pya.Box(t.x - 1, t.y - 1, t.x + 1, t.y + 1)))
            if not hit.is_empty():
                pins.setdefault(t.string, {}).setdefault(lname, pya.Region())
                pins[t.string][lname] += hit
    keep = {}
    for net, by in pins.items():
        for lname, reg in by.items():
            reg = reg.merged()
            sp = LAYERS[lname][2]
            corr = pya.Region()
            for p in reg.each():
                b = p.bbox()
                if b.left - bb.left < EDGE_REACH:
                    corr.insert(pya.Box(bb.left, b.bottom, b.left, b.top))
                if bb.right - b.right < EDGE_REACH:
                    corr.insert(pya.Box(b.right, b.bottom, bb.right, b.top))
                if b.bottom - bb.bottom < EDGE_REACH:
                    corr.insert(pya.Box(b.left, bb.bottom, b.right, b.bottom))
                if bb.top - b.top < EDGE_REACH:
                    corr.insert(pya.Box(b.left, b.top, b.right, bb.top))
            keep.setdefault(lname, pya.Region())
            keep[lname] += (reg + corr).sized(sp)
            by[lname] = reg
    # pins are offered only where they are reachable: their part in the edge band (the rest stays obstruction)
    edge_band = pya.Region(bb) - pya.Region(bb).sized(-BAND)
    for net, by in pins.items():
        for lname in list(by):
            clipped = by[lname] & edge_band
            if not clipped.is_empty():
                by[lname] = clipped
    ox, oy = -bb.left / 1000, -bb.bottom / 1000
    f = lambda v: f"{v / 1000:.3f}"            # noqa: E731
    L = ["VERSION 5.7 ;", 'BUSBITCHARS "[]" ;', 'DIVIDERCHAR "/" ;', f"MACRO {cell}", "  CLASS BLOCK ;",
         f"  FOREIGN {cell} ;", f"  ORIGIN {ox:.3f} {oy:.3f} ;", f"  SIZE {bb.width() / 1000:.3f} BY {bb.height() / 1000:.3f} ;",
         "  SYMMETRY X Y ;"]
    for net in sorted(pins):
        L += [f"  PIN {net}", "    DIRECTION INOUT ;", f"    USE {(use or {}).get(net, 'SIGNAL')} ;", "    PORT"]
        for lname, reg in pins[net].items():
            L.append(f"      LAYER {lname} ;")
            for b in _rects(reg):
                L.append(f"        RECT {f(b.left)} {f(b.bottom)} {f(b.right)} {f(b.top)} ;")
        L += ["    END", f"  END {net}"]
    L.append("  OBS")
    core = pya.Region(bb).sized(-BAND)
    band = pya.Region(bb) - core
    for lname, (dl, ll, sp) in LAYERS.items():
        metal = pya.Region(top.begin_shapes_rec(ly.layer(*dl))) if ly.find_layer(*dl) is not None else pya.Region()
        pin_reg = pya.Region()
        for net, by in pins.items():
            if lname in by:
                pin_reg += by[lname]
        # solid core (no routing over the analog circuits) + the real metal in the edge band, pins excluded
        obs = ((core - pin_reg) + ((metal & band) - pin_reg)).merged()
        L.append(f"    LAYER {lname} ;")
        for b in _rects(obs):
            L.append(f"      RECT {f(b.left)} {f(b.bottom)} {f(b.right)} {f(b.top)} ;")
    L += ["  END", f"END {cell}", "END LIBRARY"]
    os.makedirs(LEF, exist_ok=True)
    out = out or os.path.join(LEF, cell + ".lef")
    open(out, "w").write("\n".join(L) + "\n")
    return out, {n: sorted(by) for n, by in pins.items()}


if __name__ == "__main__":
    if sys.argv[1] == "--extend":
        for c in sys.argv[2:]:
            print(c, "pin extensions:", extend_pins(c))
        sys.exit(0)
    for c in sys.argv[1:]:
        o, p = make(c)
        print(o, len(p), "pins")
