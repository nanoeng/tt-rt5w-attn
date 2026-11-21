"""Flatten the xschem hierarchy of rt5w_analog down to leaf-block instances (the blocks that have a generated layout).
    instances, top_ports = flatten("rt5w_analog")
Each instance: dict(path='xarr/xc00', block='rt5w_keycell', conn={port: top-level net}). Nets internal to a
hierarchical block get the instance path as prefix (xarr/dcol0); supplies stay vdd/vss."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NETLIST = os.path.join(ROOT, "netlist")
LEAVES = ["rt5w_idac4", "rt5w_coldiode", "rt5w_keycell", "rt5w_trimcell", "rt5w_pumpinv", "rt5w_kscale",
          "rt5w_softmax", "rt5w_bias", "rt5w_readout", "rt5w_vbbuf"]
GLOBAL = ("vdd", "vss")


def read_subckts(path):
    txt = open(path).read().replace("\n+", " ")
    subs = {}
    for m in re.finditer(r"^\.subckt (\S+) (.*?)$(.*?)^\.ends", txt, re.M | re.S):
        name, ports, body = m.group(1), [w for w in m.group(2).split() if "=" not in w], m.group(3)
        insts = []
        for line in body.splitlines():
            t = line.split()
            if not t or not t[0].lower().startswith("x"):
                continue
            first = next((k for k, w in enumerate(t) if "=" in w), len(t))
            insts.append((t[0], t[first - 1], t[1:first - 1]))
        subs[name] = (ports, insts)
    return subs


def flatten(top="rt5w_analog"):
    subs = read_subckts(os.path.join(NETLIST, top + ".spice"))
    out = []

    def walk(cell, prefix, netmap):
        ports, insts = subs[cell]
        for iname, sub, nets in insts:
            mapped = [n if n in GLOBAL else netmap.get(n, (prefix + "/" + n) if prefix else n) for n in nets]
            path = (prefix + "/" + iname) if prefix else iname
            if sub in LEAVES:
                sports = subs[sub][0]
                out.append(dict(path=path, block=sub, conn=dict(zip(sports, mapped))))
            elif sub in subs:
                walk(sub, path, dict(zip(subs[sub][0], mapped)))
            else:
                raise ValueError(f"{cell}/{iname}: {sub} is neither a leaf block nor a subckt")

    top_ports = subs[top][0]
    walk(top, "", {p: p for p in top_ports})
    return out, top_ports


if __name__ == "__main__":
    inst, ports = flatten()
    from collections import Counter
    print(len(inst), "leaf instances:", dict(Counter(i["block"] for i in inst)))
    print("top ports:", len(ports))
