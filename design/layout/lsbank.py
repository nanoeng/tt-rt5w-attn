"""Level-shifter bank from the sky130_fd_sc_hvl library cells (skywater-pdk-libs-sky130_fd_sc_hvl 4fd4f85):
lsbuflv2hv_1 (1.8 V -> 3.3 V, 10.56 x 8.14 um) and lsbufhv2lv_1 (3.3 V -> 1.8 V, 8.16 x 8.14 um).

Two rows, row 1 mirrored onto row 0 (shared VNB rail at y = 8.14). Row 0's pins leave through the bottom edge, row 1's
through the top edge, on met2 verticals (the cells use no met2) ending in a via2 + met3 pad (the pin).
Power: LVPWR met1 stops 0.07 um short of each cell edge -> bridged at every abutment; VGND + VNB = vss,
VPWR + VPB = vdd (3.3 V), LVPWR = vddl (1.8 V). The rails run into a power column at the left with met2 straps,
each strap carries a via2/via3 stack to a met4 pin.

    USER=$USER pixi run -e layout python design/layout/lsbank.py      -> layout/gds/rt5w_lsbank.gds/.json,
                                                                         netlist/rt5w_lsbank.spice
"""
import json
import os
import sys

import klayout.db as pya

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "design"), os.path.join(ROOT, "design", "blocks")]
import pdkcells as P  # noqa: E402
from blockgen import Canvas  # noqa: E402

HVL = os.path.join(ROOT, "layout", "gds")
UP, DN = "sky130_fd_sc_hvl__lsbuflv2hv_1", "sky130_fd_sc_hvl__lsbufhv2lv_1"
WIDTH = {UP: 10560, DN: 8160}
H = 8140
# li1 pin rectangles (LEF) and the met1-free y-window used for the contact (between rails)
PIN = {UP: {"A": (2495, 1530, 2805, 2200, (1700, 2050)), "X": (10120, 4405, 10450, 6055, (5300, 5900))},
       DN: {"A": (630, 4870, 1300, 5200, (4950, 5150)), "X": (3485, 735, 3960, 3245, (1500, 2300))}}
RAILS = [("vss", -115, 625), ("vddl", 3020, 3305), ("vdd", 3445, 4695), ("vss", 7515, 8255)]   # merged per net
STRAP_X = {"vddl": -1200, "vdd": -2400, "vss": -3600}
STRAP_W = 600
PIN_OUT = 1300                  # met2 runs this far beyond the row's outer rail


def mirror_y(y, row):
    return y if row == 0 else 2 * H - y


OFFSET = 5280                  # v2: row 1 shifted by half a cell, so A (up) and X (down) met2 lines never cross


