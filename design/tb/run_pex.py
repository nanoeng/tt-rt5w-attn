"""Schematic vs post-layout (C-only PEX, design/layout/pex.py) for one test at one corner.
    RT5W_NETLIST=netlist_pex python design/tb/run_pex.py <keycell|softmax|readout|chain> <tt|ss|ff>
Writes results/pex/<mode>_<test>_<corner>.json (mode = sch | pex from RT5W_NETLIST)."""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE), os.path.join(os.path.dirname(HERE), "blocks")]
ROOT = os.path.dirname(os.path.dirname(HERE))
T = {"tt": 27.0, "ss": -40.0, "ff": 125.0}


def jsonable(o):
    if isinstance(o, dict):
        return {k: jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return o


def main(test, corner):
    mode = "pex" if os.environ.get("RT5W_NETLIST", "netlist") != "netlist" else "sch"
    temp = T[corner]
    t0 = time.time()
    if test == "keycell":
        import tb_keycell
        r = tb_keycell.run(corner, temp)
        out = dict(gain0=r["gain0"], nUT_fit=r["nUT_fit"], shape_err_max=float(np.abs(r["shape_err"]).max()))
    elif test == "softmax":
        import tb_softmax
        r = tb_softmax.run(corner, temp)
        out = dict(err_raw=max(x["err_lsb"] for x in r["rows"]), err_cal=r["err_cal"], x_scale=r["x_scale"],
                   vb_slope=r["vb_slope"], vb_off=r["vb_off"])
    elif test == "readout":
        import tb_readout
        r = tb_readout.run(corner, temp)
        out = dict(codes=r["codes"], got=r["got"], model=r["model"], err_model=r["err_model"], err_ideal=r["err_ideal"])
    elif test == "chain":
        import tb_chain
        out = dict(vectors=[])
        for q, k, ks in tb_chain.VECTORS:
            r = tb_chain.run(q, k, ks, corner, temp)
            out["vectors"].append(dict(q=q, ks=ks, model=r["model"], spice=r["spice"], err=r["err"]))
        out["err"] = max(v["err"] for v in out["vectors"])
    else:
        raise ValueError(test)
    out.update(mode=mode, test=test, corner=corner, temp=temp, seconds=round(time.time() - t0, 1))
    d = os.path.join(ROOT, "results", "pex")
    os.makedirs(d, exist_ok=True)
    json.dump(jsonable(out), open(os.path.join(d, f"{mode}_{test}_{corner}.json"), "w"), indent=1)
    print(mode, test, corner, {k: v for k, v in jsonable(out).items() if k not in ("vectors",)})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
