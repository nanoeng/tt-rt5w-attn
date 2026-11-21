"""Top-level assembly and routing of the analog macro from a floorplan exported by the floorplanner.

    USER=$USER pixi run -e layout python design/layout/toplevel.py layout/floorplan/floorplan.json
        -> layout/gds/rt5w_analog.gds (+ .route.json report)

1. Every leaf block GDS (blockgen.py) is placed at its floorplan position / orientation (N, FN, S, FS).
2. Nets come from the flattened xschem hierarchy (hier.py): block pins (Metal3 trunk ends on the block's left/right
   edge; supply rail ends) + the TT analog pins ua[0..7] (Metal4, tile bottom edge) + the VDPWR / VGND stripes this
   script draws (Metal4, full height, left edge of the tile).
3. Routing is a grid maze router (A*, 1 um pitch) on Metal3 (horizontal preferred) and Metal4 (vertical preferred),
   via3 where it changes layer; block outlines + 1 um keep-out are obstacles on both layers (the blocks use Metal1-4
   inside), Metal5 is never used (TT rule). Multi-pin nets grow a tree: each further pin is joined to the nearest
   point of the tree. Nets are routed shortest-first; each net reserves its cells and the 4-neighbourhood of every
   via, so different nets are always >= 1 grid apart (0.6 um space between 0.4 um wires).
"""
import heapq
import json
import os
import sys

import numpy as np
import klayout.db as pya

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hier  # noqa: E402
import pdkcells as P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
GDS = os.path.join(ROOT, "layout", "gds")
FP = os.path.join(ROOT, "layout", "floorplan")
UM = 1000
G = 1.0                          # routing grid pitch (um)
W_WIRE = 400                     # nm
KEEPOUT = 1.0                    # um around blocks
STRIPE_W = 2.4                   # power stripes (um)
COST_PREF, COST_NONPREF, COST_VIA = 1.0, 4.0, 6.0


def orient_trans(o, x, y, w, h):
    """KLayout transformation that places a block (outline origin at 0,0, size w x h) with its lower-left at x, y."""
    xn, yn, wn, hn = (int(round(v * UM)) for v in (x, y, w, h))
    return {"N": pya.Trans(pya.Trans.R0, xn, yn), "FN": pya.Trans(pya.Trans.M90, xn + wn, yn),
            "S": pya.Trans(pya.Trans.R180, xn + wn, yn + hn), "FS": pya.Trans(pya.Trans.M0, xn, yn + hn)}[o]


def pin_abs(pin, pl, b):
    x, y = pin["x"], pin["y"]
    side = pin["side"]
    if pl["orient"] in ("FN", "S"):
        x, side = b["w"] - x, {"L": "R", "R": "L"}[side]
    if pl["orient"] in ("S", "FS"):
        y = b["h"] - y
    return pl["x"] + x, pl["y"] + y, side


class Grid:
    def __init__(self, w, h):
        self.nx, self.ny = int(w / G) + 1, int(h / G) + 1
        self.block = np.zeros((2, self.nx, self.ny), bool)     # hard obstacles per layer (0 = M3, 1 = M4)
        self.owner = np.full((2, self.nx, self.ny), -1, np.int32)

    def idx(self, x, y):
        return int(round(x / G)), int(round(y / G))

    def free(self, l, i, j, net):
        if not (0 <= i < self.nx and 0 <= j < self.ny) or self.block[l, i, j]:
            return False
        o = self.owner[l, i, j]
        return o == -1 or o == net


