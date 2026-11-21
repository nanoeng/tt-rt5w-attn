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
LANE_PITCH, LANE_W = 900, 300
TRACK_PITCH, TRACK_W = 680, 300
EDGE_GAP = 1000                    # block bbox to the first lane
PWR_W = 900                        # supply stub / rail-pin width


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
        pins = {i.name: i.pins() for i in self.insts}
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
            if len(set(used.values())) > 1 or n in self.ports:
                self.bus_nets.add(n)
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
                self.pwr.setdefault((ch, cs, n), []).append((i.name, side, y))
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
                iv[n] = (lo, top + 10 ** 6) if n in self.bus_nets else (lo, hi)
            la = left_edge(iv, 1500)
            self.lane_of[ch] = la
            nlanes[ch] = 1 + max(la.values(), default=-1)
        # channel widths: [l-vdd l-vss] signal lanes [r-vss r-vdd]
        self.chx = {}
        x = 0
        for ch in range(self.ncol + 1):
            npw_l = sum(1 for n in ("vdd", "vss") if (ch, "l", n) in self.pwr)
            npw_r = sum(1 for n in ("vdd", "vss") if (ch, "r", n) in self.pwr)
            width = 2 * EDGE_GAP + (npw_l + nlanes[ch] + npw_r) * LANE_PITCH
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
            return x0 + EDGE_GAP + LANE_PITCH // 2 + k * LANE_PITCH

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
        self.outline = pya.Box(0, y_vss - PWR_W, self.width, y_vdd + PWR_W)
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
            return b.left if side == "L" else b.right

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
            hw(y, xl - 10, xr + 10, n, w=max(w, TRACK_W))
        # signal stubs and lanes
        for ch, stubs in self.stubs.items():
            npl = self.chx[ch][2]
            for n, a, side, y, w in stubs:
                lx = lane_x(ch, npl + self.lane_of[ch][n])
                hw(y, edge_x(ix[a], side), lx, n)
                v3(lx, y, n)
            for n, (lo, hi) in self.chan_nets[ch].items():
                lx = lane_x(ch, npl + self.lane_of[ch][n])
                yt = bus_y[n] if n in self.bus_nets else hi
                vw(lx, lo, yt, n)
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
            ys = [y for _, _, y in lst]
            for a, side, y in lst:
                hw(y, edge_x(ix[a], side), lx, n, w=PWR_W)
                v3(lx, y, n)
            if n == "vdd":
                vw(lx, min(ys), y_vdd, n, w=600)
                v3(lx, y_vdd, n)
            else:
                vw(lx, max(ys), y_vss, n, w=600)
                v3(lx, y_vss, n)

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
            lab = P.LABEL[P.L_M3]
            x = int(p["x"] * UM) + (400 if p["side"] == "L" else -400)
            top.shapes(ly.layer(*lab)).insert(pya.Text(p["net"], pya.Trans(x, int(p["y"] * UM))))
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
        d.y = ytop
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


if __name__ == "__main__":
    a = array_assembly()
    a.build()
    out, shorts = a.write()
    print(f"{out}: {a.outline.width() / UM:.1f} x {a.outline.height() / UM:.1f} um, "
          f"{len(a.bus_nets)} bus nets, {len(a.straight)} straight joins, shorts {len(shorts)}")
    for s in shorts[:10]:
        print("  SHORT", s)
