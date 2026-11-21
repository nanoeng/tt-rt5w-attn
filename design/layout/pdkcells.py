"""Known-good sky130A devices from the PDK's own magic device generators (sky130::<device>_draw in
libs.tech/magic/sky130A.tcl -- the generators behind magic's "Devices" menu, DRC-clean by construction and the
TinyTapeout sky130 standard), written to GDS once per geometry (layout/devcache/) and read into KLayout here, with
their terminals identified on met1 so the block generator can wire them.

(The KLayout sky130 pcells in libs.tech/klayout/python/cells need gdsfactory >= 8 / kfactory; magic's generators
need nothing beyond magic and are the same ones the PDK's LVS/extraction was validated with.)

Terminal extraction (cell coordinates, dbu 1 nm, device centred on the origin):
  FET   met1 strips crossing the diffusion (65/20), sorted by x, alternate S, D, S ...; met1 boxes outside the
        diffusion's y-range on the gate side are the per-finger gate contacts; the guard ring (p-tap for NMOS,
        n-tap in the n-well for PMOS) always surrounds the device and carries met1 on the side opposite the gates
        (viagb / viagt) = body terminal B, offered as a small box at its left end.
  RES   res_xhigh_po_0p35, nx parallel-drawn segments joined in series (snake) inside one guard ring: R1 (top) and
        R2 (bottom) met1 contacts = P / M; guard ring met1 on the bottom side = B.
"""
import hashlib
import os
import subprocess
import sys

import klayout.db as pya

PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/ext/pdk")
PDK = os.environ.get("PDK", "sky130A")
MAGICRC = os.path.join(PDK_ROOT, PDK, "libs.tech", "magic", f"{PDK}.magicrc")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CACHE = os.path.join(ROOT, "layout", "devcache")

# sky130 GDS layers (drawing / label)
L_LI, L_MCON = (67, 20), (67, 44)
L_M1, L_V1, L_M2, L_V2, L_M3, L_V3, L_M4, L_V4, L_M5 = (68, 20), (68, 44), (69, 20), (69, 44), (70, 20), (70, 44), \
    (71, 20), (71, 44), (72, 20)
L_NW, L_DNW, L_DIFF, L_TAP, L_POLY, L_HVI = (64, 20), (64, 18), (65, 20), (65, 44), (66, 20), (75, 20)
L_PR = (235, 4)
LABEL = {L_M1: (68, 5), L_M2: (69, 5), L_M3: (70, 5), L_M4: (71, 5), L_M5: (72, 5)}
PIN = {L_M3: (70, 16), L_M4: (71, 16)}
DBU = 0.001
# via geometry per cut layer: cut size, landing pad (x, y) per metal. met2 pads are narrow in x (stubs run
# vertically, 0.395 um apart at minimum-L devices): via1 0.055 / 0.085 um, via2 0.04 / 0.085 um enclosure;
# met3/met4 pads 0.5 um square (0.24 um2 min-area rule for isolated pads in the Metal4 escape stacks)
VIA = {L_V1: 150, L_V2: 200, L_V3: 200, L_V4: 800}
PADS = {L_V1: {L_M1: (260, 320), L_M2: (260, 320)}, L_V2: {L_M2: (280, 370), L_M3: (330, 330)},
        L_V3: {L_M3: (390, 330), L_M4: (500, 500)}, L_V4: {L_M4: (1180, 1180), L_M5: (1580, 1580)}}


class Device:
    """A placed-ready device: KLayout cell + terminal boxes (in nm, cell coordinates)."""

    def __init__(self, cell, pins, kind, bbox, nwell=None, dnw=False):
        self.cell, self.pins, self.kind, self.bbox, self.nwell, self.dnw = cell, pins, kind, bbox, nwell, dnw


_cache = {}


def _magic_gds(name, proc, params):
    """Run one sky130 device generator in magic batch mode -> CACHE/<name>.gds (cached)."""
    os.makedirs(CACHE, exist_ok=True)
    gds = os.path.join(CACHE, name + ".gds")
    if os.path.exists(gds):
        return gds
    sets = " ".join(f"{k} {v}" for k, v in params.items())
    tcl = f"""drc off
load {name}
box 0um 0um 0um 0um
set p [sky130::{proc}_defaults]
foreach {{k v}} {{{sets}}} {{dict set p $k $v}}
sky130::{proc}_draw $p
gds write {gds}
quit -noprompt
"""
    path = os.path.join(CACHE, name + ".tcl")
    open(path, "w").write(tcl)
    r = subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", MAGICRC, path], capture_output=True, text=True,
                       cwd=CACHE, timeout=300, env=dict(os.environ, PDK_ROOT=PDK_ROOT))
    if not os.path.exists(gds):
        raise RuntimeError(f"magic generator failed for {name}:\n{r.stdout[-1500:]}{r.stderr[-1500:]}")
    return gds