def astar(grid, net, sources, targets, max_expand=2_000_000):
    """sources/targets: sets of (l, i, j). Returns the node path or None."""
    xs = [t[1] for t in targets]
    ys = [t[2] for t in targets]
    bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)

    def h(i, j):                                   # distance to the targets' bounding box (admissible, O(1))
        return (max(bx0 - i, 0, i - bx1) + max(by0 - j, 0, j - by1)) * COST_PREF
    openq, g, came = [], {}, {}
    for s in sources:
        g[s] = 0.0
        heapq.heappush(openq, (h(s[1], s[2]), 0.0, s))
    n = 0
    while openq:
        f, gc, cur = heapq.heappop(openq)
        if cur in targets:
            path = [cur]
            while cur in came:
                cur = came[cur]
                path.append(cur)
            return path[::-1]
        if gc > g.get(cur, 1e18):
            continue
        n += 1
        if n > max_expand:
            return None
        l, i, j = cur
        moves = [((l, i + 1, j), COST_PREF if l == 0 else COST_NONPREF), ((l, i - 1, j), COST_PREF if l == 0 else COST_NONPREF),
                 ((l, i, j + 1), COST_PREF if l == 1 else COST_NONPREF), ((l, i, j - 1), COST_PREF if l == 1 else COST_NONPREF),
                 ((1 - l, i, j), COST_VIA)]
        for nxt, c in moves:
            if not grid.free(nxt[0], nxt[1], nxt[2], net):
                continue
            if nxt[0] != l and not (grid.free(0, i, j, net) and grid.free(1, i, j, net)):
                continue
            ng = gc + c
            if ng < g.get(nxt, 1e18):
                g[nxt] = ng
                came[nxt] = cur
                heapq.heappush(openq, (ng + h(nxt[1], nxt[2]), ng, nxt))
    return None


def route_all(grid, terms, order, net_ids, max_expand=600_000):
    import time
    t0 = time.time()
    shapes = []
    for net, tl in terms.items():                     # every access node belongs to its net from the start
        for nodes, _ in tl:
            for l, i, j in nodes:
                if 0 <= i < grid.nx and 0 <= j < grid.ny and grid.owner[l, i, j] in (-1, -2):
                    grid.owner[l, i, j] = net_ids[net]
    routed, failed = [], []
    for net in order:
        nid = net_ids[net]
        pend = sorted(terms[net], key=lambda t: min(n[1] for n in t[0]))
        tree = set(pend[0][0])
        ok = True
        for nodes, _ in pend[1:]:
            path = astar(grid, nid, nodes, tree, max_expand=max_expand)
            if path is None:
                ok = False
                break
            for nd in path:
                tree.add(nd)
                grid.owner[nd] = nid
            for a, c in zip(path, path[1:]):
                if a[0] != c[0]:                      # via: keep other nets off the 4 neighbours on both layers
                    for l in (0, 1):
                        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            ii, jj = a[1] + di, a[2] + dj
                            if 0 <= ii < grid.nx and 0 <= jj < grid.ny and grid.owner[l, ii, jj] == -1:
                                grid.owner[l, ii, jj] = nid
            terms_geom_path(path, shapes)
        (routed if ok else failed).append(net)
        for nodes, geom in terms[net]:
            shapes.extend(geom)
        if os.environ.get("ROUTE_VERBOSE"):
            print(f"  {net:14s} {len(terms[net]):3d} pins  {'ok' if ok else 'FAILED'}  t={time.time() - t0:6.1f}s", flush=True)
    return dict(routed=routed, failed=failed, shapes=shapes)


