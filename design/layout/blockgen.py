"""Block layout generator: PDK-pcell devices placed in two rows around one routing channel, wired by a channel router.

    USER=$USER pixi run -e layout python design/layout/blockgen.py [block ...]     -> layout/gds/<block>.gds + .json

sky130A port: devices are the PDK's magic generators (pdkcells.py), each in its own guard ring (= body tie); routing
layers met1 (device terminals) / met2 stubs / met3 trunks and rails / met4 escapes, spine and power straps; the
whole block is covered by HVI (all devices are the 3.3/5 V g5v0d10v5 family).

Floorplan of a block (textbook analog row style):
    vdd rail (met3) ......................................................
    PMOS row      (gate contacts at the bottom, guard-ring met1 at the top, merged n-well per body net)
    ===== routing channel: met3 horizontal trunks (left-edge track assignment), met2 vertical stubs =====
    NMOS / resistor row (gate contacts at the top, guard-ring met1 at the bottom)
    vss rail (met3) ......................................................
Every terminal is a met1 shape of a known-good device. Terminals on the row's own supply (PMOS on vdd, NMOS/resistor
taps on vss) go straight to the rail with a Metal2 stub; all other terminals get a Metal2 stub into the channel and a
via2 onto their net's Metal3 trunk. The NMOS row is shifted so no NMOS stub shares an x column (+-0.8 um) with a PMOS
stub: the vertical-constraint graph is empty and plain left-edge track assignment is exact (no doglegs needed).
Block ports leave on Metal3 at the nearer block edge (trunk extended to the edge, text label on 42/10); vdd/vss are the
rails (labels at both ends). The JSON next to the GDS lists the block outline and every pin for the top-level router.
"""
import json
import math
import os
import re
import sys

import klayout.db as pya

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import pdkcells as P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
NETLIST = os.path.join(ROOT, "netlist")
OUT = os.path.join(ROOT, "layout", "gds")

UM = 1000                       # nm per um
GAP = 600                       # device-to-device gap (bbox to bbox)
GAP_WELL = 3000                 # extra gap where the n-well potential changes / around deep-n-well devices
STUB_W, PAD = 200, 500           # met2 stub width; largest via landing pad (met3/met4, min-area rule)
M4_W = 300                       # met4 minimum width (escapes)
TRUNK_W, PITCH = 300, 680       # met3 trunks: 0.3 um wide, 0.68 um pitch (0.33 um via pads)
COL_CLEAR = 520                 # min |x_top - x_bottom| between channel stubs of the two rows (pads 0.28 + 0.14 space)
SPINE_PITCH = 900               # met4 spine verticals: 0.5 um via pads + 0.3 um space
ESC_PITCH = 820                 # min distance between two met4 escape columns (0.5 pads + 0.3 space)
COL_SEARCH = 15000              # how far a bottom-row device may slide to avoid shared stub columns
ESC_GAP = 1700                  # bottom row to channel: room for the two levels of Metal4-escape landing stacks
RAIL_H = 900
# high-impedance analog nets routed with GUARD empty met3 tracks on each side of their channel trunk (and never in an
# over-the-row band): the readout's integration node 'int' ran 51 um at 0.38 um beside the StrongARM drain xa
# (5.8 fF, vs 0.3 fF on intr/xb): asymmetric kickback = -3 LSB offset in PEX (21 Nov). 2 empty tracks: gap 1.74 um.
SENSITIVE = {"rt5w_readout": {"int", "intr"}}
GUARD = 2
MAX_FINGERS = 32
BLOCK_MAXW = {"rt5w_idac4": 71.0}       # um: tiled above a key-cell column (70.8 um wide)
# port side overrides for blocks that are tiled: "B" = the trunk runs edge to edge with a pin on both sides
# (feed-through by abutment), "L" / "R" = forced side
PORT_SIDES = {
    "rt5w_keycell": {"row": "B", "w": "B", "vw": "B", "vbn": "B", "dcol": "R", "wsel": "R"},
    "rt5w_idac4": {"nd": "R", "b0": "R", "b1": "R", "b2": "R", "b3": "R", "col": "R"},
    "rt5w_coldiode": {"dcol": "R"},
    "rt5w_trimcell": {n: "R" for n in ("wsel", "vw", "w", "pg", "up_b", "up", "vmid", "dn", "ng", "dn_b")},
    "rt5w_pumpinv": {n: "L" for n in ("upb", "up", "dnb", "dn")},     # 6x2 array: pins face the trim column
}
W_FINGER_MAX = 8.0              # um per finger (wider devices are folded)
CHUNK_W = 60.0                  # um: widest device chunk between two row taps (taps on both sides: < 15 um)
R_SEG_MAX = 25.0                # um per resistor segment (res_xhigh_po snake)


# ------------------------------------------------------------------------------------------------ netlist
def _subckts(path):
    txt = open(path).read().replace("\n+", " ")
    subs = {}
    for m in re.finditer(r"^\.subckt (\S+) (.*?)$(.*?)^\.ends", txt, re.M | re.S):
        subs[m.group(1)] = ([w for w in m.group(2).split() if "=" not in w], m.group(3))
    return subs


def _parse_dev(line, block):
    t = line.split()
    params = dict(re.findall(r"(\w+)=([^\s]+)", line))
    first_param = next((k for k, w in enumerate(t) if "=" in w), len(t))
    nodes = t[1:first_param]
    model = nodes[-1].replace("sky130_fd_pr__", "")
    nodes = nodes[:-1]
    if model in ("nfet_g5v0d10v5", "pfet_g5v0d10v5"):
        return dict(name=t[0][1:], kind=model[0], D=nodes[0], G=nodes[1], S=nodes[2], B=nodes[3],
                    W=float(params["W"]), L=float(params["L"]), nf=int(params.get("nf", 1)),
                    m=int(params.get("mult", params.get("m", 1))))
    if model.startswith("res_xhigh_po"):
        return dict(name=t[0][1:], kind="r", P=nodes[0], M=nodes[1], B=nodes[2],
                    W=0.35, L=float(params["L"]), m=int(params.get("mult", params.get("m", 1))))
    return None


def parse_subckt(block):
    """Devices of a block's .subckt. Instances of other subckts in the same netlist are flattened (one layout
    for e.g. the whole 4x4 array): device names and internal nets get the instance path as prefix."""
    subs = _subckts(os.path.join(NETLIST, block + ".spice"))
    ports = subs[block][0]
    devs = []

    def walk(cell, prefix, netmap):
        for line in subs[cell][1].splitlines():
            t = line.split()
            if not t or not t[0].upper().startswith("X"):
                continue
            d = _parse_dev(line, block)
            m = lambda n: n if n in ("vdd", "vss") else netmap.get(n, prefix + n)   # noqa: E731
            if d is not None:
                for k in ("D", "G", "S", "B", "P", "M"):
                    if k in d:
                        d[k] = m(d[k])
                d["name"] = prefix + d["name"]
                devs.append(d)
                continue
            first_param = next((k for k, w in enumerate(t) if "=" in w), len(t))
            sub = t[first_param - 1]
            if sub not in subs:
                raise ValueError(f"{block}: unsupported device {line}")
            nets = [m(n) for n in t[1:first_param - 1]]
            walk(sub, prefix + t[0][1:] + "_", dict(zip(subs[sub][0], nets)))

    walk(block, "", {p: p for p in ports})
    alias = SUPPLY_ALIAS.get(block, {})
    if alias:                                  # e.g. the 1.8 V down-shifter: its vddl is laid out on the vdd rails
        for d in devs:
            for k in ("D", "G", "S", "B", "P", "M"):
                if k in d:
                    d[k] = alias.get(d[k], d[k])
        ports = [alias.get(p, p) for p in ports]
    return ports, devs


