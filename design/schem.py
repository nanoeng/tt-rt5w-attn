"""Schematic capture by code: textbook-style xschem schematics for the RT5W analog blocks.

A block is described as placed devices (PDK xschem symbols, x/y on a 10-unit grid, rotation, flip) plus, for every
device pin, the net it belongs to. The writer then
  * draws the supply rails as VDD / GND symbols on short stubs (textbook convention: power up, ground down);
  * routes every other net as an orthogonal tree of wires between its pins (L-shaped hops, choosing the bend that
    does not overlap or touch another net); a net that cannot be drawn cleanly gets net labels instead;
  * places ipin / opin / iopin symbols for the block's ports;
  * writes a block symbol (.sym) so the block can be used in a parent schematic;
  * netlists with xschem and CHECKS that xschem's connectivity equals the intended one (verify()), so a drawing error
    can never reach simulation or LVS unnoticed.
"""
import itertools
import os
import re
import shutil
import subprocess
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/ext/pdk")
PDK = os.environ.get("PDK", "sky130A")
XSCHEM_PDK = os.path.join(PDK_ROOT, PDK, "libs.tech", "xschem")
SYMDIR = os.path.join(XSCHEM_PDK, "sky130_fd_pr")
XSCHEM_DIR = os.path.join(ROOT, "xschem")
GLOBAL_RAILS = {"vdd": "vdd.sym", "vss": "gnd.sym"}

_pin_cache = {}


def _devlib():
    for base in (os.environ.get("CONDA_PREFIX", ""), os.path.join(ROOT, ".pixi", "envs", "pd")):
        d = os.path.join(base, "share", "xschem", "xschem_library", "devices")
        if os.path.isdir(d):
            return d
    raise RuntimeError("xschem device library not found (run in the pixi 'pd' environment)")


def sym_path(sym):
    if sym.startswith("sky130_fd_pr/"):
        return os.path.join(XSCHEM_PDK, sym)
    if os.path.exists(os.path.join(XSCHEM_DIR, sym)):
        return os.path.join(XSCHEM_DIR, sym)
    return os.path.join(_devlib(), sym)


def sym_pins(sym):
    """Pin name -> (x, y) centre, from the symbol's 'B 5' boxes."""
    if sym not in _pin_cache:
        pins = {}
        for line in open(sym_path(sym)):
            m = re.match(r"B 5 (\S+) (\S+) (\S+) (\S+) \{(.*)", line)
            if m:
                x1, y1, x2, y2 = map(float, m.groups()[:4])
                name = re.search(r"name=(\S+?)[\s}]", m.group(5) + " ").group(1)
                pins[name] = ((x1 + x2) / 2, (y1 + y2) / 2)
        _pin_cache[sym] = pins
    return _pin_cache[sym]


def xform(p, rot, flip):
    x, y = p
    if flip:
        x = -x
    for _ in range(rot % 4):
        x, y = -y, x
    return x, y


def snap(v):
    return round(v / 10.0) * 10


class Inst:
    def __init__(self, name, sym, x, y, rot=0, flip=0, params=None, conn=None):
        self.name, self.sym, self.x, self.y, self.rot, self.flip = name, sym, x, y, rot, flip
        self.params = params or {}
        self.conn = conn or {}

    def pin_xy(self, pin):
        dx, dy = xform(sym_pins(self.sym)[pin], self.rot, self.flip)
        return (self.x + dx, self.y + dy)


MOS_DEFAULTS = dict(nf=1, m=1)


