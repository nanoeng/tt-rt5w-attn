"""Tiled assembly + channel routing of leaf-block layouts (sky130A).

Used for the 4x4 key array (rt5w_array) and reusable for the top level. Model:

  * blocks stand in COLUMNS (stacks); between and beside the columns run vertical CHANNELS; above all columns
    runs the horizontal BUS; a vdd rail above the bus and a vss rail below the columns close the outline.
  * every leaf pin is a met3 trunk end on the block's left or right bbox edge (blockgen.py), so a pin faces one
    channel.  Pins of one net on facing edges at the same y (feed-throughs of abutting tiles, aligned rails) are
    joined by a straight met3 piece across the channel.
  * remaining pins: met3 stub from the pin into the channel, via3 onto a met4 LANE (vertical); lanes are packed
    by left-edge on their y-extent.  Nets that live in several channels, and ports of the assembly, run their
    lanes up into the bus, where a met3 bus track (left-edge on x) joins them; port tracks run on to the left edge.
  * supplies: per channel side a vdd lane (up to the top rail) and a vss lane (down to the bottom rail), fed by
    0.9 um met3 stubs from the rail ends of the blocks on that side.

Layers: met3 horizontal, met4 vertical (met4 lanes 0.3 um on a 0.9 um pitch; via3 pads 0.39 x 0.33 / 0.5 um).
"""
import json
import os
import re
import sys

import klayout.db as pya

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pdkcells as P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
GDS = os.path.join(ROOT, "layout", "gds")
NETLIST = os.path.join(ROOT, "netlist")
UM = 1000
LANE_PITCH, LANE_W = 920, 300         # 2 x the 0.46 um met4 track pitch: lanes snap to the top-level tracks
TOP_PIN_EXT = 1200                     # top-edge pins extend this far above the top vdd rail (met3-free)
TRACK4 = 460                           # met4 track grid (array-local x = 230 + 460 k; array placed at x = 0 mod 0.46)
TRACK_PITCH, TRACK_W = 680, 300
EDGE_GAP = 1000                    # block bbox to the first lane
PWR_W = 900                        # supply stub / rail-pin width
EDGE_IN = 400                      # stubs start this far inside the block bbox (trunks stop 0.3 um short of it)


def subckt_instances(block):
    """Instances of a hierarchical subckt: [(name, subckt, {pin: net})], ports of the block."""
    txt = open(os.path.join(NETLIST, block + ".spice")).read().replace("\n+", " ")
    subs = {}
    for m in re.finditer(r"^\.subckt (\S+) (.*?)$(.*?)^\.ends", txt, re.M | re.S):
        subs[m.group(1)] = ([w for w in m.group(2).split() if "=" not in w], m.group(3))
    ports, body = subs[block]
    insts = []
    for line in body.splitlines():
        t = line.split()
        if not t or not t[0].lower().startswith("x"):
            continue
        sub = t[-1] if "=" not in t[-1] else next(w for w in reversed(t) if "=" not in w)
        nets = t[1:t.index(sub)]
        insts.append((t[0], sub, dict(zip(subs[sub][0], nets))))
    return insts, ports


class Block:
    def __init__(self, name):
        self.name = name
        j = json.load(open(os.path.join(GDS, name + ".json")))
        ly = pya.Layout()
        ly.read(os.path.join(GDS, name + ".gds"))
        self.bbox = ly.top_cell().bbox()                     # nm, block frame
        self.pins = [p for p in j["pins"] if p["layer"] == "met3"]
        self.w, self.h = self.bbox.width(), self.bbox.height()


