"""Write, netlist, verify and render every block schematic.  Run in the pixi 'pd' environment:
    pixi run -e pd python design/capture.py [block ...]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "blocks"))
import schem  # noqa: E402
import sim  # noqa: E402
from blocks import array, bias, idac, kscale, lshift, readout, softmax, top, vbbuf  # noqa: E402

BLOCKS = {"rt5w_idac4": idac.idac4, "rt5w_coldiode": array.coldiode, "rt5w_keycell": array.keycell,
          "rt5w_trimcell": array.trimcell, "rt5w_softmax": softmax.softmax,
          "rt5w_bias": bias.bias, "rt5w_readout": readout.readout,
          "rt5w_vbbuf": vbbuf.vbbuf, "rt5w_kscale": kscale.kscale, "rt5w_pumpinv": array.pumpinv, "rt5w_array": array.array_top,
          "rt5w_lsup": lshift.lsup, "rt5w_lsdn": lshift.lsdn, "rt5w_lsbank8": lshift.lsbank, "rt5w_analog": top.analog_top}


def main(names):
    ok = True
    for name in names or BLOCKS:
        s = BLOCKS[name]()
        s.write()
        path = schem.netlist(name)
        order = sim.ports(name)
        s.write_symbol(order=order)              # symbol pins in the .subckt order
        problems = schem.verify(s, path)
        svg = schem.render_svg(name)
        n_lab = len(s._labels)
        print(f"{name}: {len(s.insts)} devices, {len(s._wires)} wires, {n_lab} labels -> {path}; "
              f"{'connectivity OK' if not problems else 'CONNECTIVITY ERRORS'}; svg {os.path.getsize(svg) if os.path.exists(svg) else 0} B")
        for p in problems:
            print("   ", p)
        ok &= not problems
    return ok


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1:]) else 1)