def build(cells, name="rt5w_lsbank", v2=True):
    """cells: list of (kind 'up'|'dn', input net, output net), in slot order. v2 (6x2 floorplan): slot s goes to
    row s % 2, column s // 2; row 1 is offset by half a cell; every A pin leaves through the top edge and every X pin
    through the bottom edge on met2 (row 0's A crosses row 1 at local x 7.93 um, row 1's X crosses row 0 at local
    x 5.005 um: no metal of the crossed cell there). v1: rows of consecutive cells, row 0 down, row 1 up."""
    ly = pya.Layout()
    ly.dbu = 0.001
    for c in (UP, DN):
        ly.read(os.path.join(HVL, c + ".gds"))
    top = ly.create_cell(name)
    cv = Canvas(ly, top)
    if v2:
        rows = [cells[0::2], cells[1::2]]
    else:
        n0 = len(cells) // 2     # row 1 gets the extra cell: the down-shifter (last) then has no cell below it
        rows = [cells[:n0], cells[n0:]]   # (a mirrored lsbufhv2lv over an lsbuflv2hv violates hvi.5 / hvntm.1)
    pins, xmax = [], 0
    x_start = [0, OFFSET if v2 else 0]
    for r, row in enumerate(rows):
        x = x_start[r]
        for k, (kind, nin, nout) in enumerate(row):
            cell = UP if kind == "up" else DN
            t = pya.Trans(x, 0) if r == 0 else pya.Trans(pya.Trans.M0, x, 2 * H)
            top.insert(pya.CellInstArray(ly.cell(cell).cell_index(), t))
            if k:                                                   # LVPWR bridge at the abutment
                cv.box(P.L_M1, x - 100, mirror_y(3020, r), x + 100, mirror_y(3305, r), "vddl")
            for pin, net in (("A", nin), ("X", nout)):
                x0, y0, x1, y1, (wy0, wy1) = PIN[cell][pin]
                cx = x + (x0 + x1) // 2
                cy = mirror_y((wy0 + wy1) // 2, r)
                cv.box(P.L_MCON, cx - 85, cy - 85, cx + 85, cy + 85)
                cv.box(P.L_M1, cx - 145, cy - 175, cx + 145, cy + 175, net)
                cv.via(P.L_V1, [P.L_M1, P.L_M2], cx, cy, net=net)
                if v2:
                    ye = 2 * H + PIN_OUT if pin == "A" else -PIN_OUT
                    cv.vwire(P.L_M2, cx, cy, ye, w=200, net=net)
                    cv.label(P.L_M2, net, cx, ye + (-100 if pin == "A" else 100))
                    pins.append(dict(net=net, layer="met2", x=cx / 1000, y=ye / 1000, side="T" if pin == "A" else "B",
                                     domain="1v8" if (pin == "A") == (kind == "up") else "3v3"))
                    continue
                ye = -PIN_OUT if r == 0 else 2 * H + PIN_OUT
                cv.vwire(P.L_M2, cx, cy, ye, w=200, net=net)
                cv.via(P.L_V2, [P.L_M2, P.L_M3], cx, ye, net=net, big=True)
                cv.label(P.L_M3, net, cx, ye)
                pins.append(dict(net=net, layer="met3", x=cx / 1000, y=ye / 1000, side="B" if r == 0 else "T",
                                 domain="1v8" if (pin == "A") == (kind == "up") else "3v3"))
            x += WIDTH[cell]
        xmax = max(xmax, x)
    # power column: rails extended to their straps, straps with via stacks to met4 pins
    for r in (0, 1):
        for net, y0, y1 in RAILS:
            a, b = sorted((mirror_y(y0, r), mirror_y(y1, r)))
            cv.box(P.L_M1, STRAP_X[net] - STRAP_W // 2, a, x_start[r] + (0 if net != "vddl" else 70), b, net)
            for xx in range(STRAP_X[net], STRAP_X[net] + 1, 1000):
                cv.via(P.L_V1, [P.L_M1, P.L_M2], xx, 5 * round((a + b) / 10), net=net, vertical=False)   # 5 nm grid
    ylo, yhi = -PIN_OUT - 700, 2 * H + PIN_OUT + 700
    for net, xs in STRAP_X.items():
        cv.box(P.L_M2, xs - STRAP_W // 2, -400, xs + STRAP_W // 2, 2 * H + 400, net)
        for yy in (H - 2000, H + 2000):
            cv.via(P.L_V2, [P.L_M2, P.L_M3], xs, yy, net=net, big=True)
            cv.via(P.L_V3, [P.L_M3, P.L_M4], xs, yy, net=net, big=True)
        cv.box(P.L_M4, xs - 300, ylo + 500, xs + 300, yhi - 500, net)
        cv.via(P.L_V3, [P.L_M3, P.L_M4], xs, ylo + 900, net=net, big=True)     # met3 landing pad at the bottom end
        cv.label(P.L_M3, net, xs, ylo + 900)
        cv.label(P.L_M4, net, xs, H)
        pins.append(dict(net=net, layer="met4", x=xs / 1000, y=H / 1000, side="L", width=0.6))
    shorts = cv.check_shorts()
    xmin = STRAP_X["vss"] - STRAP_W // 2 - 500
    out = os.path.join(ROOT, "layout", "gds", name + ".gds")
    ly.write(out)
    info = dict(block=name, width=(xmax - xmin) / 1000, height=(yhi - ylo) / 1000, origin=[xmin / 1000, ylo / 1000],
                shorts=len(shorts), cells=len(cells), pins=pins)
    json.dump(info, open(out.replace(".gds", ".json"), "w"), indent=1)
    # reference netlist for LVS (library cells from their CDL, devices as sky130_fd_pr subckts)
    ports = [n for _, a, b in cells for n in (a, b)] + ["vdd", "vss", "vddl"]
    L = [open(os.path.join(ROOT, "netlist", c + ".spice")).read() for c in (UP, DN)]
    L.append(f".subckt {name} " + " ".join(ports))
    for k, (kind, a, b) in enumerate(cells):
        L.append(f"Xls{k} {a} vddl vss vss vdd vdd {b} {UP if kind == 'up' else DN}")
    L.append(".ends")
    open(os.path.join(ROOT, "netlist", name + ".spice"), "w").write("\n".join(L) + "\n")
    return info


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(ROOT, "design", "blocks"))
    # 74 up-shifters only: lsbufhv2lv_1 carries a magic hvi.5 / hvntm.1 error inside the cell next to its X pin, which
    # any pin contact exposes (TT precheck = hierarchical magic DRC) -> the single down-shifter is rt5w_lsdn (blockgen)
    from topflow import bank_order, LS_IN
    order = bank_order()                       # slot order = destination x (6x2 floorplan); 30 crossings since hvif
    assert sorted(order) == sorted(LS_IN)
    cells = [("up", f"{s}_lv", s) for s in order]
    print(build(cells))
