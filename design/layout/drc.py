"""DRC of a block / top GDS with magic's sky130A rule set (drc(full), mask hints, euclidean -- the TinyTapeout precheck settings), summarised by rule.

The KLayout runset in open_pdks e8daeda needs KLayout >= 0.30 *with Ruby* (it uses EdgePairs#interacting and
evaluate_nets); the conda KLayout here has no Ruby and Ubuntu's 0.28.16 is too old, so the batch DRC uses magic, the
other sign-off engine shipped with the PDK (TinyTapeout's precheck re-runs the KLayout deck on the final GDS).
    pixi run -e pd python design/layout/drc.py layout/gds/rt5w_keycell.gds [topcell]
"""
import os
import re
import subprocess
import sys

PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/ext/pdk")
PDK = os.environ.get("PDK", "sky130A")
RC = os.path.join(PDK_ROOT, PDK, "libs.tech", "magic", f"{PDK}.magicrc")
TCL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "magic_drc.tcl")


def run(gds, top=None, report=None):
    gds = os.path.abspath(gds)
    if not os.path.exists(gds):
        raise FileNotFoundError(gds)
    top = top or os.path.splitext(os.path.basename(gds))[0]
    report = os.path.abspath(report or os.path.splitext(gds)[0] + ".drc.txt")
    env = dict(os.environ, PDK_ROOT=PDK_ROOT)
    r = subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", RC, TCL, gds, top, report],
                       capture_output=True, text=True, env=env, cwd=os.path.dirname(gds), timeout=7200)
    if not os.path.exists(report):
        raise RuntimeError(r.stdout[-2000:] + r.stderr[-2000:])
    rules = []
    total = 0
    for line in open(report):
        if line.startswith("SCALE"):
            continue
        if line.startswith("TOTAL"):
            total = int(line.split()[1])
        elif line.strip():
            n, why, *rest = line.rstrip("\n").split("\t")
            rules.append((int(n), why, rest[0] if rest else ""))
    return total, rules


if __name__ == "__main__":
    total, rules = run(sys.argv[1], *(sys.argv[2:3]))
    print(f"{sys.argv[1]}: {total} DRC errors (magic, drc(full), as TT precheck) in {len(rules)} rules")
    for n, why, where in sorted(rules, reverse=True):
        print(f"  {n:5d}  {why}   e.g. {where[:80]}")