class Schematic:
    """One block. Coordinates in xschem units (y grows downwards)."""

    def __init__(self, name, title="", ports=None):
        self.name, self.title = name, title
        self.insts = []
        self.ports = []                # (net, dir, x, y)
        self.port_order = ports or []
        self.labels_only = set()       # nets forced to labels
        self.trunks = {}               # net -> ('h', y) or ('v', x): bus with straight drops
        self.texts = []

    # ---------------------------------------------------------------- devices
    def nmos(self, name, x, y, D, G, S, B="vss", W=1, L=1, m=1, nf=1, flip=0, model="nfet_g5v0d10v5"):
        return self._mos(name, "sky130_fd_pr/nfet_g5v0d10v5.sym", model, x, y, D, G, S, B, W, L, m, nf, flip)

    def pmos(self, name, x, y, D, G, S, B="vdd", W=1, L=1, m=1, nf=1, flip=0, model="pfet_g5v0d10v5"):
        return self._mos(name, "sky130_fd_pr/pfet_g5v0d10v5.sym", model, x, y, D, G, S, B, W, L, m, nf, flip)

    def _mos(self, name, sym, model, x, y, D, G, S, B, W, L, m, nf, flip):
        """sky130 4-terminal 3.3/5 V device (g5v0d10v5). W, L in um (the PDK models are scaled in um).
        W, L may come from sizing.dev() (gm/ID LUT); W >= 0.42, L >= 0.5."""
        if isinstance(W, dict):
            W, L = W["W"], W["L"]
        W, L = round(max(float(W), 0.42), 2), round(max(float(L), 0.5), 2)
        # source/drain geometry as the PDK symbol template computes it (0.29 um diffusion each side, nf = 1)
        a, pp = W * 0.29, 2 * (W + 0.29)
        p = dict(name=name, L=f"{L:g}", W=f"{W:g}", nf=nf, mult=m, model=model, spiceprefix="X",
                 ad=f"{a:.4g}", pd=f"{pp:.4g}", nrd=f"{0.29 / W:.4g}", nrs=f"{0.29 / W:.4g}", sa=0, sb=0, sd=0)
        p["as"] = f"{a:.4g}"
        p["ps"] = f"{pp:.4g}"
        i = Inst(name, sym, x, y, 0, flip, p, dict(D=D, G=G, S=S, B=B))
        i.body = None
        self.insts.append(i)
        return i

    def moscap(self, name, x, y, G, B, W=10, L=10, m=1, rot=0, kind="nmos"):
        """MOS capacitor built as a transistor with D = S = B (charge-conserving BSIM4 gate charge, no C(V) element);
        LVS sees an ordinary transistor."""
        f = self.nmos if kind == "nmos" else self.pmos
        return f(name, x, y, D=B, G=G, S=B, B=B, W=W, L=L, m=m)

    def res(self, name, x, y, P, M, B="vss", W=0.35, L=10, m=1, rot=0, model="res_xhigh_po_0p35"):
        """sky130 precision poly resistor, fixed width (0p35 = 0.35 um); res_xhigh_po ~2 kOhm/sq."""
        sym = f"sky130_fd_pr/{model}.sym"
        p = dict(name=name, L=f"{L:g}", model=model, spiceprefix="X", mult=m)
        i = Inst(name, sym, x, y, rot, 0, p, dict(P=P, M=M, B=B))
        self.insts.append(i)
        return i

    def block(self, name, sym, x, y, conn, rot=0, flip=0):
        i = Inst(name, sym, x, y, rot, flip, dict(name=name), conn)
        self.insts.append(i)
        return i

    def port(self, net, direction, x, y):
        self.ports.append((net, direction, x, y))

    def bus(self, net, axis, at):
        """Draw `net` as a straight trunk (horizontal at y=at, or vertical at x=at) with straight drops to each pin."""
        self.trunks[net] = (axis, at)

    def text(self, s, x, y, size=0.4):
        self.texts.append((s, x, y, size))

    # ---------------------------------------------------------------- routing
    def _pins_by_net(self):
        nets = defaultdict(list)
        for i in self.insts:
            for pin, net in i.conn.items():
                nets[net].append(i.pin_xy(pin))
        for net, d, x, y in self.ports:
            nets[net].append((x, y))
        return nets

    def route(self):
        nets = self._pins_by_net()
        pin_points = {}
        for net, pts in nets.items():
            for p in pts:
                pin_points.setdefault(p, set()).add(net)
        wires, labels, rails = [], [], []
        occupied = []                       # (net, segment)

        def seg_conflict(net, a, b):
            (x1, y1), (x2, y2) = a, b
            if (x1, y1) == (x2, y2):
                return False
            for p, ns in pin_points.items():   # passes through another net's pin
                if net in ns:
                    continue
                if _on_seg(p, a, b):
                    return True
            for onet, (c, d) in occupied:
                if onet == net:
                    continue
                if _overlap(a, b, c, d) or _on_seg(c, a, b) or _on_seg(d, a, b) or _on_seg(a, c, d) or _on_seg(b, c, d):
                    return True
            return False

        # supply stubs first: they become obstacles for every signal net. A supply tied to a *signal* pin of a block
        # symbol gets a label instead (a stub could land on the neighbouring pin 20 units away).
        rail_lab = {(net, i.pin_xy(pin)) for i in self.insts if not i.sym.startswith("sky130_fd_pr/")
                    for pin, net in i.conn.items() if net in GLOBAL_RAILS and pin not in GLOBAL_RAILS}
        # MOS bulk pins sit on the drain/source line of the sky130 symbols: always drawn as net labels
        body_lab = {(net, i.pin_xy("B")) for i in self.insts if i.sym.startswith("sky130_fd_pr/") and "fet" in i.sym
                    for pin, net in i.conn.items() if pin == "B"}
        rail_lab |= body_lab
        labels += list(rail_lab)
        port_xy = {(n, (x, y)) for n, d, x, y in self.ports} | rail_lab
        for net in GLOBAL_RAILS:
            for p in sorted(set(nets.get(net, []))):
                if (net, p) in port_xy:
                    continue
                stub = -20 if net == "vdd" else 20
                q = (p[0], p[1] + stub)
                occupied.append((net, (p, q)))
                pin_points.setdefault(q, set()).add(net)
        order = sorted(nets.items(), key=lambda kv: (kv[0] in GLOBAL_RAILS, len(kv[1])))
        for net, pts in order:
            pts = sorted(set(p for p in pts if (net, p) not in body_lab or net in GLOBAL_RAILS))
            if net in GLOBAL_RAILS:
                for p in pts:
                    if p in [(x, y) for n, d, x, y in self.ports if n == net] or (net, p) in rail_lab:
                        continue
                    rails.append((net, p))
                continue
            if len(pts) < 2 and net not in [n for n, *_ in self.ports]:
                continue
            if net in self.labels_only:
                labels += [(net, p) for p in pts]
                continue
            if net in self.trunks:
                axis, at = self.trunks[net]
                segs = []
                if axis == "h":
                    for (x, y) in pts:
                        if y != at:
                            segs.append(((x, y), (x, at)))
                    xs = sorted({x for x, _ in pts})
                    segs += [((a, at), (b, at)) for a, b in zip(xs, xs[1:])]
                else:
                    for (x, y) in pts:
                        if x != at:
                            segs.append(((x, y), (at, y)))
                    ys = sorted({y for _, y in pts})
                    segs += [((at, a), (at, b)) for a, b in zip(ys, ys[1:])]
                if not any(seg_conflict(net, a, b) for a, b in segs):
                    wires += [(net, a, b) for a, b in segs]
                    occupied += [(net, sg) for sg in segs]
                else:
                    labels += [(net, p) for p in pts]
                continue
            tree = [pts[0]]
            segs = []
            ok = True
            for p in pts[1:]:
                best = None
                for q in sorted(tree, key=lambda t: abs(t[0] - p[0]) + abs(t[1] - p[1])):
                    for corner in ((q[0], p[1]), (p[0], q[1])):
                        cand = [(q, corner), (corner, p)]
                        if not any(seg_conflict(net, a, b) for a, b in cand):
                            best = cand
                            break
                    if best:
                        break
                if best is None:
                    ok = False
                    break
                for a, b in best:
                    if a != b:
                        segs.append((a, b))
                        occupied.append((net, (a, b)))
                tree += [best[0][1], p]
            if ok:
                wires += [(net, a, b) for a, b in segs]
            else:
                for s in segs:
                    occupied.remove((net, s))
                labels += [(net, p) for p in pts]
        # nets referenced by name in a body= parameter must carry that name in the drawing
        body_nets = {getattr(i, "body", None) for i in self.insts} - set(GLOBAL_RAILS) - {None}
        labelled = {n for n, _ in labels} | {n for n, *_ in self.ports}
        internal = set(nets) - set(GLOBAL_RAILS)        # every internal node gets its name in the drawing
        for net in sorted((body_nets | internal) - labelled):
            if nets.get(net):
                labels.append((net, sorted(set(nets[net]))[0]))
        self._wires, self._labels, self._rails = wires, labels, rails

    # ---------------------------------------------------------------- output
    def write(self, outdir=XSCHEM_DIR):
        os.makedirs(outdir, exist_ok=True)
        self.route()
        L = ["v {xschem version=3.4.5 file_version=1.2}", "G {}", "K {}", "V {}", "S {}", "E {}"]
        for s, x, y, size in self.texts:
            L.append(f"T {{{s}}} {x} {y} 0 0 {size} {size} {{}}")
        for net, (x1, y1), (x2, y2) in self._wires:
            L.append(f"N {x1:g} {y1:g} {x2:g} {y2:g} {{lab={net}}}")
        k = 0
        for net, (x, y) in self._rails:
            k += 1
            stub = -20 if net == "vdd" else 20
            L.append(f"N {x:g} {y:g} {x:g} {y + stub:g} {{lab={net.upper() if False else net}}}")
            sym = GLOBAL_RAILS[net]
            L.append(f"C {{{sym}}} {x:g} {y + stub:g} 0 0 {{name=r{k} lab={net}}}")
        for net, (x, y) in self._labels:
            k += 1
            L.append(f"C {{lab_pin.sym}} {x:g} {y:g} 0 0 {{name=l{k} sig_type=std_logic lab={net}}}")
        for net, d, x, y in self.ports:
            k += 1
            sym = {"in": "ipin.sym", "out": "opin.sym", "inout": "iopin.sym"}[d]
            L.append(f"C {{{sym}}} {x:g} {y:g} 0 0 {{name=p{k} lab={net}}}")
        for i in self.insts:
            attrs = " ".join(f"{k}={v}" for k, v in i.params.items())
            L.append(f"C {{{i.sym}}} {i.x:g} {i.y:g} {i.rot} {i.flip} {{{attrs}}}")
        path = os.path.join(outdir, self.name + ".sch")
        open(path, "w").write("\n".join(L) + "\n")
        self.write_symbol(outdir)
        return path

    def write_symbol(self, outdir=XSCHEM_DIR, order=None):
        """Block symbol: box, inputs on the left, outputs on the right, supplies on top/bottom.
        Pins are written in `order` (the netlisted .subckt order) so instance and definition always agree."""
        names = order or self.port_order or [n for n, *_ in self.ports]
        dirs = {n: d for n, d, *_ in self.ports}
        left = [n for n in names if dirs.get(n) == "in"]
        right = [n for n in names if dirs.get(n) in ("out", "inout") and n not in GLOBAL_RAILS]
        top = [n for n in names if n == "vdd"]
        bot = [n for n in names if n == "vss"]
        h = 20 * max(len(left), len(right), 2) + 20
        w = 160
        L = ["v {xschem version=3.4.5 file_version=1.2}", "G {}",
             f"K {{type=subcircuit\nformat=\"@name @pinlist @symname\"\ntemplate=\"name=x1\"\n}}", "V {}", "S {}", "E {}",
             f"B 4 {-w // 2} {-h // 2} {w // 2} {h // 2} {{}}",
             f"T {{@symname}} 0 {-h // 2 - 20} 0 0 0.3 0.3 {{hcenter=true}}",
             f"T {{@name}} 0 {h // 2 + 5} 0 0 0.25 0.25 {{hcenter=true}}"]
        pin_lines = {}
        for k, n in enumerate(left):
            y = -h // 2 + 20 + 20 * k
            pin_lines[n] = [f"L 4 {-w // 2 - 20} {y} {-w // 2} {y} {{}}",
                  f"B 5 {-w // 2 - 22.5} {y - 2.5} {-w // 2 - 17.5} {y + 2.5} {{name={n} dir=in}}",
                  f"T {{{n}}} {-w // 2 + 5} {y - 6} 0 0 0.2 0.2 {{}}"]
        for k, n in enumerate(right):
            y = -h // 2 + 20 + 20 * k
            d = dirs[n]
            pin_lines[n] = [f"L 4 {w // 2} {y} {w // 2 + 20} {y} {{}}",
                  f"B 5 {w // 2 + 17.5} {y - 2.5} {w // 2 + 22.5} {y + 2.5} {{name={n} dir={d}}}",
                  f"T {{{n}}} {w // 2 - 5} {y - 6} 0 1 0.2 0.2 {{}}"]
        for n, y0, sgn in [(n, -h // 2, -1) for n in top] + [(n, h // 2, 1) for n in bot]:
            pin_lines[n] = [f"L 4 0 {y0} 0 {y0 + 20 * sgn} {{}}",
                  f"B 5 -2.5 {y0 + 20 * sgn - 2.5} 2.5 {y0 + 20 * sgn + 2.5} {{name={n} dir=inout}}",
                  f"T {{{n}}} 5 {y0 + 4 * sgn - (8 if sgn < 0 else 0)} 0 0 0.2 0.2 {{}}"]
        for n in names:
            L += pin_lines.get(n, [])
        open(os.path.join(outdir, self.name + ".sym"), "w").write("\n".join(L) + "\n")
        _pin_cache.pop(self.name + ".sym", None)

    # ---------------------------------------------------------------- tools
    def intended(self):
        """Instance -> pin -> net, as designed."""
        out = {}
        for i in self.insts:
            c = dict(i.conn)
            if getattr(i, "body", None) is not None:
                c["@body"] = i.body
            out[i.name] = c
        return out


def _on_seg(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    if x1 == x2 == x:
        return min(y1, y2) <= y <= max(y1, y2)
    if y1 == y2 == y:
        return min(x1, x2) <= x <= max(x1, x2)
    return False


def _overlap(a, b, c, d):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a, b, c, d
    if x1 == x2 == x3 == x4:
        return max(min(y1, y2), min(y3, y4)) < min(max(y1, y2), max(y3, y4))
    if y1 == y2 == y3 == y4:
        return max(min(x1, x2), min(x3, x4)) < min(max(x1, x2), max(x3, x4))
    return False


def xschem(*args, cwd=XSCHEM_DIR, x=False):
    env = dict(os.environ, PDK_ROOT=PDK_ROOT, PDK=PDK)
    rc = os.path.join(XSCHEM_DIR, "xschemrc")
    if not os.path.exists(rc):
        os.makedirs(XSCHEM_DIR, exist_ok=True)
        base = open(os.path.join(XSCHEM_PDK, "xschemrc")).read()
        open(rc, "w").write(base + f"\nappend XSCHEM_LIBRARY_PATH :{XSCHEM_PDK}\nappend XSCHEM_LIBRARY_PATH :{XSCHEM_DIR}\nset dark_colorscheme 0\nset color_ps 1\n")
    cmd = (["xvfb-run", "-a"] if x else []) + ["xschem", "--rcfile", rc] + list(args)
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=600)


def netlist(name, outdir=None, lvs=False):
    outdir = outdir or os.path.join(ROOT, "netlist")
    os.makedirs(outdir, exist_ok=True)
    args = ["-n", "-s", "-q", "--no_x", "-o", outdir]
    if lvs:
        args += ["--tcl", "set lvs_netlist 1; set top_is_subckt 1"]
    else:
        args += ["--tcl", "set top_is_subckt 1"]
    r = xschem(*args, name + ".sch")
    path = os.path.join(outdir, name + ".spice")
    if not os.path.exists(path):
        raise RuntimeError(r.stdout + r.stderr)
    txt = open(path).read()
    txt = re.sub(r"^\*\*\.subckt ", ".subckt ", txt, flags=re.M)
    txt = re.sub(r"^\*\*\.ends", ".ends", txt, flags=re.M)
    lines, fixed, in_hdr = txt.splitlines(), [], False
    for l in lines:                                     # '*+' continuations of the .subckt line
        if l.startswith(".subckt "):
            in_hdr = True
        elif in_hdr and l.startswith("*+"):
            l = l[1:]
        else:
            in_hdr = False
        fixed.append(l)
    txt = "\n".join(fixed) + "\n"
    open(path, "w").write(txt)
    return path


def render_svg(name, outdir=None):
    """SVG of the schematic (light colours, zoomed to fit), via xschem under a virtual X server."""
    outdir = outdir or os.path.join(ROOT, "docs", "schematics")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, name + ".svg")
    if os.path.exists(out):
        os.remove(out)
    xschem("--command", f"xschem zoom_full; xschem print svg {out}; xschem exit closewindow force", name + ".sch", x=True)
    return out


def parse_netlist(path):
    """Instance (without the X prefix) -> list of nets in symbol pin order, from an xschem netlist."""
    txt = open(path).read().replace("\n+", " ")
    inst = {}
    for line in txt.splitlines():
        line = line.strip()
        if not line or line[0] in "*." or "=" not in line and not line.startswith("x"):
            continue
        tok = line.split()
        name = tok[0]
        if name[0] not in "Xx":
            continue
        nets = []
        for t in tok[1:]:
            if "=" in t:
                break
            nets.append(t)
        inst[name.lower()] = nets      # last element is the model / subckt name
    return inst


def verify(sch, path):
    """Compare xschem's connectivity with the intended one; returns list of problems (empty = OK)."""
    got = parse_netlist(path)
    want = sch.intended()
    mapping, problems = {}, []
    for name, conn in want.items():
        key = next((k for k in ("x" + name.lower(), name.lower()) if k in got), None)
        if key is None:
            problems.append(f"{name}: missing from netlist")
            continue
        inst = next(i for i in sch.insts if i.name == name)
        order = _pin_order(inst.sym) + (["@body"] if getattr(inst, "body", None) is not None else [])
        nets = got[key][:len(order)]
        for pin, net_x in zip(order, nets):
            want_net = conn.get(pin)
            if want_net is None:
                continue
            m = mapping.setdefault(want_net, net_x)
            if m != net_x:
                problems.append(f"{name}.{pin}: intended {want_net} but drawn on '{net_x}' (expected '{m}')")
    inv = defaultdict(set)
    for w, x in mapping.items():
        inv[x].add(w)
    for x, ws in inv.items():
        if len(ws) > 1:
            problems.append(f"nets {sorted(ws)} are shorted in the drawing (xschem net '{x}')")
    return problems


def _pin_order(sym):
    """Pin order of the symbol's netlist line (order of B 5 boxes, as xschem's @pinlist)."""
    order = []
    for line in open(sym_path(sym)):
        m = re.match(r"B 5 .*\{(.*)", line)
        if m:
            order.append(re.search(r"name=(\S+?)[\s}]", m.group(1) + " ").group(1))
    pinnum = []
    for line in open(sym_path(sym)):
        m = re.match(r"B 5 .*pinnumber=(\d+)", line)
        if m:
            pinnum.append(int(m.group(1)))
    return order
