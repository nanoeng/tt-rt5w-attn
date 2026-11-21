"""ngspice runner for the captured schematics, on the open_pdks sky130A models (combined lib: nfet/pfet_g5v0d10v5,
res_xhigh_po ...). Corners: tt / ss / ff (and sf / fs); temperatures are set per run.

A testbench is SPICE text that instantiates xschem-netlisted blocks (netlist/<block>.spice). run() adds the model
library for the requested corner, runs ngspice in batch mode, and returns the scalar results printed by the
testbench's control section ('print' lines) plus any wrdata table.
"""
import os
import re
import subprocess
import tempfile

import numpy as np

from schem import PDK, PDK_ROOT, ROOT

NETLIST_DIR = os.path.join(ROOT, os.environ.get("RT5W_NETLIST", "netlist"))   # netlist_pex: post-layout (design/layout/pex.py)


def ports(block):
    """Port order of a netlisted block (its .subckt line)."""
    lines = open(os.path.join(NETLIST_DIR, block + ".spice")).read().splitlines()
    for k, line in enumerate(lines):
        if line.lower().startswith(".subckt"):
            words = line.split()[2:]
            for cont in lines[k + 1:]:              # '+' continuation lines
                if not cont.startswith("+"):
                    break
                words += cont[1:].split()
            return [w for w in words if "=" not in w]
    raise ValueError(block)


def inst(name, block, **conn):
    """Instance line with ports connected by name (missing ports are an error)."""
    order = ports(block)
    missing = [p for p in order if p not in conn]
    if missing:
        raise ValueError(f"{name}: unconnected ports {missing}")
    return f"{name} " + " ".join(str(conn[p]) for p in order) + f" {block}"


# the PDK's spinit (libs.tech/ngspice/spinit): HSPICE-compatible lib parsing, faster loading
SPICEINIT = "set ngbehavior=hsa\nset skywaterpdk\nset ng_nomodcheck\nset num_threads=4\noption noinit\n"
CORNER_ALIASES = {"typical": "tt"}


def header(corner="tt", temp=27.0, blocks=(), options="", mc=False):
    corner = CORNER_ALIASES.get(corner, corner)
    L = [f".lib {PDK_ROOT}/{PDK}/libs.tech/combined/sky130.lib.spice {corner}",
         f".param MC_MM_SWITCH={1 if mc else 0} MC_PR_SWITCH=0",
         f".temp {temp}", f".option gmin=1e-15 method=gear maxord=2 {options}".rstrip()]
    for b in blocks:
        L.append(f".include {os.path.join(NETLIST_DIR, b + '.spice')}")
    return "\n".join(L)


def run(body, control, corner="tt", temp=27.0, blocks=(), timeout=900, options="", mc=False):
    """body: circuit lines; control: lines inside .control (use 'print' for scalars, 'wrdata FILE ...' for tables).
    options: extra .option text; the full chain needs 'rshunt=1e12' (1 pA/V per node) for the DC operating point to
    converge -- without it ngspice falls back to a 'transient op' that leaves nA-biased diodes unsettled."""
    with tempfile.TemporaryDirectory() as td:
        data = os.path.join(td, "data.txt")
        ctl = control.replace("__DATA__", data)
        net = f"* tb\n{header(corner, temp, blocks, options, mc)}\n{body}\n.control\nset filetype=ascii\n{ctl}\n.endc\n.end\n"
        path = os.path.join(td, "tb.sp")
        open(path, "w").write(net)
        open(os.path.join(td, ".spiceinit"), "w").write(SPICEINIT)
        r = subprocess.run(["ngspice", "-b", path], capture_output=True, text=True, timeout=timeout, cwd=td)
        out = r.stdout + r.stderr
        vals = {}
        for m in re.finditer(r"^\s*([-+@\w\(\)#\.\[\]:,]+)\s*=\s*([-+0-9.eE]+)\s*$", r.stdout, re.M):
            vals[m.group(1).lower()] = float(m.group(2))
        table = np.loadtxt(data) if os.path.exists(data) and os.path.getsize(data) else None
        if not vals and table is None:
            raise RuntimeError("ngspice produced no results:\n" + out[-3000:])
        return vals, table, out
