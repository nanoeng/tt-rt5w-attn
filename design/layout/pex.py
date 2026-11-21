"""Post-layout netlists for simulation: flat magic extraction of the drawn blocks with parasitic capacitance
(area/fringe to substrate and coupling between nets, every value kept: cthresh 0), no wire resistance.

Why C only: every analog net here carries <= a few uA (unit current I_u ~ 120 nA); a 100-ohm wire drops <= 0.1 mV,
far below the 43..69 mV/e-fold slope of the weak-inversion law, while the capacitance sets the readout integration
and the settling of the high-impedance nodes. The supply rails (VAPWR, VGND) carry ~5 uA in total.

Output: netlist_pex/<cell>.spice with the flat extraction as <cell>__pex and a wrapper subckt <cell> with the
schematic's port order (netlist/<cell>.spice), so every testbench runs unchanged with RT5W_NETLIST=netlist_pex.
netlist_pex/rt5w_analog.spice: the schematic top with the extracted blocks. layout/pex/array_nodes.json: the
storage nodes (h of each key cell, w of each row trim) in the extracted array, for the chain testbench.

    pixi run -e pd python design/layout/pex.py
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/ext/pdk")
RC = os.path.join(PDK_ROOT, "sky130A", "libs.tech", "magic", "sky130A.magicrc")
GDS = os.path.join(ROOT, "layout", "gds")
OUT = os.path.join(ROOT, "layout", "pex")
NET = os.path.join(ROOT, "netlist")
NETP = os.path.join(ROOT, "netlist_pex")
# cell -> GDS file that contains it
CELLS = {"rt5w_softmax": "rt5w_softmax", "rt5w_readout": "rt5w_readout", "rt5w_bias": "rt5w_bias",
         "rt5w_kscale": "rt5w_kscale", "rt5w_vbbuf": "rt5w_vbbuf", "rt5w_array": "rt5w_array",
         "rt5w_keycell": "rt5w_array", "rt5w_coldiode": "rt5w_array"}
ANALOG_CHILDREN = ["rt5w_bias", "rt5w_array", "rt5w_softmax", "rt5w_kscale", "rt5w_readout", "rt5w_vbbuf"]


def extract(cell):
    os.makedirs(OUT, exist_ok=True)
    d = os.path.join(OUT, cell)
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, cell + ".pex.spice")
    subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", RC, os.path.join(HERE, "magic_pex.tcl"),
                    os.path.join(GDS, CELLS[cell] + ".gds"), cell, out], capture_output=True, text=True,
                   cwd=d, timeout=7200, env=dict(os.environ, PDK_ROOT=PDK_ROOT), check=False)
    if not os.path.exists(out):
        raise RuntimeError(f"{cell}: no extraction")
    return out


def subckt_ports(text, name):
    m = re.search(rf"^\.subckt\s+{re.escape(name)}\s+(.*?)$((?:\n\+.*$)*)", text, re.M | re.I)
    words = (m.group(1) + " " + m.group(2).replace("\n+", " ")).split()
    return [w for w in words if "=" not in w]


def sch_ports(cell):
    for f in (os.path.join(NET, cell + ".spice"), os.path.join(NET, "rt5w_analog.spice")):
        t = open(f).read()
        if re.search(rf"^\.subckt\s+{cell}\s", t, re.M | re.I):
            return subckt_ports(t, cell)
    raise ValueError(cell)


def wrapped(cell, pex_file):
    """flat extraction renamed <cell>__pex + wrapper <cell> in the schematic port order"""
    t = open(pex_file).read().replace("\n+", " ")
    body = []
    keep = False
    for line in t.splitlines():
        if re.match(rf"\.subckt\s+{cell}\s", line, re.I):
            keep = True
            line = re.sub(rf"^\.subckt\s+{cell}", f".subckt {cell}__pex", line, flags=re.I)
        if keep and line.strip():
            body.append(line)
        if keep and re.match(r"\.ends", line, re.I):
            break
    pports = subckt_ports("\n".join(body), cell + "__pex")
    sports = sch_ports(cell)
    missing = [p for p in sports if p not in pports]
    alias = {}
    if missing:      # a schematic port the layout has no label for (e.g. a supply joined to another): report
        raise ValueError(f"{cell}: schematic ports without a layout port: {missing}")
    # a layout port the schematic does not have: the substrate (vss / VSUBS of a cell without a vss pin) goes to
    # ground, anything else stays an internal node of the wrapper
    conn = [p if p in sports else ("0" if p.lower() in ("vss", "vsubs") else f"nc_{re.sub(r'[^A-Za-z0-9_]', '_', p)}")
            for p in pports]
    wrap = [f".subckt {cell} " + " ".join(sports), f"Xp {' '.join(alias.get(c, c) for c in conn)} {cell}__pex", ".ends"]
    # wrapper first: sim.ports() reads the first .subckt of the file
    return "\n".join(wrap) + "\n\n" + "\n".join(body) + "\n", len([l for l in body if l[:1] in "Cc"]), \
        sum(_cap(l) for l in body if l[:1] in "Cc")


def _cap(line):
    v = line.split()[3]
    mult = {"f": 1e-15, "p": 1e-12, "a": 1e-18, "n": 1e-9}
    return float(v[:-1]) * mult[v[-1].lower()] if v[-1].lower() in mult else float(v)


def array_nodes(pex_file):
    """storage nodes in the flat array: h_ji = the non-vw terminal of the 0.84/0.5 um write NMOS gated by wsel(4j+i);
    w_j = the gate of the key cell's second input NMOS (shares the tail with the device gated by h)"""
    t = open(pex_file).read().replace("\n+", " ")
    devs = []
    for line in t.splitlines():
        if line[:1] in "Xx" and "fet" in line:
            tk = line.split()
            p = dict(kv.split("=") for kv in tk[6:] if "=" in kv)
            devs.append(dict(d=tk[1], g=tk[2], s=tk[3], model=tk[5], w=float(p["w"]), l=float(p["l"])))
    h = {}
    for dv in devs:
        if "nfet" in dv["model"] and abs(dv["w"] - 0.84) < 1e-3 and abs(dv["l"] - 0.5) < 1e-3:
            m = re.fullmatch(r"wsel(\d+)", dv["g"])
            if m and int(m.group(1)) < 16 and "vw" in (dv["d"], dv["s"]):
                n = int(m.group(1))
                h[f"{n // 4}{n % 4}"] = dv["s"] if dv["d"] == "vw" else dv["d"]
    w = {}
    for ji, hn in h.items():
        pair = [dv for dv in devs if abs(dv["w"] - 0.62) < 1e-3 and abs(dv["l"] - 4) < 1e-3 and "nfet" in dv["model"]]
        m3 = [dv for dv in pair if dv["g"] == hn]
        if len(m3) != 1:
            raise ValueError(f"key cell {ji}: {len(m3)} devices gated by h")
        tail = m3[0]["s"] if m3[0]["d"] != m3[0]["s"] else m3[0]["d"]
        m4 = [dv for dv in pair if dv["g"] != hn and tail in (dv["s"], dv["d"]) and dv is not m3[0]]
        gates = {dv["g"] for dv in m4}
        if len(gates) != 1:
            raise ValueError(f"key cell {ji}: w gate ambiguous {gates}")
        w.setdefault(ji[0], gates.pop())
    if len(h) != 16 or len(w) != 4:
        raise ValueError(f"found {len(h)} h, {len(w)} w nodes")
    return dict(h=h, w=w)


