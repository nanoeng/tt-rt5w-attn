"""PNG snapshot of a GDS (KLayout LayoutView, PDK layer properties if present)."""
import os
import sys

import klayout.db as pya
import klayout.lay as lay

PDK_ROOT = os.environ.get("PDK_ROOT", "/home/claude/ext/pdk")
LYP = os.path.join(PDK_ROOT, os.environ.get("PDK", "sky130A"), "libs.tech", "klayout", "tech", "sky130A.lyp")


def render(gds, png, w=1600, h=900):
    lv = lay.LayoutView()
    lv.load_layout(gds, True)
    if os.path.exists(LYP):
        lv.load_layer_props(LYP)
    lv.max_hier()
    lv.zoom_fit()
    lv.save_image(png, w, h)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], *(int(a) for a in sys.argv[3:5]))