def _load(ly, gds, name):
    tmp = pya.Layout()
    tmp.read(gds)
    src = tmp.top_cell()
    src.flatten(True)
    for li in tmp.layer_indexes():                  # device-internal port labels would become block nets
        info = tmp.get_info(li)
        if info.datatype in (5, 16):
            src.shapes(li).clear()
    cell = ly.create_cell(name)
    cell.copy_tree(src)
    return cell


def _boxes(ly, cell, layer):
    return [s.bbox() for s in cell.shapes(ly.layer(*layer)).each()]


def fet(ly, kind, W, L, nf, side, dnw=False, tie=False):
    """kind 'n'|'p' (g5v0d10v5 3.3/5 V devices); side = 'top' or 'bottom' = where the gate contacts go (the routing
    channel side). No per-device guard ring (it doubles the area of folded devices): the block generator puts
    substrate / n-well taps (tap()) in the rows, at least every TAP_EVERY um and in every n-well."""
    key = (id(ly), kind, W, L, nf, side)
    if key in _cache:
        return _cache[key]
    proc = f"sky130_fd_pr__{'n' if kind == 'n' else 'p'}fet_g5v0d10v5"
    gate_top = side == "top"
    params = dict(w=f"{W:.3f}", l=f"{L:.3f}", nf=nf, m=1, guard=0, full_metal=1,
                  topc=1 if gate_top else 0, botc=0 if gate_top else 1, diffcov=100, polycov=100)
    name = f"{kind}fet_W{W:g}_L{L:g}_nf{nf}_{side[0]}_ng".replace(".", "p")
    gds = _magic_gds(name, proc, params)
    cell = _load(ly, gds, name)
    diff = _boxes(ly, cell, L_DIFF)
    act = max(diff, key=lambda b: b.width() * b.height())
    m1 = _boxes(ly, cell, L_M1)
    gates = [b for b in m1 if b.top <= act.bottom + 1 or b.bottom >= act.top - 1]
    strips = sorted([b for b in m1 if b not in gates], key=lambda b: b.left)
    if len(strips) != nf + 1:
        raise RuntimeError(f"{name}: expected {nf + 1} S/D strips, found {len(strips)}")
    pins = {"SD": strips, "G": sorted(gates, key=lambda b: b.left)}
    nw = _boxes(ly, cell, L_NW)
    nwell = None
    if nw:               # 3.3/5 V p-diffusion needs 0.33 um n-well overlap (diff/tap.17); the guard-less generator
        nwell = nw[0] + act.enlarged(400, 400)    # draws 0.18 um -- the parent's merged n-well uses this box
        cell.shapes(ly.layer(*L_NW)).insert(nwell)
    dev = Device(cell, pins, kind, cell.bbox(), nwell=nwell)
    _cache[key] = dev
    return dev


def tap(ly, kind):
    """Row tap: kind 'n' = substrate p+ tap (NMOS / resistor rows), 'p' = n+ tap in its own n-well (PMOS rows;
    the generator merges it with the devices' n-well of the same body net). tap 0.42 x 2.0 um, 4 licon + 4 mcon,
    li1 and met1 strips; pin B = the met1 strip."""
    key = (id(ly), "tap", kind)
    if key in _cache:
        return _cache[key]
    cell = ly.create_cell(f"tap_{kind}")
    sh = lambda layer, b: cell.shapes(ly.layer(*layer)).insert(b)   # noqa: E731
    sh(L_TAP, pya.Box(0, 0, 420, 2000))
    sh((94, 20) if kind == "n" else (93, 44), pya.Box(-125, -125, 545, 2125))
    for k in range(4):
        y = 155 + k * 480
        sh((66, 44), pya.Box(125, y, 295, y + 170))
        sh(L_MCON, pya.Box(125, y + 60, 295, y + 230))
    sh(L_LI, pya.Box(45, 75, 375, 1925))
    m1 = pya.Box(50, 85, 370, 1915)
    sh(L_M1, m1)
    nwell = None
    if kind == "p":
        nwell = pya.Box(-340, -340, 760, 2340)          # 0.34 um n-well enclosure of the 3.3/5 V n-tap
        sh(L_NW, nwell)
    # HVI in the cell itself: magic types the diffusion (3.3/5 V "mv" tap) per cell at GDS read
    sh(L_HVI, pya.Box(-340, -340, 760, 2340))
    dev = Device(cell, {"B": [m1]}, "tap", cell.bbox(), nwell=nwell)
    _cache[key] = dev
    return dev