class Inst:
    def __init__(self, name, block, col, conn):
        self.name, self.block, self.col, self.conn = name, block, col, conn
        self.orient = "N"
        self.x = self.y = 0                                  # lower-left of the placed bbox (nm)

    def trans(self):
        b = self.block.bbox
        if self.orient == "N":
            return pya.Trans(pya.Trans.R0, self.x - b.left, self.y - b.bottom)
        return pya.Trans(pya.Trans.M0, self.x - b.left, self.y + b.top)          # FS: mirror about x

    def box(self):
        return pya.Box(self.x, self.y, self.x + self.block.w, self.y + self.block.h)

    def pins(self):
        """(net, side, x, y, width) of every met3 pin, absolute; net = the net it connects to here."""
        t = self.trans()
        out = []
        for p in self.block.pins:
            if p["net"] not in self.conn:
                continue
            pt = t * pya.Point(int(round(p["x"] * UM)), int(round(p["y"] * UM)))
            out.append((self.conn[p["net"]], p["side"], pt.x, pt.y, int(round(p.get("width", 0.3) * UM))))
        return out


def left_edge(intervals, gap):
    """intervals: {key: (lo, hi)} -> {key: track}, smallest number of tracks (interval graph colouring)."""
    ends, out = [], {}
    for k, (lo, hi) in sorted(intervals.items(), key=lambda kv: kv[1][0]):
        for t, e in enumerate(ends):
            if e + gap <= lo:
                ends[t] = hi
                out[k] = t
                break
        else:
            out[k] = len(ends)
            ends.append(hi)
    return out


