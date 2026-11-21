"""Harden the RT5W digital macro: yosys synthesis -> OpenROAD place & route -> KLayout DEF+LEF -> GDS, plus the pin
JSON the floorplanner / top-level router read (layout/gds/rt5w_ctrl.json).
    pixi run -e openroad python design/digital/harden.py      (yosys from PATH, OpenROAD from the 'openroad' env)"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/ext/pdk")
PDK = os.environ.get("PDK", "sky130A")
SC = os.path.join(PDK_ROOT, PDK, "libs.ref", "sky130_fd_sc_hd")
LIB = os.path.join(SC, "lib", "sky130_fd_sc_hd__tt_025C_1v80.lib")
B = os.path.join(HERE, "build")
DIE = (float(os.environ.get("DIE_W", 160)), float(os.environ.get("DIE_H", 120)))
DENS = os.environ.get("PLACE_DENSITY", "0.80")


def sh(cmd, log, env=None):
    with open(os.path.join(B, log), "w") as f:
        r = subprocess.run(cmd, cwd=HERE, stdout=f, stderr=subprocess.STDOUT, env=env, timeout=7200)
    if r.returncode:
        raise RuntimeError(f"{cmd[0]} failed, see {os.path.join(B, log)}")


def def_pins(path):
    txt = open(path).read()
    units = int(re.search(r"UNITS DISTANCE MICRONS (\d+)", txt).group(1))
    die = [int(v) / units for v in re.search(r"DIEAREA \( (\d+) (\d+) \) \( (\d+) (\d+) \)", txt).groups()]
    pins = []
    for m in re.finditer(r"- (\S+) \+ NET (\S+).*?\+ LAYER (\S+) \( (-?\d+) (-?\d+) \) \( (-?\d+) (-?\d+) \).*?\+ PLACED \( (-?\d+) (-?\d+) \)",
                         txt, re.S):
        name, net, layer, *v = m.groups()
        name = name.replace("\\[", "[").replace("\\]", "]")
        x0, y0, x1, y1, px, py = (int(a) / units for a in v)
        side = "L" if px < die[2] / 2 else "R"
        pins.append(dict(net=name, layer=layer, x=px if side == "L" else die[2], y=py + (y0 + y1) / 2, side=side))
    # supply access: the Metal3 sides of the core ring reach the left/right core edge; expose their ends
    sn = txt[txt.index("SPECIALNETS"):txt.index("END SPECIALNETS")]
    for net in ("VPWR", "VGND"):
        body = sn[sn.index(f"- {net} "):]
        body = body[:body.index(";")]
        for x0, y0, x1, y1 in re.findall(r"met3 \d+ \+ SHAPE STRIPE \( (\d+) (\d+) \) \( (\d+) (\d+) \)", body):
            if y0 == y1 and (int(x1) - int(x0)) / units > 0.8 * die[2]:
                y = int(y0) / units
                nn = {"VPWR": "vdpwr", "VGND": "vss"}[net]
                pins.append(dict(net=nn, layer="met3", x=0.0, y=y, side="L", ring=True))
                pins.append(dict(net=nn, layer="met3", x=die[2], y=y, side="R", ring=True))
    return die, pins


def main():
    os.makedirs(B, exist_ok=True)
    ys = open(os.path.join(HERE, "synth.ys")).read().replace("LIB", LIB)
    open(os.path.join(B, "synth.ys"), "w").write(ys)
    sh(["yosys", "-q", "-s", os.path.join(B, "synth.ys")], "yosys.log")
    env = dict(os.environ, PDK_ROOT=PDK_ROOT, PDK=PDK, DIE_W=str(DIE[0]), DIE_H=str(DIE[1]), PLACE_DENSITY=DENS)
    sh(["openroad", "-exit", "-no_init", os.path.join(HERE, "pnr.tcl")], "openroad.log", env=env)
    sh([sys.executable, os.path.join(HERE, "pwrv_fix.py"), os.path.join(B, "rt5w_digital.pwr.v")], "pwrv_fix.log")
    # GDS: KLayout reads the DEF with the tech + cell LEFs and merges the standard-cell GDS
    sh([os.environ.get("KLAYOUT_PY", "/home/claude/rt5w_tt/.pixi/envs/layout/bin/python"), os.path.join(HERE, "def2gds.py"), os.path.join(B, "rt5w_digital.def"),
        os.path.join(ROOT, "layout", "gds", "rt5w_ctrl.gds")], "def2gds.log")
    die, pins = def_pins(os.path.join(B, "rt5w_digital.def"))
    stat = open(os.path.join(B, "synth_stat.txt")).read()
    cells = int(re.search(r"Number of cells:\s+(\d+)", stat).group(1))
    info = dict(block="rt5w_ctrl", gds="layout/gds/rt5w_ctrl.gds", width=die[2], height=die[3], origin=[0.0, 0.0],
                cells=cells, pins=pins, timing=[l.strip() for l in open(os.path.join(B, "openroad.log")) if l.startswith(("worst slack", "tns"))],
                route_drc=sum(1 for l in open(os.path.join(B, "route_drc.rpt"))) if os.path.exists(os.path.join(B, "route_drc.rpt")) else 0)
    json.dump(info, open(os.path.join(ROOT, "layout", "gds", "rt5w_ctrl.json"), "w"), indent=1)
    print(f"rt5w_digital hardened: {cells} cells, die {die[2]:.0f} x {die[3]:.0f} um, {len(pins)} pins; "
          f"timing {info['timing']}; detailed-route DRC report lines {info['route_drc']}")


if __name__ == "__main__":
    main()