def build(fp_path, out=None):
    data = json.load(open(os.path.join(FP, "fp_data.json")))
    fp = json.load(open(fp_path))
    tile = fp["tile"]
    blocks, insts = data["blocks"], {i["path"]: i for i in data["instances"]}
    ly = pya.Layout()
    ly.dbu = P.DBU
    top = ly.create_cell("rt5w_analog")
    li = {k: ly.layer(*v) for k, v in dict(M3=P.L_M3, V3=P.L_V3, M4=P.L_M4, PR=(0, 0)).items()}

    # ---- place the blocks
    cells = {}
    for path, pl in fp["placements"].items():
        i = insts.get(path)
        b = blocks[i["block"]] if i else None
        if b is None or not b.get("gds"):
            continue                                 # the controller placeholder until it is hardened
        if i["block"] not in cells:
            src = pya.Layout()
            src.read(os.path.join(ROOT, b["gds"]))
            c = ly.create_cell(i["block"])
            c.copy_tree(src.cell(i["block"]))
            cells[i["block"]] = c
        origin = json.load(open(os.path.join(GDS, i["block"] + ".json")))["origin"]
        t = orient_trans(pl["orient"], pl["x"], pl["y"], b["w"], b["h"])
        top.insert(pya.CellInstArray(cells[i["block"]].cell_index(),
                                     t * pya.Trans(-int(round(origin[0] * UM)), -int(round(origin[1] * UM)))))
    # ---- grid, obstacles
    grid = Grid(tile["w"], tile["h"])
    for path, pl in fp["placements"].items():
        b = blocks[insts[path]["block"]]
        i0, j0 = grid.idx(pl["x"] - KEEPOUT, pl["y"] - KEEPOUT)
        i1, j1 = grid.idx(pl["x"] + b["w"] + KEEPOUT, pl["y"] + b["h"] + KEEPOUT)
        grid.block[:, max(i0, 0):min(i1 + 1, grid.nx), max(j0, 0):min(j1 + 1, grid.ny)] = True
    # ---- power stripes (Metal4, left edge of the tile)
    stripes = {"vdd": 3.0, "vss": 3.0 + STRIPE_W + 2.0}
    shapes = []                                       # (layer, box nm)
    terms = {}                                        # net -> list of (access node set, connect geometry)
    for net, x in stripes.items():
        y0, y1 = 4.0, tile["h"] - 4.0
        shapes.append(("M4", (x * UM, y0 * UM, (x + STRIPE_W) * UM, y1 * UM)))
        i0, i1 = grid.idx(x, 0)[0], grid.idx(x + STRIPE_W, 0)[0]
        nodes = {(1, i, j) for i in range(i0, i1 + 1) for j in range(grid.idx(0, y0)[1], grid.idx(0, y1)[1] + 1)
                 if 0 <= i < grid.nx and 0 <= j < grid.ny}
        for l, i, j in nodes:
            grid.owner[l, i, j] = -2                  # reserved; claimed per net below
        terms.setdefault(net, []).append((nodes, []))
        label_net = "VDPWR" if net == "vdd" else "VGND"
        top.shapes(ly.layer(*P.LABEL[P.L_M4])).insert(pya.Text(label_net, pya.Trans(int((x + 1) * UM), int(tile["h"] / 2 * UM))))
    # ---- TT pins: analog ua[k] on the bottom edge, digital pins on the top edge (moved to this tile's top)
    for p in data["tt_pins"]:
        if p["name"] in ("VDPWR", "VGND", "VAPWR"):
            continue
        p = dict(p)
        if not p["name"].startswith("ua["):
            p["y"] = tile["h"] - p["h"]
        if True:
            net = "ua" + p["name"][3:-1] if p["name"].startswith("ua[") else p["name"]
            i0, j0 = grid.idx(p["x"], p["y"])
            i1, j1 = grid.idx(p["x"] + p["w"], p["y"] + p["h"])
            nodes = {(1, i, j) for i in range(i0, i1 + 1) for j in range(j0, j1 + 2) if 0 <= j < grid.ny}
            terms.setdefault(net, []).append((nodes, [("M4", (p["x"] * UM, p["y"] * UM, (p["x"] + p["w"]) * UM, (p["y"] + p["h"]) * UM))]))
            top.shapes(ly.layer(*P.LABEL[P.L_M4])).insert(pya.Text(p["name"], pya.Trans(int((p["x"] + p["w"] / 2) * UM), int((p["y"] + p["h"] / 2) * UM))))
    # ---- block pins -> access nodes just outside the block edge
    for path, pl in fp["placements"].items():
        i = insts[path]
        b = blocks[i["block"]]
        for pin in b["pins"]:
            if pin["layer"] != "Metal3":
                continue
            net = pin["net"] if pin["net"] in ("vdd", "vss") else i["conn"].get(pin["net"])
            if net is None or (net not in ("vdd", "vss") and net.startswith("uio_oe")) and False:
                continue
            if net is None:
                continue
            x, y, side = pin_abs(pin, pl, b)
            xa = (pl["x"] - KEEPOUT - G) if side == "L" else (pl["x"] + b["w"] + KEEPOUT + G)
            ia, ja = grid.idx(xa, y)
            if not (0 <= ia < grid.nx and 0 <= ja < grid.ny):
                continue
            geom = [("M3", (min(x, ia * G) * UM - W_WIRE / 2, y * UM - W_WIRE / 2, max(x, ia * G) * UM + W_WIRE / 2, y * UM + W_WIRE / 2)),
                    ("M3", (ia * G * UM - W_WIRE / 2, min(y, ja * G) * UM - W_WIRE / 2, ia * G * UM + W_WIRE / 2, max(y, ja * G) * UM + W_WIRE / 2))]
            dout = -1 if side == "L" else 1               # the pin owns its node and the next one outwards, on both
            nodes = {(0, ia, ja), (1, ia, ja), (0, ia + dout, ja), (1, ia + dout, ja)}     # layers (an escape)
            terms.setdefault(net, []).append(({n for n in nodes if 0 <= n[1] < grid.nx}, geom))
    # ---- route, shortest nets first; nets that fail are moved to the front and everything is re-routed
    net_ids = {n: k for k, n in enumerate(sorted(terms))}

    def span(n):
        pts = [nd for nodes, _ in terms[n] for nd in nodes]
        xs, ys = [p[1] for p in pts], [p[2] for p in pts]
        return (max(xs) - min(xs)) + (max(ys) - min(ys))
    order = sorted((n for n in terms if len(terms[n]) > 1), key=lambda n: (n not in ("vdd", "vss"), span(n)))
    owner0 = grid.owner.copy()
    for attempt in range(5):
        grid.owner = owner0.copy()
        res = route_all(grid, terms, order, net_ids, max_expand=600_000 * (attempt + 1))
        if not res["failed"]:
            break
        order = res["failed"] + [n for n in order if n not in res["failed"]]
    shapes += res["shapes"]
    report = dict(routed=res["routed"], failed=res["failed"], attempts=attempt + 1,
                  single_pin=[n for n in terms if len(terms[n]) < 2])
    # ---- draw
    for lay, (x0, y0, x1, y1) in shapes:
        top.shapes(li[lay]).insert(pya.Box(int(x0), int(y0), int(x1), int(y1)))
    top.shapes(li["PR"]).insert(pya.Box(0, 0, int(tile["w"] * UM), int(tile["h"] * UM)))
    out = out or os.path.join(GDS, "rt5w_analog.gds")
    keep = set(top.called_cells()) | {top.cell_index()}
    for c in [c for c in ly.each_cell() if c.cell_index() not in keep]:
        ly.delete_cell(c.cell_index())
    ly.write(out)
    report.update(tile=tile, gds=os.path.relpath(out, ROOT), nets=len(order))
    json.dump(report, open(os.path.splitext(out)[0] + ".route.json", "w"), indent=1)
    return report


def terms_geom_path(path, shapes):
    """Wire boxes between consecutive grid nodes of one layer; via3 with Metal3/Metal4 pads where the layer changes."""
    hw = W_WIRE // 2
    for a, c in zip(path, path[1:]):
        xa, ya, xc, yc = a[1] * G * UM, a[2] * G * UM, c[1] * G * UM, c[2] * G * UM
        if a[0] == c[0]:
            shapes.append(("M3" if a[0] == 0 else "M4", (min(xa, xc) - hw, min(ya, yc) - hw, max(xa, xc) + hw, max(ya, yc) + hw)))
        else:
            shapes.append(("V3", (xa - 130, ya - 130, xa + 130, ya + 130)))
            shapes.append(("M3", (xa - 200, ya - 200, xa + 200, ya + 200)))
            shapes.append(("M4", (xa - 200, ya - 200, xa + 200, ya + 200)))


if __name__ == "__main__":
    fpp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(FP, "floorplan.json")
    r = build(fpp)
    print(f"{r['gds']}: {len(r['routed'])}/{r['nets']} nets routed, failed: {r['failed']}, "
          f"single-pin (controller side): {len(r['single_pin'])}")