class Assembly:
    def __init__(self, name, columns, ports, col_gap_min=0):
        """columns: list of lists of Inst (top to bottom, already oriented and given y); ports: external nets."""
        self.name, self.columns, self.ports = name, columns, [p for p in ports if p not in ("vdd", "vss")]
        self.insts = [i for c in columns for i in c]
        self.shapes = []                                     # (layer, box, net)
        self.pins_out = []

    # ------------------------------------------------------------------ routing plan (independent of x)
    def plan(self):
        ncol = len(self.columns)
        pins = {}
        for col in self.columns:
            cw = max(i.block.w for i in col)
            for i in col:
                ps = i.pins()
                if i.block.w < cw - 10:                      # narrower tile: the inner edge faces a channel only where the
                    inner = "L" if getattr(i, "align_right", False) else "R"   # ray to the column edge is free
                    others = [o for o in col if o is not i and o.block.w < cw - 10 and
                              getattr(o, "align_right", False) != getattr(i, "align_right", False)]
                    ps = [p for p in ps if p[1] != inner or
                          not any(o.y - 1200 <= p[3] <= o.y + o.block.h + 1200 for o in others)]
                pins[i.name] = ps
        self.straight = []                                   # (channel, net, y, width)
        nets = {}
        for i in self.insts:
            for n, side, x, y, w in pins[i.name]:
                nets.setdefault(n, {}).setdefault(i.name, []).append((side, y, w))
        self.nets = nets
        parent = {}

        def find(a):
            while parent.get(a, a) != a:
                a = parent[a]
            return a

        # straight joins across a channel: R pin of column c and L pin of column c+1 at the same y
        for n, terms in nets.items():
            for a, pa in terms.items():
                ia = next(i for i in self.insts if i.name == a)
                for b, pb in terms.items():
                    ib = next(i for i in self.insts if i.name == b)
                    if ib.col != ia.col + 1:
                        continue
                    for sa, ya, wa in pa:
                        for sb, yb, wb in pb:
                            if sa == "R" and sb == "L" and abs(ya - yb) < 5:
                                self.straight.append((ia.col + 1, n, ya, max(wa, wb)))
                                parent[find((n, a))] = find((n, b))
        # stubs and lanes for what is left
        self.stubs = {}                                      # channel -> [(net, inst, side, y, w)]
        self.chan_nets = {}                                  # channel -> {net: (ylo, yhi)}
        self.bus_nets = set()
        self.top_nets = set()
        for n, terms in nets.items():
            if n in ("vdd", "vss"):
                continue
            comps = {}
            for a in terms:
                comps.setdefault(find((n, a)), []).append(a)
            if len(comps) == 1 and n not in self.ports:
                continue
            cand = {}
            for root, members in comps.items():
                for a in members:
                    ia = next(i for i in self.insts if i.name == a)
                    for side, y, w in terms[a]:
                        ch = ia.col if side == "L" else ia.col + 1
                        cand.setdefault(ch, set()).add(root)
            used = {}
            for root in comps:
                chs = [ch for ch, rs in cand.items() if root in rs]
                ch = max(chs, key=lambda c: (len(cand[c]), n in self.ports and c == 0, -c))
                used[root] = ch
            for root, ch in used.items():
                # one pin of this component facing channel ch
                for a in comps[root]:
                    ia = next(i for i in self.insts if i.name == a)
                    pick = [(side, y, w) for side, y, w in terms[a]
                            if (side == "L" and ia.col == ch) or (side == "R" and ia.col + 1 == ch)]
                    if pick:
                        side, y, w = pick[0]
                        self.stubs.setdefault(ch, []).append((n, a, side, y, w))
                        lo, hi = self.chan_nets.setdefault(ch, {}).get(n, (y, y))
                        self.chan_nets[ch][n] = (min(lo, y), max(hi, y))
                        break
            if len(set(used.values())) > 1:
                self.bus_nets.add(n)
            elif n in self.ports:
                self.top_nets.add(n)                         # one lane, straight up to a met4 pin on the top edge
        # supply stubs: every rail pin not joined straight goes to its side's supply lane
        straight_keys = {(ch, n, y) for ch, n, y, w in self.straight}
        self.pwr = {}                                        # (channel, side_of_channel 'l'|'r', net) -> [y]
        for i in self.insts:
            for n, side, x, y, w in pins[i.name]:
                if n not in ("vdd", "vss"):
                    continue
                ch = i.col if side == "L" else i.col + 1
                if (ch, n, y) in straight_keys:
                    continue
                cs = "r" if side == "L" else "l"              # the block sits on the channel's right / left
                self.pwr.setdefault((ch, cs, n), []).append((i.name, side, y, w))
        self.ncol = ncol

    # ------------------------------------------------------------------ geometry
    def build(self):
        self.plan()
        top = max(i.box().top for i in self.insts)
        bot = min(i.box().bottom for i in self.insts)
        # bus tracks (x unknown yet: left-edge after x placement); lanes per channel
        self.lane_of = {}
        nlanes = {}
        for ch in range(self.ncol + 1):
            iv = {}
            for n, (lo, hi) in self.chan_nets.get(ch, {}).items():
                iv[n] = (lo, top + 10 ** 6) if (n in self.bus_nets or n in self.top_nets) else (lo, hi)
            # lanes ordered so stubs from opposite sides cannot overlap: nets reached only from the channel's left
            # blocks (their R pins) take the left lanes, nets reached only from the right blocks the right lanes,
            # nets with stubs on both sides the middle
            sides = {}
            for n, a, side, y, w in self.stubs.get(ch, []):
                sides.setdefault(n, set()).add(side)
            groups = [[n for n in iv if sides.get(n, {"R"}) == {"R"}],
                      [n for n in iv if len(sides.get(n, ())) == 2],
                      [n for n in iv if sides.get(n) == {"L"}]]
            # two-sided nets: a left stub at y must end left of any right stub near y -> precedence order, own lanes
            mixed = groups[1]
            st = [(n, side, y) for n, a, side, y, w in self.stubs.get(ch, []) if n in mixed]
            after = {n: set() for n in mixed}
            for n1, s1, y1 in st:
                for n2, s2, y2 in st:
                    if n1 != n2 and s1 == "R" and s2 == "L" and abs(y1 - y2) < 1500:
                        after[n1].add(n2)            # n1 (stub from the left) before n2 (stub from the right)
            order, seen = [], set()

            def visit(n, stack=()):
                if n in seen or n in stack:
                    return
                for m in sorted(after[n]):
                    visit(m, stack + (n,))
                seen.add(n)
                order.append(n)
            for n in sorted(mixed):
                visit(n)
            order.reverse()
            la, base = {}, 0
            for gi, g in enumerate(groups):
                if gi == 1:
                    la.update({n: base + k for k, n in enumerate(order)})
                    base += len(order)
                    continue
                lg = left_edge({n: iv[n] for n in g}, 1500)
                la.update({n: base + k for n, k in lg.items()})
                base += 1 + max(lg.values(), default=-1)
            self.lane_of[ch] = la
            nlanes[ch] = 1 + max(la.values(), default=-1)
        # channel widths: [l-vdd l-vss] signal lanes [r-vss r-vdd]
        self.chx = {}
        x = 0
        for ch in range(self.ncol + 1):
            npw_l = sum(1 for n in ("vdd", "vss") if (ch, "l", n) in self.pwr)
            npw_r = sum(1 for n in ("vdd", "vss") if (ch, "r", n) in self.pwr)
            width = 2 * EDGE_GAP + (npw_l + nlanes[ch] + npw_r) * LANE_PITCH + TRACK4     # + snap room
            self.chx[ch] = (x, x + width, npw_l, npw_r)
            x += width
            if ch < self.ncol:
                cw = max(i.block.w for i in self.columns[ch])
                for i in self.columns[ch]:
                    i.x = x if not getattr(i, "align_right", False) else x + cw - i.block.w
                    i.x += getattr(i, "dx", 0)
                x += cw
        self.width = x
        # lane x
        def lane_x(ch, k):
            x0, x1, npl, npr = self.chx[ch]
            first = x0 + EDGE_GAP + LANE_PITCH // 2
            first = 230 + -(-(first - 230) // TRACK4) * TRACK4            # snap up onto the met4 track grid
            return first + k * LANE_PITCH

        self.lane_x = lane_x
        # bus: tracks over the columns
        bus_iv = {}
        for n in self.bus_nets:
            xs = [lane_x(ch, self.chx[ch][2] + self.lane_of[ch][n]) for ch in self.lane_of if n in self.lane_of[ch]]
            lo = 0 if n in self.ports else min(xs)
            bus_iv[n] = (lo, max(xs))
        btrack = left_edge(bus_iv, 1500)
        nb = 1 + max(btrack.values(), default=-1)
        y_bus0 = top + 1500
        bus_y = {n: y_bus0 + TRACK_PITCH // 2 + t * TRACK_PITCH for n, t in btrack.items()}
        y_vdd = y_bus0 + nb * TRACK_PITCH + 1500 + PWR_W
        y_vss = bot - 1500 - PWR_W
        y_rail = y_vdd + PWR_W
        y_top = y_rail + (TOP_PIN_EXT if self.top_nets else 0)   # top pins stand out above the vdd rail: via
        self.outline = pya.Box(0, y_vss - PWR_W, self.width, y_top)   # access to met3 for the top-level router
        S = self.shapes
        # rails
        S.append((P.L_M3, pya.Box(0, y_vdd - PWR_W, self.width, y_vdd + PWR_W), "vdd"))
        S.append((P.L_M3, pya.Box(0, y_vss - PWR_W, self.width, y_vss + PWR_W), "vss"))
        self.pins_out += [dict(net="vdd", layer="met3", x=0, y=y_vdd / UM, side="L", width=2 * PWR_W / UM),
                          dict(net="vss", layer="met3", x=0, y=y_vss / UM, side="L", width=2 * PWR_W / UM),
                          dict(net="vdd", layer="met3", x=self.width / UM, y=y_vdd / UM, side="R", width=2 * PWR_W / UM),
                          dict(net="vss", layer="met3", x=self.width / UM, y=y_vss / UM, side="R", width=2 * PWR_W / UM)]
        ix = {i.name: i for i in self.insts}

        def edge_x(inst, side):
            b = inst.box()
            return b.left + EDGE_IN if side == "L" else b.right - EDGE_IN      # overlap the trunk end inside the block

        def hw(y, x0, x1, net, w=TRACK_W, layer=P.L_M3):
            S.append((layer, pya.Box(min(x0, x1), y - w // 2, max(x0, x1), y + w // 2), net))

        def vw(x, y0, y1, net, w=LANE_W):
            S.append((P.L_M4, pya.Box(x - w // 2, min(y0, y1), x + w // 2, max(y0, y1)), net))

        def v3(x, y, net):
            S.append((P.L_V3, pya.Box(x - 100, y - 100, x + 100, y + 100), net))
            S.append((P.L_M3, pya.Box(x - 195, y - 165, x + 195, y + 165), net))
            S.append((P.L_M4, pya.Box(x - 250, y - 250, x + 250, y + 250), net))

        # straight joins
        for ch, n, y, w in self.straight:
            x0, x1 = self.chx[ch][0], self.chx[ch][1]
            # from the left column's right edge to the right column's left edge
            xl = max((i.box().right for i in self.insts if i.col == ch - 1), default=x0)
            xr = min((i.box().left for i in self.insts if i.col == ch), default=x1)
            hw(y, xl - EDGE_IN, xr + EDGE_IN, n, w=max(w, TRACK_W))
        # signal stubs and lanes
        for ch, stubs in self.stubs.items():
            npl = self.chx[ch][2]
            for n, a, side, y, w in stubs:
                lx = lane_x(ch, npl + self.lane_of[ch][n])
                hw(y, edge_x(ix[a], side), lx, n)
                v3(lx, y, n)
            for n, (lo, hi) in self.chan_nets[ch].items():
                lx = lane_x(ch, npl + self.lane_of[ch][n])
                yt = bus_y[n] if n in self.bus_nets else (y_top if n in self.top_nets else hi)
                vw(lx, lo, yt, n)
                if n in self.top_nets:
                    self.pins_out.append(dict(net=n, layer="met4", x=lx / UM, y=y_top / UM, side="T"))
                    # second access option for the top-level router: via3 + isolated met3 landing pad (0.25 um2,
                    # >= met3 min area) at the lane top, above the vdd rail (0.55 um clear of it)
                    yp = y_top - 400
                    S.append((P.L_V3, pya.Box(lx - 100, yp - 100, lx + 100, yp + 100), n))
                    S.append((P.L_M3, pya.Box(lx - 250, yp - 250, lx + 250, yp + 250), n))
                    S.append((P.L_M4, pya.Box(lx - 165, yp - 250, lx + 165, yp + 250), n))
                if n in self.bus_nets:
                    v3(lx, yt, n)
        # bus tracks + ports
        for n, (lo, hi) in bus_iv.items():
            hw(bus_y[n], lo, hi + 250, n)
            if n in self.ports:
                self.pins_out.append(dict(net=n, layer="met3", x=0, y=bus_y[n] / UM, side="L"))
        # supply lanes
        for (ch, cs, n), lst in self.pwr.items():
            x0, x1, npl, npr = self.chx[ch]
            order = ["vdd", "vss"]
            if cs == "l":
                k = [m for m in order if (ch, "l", m) in self.pwr].index(n)
                lx = x0 + EDGE_GAP + LANE_PITCH // 2 + k * LANE_PITCH
            else:
                k = [m for m in reversed(order) if (ch, "r", m) in self.pwr].index(n)
                lx = x1 - EDGE_GAP - LANE_PITCH // 2 - k * LANE_PITCH
            ys = [y for _, _, y, _ in lst]
            for a, side, y, w in lst:
                hw(y, edge_x(ix[a], side), lx, n, w=min(PWR_W, max(w, TRACK_W)))
                v3(lx, y, n)
            if n == "vdd":
                vw(lx, min(ys), y_vdd, n, w=600)
                v3(lx, y_vdd, n)
            else:
                vw(lx, max(ys), y_vss, n, w=600)
                v3(lx, y_vss, n)

    def _bridge_nwell(self, ly, top, band=2500, close=1000):
        """Merge nwells of vertically adjacent tiles that face each other closer than nwell.8 (2 um, HV) allows:
        morphological closing restricted to a band around each seam; the filler also gets HVI."""
        nw, hvi = ly.layer(*P.L_NW), ly.layer(*P.L_HVI)
        allnw = pya.Region(top.begin_shapes_rec(nw)).merged()
        fill = pya.Region()
        for col in self.columns:
            boxes = sorted((i.box() for i in col), key=lambda b: -b.top)
            for a in boxes:
                for b in boxes:
                    if b is a or b.top < a.bottom - 100 or b.top > a.bottom + band:
                        continue
                    xs = max(a.left, b.left), min(a.right, b.right)
                    if xs[1] <= xs[0]:
                        continue
                    seam = pya.Region(pya.Box(xs[0], min(a.bottom, b.top) - band, xs[1], max(a.bottom, b.top) + band))
                    loc = allnw & seam
                    closed = loc.sized(close).sized(-close) & seam
                    fill += closed - loc
        fill.merge()
        top.shapes(nw).insert(fill)
        top.shapes(hvi).insert(fill)
        self.nwell_fill = fill.area() / 1e6

    def write(self, out=None):
        ly = pya.Layout()
        ly.dbu = 0.001
        opt = pya.LoadLayoutOptions()
        opt.cell_conflict_resolution = pya.LoadLayoutOptions.CellConflictResolution.RenameCell
        cells = {}
        for i in self.insts:
            if i.block.name not in cells:
                ly.read(os.path.join(GDS, i.block.name + ".gds"), opt)
                cells[i.block.name] = ly.cell(i.block.name).cell_index()
        top = ly.create_cell(self.name)
        for i in self.insts:
            top.insert(pya.CellInstArray(cells[i.block.name], i.trans()))
        for layer, b, n in self.shapes:
            top.shapes(ly.layer(*layer)).insert(b)
        for p in self.pins_out:
            if p["side"] == "T":
                top.shapes(ly.layer(*P.LABEL[P.L_M4])).insert(
                    pya.Text(p["net"], pya.Trans(int(p["x"] * UM), int(p["y"] * UM) - 400)))
                continue
            lab = P.LABEL[P.L_M3]
            x = int(p["x"] * UM) + (400 if p["side"] == "L" else -400)
            top.shapes(ly.layer(*lab)).insert(pya.Text(p["net"], pya.Trans(x, int(p["y"] * UM))))
        self._bridge_nwell(ly, top)
        for c in list(ly.top_cells()):
            if c.name != self.name:
                c.delete()
        out = out or os.path.join(GDS, self.name + ".gds")
        ly.write(out)
        # short check: overlapping met3 / met4 shapes of different nets
        shorts = []
        for layer in (P.L_M3, P.L_M4):
            items = sorted([(b, n) for l, b, n in self.shapes if l == layer], key=lambda t: t[0].left)
            for k, (a, na) in enumerate(items):
                for b, nb in items[k + 1:]:
                    if b.left > a.right:
                        break
                    if na != nb and a.overlaps(b):
                        shorts.append((layer, na, nb, a, b))
        bb = self.outline
        json.dump(dict(block=self.name, width=bb.width() / UM, height=bb.height() / UM, pins=[
            dict(p, x=p["x"] - bb.left / UM, y=p["y"] - bb.top / UM) for p in self.pins_out],
            shorts=len(shorts)), open(out.replace(".gds", ".json"), "w"), indent=1)
        return out, shorts


# ---------------------------------------------------------------------------------------------- the 4x4 array
def array_assembly():
    insts, ports = subckt_instances("rt5w_array")
    B = {}

    def blk(name):
        if name not in B:
            B[name] = Block(name)
        return B[name]

    by = {n: (s, c) for n, s, c in insts}
    cols = []
    for i in range(4):
        col = []
        q = Inst(f"xq{i}", blk("rt5w_idac4"), i, by[f"xq{i}"][1])
        d = Inst(f"xd{i}", blk("rt5w_coldiode"), i, by[f"xd{i}"][1])
        cells = []
        for j in range(4):
            c = Inst(f"xc{j}{i}", blk("rt5w_keycell"), i, by[f"xc{j}{i}"][1])
            c.orient = "N" if j % 2 == 0 else "FS"
            cells.append(c)
        # key cells stacked with shared rails (pitch = height - rail width); IDAC + column diode on top
        h = cells[0].block.h
        y = 0
        for c in cells:
            c.y = y - h
            y = y - h + int(0.9 * UM)
        ytop = cells[0].y + h + 2000
        q.y = ytop
        d.y = ytop + 16000                 # between the IDAC's low q/dcol pins (9.7-13.1 um) and its nd pin (40.3 um)
        d.align_right = True
        col += [q, d] + cells
        cols.append(col)
    # column 4: trims and pump inverters
    col = []
    y = cols[0][0].y + cols[0][0].block.h
    for name in ("xt0", "xpi1", "xt1", "xpi2", "xt2", "xpi3", "xt3"):
        b = blk("rt5w_trimcell" if name.startswith("xt") else "rt5w_pumpinv")
        it = Inst(name, b, 4, by[name][1])
        y -= b.h
        it.y = y
        y -= 1500
        col.append(it)
    cols.append(col)
    # the column diode sits beside the IDAC (right-aligned in the column): give the IDAC its own x
    return Assembly("rt5w_array", cols, ports)


def array_assembly_flat():
    """6x2 floorplan (20 Nov): the array about 100 um tall instead of 161 um, so the shifter bank and the digital
    macro can sit above it. Columns: trims | pump inverters + column diodes | key cells dim 0..3 | IDAC 0,1 | IDAC 2,3.
    dcol_i (key-cell column i, IDAC i, column diode i) goes on the top bus."""
    insts, ports = subckt_instances("rt5w_array")
    B = {}

    def blk(name):
        if name not in B:
            B[name] = Block(name)
        return B[name]

    by = {n: (s, c) for n, s, c in insts}
    GAP = 1500

    def stack(names, col, block_of, orient=None):
        out, y = [], 0
        for k, name in enumerate(names):
            it = Inst(name, blk(block_of(name)), col, by[name][1])
            if orient:
                it.orient = orient(k)
            y -= it.block.h
            it.y = y
            y -= GAP
            out.append(it)
        return out

    cols = [stack(["xt0", "xt1", "xt2", "xt3"], 0, lambda n: "rt5w_trimcell"),
            stack(["xpi1", "xpi2", "xpi3", "xd0", "xd1", "xd2", "xd3"], 1,
                  lambda n: "rt5w_pumpinv" if n.startswith("xpi") else "rt5w_coldiode")]
    for i in range(4):                       # key cells: shared rails (pitch = height - rail width), N / FS
        cells = []
        y = 0
        for j in range(4):
            c = Inst(f"xc{j}{i}", blk("rt5w_keycell"), 2 + i, by[f"xc{j}{i}"][1])
            c.orient = "N" if j % 2 == 0 else "FS"
            h = c.block.h
            c.y = y - h
            y = y - h + int(0.9 * UM)
            cells.append(c)
        cols.append(cells)
    cols.append(stack(["xq0", "xq1"], 6, lambda n: "rt5w_idac4"))
    cols.append(stack(["xq2", "xq3"], 7, lambda n: "rt5w_idac4"))
    return Assembly("rt5w_array", cols, ports)


if __name__ == "__main__":
    a = array_assembly_flat() if "--v1" not in sys.argv else array_assembly()
    a.build()
    out, shorts = a.write()
    print(f"{out}: {a.outline.width() / UM:.1f} x {a.outline.height() / UM:.1f} um, "
          f"{len(a.bus_nets)} bus nets, {len(a.top_nets)} top pins, {len(a.straight)} straight joins, shorts {len(shorts)}")
    for s in shorts[:10]:
        print("  SHORT", s)