def main():
    os.makedirs(NETP, exist_ok=True)
    stats = {}
    texts = {}
    for cell in CELLS:
        f = extract(cell)
        txt, ncap, ctot = wrapped(cell, f)
        texts[cell] = txt
        open(os.path.join(NETP, cell + ".spice"), "w").write(txt)
        nd = sum(1 for l in txt.splitlines() if l[:1] in "Xx" and "sky130_fd_pr" in l)
        stats[cell] = dict(devices=nd, caps=ncap, c_total_pF=round(ctot * 1e12, 3))
        print(f"{cell:14s} devices {nd:5d}  parasitic C {ncap:6d}  total {ctot * 1e12:8.3f} pF")
    nodes = array_nodes(os.path.join(OUT, "rt5w_array", "rt5w_array.pex.spice"))
    json.dump(nodes, open(os.path.join(OUT, "array_nodes.json"), "w"), indent=1)
    # analog top: schematic top subckt + extracted children
    t = open(os.path.join(NET, "rt5w_analog.spice")).read()
    a = re.search(r"^\.subckt\s+rt5w_analog\s.*?^\.ends", t, re.M | re.S | re.I).group(0)
    open(os.path.join(NETP, "rt5w_analog.spice"), "w").write(a + "\n\n" + "\n".join(texts[c] for c in ANALOG_CHILDREN))
    json.dump(stats, open(os.path.join(OUT, "pex_stats.json"), "w"), indent=1)
    return stats


if __name__ == "__main__":
    main()
