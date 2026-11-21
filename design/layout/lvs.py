"""LVS of a generated block (or the top) against its xschem netlist: magic extraction + netgen compare.
    pixi run -e pd python design/layout/lvs.py rt5w_keycell
Netgen's gf180mcuD setup merges series/parallel resistors and parallel transistors (fingers, m), so the serpentine
resistors and the per-finger pcells compare against the schematic's single devices."""
import os
import re
import subprocess
import sys
import tempfile

PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/ext/pdk")
PDK = os.environ.get("PDK", "sky130A")
RC = os.path.join(PDK_ROOT, PDK, "libs.tech", "magic", f"{PDK}.magicrc")
SETUP = os.path.join(PDK_ROOT, PDK, "libs.tech", "netgen", f"{PDK}_setup.tcl")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def extract(gds, top, out):
    env = dict(os.environ, PDK_ROOT=PDK_ROOT)
    r = subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", RC, os.path.join(HERE, "magic_ext.tcl"),
                        os.path.abspath(gds), top, os.path.abspath(out)], capture_output=True, text=True, env=env,
                       cwd=os.path.dirname(os.path.abspath(out)), timeout=7200)
    if not os.path.exists(out):
        raise RuntimeError(r.stdout[-2000:] + r.stderr[-2000:])
    return out


def schematic_netlist(block, out):
    """xschem netlist -> netgen input: keep the .subckt (and any children), drop the analysis-only lines."""
    txt = open(os.path.join(ROOT, "netlist", block + ".spice")).read()
    txt = "\n".join(l for l in txt.splitlines() if not l.startswith(("**", ".GLOBAL", ".end ")) and l != ".end")
    open(out, "w").write(txt + "\n.end\n")
    return out


def run(block, gds=None):
    gds = gds or os.path.join(ROOT, "layout", "gds", block + ".gds")
    rep_dir = os.path.join(ROOT, "layout", "lvs")
    os.makedirs(rep_dir, exist_ok=True)
    lay = extract(gds, block, os.path.join(rep_dir, block + ".ext.spice"))
    sch = schematic_netlist(block, os.path.join(rep_dir, block + ".sch.spice"))
    rpt = os.path.join(rep_dir, block + ".lvs.txt")
    r = subprocess.run(["netgen", "-batch", "lvs", f"{lay} {block}", f"{sch} {block}", SETUP, rpt, "-json"],
                       capture_output=True, text=True, timeout=7200, cwd=rep_dir)
    txt = open(rpt).read() if os.path.exists(rpt) else r.stdout
    fin = re.findall(r"Final result:.*", txt)
    ok = bool(fin) and ("match uniquely" in fin[-1] or "Circuits match" in fin[-1]) and "do not" not in fin[-1]
    final = re.findall(r"(Final result:.*|Netlists do not match.*|Netlists match.*)", txt)
    return ok, final[-1] if final else r.stdout[-400:], rpt


if __name__ == "__main__":
    for b in sys.argv[1:]:
        ok, msg, rpt = run(b)
        print(f"{b}: {'LVS CLEAN' if ok else 'LVS MISMATCH'} - {msg.strip()}  ({os.path.relpath(rpt, ROOT)})")
