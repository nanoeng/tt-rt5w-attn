"""Top-level LVS of tt_um_rt5w_attn: magic extraction of layout/gds/tt_um_rt5w_attn.gds against a reference built
from the block schematics (xschem netlists), the level-shifter bank netlist (hvl cells from their CDL), the digital
macro's power-aware gate netlist (OpenROAD) over the sky130_fd_sc_hd SPICE models, and the structural top
(layout/top/tt_um_rt5w_attn.v).

    pixi run -e pd python design/layout/lvs_top.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import lvs  # noqa: E402

TOP = "tt_um_rt5w_attn"
BLOCKS = ["rt5w_array", "rt5w_readout", "rt5w_bias", "rt5w_softmax", "rt5w_kscale", "rt5w_vbbuf", "rt5w_lsdn",
          "rt5w_lsbank", "rt5w_hvif"]
HD_SPICE = os.path.join(lvs.PDK_ROOT, "sky130A", "libs.ref", "sky130_fd_sc_hd", "spice", "sky130_fd_sc_hd.spice")


def reference(out):
    """All block subcircuits, each defined once."""
    seen, L = set(), []
    for b in BLOCKS:
        txt = open(os.path.join(ROOT, "netlist", b + ".spice")).read().replace("\n+", " ")
        cur = None
        for line in txt.splitlines():
            if line.startswith(("**", ".GLOBAL", ".end ")) or line.strip() == ".end":
                continue
            m = re.match(r"\.subckt\s+(\S+)", line, re.I)
            if m:
                cur = m.group(1)
                skip = cur in seen
                seen.add(cur)
            if cur is None or not skip:
                L.append(line)
            if re.match(r"\.ends", line, re.I):
                cur = None
    open(out, "w").write("\n".join(L) + "\n.end\n")
    return out


def run():
    rep = os.path.join(ROOT, "layout", "lvs")
    os.makedirs(rep, exist_ok=True)
    gds = os.path.join(ROOT, "layout", "gds", TOP + ".gds")
    lay = lvs.extract(gds, TOP, os.path.join(rep, TOP + ".ext.spice"))
    ref = reference(os.path.join(rep, TOP + ".blocks.spice"))
    dig = os.path.join(ROOT, "design", "digital", "build", "rt5w_digital.pwr.v")
    topv = os.path.join(ROOT, "layout", "top", TOP + ".v")
    rpt = os.path.join(rep, TOP + ".lvs.txt")
    tcl = os.path.join(rep, TOP + ".netgen.tcl")
    open(tcl, "w").write(f"""
set lay [readnet spice {lay}]
set ref [readnet spice {ref}]
readnet spice {HD_SPICE} $ref
readnet verilog {dig} $ref
readnet verilog {topv} $ref
lvs "$lay {TOP}" "$ref {TOP}" {lvs.SETUP} {rpt} -json
""")
    r = subprocess.run(["netgen", "-batch", "source", tcl], capture_output=True, text=True, timeout=14400, cwd=rep)
    txt = open(rpt).read() if os.path.exists(rpt) else r.stdout
    fin = re.findall(r"Final result:.*", txt)
    ok = bool(fin) and "match uniquely" in fin[-1] and "do not" not in fin[-1]
    return ok, (fin[-1] if fin else (r.stdout + r.stderr)[-1500:]), rpt


if __name__ == "__main__":
    ok, msg, rpt = run()
    print(f"{TOP}: {'LVS CLEAN' if ok else 'LVS MISMATCH'} - {msg.strip()}  ({os.path.relpath(rpt, ROOT)})")