def _hairpin(ly, seg):
    """Two-segment res_xhigh_po_0p35 snake (magic generator, nx = 2): both ends at the bottom, side by side.
    This is the unit that is DRC-clean as drawn: magic's rpm.1 (URPM >= 1.27 um) is met where the two legs' URPM
    regions merge; a single 0p35 segment, or the free ends of a longer snake, are only 0.75 um wide."""
    key = (id(ly), "hp", seg)
    if key in _cache:
        return _cache[key]
    name = f"rxhigh_hp_L{seg:g}".replace(".", "p")
    gds = _magic_gds(name, "sky130_fd_pr__res_xhigh_po_0p35",
                     dict(l=f"{seg:.3f}", nx=2, snake=1, guard=1, full_metal=1, viagb=100, glc=1, grc=1, gtc=1, gbc=1))
    cell = _load(ly, gds, name)
    m1 = _boxes(ly, cell, L_M1)
    bb = cell.bbox()
    ring = [b for b in m1 if b.width() > 1000 and b.bottom < bb.bottom + 400]
    terms = sorted([b for b in m1 if b not in ring], key=lambda t: t.left)
    if len(terms) != 2:
        raise RuntimeError(f"{name}: expected 2 resistor terminals, found {len(terms)}")
    _cache[key] = (cell, terms[0], terms[1], ring[0], bb)
    return _cache[key]


def res_segment(ly, L, nx=1):
    """res_xhigh_po_0p35 of total length L (um): ceil(L / 25 um / 2) hairpins (2-segment snakes) side by side,
    joined in series by met2 jumpers between neighbouring ends; pins P (first hairpin, left end), M (last hairpin,
    right end), B (guard-ring met1 at the bottom). netgen merges the series segments for LVS."""
    n_seg = max(2, nx + (nx % 2))
    n_hp = n_seg // 2
    seg = round(L / n_seg, 3)
    key = (id(ly), "r", L, n_hp)
    if key in _cache:
        return _cache[key]
    hcell, pa, pb, ring, hb = _hairpin(ly, seg)
    name = f"rser_L{L:g}_h{n_hp}".replace(".", "p")
    cell = ly.create_cell(name)
    pitch = hb.width() + 300                            # guard rings 0.3 um apart (diff/tap.3: 0.27 um)
    m2, v1, m1 = ly.layer(*L_M2), ly.layer(*L_V1), ly.layer(*L_M1)
    for k in range(n_hp):
        dx = k * pitch
        cell.insert(pya.CellInstArray(hcell.cell_index(), pya.Trans(dx, 0)))
        if k < n_hp - 1:                                # jumper: right end of hairpin k -> left end of hairpin k+1
            ya = 5 * round((pb.top + pb.bottom) / 10)        # manufacturing grid (5 nm)
            xa, xb = (pb.left + pb.right) // 2 + dx, (pa.left + pa.right) // 2 + dx + pitch
            for x in (xa, xb):
                cell.shapes(v1).insert(pya.Box(x - 75, ya - 75, x + 75, ya + 75))
                cell.shapes(m1).insert(pya.Box(x - 130, ya - 160, x + 130, ya + 160))
                cell.shapes(m2).insert(pya.Box(x - 130, ya - 160, x + 130, ya + 160))
            cell.shapes(m2).insert(pya.Box(xa - 130, ya - 160, xb + 130, ya + 160))
    last = (n_hp - 1) * pitch
    p = pa
    m = pya.Box(pb.left + last, pb.bottom, pb.right + last, pb.top)
    bb = pya.Box(hb.left, hb.bottom, hb.right + last, hb.top)
    dev = Device(cell, {"P": [p], "M": [m], "B": [pya.Box(ring.left, ring.bottom, ring.left + 320, ring.top)]}, "r", bb)
    dev.jumper_y = 5 * round((pb.top + pb.bottom) / 10)
    _cache[key] = dev
    return dev
