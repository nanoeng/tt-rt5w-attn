"""Floorplan data for the drag-and-drop floorplanner and the top-level router.

    python3 design/layout/floorplan.py            -> layout/floorplan/fp_data.json, default_floorplan.json,
                                                      floorplanner.html (self-contained, data embedded)
The floorplanner exports a JSON of the form
    {"tile": {"w": 711.2, "h": 325.36}, "placements": {"xarr/xc00": {"x": .., "y": .., "orient": "N"}, ...}}
(x, y = lower-left corner of the block outline in um, orient N | FN | S | FS), which toplevel.py turns into the GDS."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hier  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
GDS = os.path.join(ROOT, "layout", "gds")
FP = os.path.join(ROOT, "layout", "floorplan")
TT_DEF = os.environ.get("TT_DEF", "/home/claude/ext/tt/tt-support-tools/tech/gf180mcuD/def/analog/tt_analog_2x2.def")
TILE = dict(w=711.2, h=325.36, name="TT gf180mcuD analog 2x2")
CTRL = "u_ctrl"


def tt_pins(path=TT_DEF):
    txt = open(path).read()
    units = int(re.search(r"UNITS DISTANCE MICRONS (\d+)", txt).group(1))
    pins = []
    for m in re.finditer(r"- (\S+) \+ NET \S+.*?\+ LAYER (\S+) \( (-?\d+) (-?\d+) \) \( (-?\d+) (-?\d+) \).*?\+ PLACED \( (-?\d+) (-?\d+) \) (\S+)",
                         txt, re.S):
        name, layer, x0, y0, x1, y1, px, py, o = m.groups()
        x0, y0, x1, y1, px, py = (int(v) / units for v in (x0, y0, x1, y1, px, py))
        pins.append(dict(name=name, layer=layer, x=px + x0, y=py + y0, w=x1 - x0, h=y1 - y0))
    return pins


def block_info(block):
    p = os.path.join(GDS, block + ".json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    ox, oy = d["origin"]
    pins = [dict(net=q["net"], x=round(q["x"] - ox, 3), y=round(q["y"] - oy, 3), side=q["side"], layer=q["layer"])
            for q in d["pins"]]
    return dict(w=round(d["width"], 3), h=round(d["height"], 3), pins=pins, gds=d["gds"],
                devices=d.get("devices"), area=d.get("device_area_um2"))


def ctrl_conn(pins):
    """Hardened macro port -> top-level net (TT pin names for the digital pins, analog-macro nets otherwise)."""
    conn = {}
    for p in pins:
        n = p["net"]
        m = re.match(r"(\w+)\[(\d+)\]$", n)
        base, k = (m.group(1), int(m.group(2))) if m else (n, None)
        if base in ("ui_in", "uo_out", "uio_in", "uio_out", "uio_oe") or n in ("clk", "rst_n", "ena"):
            conn[n] = n
        elif base == "q_code":
            conn[n] = f"q{k // 4}_{k % 4}"
        elif base == "k_code":
            conn[n] = f"k{k // 4}_{k % 4}"
        elif base == "adc_ch":
            conn[n] = f"adc_ch{k}"
        elif base == "adc_dac":
            conn[n] = f"dac{k}"
        elif n == "adc_cmp":
            conn[n] = "cmp"
        elif base in ("pump_up", "pump_dn"):
            if k:                                     # row 0 has no pump
                conn[n] = f"{base}{k}"
        elif base == "wsel":
            conn[n] = f"wsel{k}"
        elif n in ("bias_en", "adc_rst", "adc_lat", "vb_probe_en"):
            conn[n] = n
    return conn


def ctrl_info():
    p = os.path.join(GDS, "rt5w_ctrl.json")
    if os.path.exists(p):
        d = json.load(open(p))
        return dict(w=d["width"], h=d["height"], pins=d["pins"], gds=d["gds"], devices=d.get("cells"), area=None,
                    digital=True)
    return dict(w=180.0, h=120.0, pins=[], gds=None, devices=None, area=None, digital=True, placeholder=True)


def default_placement(insts, blocks, tile, gap=4.0):
    """Shelf packing, biggest first, in the tile (may overflow to the right: the floorplanner shows it)."""
    order = sorted(insts, key=lambda i: -blocks[i["block"]]["h"] * blocks[i["block"]]["w"])
    x = y = shelf_h = 0.0
    margin = 16.0
    pl = {}
    for i in order:
        b = blocks[i["block"]]
        if x + b["w"] > tile["w"] - margin and x > margin:
            x, y, shelf_h = margin, y + shelf_h + gap, 0.0
        if x == 0:
            x = margin
        pl[i["path"]] = dict(x=round(x, 1), y=round(y + margin, 1), orient="N")
        x += b["w"] + gap
        shelf_h = max(shelf_h, b["h"])
    return pl


def build():
    insts, top_ports = hier.flatten()
    blocks = {}
    for i in insts:
        if i["block"] not in blocks:
            info = block_info(i["block"])
            if info is None:
                raise FileNotFoundError(f"no layout for {i['block']}: run design/layout/blockgen.py first")
            blocks[i["block"]] = info
    blocks["rt5w_ctrl"] = ctrl_info()
    insts = insts + [dict(path=CTRL, block="rt5w_ctrl", conn=ctrl_conn(blocks["rt5w_ctrl"]["pins"]))]
    data = dict(tile=TILE, tt_pins=tt_pins(), blocks=blocks, instances=insts, top_ports=top_ports)
    os.makedirs(FP, exist_ok=True)
    json.dump(data, open(os.path.join(FP, "fp_data.json"), "w"), indent=1)
    fp = dict(tile=dict(w=TILE["w"], h=TILE["h"]), placements=default_placement(insts, blocks, TILE))
    json.dump(fp, open(os.path.join(FP, "default_floorplan.json"), "w"), indent=1)
    study = dict(w=1422.4, h=900.0)               # a tile the current blocks fit into, to exercise the full flow
    json.dump(dict(tile=study, placements=default_placement(insts, blocks, study, gap=20.0)),
              open(os.path.join(FP, "study_floorplan.json"), "w"), indent=1)
    tpl = open(os.path.join(HERE, "floorplanner_template.html")).read()
    html = tpl.replace("/*__FP_DATA__*/null", json.dumps(data)).replace("/*__FP_DEFAULT__*/null", json.dumps(fp))
    open(os.path.join(FP, "floorplanner.html"), "w").write(html)
    tot = sum(blocks[i["block"]]["w"] * blocks[i["block"]]["h"] for i in insts)
    return data, fp, tot


if __name__ == "__main__":
    data, fp, tot = build()
    t = data["tile"]
    print(f"{len(data['instances'])} instances, block area {tot:.0f} um2 = {tot / (t['w'] * t['h']):.2f} x the tile "
          f"({t['w']} x {t['h']} um); {len(data['tt_pins'])} TT pins -> layout/floorplan/floorplanner.html")