def schematic_positions(block):
    """Device name -> schematic (x, y); flattened children: parent instance position x 20 + device position."""
    try:
        import capture
        s = capture.BLOCKS[block]()
        pos = {}
        for i in s.insts:
            pos[i.name] = (i.x, i.y)
            child = i.sym.replace(".sym", "")
            if child in capture.BLOCKS:
                for c in capture.BLOCKS[child]().insts:
                    pos[f"{i.name}_{c.name}"] = (i.x * 20 + c.x, i.y * 20 + c.y)
        return pos
    except Exception:
        return {}


# ------------------------------------------------------------------------------------------------ geometry helpers
class Canvas:
    """Drawing helper. Every routing shape carries its intended net, so check_shorts() can prove that no two
    different nets touch on a routing layer (a cheap, exact pre-LVS check of the router's own geometry)."""

    def __init__(self, ly, top):
        self.ly, self.top = ly, top
        self.tagged = []                 # (layer, Box, net)

    def box(self, layer, x0, y0, x1, y1, net=None):
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        b = pya.Box(x0, y0, x1, y1)
        self.top.shapes(self.ly.layer(*layer)).insert(b)
        if net is not None:
            self.tagged.append((layer, b, net))

    def via(self, layer_via, layers_metal=None, x=0, y=0, pad=None, net=None, vertical=True, big=False):
        """Cut + landing pads on both metals (sky130 sizes, pdkcells.VIA / PADS). The met1 pad under via1 is
        0.26 x 0.32 um (0.055 / 0.085 um enclosure), long side along the device terminal (vertical=True: a
        source/drain strip; False: a gate contact or guard-ring bar)."""
        h = P.VIA[layer_via] // 2
        cuts = self.__dict__.setdefault("_cuts", {}).setdefault(layer_via, [])
        near = [(cx, cy) for cx, cy, cn in cuts if cn == net and net is not None and abs(cx - x) < 2 * h + 220
                and abs(cy - y) < 2 * h + 220]
        if not near:            # a same-net cut closer than the cut spacing: skip it (the pads bridge on metal)
            self.box(layer_via, x - h, y - h, x + h, y + h)
            cuts.append((x, y, net))
        for lm, pd in P.PADS[layer_via].items():
            if lm == P.L_M1:
                wx, wy = (260, 320) if vertical else (320, 260)
                self.box(lm, x - wx // 2, y - wy // 2, x + wx // 2, y + wy // 2, net)
            else:
                if big and lm in (P.L_M3, P.L_M4):          # isolated landing pad: 0.24 um2 minimum area
                    pd = (500, 500)
                self.box(lm, x - pd[0] // 2, y - pd[1] // 2, x + pd[0] // 2, y + pd[1] // 2, net)

    def vwire(self, layer, x, y0, y1, w=STUB_W, net=None):
        self.box(layer, x - w // 2, min(y0, y1) - w // 2, x + w // 2, max(y0, y1) + w // 2, net)

    def hwire(self, layer, y, x0, x1, w=TRUNK_W, net=None):
        self.box(layer, min(x0, x1) - w // 2, y - w // 2, max(x0, x1) + w // 2, y + w // 2, net)

    def check_shorts(self, extra=()):
        """Pairs of touching shapes of different nets per layer (extra: pin boxes on Metal1 as (layer, box, net))."""
        out = []
        by_layer = {}
        for layer, b, net in list(self.tagged) + list(extra):
            by_layer.setdefault(layer, []).append((b, net))
        for layer, items in by_layer.items():
            items.sort(key=lambda t: t[0].left)
            active = []
            for b, net in items:
                active = [(a, n) for a, n in active if a.right >= b.left]
                for a, n in active:
                    if n != net and a.touches(b):
                        out.append((layer, n, net, a, b))
                active.append((b, net))
        return out

    def fill_same_net_gaps(self, layer, space):
        """Same-net shapes closer than the layer's min spacing (magic flags those too): fill the notch between them
        (over their common x- or y-projection)."""
        items = sorted([(b, n) for l, b, n in self.tagged if l == layer], key=lambda t: t[0].left)
        added = 0
        for i, (a, na) in enumerate(items):
            for b, nb in items[i + 1:]:
                if b.left > a.right + space:
                    break
                if na != nb or a.touches(b):
                    continue
                gx = max(b.left - a.right, a.left - b.right, 0)
                gy = max(b.bottom - a.top, a.bottom - b.top, 0)
                if gx >= space or gy >= space:
                    continue
                if gy == 0:            # side by side: bridge over the common y-span
                    y0, y1 = max(a.bottom, b.bottom), min(a.top, b.top)
                    x0, x1 = min(a.right, b.right), max(a.left, b.left)
                    self.box(layer, min(x0, x1), y0, max(x0, x1), y1, na)
                elif gx == 0:          # stacked
                    x0, x1 = max(a.left, b.left), min(a.right, b.right)
                    y0, y1 = min(a.top, b.top), max(a.bottom, b.bottom)
                    self.box(layer, x0, min(y0, y1), x1, max(y0, y1), na)
                elif gx * gx + gy * gy >= space * space:
                    continue           # diagonal, corners already >= the min spacing apart (euclidean): no fill
                else:                  # diagonal: fill the bounding box of the corner gap
                    self.box(layer, min(a.right, b.right), min(a.top, b.top), max(a.left, b.left),
                             max(a.bottom, b.bottom), na)
                added += 1
        return added

    def label(self, layer, text, x, y):
        self.top.shapes(self.ly.layer(*P.LABEL[layer])).insert(pya.Text(text, pya.Trans(int(x), int(y))))


# ------------------------------------------------------------------------------------------------ device instances
class Placed:
    """One pcell (or resistor macro) instance in the block: pins as absolute boxes with their nets."""

    def __init__(self, name, row, dev, conn, body, sd_nets=(), kind=None, make=None):
        self.name, self.row, self.dev, self.conn, self.body = name, row, dev, conn, body
        self.sd_nets = list(sd_nets)
        self.kind = kind or (dev.kind if dev else None)
        self.make = make                 # side -> Device (FETs: gate contacts towards the channel)
        self.ox = self.oy = 0

    @property
    def rail(self):
        return "vdd" if self.kind in ("p", "tap_p") else "vss"
        self.extra_pins = []            # resistor macros: (net, box, side)

    def bbox(self):
        b = self.dev.bbox
        return pya.Box(b.left + self.ox, b.bottom + self.oy, b.right + self.ox, b.top + self.oy)

    def pin_list(self, absolute=True):
        """(terminal, net, box) for every Metal1 terminal; source/drain strips carry their own nets."""
        dx, dy = (self.ox, self.oy) if absolute else (0, 0)
        out = []
        for term, boxes in self.dev.pins.items():
            for i, b in enumerate(boxes):
                net = self.sd_nets[i] if term == "SD" else self.conn.get(term)
                if net is None:
                    continue
                out.append(("S" if term == "SD" else term, net,
                            pya.Box(b.left + dx, b.bottom + dy, b.right + dx, b.top + dy)))
        return out

    def pins(self):
        return self.pin_list(True)


def build_resistor_macro(ly, name, d):
    """Odd number of series segments stacked downwards; returns a Device whose pins are P (top-left), M (free end),
    B (tap strap)."""
    n = max(1, math.ceil(d["L"] / R_SEG_MAX))
    if n % 2 == 0:
        n += 1
    seg = P.res_segment(ly, round(d["L"] / n, 3), d["W"])
    cell = ly.create_cell(f"rser_{name}")
    pitch = seg.bbox.height() + 2000
    m1 = ly.layer(*P.L_M1)
    pins = {"P": [], "M": [], "B": []}
    tap_x = (seg.pins["B"][0].left + seg.pins["B"][0].right) // 2
    for k in range(n):
        y = -k * pitch
        cell.insert(pya.CellInstArray(seg.cell.cell_index(), pya.Trans(0, y)))
        if k < n - 1:                                     # jumper to the next segment: right for even k, left for odd
            side = "M" if k % 2 == 0 else "P"
            b = seg.pins[side][0]
            cell.shapes(m1).insert(pya.Box(b.left, y - pitch + b.bottom, b.right, y + b.top))
    tb = seg.pins["B"][0]
    cell.shapes(m1).insert(pya.Box(tb.left, -(n - 1) * pitch + tb.bottom, tb.right, tb.top))
    pins["P"] = [seg.pins["P"][0]]
    free = seg.pins["M" if (n - 1) % 2 == 0 else "P"][0]
    pins["M"] = [pya.Box(free.left, free.bottom - (n - 1) * pitch, free.right, free.top - (n - 1) * pitch)]
    pins["B"] = [pya.Box(tb.left, -(n - 1) * pitch + tb.bottom, tb.right, -(n - 1) * pitch + tb.top)]
    return P.Device(cell, pins, "r", cell.bbox())


def instances(ly, block, devs, pos):
    out, fets = [], []
    for d in devs:
        x, y = pos.get(d["name"], (0, 0))
        if d["kind"] == "r":
            for k in range(d["m"]):
                nx = max(1, math.ceil(d["L"] / R_SEG_MAX))
                dev = P.res_segment(ly, d["L"], nx)
                pl = Placed(f"{d['name']}_{k}", "bot", dev, {"P": d["P"], "M": d["M"], "B": d["B"]}, "vss", kind="r")
                pl.sx = (x, y)
                out.append(pl)
            continue
        fets.append((d, x, y))
    out += merged_fets(ly, block, fets)
    return out


def _unit_fingers(W):
    """Fingers per unit device: W folded to <= W_FINGER_MAX per finger, rounded up to an even count so that a
    unit starts and ends on its shared (common) strip; odd (1) only when W / 2 is below the minimum width."""
    k = max(1, math.ceil(W / W_FINGER_MAX - 1e-9))
    return k, round(W / k / 0.005) * 0.005


def merged_fets(ly, block, fets):
    """Dense rows: transistors of one kind, finger width, L, gate and body that share a source (or a drain) net
    are drawn as ONE multi-finger diffusion, unit after unit, strips  C X1 C X1 C X2 C ...  (C = the common net).
    Mirror / DAC / IDAC arrays collapse from n separate devices into one strip of shared diffusion; netgen merges
    the parallel fingers of each unit back into the schematic device (total W, same L)."""
    out = []
    items = []
    for d, x, y in fets:
        if d["kind"] == "n" and d["B"] != "vss":
            raise ValueError(f"{block}/{d['name']}: NMOS body {d['B']} needs an isolated p-well (not supported)")
        k, wf = _unit_fingers(d["W"] * d["nf"])
        items.append(dict(d=d, x=x, y=y, k=k, wf=wf))
    groups, rest = {}, []
    for it in items:
        d = it["d"]
        groups.setdefault((d["kind"], it["wf"], d["L"], d["G"], d["B"], "S", d["S"]), []).append(it)
    left = []
    for key, g in list(groups.items()):
        if len(g) == 1:
            left += g
            del groups[key]
    for it in left:                                   # second chance: share the drain instead
        d = it["d"]
        groups.setdefault((d["kind"], it["wf"], d["L"], d["G"], d["B"], "D", d["D"]), []).append(it)
    for key in [k for k, g in groups.items() if k[5] == "D" and len(g) == 1]:
        rest += groups.pop(key)
    for gi, (key, g) in enumerate(sorted(groups.items(), key=lambda kv: min(i["x"] for i in kv[1]))):
        kind, wf, L, G, B, side, common = key
        other = "D" if side == "S" else "S"
        g = sorted(g, key=lambda i: (i["d"][other], i["x"]))
        # islands of shared diffusion: an interior strip is shared by two fingers, so it is either the common
        # net or a drain shared by two units of the SAME net; a change of drain net on a drain strip starts a
        # new island
        fing = [it["d"][other] for it in g for _ in range(it["d"]["m"] * it["k"])]
        islands, cur = [], None
        for x in fing:
            if cur is None:
                cur = [x, common]
            elif cur[-1] == common:
                cur.append(x)
            elif cur[-1] == x:
                cur.append(common)
            else:
                islands.append(cur)
                cur = [x, common]
        islands.append(cur)
        cw = CHUNK_W if (kind == "n" or B == "vdd") else 22.0      # other-body n-wells: in-row taps
        per = max(1, min(2 * MAX_FINGERS, int(cw // (L + 0.8))))
        x0, y0 = g[0]["x"], g[0]["y"]
        c = 0
        for strips in islands:
            F = len(strips) - 1
            for a in range(0, F, per):
                nf = min(per, F - a)
                sd = strips[a:a + nf + 1]
                make = (lambda side_, nf=nf, wf=wf, kind=kind, L=L: P.fet(ly, kind, wf, L, nf, side_))
                pl = Placed(f"g{gi}_{g[0]['d']['name']}_{c}", "top" if kind == "p" else "bot", make("top"),
                            {"G": G, "B": B}, B, sd_nets=sd, kind=kind, make=make)
                pl.sx = (x0, y0)
                out.append(pl)
                c += 1
    for it in rest:                                   # stand-alone devices (own fingers, chunked)
        d, k, wf = it["d"], it["k"], it["wf"]
        fingers = d["m"] * k
        cw = CHUNK_W if (d["kind"] == "n" or d["B"] == "vdd") else 22.0
        per = max(1, min(MAX_FINGERS, int(cw // (d["L"] + 0.8))))
        chunks = [per] * (fingers // per) + ([fingers % per] if fingers % per else [])
        for c, nf in enumerate(chunks):
            make = (lambda side_, nf=nf, d=d, wf=wf: P.fet(ly, d["kind"], wf, d["L"], nf, side_))
            sd = [d["S"] if i % 2 == 0 else d["D"] for i in range(nf + 1)]
            pl = Placed(f"{d['name']}_{c}", "top" if d["kind"] == "p" else "bot", make("top"),
                        {"G": d["G"], "B": d["B"]}, d["B"], sd_nets=sd, kind=d["kind"], make=make)
            pl.sx = (it["x"], it["y"])
            out.append(pl)
    return out


# ------------------------------------------------------------------------------------------------ the generator
def _row_width(row):
    return sum(pl.dev.bbox.width() + GAP for pl in row)


def partition(insts, target_w):
    """Rows of one device type each (PMOS / NMOS+resistors), schematic order, about target_w long; rows are then
    paired around one channel each: PMOS over NMOS while both last, then the remaining rows two by two."""
    def rows_of(items):
        rows, cur = [], []
        for pl in sorted(items, key=lambda i: (i.sx[0], i.sx[1], i.name)):
            if cur and _row_width(cur + [pl]) > target_w:
                rows.append(cur)
                cur = []
            cur.append(pl)
        return rows + ([cur] if cur else [])
    rp = rows_of([i for i in insts if i.kind == "p"])
    rn = rows_of([i for i in insts if i.kind != "p"])
    pairs = []
    while rp and rn:
        pairs.append((rp.pop(0), rn.pop(0)))
    rest = rp + rn
    while rest:
        a = rest.pop(0)
        b = rest.pop(0) if rest else []
        pairs.append((a, b))
    return pairs




def with_taps(ly, row):
    """Rail-body devices (NMOS on vss, PMOS on vdd) are tied by the continuous tap strip along the row's rail
    side (tap_strip(), drawn by the generator). Only PMOS in an n-well of another body net (vr, o1, ...) get
    in-row taps: one at the start of their n-well group, at least every TAP_EVERY, one at the end."""
    out, since, grp = [], None, None
    for pl in row:
        if pl.kind == "p" and pl.body != "vdd":
            if grp != pl.body:
                if grp is not None and out and not out[-1].kind.startswith("tap"):
                    out.append(_tap(ly, out[-1], grp))
                since, grp = None, pl.body
            if since is None or since > TAP_EVERY:
                out.append(_tap(ly, pl, pl.body))
                since = 0
            out.append(pl)
            since += pl.dev.bbox.width() + GAP
            continue
        if grp is not None and out and not out[-1].kind.startswith("tap"):
            out.append(_tap(ly, out[-1], grp))
        grp = None
        out.append(pl)
    if grp is not None and out and not out[-1].kind.startswith("tap"):
        out.append(_tap(ly, out[-1], grp))
    return out


def _tap(ly, ref, body):
    t = Placed(f"tap_{ref.name}_{body}", ref.row, P.tap(ly, "p"), {"B": body}, body, kind="tap_p")
    t.sx = ref.sx
    return t


STRIP_H = 500                   # nm: tap strip diffusion height
STRIP_ROOM = 0                  # the tap strip sits under its met3 rail (no extra room)


def tap_strip(cv, kind, x0, x1, y0, rail, rail_y, nwell_to=None, stub=False):
    """Continuous substrate (kind 'n': p+ in psub) or n-well (kind 'p': n+ in the n-well) tap along a row, at
    y0..y0+STRIP_H, x0..x1: licon / li1 / mcon / met1, tied to the rail by a met2 stub at each end. For 'p' the
    n-well is drawn from the strip to nwell_to (the row's n-well edge) so that it merges with the devices'."""
    yc = y0 + STRIP_H // 2
    cv.box(P.L_TAP, x0, y0, x1, y0 + STRIP_H)
    cv.box((94, 20) if kind == "n" else (93, 44), x0 - 125, y0 - 125, x1 + 125, y0 + STRIP_H + 125)
    x = x0 + 165
    while x + 170 <= x1 - 165:
        cv.box((66, 44), x, yc - 85, x + 170, yc + 85)
        x += 480
    cv.box(P.L_LI, x0 + 45, yc - 165, x1 - 45, yc + 165)
    x = x0 + 405
    while x + 170 <= x1 - 165:
        cv.box(P.L_MCON, x, yc - 85, x + 170, yc + 85)
        x += 480
    cv.box(P.L_M1, x0, yc - 165, x1, yc + 165, rail)
    if kind == "p":
        lo, hi = y0 - 340, y0 + STRIP_H + 340
        if nwell_to is not None:
            lo, hi = min(lo, nwell_to), max(hi, nwell_to)
        cv.box(P.L_NW, x0 - 340, lo, x1 + 340, hi)
    for xs in (x0 + 200, x1 - 200):              # via stack into the rail (above the strip, or by a stub)
        cv.via(P.L_V1, None, xs, yc, net=rail, vertical=False)
        if stub:
            cv.vwire(P.L_M2, xs, yc, rail_y, net=rail)
        cv.via(P.L_V2, [P.L_M2, P.L_M3], xs, rail_y if stub else yc, net=rail)


def strip_runs(row):
    """x-runs of consecutive rail-body devices of a row (resistors and other-body PMOS break a run)."""
    runs, cur = [], []
    for pl in sorted(row, key=lambda p: p.bbox().left):
        ok = (pl.kind == "n") or (pl.kind == "p" and pl.body == "vdd")
        if ok:
            cur.append(pl)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return runs


TAP_EVERY = 10000               # nm: taps <= ~28 um apart incl. one chunk -> every diffusion < 15 um from a tap (LU.2/LU.3)


GLOBAL_NETS = {"vdd", "vss"}
SUPPLY_ALIAS = {"rt5w_lsdn": {"vddl": "vdd"}}    # block-local supply laid out on the vdd rails
REORDER = True                  # barycentric reorder of each row pair (generate_best tries both)


def _density(rows):
    """Channel density estimate of a row pair: max number of net spans over any x (rows laid out left to right)."""
    span = {}
    for row in rows:
        x = 0
        for pl in row:
            w = pl.dev.bbox.width()
            for _, n, _b in channel_pins(pl, absolute=False):
                if n in GLOBAL_NETS:
                    continue
                lo, hi = span.get(n, (x + w // 2, x + w // 2))
                span[n] = (min(lo, x + w // 2), max(hi, x + w // 2))
            x += w + GAP
    ev = sorted([(lo, 1) for lo, hi in span.values()] + [(hi + 1, -1) for lo, hi in span.values()])
    cur = best = 0
    for _, d in ev:
        cur += d
        best = max(best, cur)
    return best, sum(hi - lo for lo, hi in span.values())


def reorder_pair(top_in, bot_in, passes=8):
    """Barycentric ordering of both rows of a pair (devices next to the devices they share nets with), keeping
    each PMOS body group contiguous; the ordering with the lowest channel density wins (ties: total span)."""
    rows = [list(top_in), list(bot_in)]
    nets = {id(pl): {n for _, n, _b in channel_pins(pl, absolute=False)} - GLOBAL_NETS for r in rows for pl in r}
    best = (_density(rows), [list(r) for r in rows])
    for it in range(passes):
        k = it % 2
        pos = {}
        for row in rows:
            x = 0
            for pl in row:
                pos[id(pl)] = x + pl.dev.bbox.width() / 2
                x += pl.dev.bbox.width() + GAP
        others = [pl for r in rows for pl in r]

        def bary(pl):
            xs = [pos[id(o)] for o in others if o is not pl and nets[id(o)] & nets[id(pl)]]
            return sum(xs) / len(xs) if xs else pos[id(pl)]
        groups = {}
        for pl in rows[k]:
            groups.setdefault(pl.body if pl.kind == "p" else None, []).append(pl)
        ordered = []
        for g in sorted(groups.values(), key=lambda g: sum(bary(p) for p in g) / len(g)):
            ordered += sorted(g, key=bary)
        rows[k] = ordered
        sc = _density(rows)
        if sc < best[0]:
            best = (sc, [list(r) for r in rows])
    return best[1][0], best[1][1]


def place_pair(cv, top_in, bot_in):
    """Place one row pair at y = 0 (top-row active bottoms); gate contacts of both rows face the channel."""
    for pl in top_in:
        pl.row = "top"
        if pl.make:
            pl.dev = pl.make("bottom")
    for pl in bot_in:
        pl.row = "bot"
        if pl.make:
            pl.dev = pl.make("top")
    top_row = with_taps(cv.ly, top_in)
    bot_row = with_taps(cv.ly, bot_in)
    x, prev = 0, None
    for pl in top_row:
        if prev is not None and pl.body != prev and pl.kind in ("p", "tap_p"):
            x += GAP_WELL
        pl.ox, pl.oy = x - pl.dev.bbox.left, 0
        x = pl.bbox().right + GAP
        prev = pl.body
    top_cols = [(b.left + b.right) // 2 for pl in top_row for _, _, b in channel_pins(pl)]
    x, prev_dnw, prev = 0, False, None
    for pl in bot_row:
        if pl.dev.dnw or prev_dnw or (pl.kind in ("p", "tap_p") and prev is not None and pl.body != prev):
            x += GAP_WELL
        ox0 = ox = x - pl.dev.bbox.left
        rel = [((b.left + b.right) // 2) for term, net, b in channel_pins(pl, absolute=False)]
        for _ in range(COL_SEARCH // 100):        # cheap first: slide right to clear the PMOS stub columns
            if all(abs(c + ox - t) >= COL_CLEAR for c in rel for t in top_cols):
                break
            ox += 100
        else:
            ox = ox0                               # dense row: the vertical constraints go to the track order
        pl.ox = ox
        x = pl.bbox().right + GAP
        prev_dnw = pl.dev.dnw
        prev = pl.body
    return top_row, bot_row


RAIL = {"top": "vdd", "bot": "vss"}


def channel_pins(pl, absolute=True):
    res = []
    items = pl.pin_list(absolute)
    for term, net, b in items:
        if term == "R" or (net == pl.rail and term in ("S", "D", "B", "P", "M")):
            continue
        res.append((term, net, b))
    return res


def rail_pins(pl):
    return [(t, n, b) for t, n, b in pl.pins() if t == "R" or (n == pl.rail and t in ("S", "D", "B", "P", "M"))]


def constrained_left_edge(nets, above, block=""):
    """Track assignment, top track first: a net may take the current track once every net that must lie above it
    is placed; intervals on one track keep PITCH + PAD apart. A constraint cycle is broken by splitting nothing but
    by dropping the weakest edge (reported) -- the slide of the bottom row makes cycles rare."""
    iv = {n: (min(xs), max(xs)) for n, xs in nets.items()}
    todo = set(nets)
    track_of = {}
    t = 0
    while todo:
        end = None
        placed_any = False
        for n in sorted(todo, key=lambda n: iv[n]):
            if any(m in todo for m in above[n]):
                continue
            a, b = iv[n]
            if end is None or end + PITCH + PAD <= a:
                track_of[n] = t
                end = b
                placed_any = True
        for n in [n for n in todo if n in track_of]:
            todo.discard(n)
        if not placed_any:                        # cycle: release the net with the fewest pending constraints
            n = min(todo, key=lambda n: (sum(m in todo for m in above[n]), iv[n]))
            print(f"  VCG cycle in {block}: {n} placed before {sorted(m for m in above[n] if m in todo)}")
            above[n] = set()
            continue
        t += 1
    return track_of


def generate(block, target_w=None):
    P._cache.clear()                                  # pcells belong to one Layout
    ports, devs = parse_subckt(block)
    pos = schematic_positions(block)
    ly = pya.Layout()
    ly.dbu = P.DBU
    top = ly.create_cell(block)
    cv = Canvas(ly, top)
    insts = instances(ly, block, devs, pos)
    area = sum(pl.dev.bbox.width() * pl.dev.bbox.height() for pl in insts) / 1e6
    if target_w is None:                              # aim at ~2.5 : 1 including channels and rails
        target_w = max(60000, int(math.sqrt(area * 1e6 * 5.0)))
    pairs = partition(insts, target_w)

    # ---- place every pair in local coordinates, then decide its channel
    geo = []
    rail_of = lambda row: ("vdd" if any(p.kind == "p" for p in row) else "vss")   # noqa: E731
    prev_bot = None
    for top_in, bot_in in pairs:
        # mirror the pair when that lets it share the rail of the pair above (vss-vss / vdd-vdd abutment)
        if prev_bot is not None and bot_in and rail_of(bot_in) == prev_bot and rail_of(top_in) != prev_bot:
            top_in, bot_in = bot_in, top_in
        prev_bot = rail_of(bot_in) if bot_in else rail_of(top_in)
        if REORDER:
            top_in, bot_in = reorder_pair(top_in, bot_in)
        top_row, bot_row = place_pair(cv, top_in, bot_in)
        geo.append((top_row, bot_row))
    insts = [pl for tr, br in geo for pl in tr + br]
    xmin = -2600
    xspine = max(pl.bbox().right for pl in insts) + 2000
    multi = {}                                        # nets with trunks in more than one pair -> spine
    for k, (tr, br) in enumerate(geo):
        for pl in tr + br:
            for _, net, _ in channel_pins(pl):
                multi.setdefault(net, set()).add(k)
    spine_nets = sorted(n for n, ks in multi.items() if len(ks) > 1 and n not in ("vdd", "vss"))
    # local spines: each multi-pair net gets its met4 vertical at the median x of its own pins (legalised to
    # SPINE_PITCH), so its trunks stay short; escapes keep clear of these columns (see the escape loop)
    pin_x = {}
    for k, (tr, br) in enumerate(geo):
        for pl in tr + br:
            for _, net, b in channel_pins(pl):
                pin_x.setdefault(net, []).append((b.left + b.right) // 2)
    want = sorted((sorted(pin_x[n])[len(pin_x[n]) // 2], n) for n in spine_nets)
    xspine_tr, last = {}, None
    for x, n in want:
        x = max(x, xmin + 4000) if last is None else max(x, last + SPINE_PITCH)
        xspine_tr[n] = x
        last = x
    xspine = max([xspine] + [x + 1000 for x in xspine_tr.values()])
    xmax = xspine + 2000
    spine_span = {n: (min(multi[n]), max(multi[n])) for n in spine_nets}
    xmid = (xmin + xspine) // 2

    port_pair = {}
    for p in ports:
        if p in ("vdd", "vss"):
            continue
        ks = sorted(multi.get(p, {0}))
        port_pair[p] = ks[0]

    # ---- vertical assembly: pair 0 on top
    y_cursor = 0
    strips = []                                       # tap strips, drawn once per rail after all pairs
    pair_info = []
    forbid = {}                                       # rail y -> x-intervals kept free of the n-tap strip
    pins_json, rails = [], []
    for k, (top_row, bot_row) in enumerate(geo):
        nets = {}
        for pl in top_row + bot_row:
            for term, net, b in channel_pins(pl):
                nets.setdefault(net, []).append((b.left + b.right) // 2)
        port_side = {}
        for p, kk in port_pair.items():
            if kk != k:
                continue
            xs = nets.setdefault(p, [])
            side = "L" if (not xs or sum(xs) / len(xs) < xmid or p in spine_nets) else "R"
            side = PORT_SIDES.get(block, {}).get(p, side)
            port_side[p] = side
            xs += {"L": [xmin], "R": [xmax], "B": [xmin, xmax]}[side]
        for n in spine_nets:
            if n in nets:
                nets[n].append(xspine_tr[n])
        for rnet in ("vdd", "vss"):                   # supplies met in the channel go to their Metal4 strap
            if rnet in nets:
                xs_ = xmin + 1000 if rnet == "vdd" else xmax - 1000
                nets[rnet] += [xs_ - 400, xs_ + 400]
        for n, xs in nets.items():                    # one-pin trunks: 0.7 um long at least (met3 minimum area)
            if xs and max(xs) - min(xs) < 700:
                xs += [min(xs) - 350, max(xs) + 350]
        # over-the-row bands: a net whose terminals are all in one row runs its met3 trunk over that row (source /
        # drain strips are tapped where the trunk crosses them); only nets of both rows use the channel
        rows_of = {}
        for tag, row in (("t", top_row), ("b", bot_row)):
            for pl in row:
                for _, n, _b in channel_pins(pl):
                    rows_of.setdefault(n, set()).add(tag)
        band_track, band_h = {}, {}
        for tag, row in (("t", top_row), ("b", bot_row)):
            cand = {n: nets[n] for n, r in rows_of.items() if r == {tag} and n in nets
                    and n not in SENSITIVE.get(block, ())}
            # band region = the y-span common to every device of the row (strip-end via pads stay 1.1 um away)
            hmin = min([pl.dev.bbox.height() for pl in row if pl.kind in ("n", "p")] + [0])
            cap = max(0, (hmin - 2200) // PITCH)
            band_h[tag] = hmin
            if not cand or cap == 0:
                continue
            tof = constrained_left_edge(cand, {n: set() for n in cand}, block)
            for n, t in tof.items():
                if t < cap:
                    band_track[n] = (tag, t)
        band_nets = set(band_track)
        all_nets = nets
        nets = {n: xs for n, xs in all_nets.items() if n not in band_nets}
        # vertical constraints: a top-row stub and a bottom-row stub of different nets in one column -> the top net's
        # track must lie above the bottom net's track (then the two stubs never meet)
        tcol = [((b.left + b.right) // 2, n) for pl in top_row for _, n, b in channel_pins(pl) if n not in band_nets]
        bcol = [((b.left + b.right) // 2, n) for pl in bot_row for _, n, b in channel_pins(pl) if n not in band_nets]
        above = {n: set() for n in nets}           # above[n] = nets that must be on a higher track than n
        tcol.sort()
        import bisect
        txs = [c for c, _ in tcol]
        escape = set()                             # bottom-row columns that climb on Metal4 instead (no constraint)
        last_esc = None
        for xb, nb in sorted(bcol):
            i = bisect.bisect_left(txs, xb - COL_CLEAR + 1)
            hits = []
            while i < len(tcol) and tcol[i][0] < xb + COL_CLEAR:
                if tcol[i][1] != nb:
                    hits.append(tcol[i][1])
                i += 1
            if not hits:
                continue
            near_spine = any(abs(xb - xspine_tr[n]) < 800 and spine_span[n][0] <= k <= spine_span[n][1]
                             for n in spine_nets)
            if (last_esc is None or xb - last_esc >= ESC_PITCH) and not near_spine:
                escape.add(xb)
                last_esc = xb
            else:                                   # too close to the previous met4 escape: order the tracks instead
                for nt in hits:
                    above[nb].add(nt)
        track_of = constrained_left_edge(nets, above, block)
        sens = {t for n, t in track_of.items() if n in SENSITIVE.get(block, ())}
        if sens:                                   # monotonic remap: GUARD empty tracks around each sensitive track
            ntr0 = 1 + max(track_of.values())
            newt, cur, prev_s = {}, 0, False
            for t in range(ntr0):
                if (t in sens and t > 0) or (prev_s and t not in sens):
                    cur += GUARD
                newt[t] = cur
                cur += 1
                prev_s = t in sens
            track_of = {n: newt[t] for n, t in track_of.items()}
        # verify: every bottom stub that shares a column with a top stub either escapes on met4 or has its track
        # below the top net's track; otherwise escape it anyway (the met4 spacing is then left to DRC)
        for xb, nb in bcol:
            if xb in escape:
                continue
            i = bisect.bisect_left(txs, xb - COL_CLEAR + 1)
            while i < len(tcol) and tcol[i][0] < xb + COL_CLEAR:
                nt = tcol[i][1]
                if nt != nb and track_of[nt] >= track_of[nb]:     # top net's track not above (track 0 = top)
                    escape.add(xb)
                    print(f"  forced escape in {block}: {nb} at x={xb} under {nt}")
                    break
                i += 1
        ntr = 1 + max(track_of.values(), default=-1)
        pair_info.append(dict(chan_tracks=ntr, band=len(band_nets), top_h=max([pl.dev.bbox.height() for pl in top_row] + [0]) / UM,
                              bot_h=max([pl.dev.bbox.height() for pl in bot_row] + [0]) / UM,
                              top_w=sum(pl.dev.bbox.width() for pl in top_row) / UM, bot_w=sum(pl.dev.bbox.width() for pl in bot_row) / UM,
                              n_nets=len(nets), ports=sorted(port_side), spine_ports=sorted(p for p in port_side if p in spine_nets),
                              spines_through=sum(1 for n in spine_nets if n in nets)))
        # local vertical layout of the pair (y grows upwards; the pair is shifted down by y_cursor)
        top_high = max([pl.bbox().top for pl in top_row] + [0])
        top_low = min([pl.bbox().bottom for pl in top_row] + [0])
        net_t = top_row[0].rail if top_row else "vdd"
        net_b = bot_row[0].rail if bot_row else "vss"
        y_vdd = top_high + 800 + RAIL_H // 2
        ch_top = top_low - 800
        ch_bot = ch_top - (ntr * PITCH + 1000)
        track_y = {n: ch_top - 500 - t * PITCH - PITCH // 2 for n, t in track_of.items()}
        if not nets:                                  # no channel nets: the rows only need the escape gap
            ch_bot = ch_top
        for pl in bot_row:
            pl.oy = 0
            pl.oy = ch_bot - (ESC_GAP if escape else 700) - pl.bbox().top
        bot_top = ch_bot - (ESC_GAP if escape else 700)
        for n, (tag, t) in band_track.items():
            if tag == "t":       # top row devices are centred on y = 0
                track_y[n] = (band_h["t"] // 2 - 1100) - PITCH // 2 - t * PITCH
            else:                # bottom row devices hang from bot_top
                track_y[n] = bot_top - 1100 - PITCH // 2 - t * PITCH
        bot_low = min([pl.bbox().bottom for pl in bot_row] + [ch_bot - 3000])
        y_vss = bot_low - 800 - RAIL_H // 2
        shift = y_cursor - (y_vdd + RAIL_H // 2)      # top of this pair's vdd rail goes to y_cursor
        if rails and rails[-1][0] == net_t:          # same supply as the pair above: share its rail
            shift = rails[-1][1] - y_vdd
        for pl in top_row + bot_row:
            pl.oy += shift
        y_vdd += shift
        y_vss += shift
        track_y = {n: y + shift for n, y in track_y.items()}
        ch_bot += shift
        ch_top += shift
        y_cursor = y_vss - RAIL_H // 2 - 600
        rails += [(net_t, y_vdd), (net_b, y_vss)]
        # n-wells per body group
        groups = []
        for pl in top_row + [None] + bot_row:          # both rows (a pair can be PMOS over PMOS)
            if pl is None:
                groups.append((None, []))
                continue
            if groups and groups[-1][0] == pl.body:
                groups[-1][1].append(pl)
            else:
                groups.append((pl.body, [pl]))
        for body, g in groups:
            if not g:
                continue
            nws = [pya.Box(p.dev.nwell.left + p.ox, p.dev.nwell.bottom + p.oy, p.dev.nwell.right + p.ox,
                           p.dev.nwell.top + p.oy) for p in g if p.dev.nwell]
            if nws:
                cv.box(P.L_NW, min(b.left for b in nws), min(b.bottom for b in nws), max(b.right for b in nws),
                       max(b.top for b in nws))
        for pl in top_row + bot_row:
            inst = top.insert(pya.CellInstArray(pl.dev.cell.cell_index(), pya.Trans(pl.ox, pl.oy)))
            if getattr(pl.dev, "urpm", None) is not None:
                pass   # (kept hierarchical)
                #                   URPM mask hints where routing overlaps it (rpm.1 false errors at the snake ends)
        cv.hwire(P.L_M3, y_vdd, xmin, xmax, w=RAIL_H, net=net_t)
        cv.hwire(P.L_M3, y_vss, xmin, xmax, w=RAIL_H, net=net_b)
        # continuous tap strips on the rail side of each row (latch-up: every diffusion < 15 um from a tap)
        for row, rail, ry, up in ((top_row, net_t, y_vdd, True), (bot_row, net_b, y_vss, False)):
            srow = sorted(row, key=lambda p: p.bbox().left)
            for run in strip_runs(row):
                i0, i1 = srow.index(run[0]), srow.index(run[-1])
                mrg = 2500 if run[0].kind == "p" else 400     # n-well: 2 um to another-body n-well (nwell.8)
                lo_lim = srow[i0 - 1].bbox().right + mrg if i0 > 0 else -10 ** 9
                hi_lim = srow[i1 + 1].bbox().left - mrg if i1 + 1 < len(srow) else 10 ** 9
                x0 = max(min(p.bbox().left for p in run) - 700, lo_lim)
                x1 = min(max(p.bbox().right for p in run) + 700, hi_lim)
                kind = run[0].kind
                if up:
                    y0 = ry - STRIP_H // 2               # under the rail
                    nw = min(p.dev.nwell.top + p.oy for p in run if p.dev.nwell) - 100 if kind == "p" else None
                else:
                    y0 = ry - STRIP_H // 2
                    nw = max(p.dev.nwell.bottom + p.oy for p in run if p.dev.nwell) + 100 if kind == "p" else None
                if abs((y0 + STRIP_H // 2) - (max(p.bbox().top for p in run) if up else
                                                min(p.bbox().bottom for p in run))) > 7000:
                    # the run sits far from its rail (a taller device sets the row): its own strip next to it
                    yy = (max(p.bbox().top for p in run) + 600) if up else \
                        (min(p.bbox().bottom for p in run) - 600 - STRIP_H)
                    tap_strip(cv, kind, x0, x1, yy, rail, ry, nwell_to=nw, stub=True)
                    continue
                strips.append((kind, x0, x1, y0, rail, ry, nw))
            if any(p.kind in ("p", "tap_p") for p in row):    # other-body n-wells next to this rail: keep out
                for pl in row:
                    if pl.body != "vdd" and pl.kind in ("p", "tap_p"):
                        forbid.setdefault(ry, []).append((pl.bbox().left - 2700, pl.bbox().right + 2700))
        # stubs (+ M2 bridges between same-net pads closer than the M2 spacing)
        pads = []

        esc_rank = {x: i for i, x in enumerate(sorted(escape))}

        def stub(b, target_y, net, esc=False):
            cx = (b.left + b.right) // 2
            vy = b.bottom + 160 if target_y < b.bottom else b.top - 160
            if b.height() < 400:
                vy = (b.bottom + b.top) // 2
            cv.via(P.L_V1, None, cx, vy, net=net, vertical=b.height() > b.width())
            if not esc:
                cv.vwire(P.L_M2, cx, vy, target_y, net=net)
                cv.via(P.L_V2, [P.L_M2, P.L_M3], cx, target_y, net=net)
                return
            # Metal4 escape: short M2 jog (staggered so neighbouring M3 landing pads keep their spacing), then
            # via2 + via3 up to Metal4, which climbs over the top-row stub's Metal2 column to the net's track
            sy = ch_bot - ESC_GAP + (500 if esc_rank[cx] % 2 == 0 else 1350)
            cv.vwire(P.L_M2, cx, vy, sy, net=net)
            cv.via(P.L_V2, [P.L_M2, P.L_M3], cx, sy, net=net, big=True)
            cv.via(P.L_V3, [P.L_M3, P.L_M4], cx, sy, net=net, big=True)
            cv.vwire(P.L_M4, cx, sy, target_y, w=M4_W, net=net)
            cv.via(P.L_V3, [P.L_M3, P.L_M4], cx, target_y, net=net)
            pads.append((net, target_y, cx))

        def tap_or_stub(b, y, net):
            """Band net: via1 + via2 straight onto the trunk where it crosses the strip; else a short stub."""
            cx = (b.left + b.right) // 2
            if b.height() > b.width() and b.bottom + 160 <= y <= b.top - 160:
                cv.via(P.L_V1, None, cx, y, net=net, vertical=True)
                cv.via(P.L_V2, [P.L_M2, P.L_M3], cx, y, net=net)
            else:
                stub(b, y, net)

        for pl in top_row:
            for term, net, b in channel_pins(pl):
                if net in band_nets:
                    tap_or_stub(b, track_y[net], net)
                    continue
                stub(b, track_y[net], net)
            for term, net, b in rail_pins(pl):
                stub(b, y_vdd, net_t)
        for pl in bot_row:
            for term, net, b in channel_pins(pl):
                if net in band_nets:
                    tap_or_stub(b, track_y[net], net)
                    continue
                stub(b, track_y[net], net, esc=((b.left + b.right) // 2) in escape)
            for term, net, b in rail_pins(pl):
                stub(b, y_vss, net_b)
        # trunks, ports, spine taps, supply ties
        for n, xs in all_nets.items():
            y = track_y[n]
            x0_, x1_ = min(xs), max(xs)
            if x1_ - x0_ < 700:                       # met3 minimum area (0.24 um2) for a one-pin trunk
                x0_, x1_ = x0_ - 350, x1_ + 350
            cv.hwire(P.L_M3, y, x0_, x1_, net=n)
            if n in port_side:
                for sd in ("L", "R") if port_side[n] == "B" else (port_side[n],):
                    xe = xmin if sd == "L" else xmax
                    cv.label(P.L_M3, n, xe + (300 if sd == "L" else -300), y)
                    pins_json.append(dict(net=n, layer="met3", x=xe / UM, y=y / UM, side=sd))
            if n in spine_nets:
                cv.via(P.L_V3, [P.L_M3, P.L_M4], xspine_tr[n], y, net=n)
            if n in ("vdd", "vss"):
                for dx in (-400, 400):
                    cv.via(P.L_V3, [P.L_M3, P.L_M4], (xmin + 1000 if n == "vdd" else xmax - 1000) + dx, y, net=n)
        for n in spine_nets:
            if n in nets:
                multi.setdefault(("y", n), []).append(track_y[n])
    # ---- tap strips: rails shared by two mirrored pairs carry one merged strip
    by_rail = {}
    for kind, x0, x1, y0, rail, ry, nw in strips:
        by_rail.setdefault((kind, y0, rail, ry), []).append((x0, x1, nw))
    for (kind, y0, rail, ry), segs in by_rail.items():
        segs.sort()
        merged = []
        for x0, x1, nw in segs:
            if merged and x0 <= merged[-1][1] + 600:
                merged[-1][1] = max(merged[-1][1], x1)
                merged[-1][2].append((x0, x1, nw))
            else:
                merged.append([x0, x1, [(x0, x1, nw)]])
        cut = []
        for x0, x1, parts in merged:                  # subtract the other-body n-well keep-outs
            pieces = [(x0, x1)]
            for f0, f1 in (forbid.get(ry, []) if kind == "p" else []):
                nxt = []
                for a, b in pieces:
                    if f1 <= a or f0 >= b:
                        nxt.append((a, b))
                        continue
                    if f0 - a > 1500:
                        nxt.append((a, f0))
                    if b - f1 > 1500:
                        nxt.append((f1, b))
                pieces = nxt
            for a, b in pieces:
                cut.append((a, b, [(max(pa, a), min(pb, b), nw) for pa, pb, nw in parts if pb > a and pa < b]))
        for x0, x1, parts in cut:
            tap_strip(cv, kind, x0, x1, y0, rail, ry)
            if kind == "p":                           # n-well bridges from the strip to each row it serves
                for a, b, nw in parts:
                    if nw is not None:
                        lo, hi = sorted((nw, y0 + STRIP_H // 2))
                        cv.box(P.L_NW, a - 340, lo, b + 340, hi)
    # ---- spine (Metal4 verticals joining the trunks of nets that live in several pairs)
    for n in spine_nets:
        ys = multi.get(("y", n), [])
        if len(ys) > 1:
            cv.vwire(P.L_M4, xspine_tr[n], min(ys), max(ys), w=TRUNK_W, net=n)
    # ---- power straps: Metal4 at the left (vdd) and right (vss) edges, via3 on every rail
    y_top = max(y for _, y in rails) + RAIL_H // 2
    y_bot = min(y for _, y in rails) - RAIL_H // 2
    xl, xr = xmin + 1000, xmax - 1000
    cv.vwire(P.L_M4, xl, y_bot, y_top, w=1600, net="vdd")
    cv.vwire(P.L_M4, xr, y_bot, y_top, w=1600, net="vss")
    for net, y in rails:
        xs = xl if net == "vdd" else xr
        for dx in (-400, 400):
            cv.via(P.L_V3, [P.L_M3, P.L_M4], xs + dx, y, net=net)
    cv.label(P.L_M4, "vdd", xl, (y_top + y_bot) // 2)
    cv.label(P.L_M4, "vss", xr, (y_top + y_bot) // 2)
    for net, y in rails:                              # rail ends on the block edges = supply access (Metal3, 2 um)
        pins_json.append(dict(net=net, layer="met3", x=xmin / UM, y=y / UM, side="L", width=RAIL_H / UM))
        pins_json.append(dict(net=net, layer="met3", x=xmax / UM, y=y / UM, side="R", width=RAIL_H / UM))
    pins_json.append(dict(net="vdd", layer="met4", x=xl / UM, y=(y_top + y_bot) / 2 / UM, side="L", width=1.6))
    pins_json.append(dict(net="vss", layer="met4", x=xr / UM, y=(y_top + y_bot) / 2 / UM, side="R", width=1.6))

    for layer, space in ((P.L_M1, 140), (P.L_M2, 140), (P.L_M3, 300), (P.L_M4, 300)):
        cv.fill_same_net_gaps(layer, space)
    m1pins = [(P.L_M1, b, n) for pl in insts for t, n, b in pl.pins() if t != "R"]
    shorts = cv.check_shorts(m1pins)
    for layer, n1, n2, a, b in shorts[:10]:
        print(f"  SHORT {block}: layer {layer} {n1} / {n2} at {a} / {b}")
    bb = pya.Box(xmin, y_bot, xmax, y_top)
    cv.box(P.L_HVI, bb.left, bb.bottom, bb.right, bb.top)     # every device is a 3.3/5 V (g5v0d10v5) device
    keep = set(top.called_cells()) | {top.cell_index()}
    for c in [c for c in ly.each_cell() if c.cell_index() not in keep]:
        ly.delete_cell(c.cell_index())
    back = {v: k for k, v in SUPPLY_ALIAS.get(block, {}).items()}
    if back:                                   # restore the schematic's supply names on labels and pins
        for li in ly.layer_indexes():
            for sh in top.shapes(li).each():
                if sh.is_text() and sh.text_string in back:
                    sh.text_string = back[sh.text_string]
        for pj in pins_json:
            pj["net"] = back.get(pj["net"], pj["net"])
        ports = [back.get(p, p) for p in ports]
    os.makedirs(OUT, exist_ok=True)
    gds = os.path.join(OUT, block + ".gds")
    ly.write(gds)
    info = dict(block=block, gds=os.path.relpath(gds, ROOT), width=bb.width() / UM, height=bb.height() / UM,
                origin=[bb.left / UM, bb.bottom / UM], pairs=len(pairs), spine=len(spine_nets), devices=len(insts),
                device_area_um2=round(area), shorts=len(shorts), pair_info=pair_info, ports=ports, pins=pins_json)
    json.dump(info, open(os.path.join(OUT, block + ".json"), "w"), indent=1)
    return info


LEAF_BLOCKS = ["rt5w_array", "rt5w_kscale", "rt5w_softmax", "rt5w_bias", "rt5w_readout", "rt5w_vbbuf"]
MAX_H = 200.0                  # um: a block must fit the 4x2 tile height (225.76 um) with routing margin


def generate_best(block):
    """Try row-pair widths from 60 to 700 um and keep the smallest outline that is at most MAX_H tall."""
    global REORDER
    best = None
    for tw in (30, 45, 60, 75, 90, 120, 140, 150, 160, 170, 180, 200, 250, 300, 380, 460, 560, 700):
        for ro in (True, False):
            REORDER = ro
            r = generate(block, target_w=tw * UM)
            key = (r["shorts"] > 0, r["height"] > MAX_H, r["width"] > BLOCK_MAXW.get(block, 1e9),
                   r["width"] * r["height"])
            if best is None or key < best[0]:
                best = (key, tw, ro)
    REORDER = best[2]
    r = generate(block, target_w=best[1] * UM)
    r["reorder"] = best[2]
    return r


if __name__ == "__main__":
    for b in sys.argv[1:] or LEAF_BLOCKS:
        r = generate_best(b)
        print(f"{b}: {r['devices']} pcells in {r['pairs']} row pair(s), spine {r['spine']} nets, "
              f"{r['width']:.1f} x {r['height']:.1f} um (device area {r['device_area_um2']} um2) -> {r['gds']}")
