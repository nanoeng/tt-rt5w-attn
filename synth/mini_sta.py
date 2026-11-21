"""Minimal liberty-table STA estimate (register-to-register / input-to-register), no wire RC, ideal clock.
import sys; sys.setrecursionlimit(100000)
Usage: python3 mini_sta.py <liberty> <gate_netlist.v> <top> <period_ns>"""
import re, sys, collections
import numpy as np

lib_txt = open(sys.argv[1]).read()
net_txt = open(sys.argv[2]).read()
TOP, PERIOD = sys.argv[3], float(sys.argv[4])


def blocks(txt, start=0):
    """yield (header, body) for top-level brace groups in txt"""
    i, n = start, len(txt)
    while True:
        j = txt.find("{", i)
        if j < 0:
            return
        hdr_start = txt.rfind(";", i, j)
        hdr_start = max(hdr_start, txt.rfind("}", i, j)) + 1
        depth, k = 1, j + 1
        while depth and k < n:
            c = txt[k]
            depth += (c == "{") - (c == "}")
            k += 1
        yield txt[hdr_start:j].split("}")[-1].split("*/")[-1].strip(), txt[j + 1:k - 1]
        i = k


def nums(s):
    return [float(v) for v in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)]


def table(body, kind):
    m = re.search(kind + r"\s*\([^)]*\)\s*\{(.*?)\}", body, re.S)
    if not m:
        return None
    b = m.group(1)
    i1 = nums(re.search(r"index_1\s*\(\"([^\"]*)\"", b).group(1))
    m2 = re.search(r"index_2\s*\(\"([^\"]*)\"", b)
    i2 = nums(m2.group(1)) if m2 else [0.0, 1.0]
    vals = np.array(nums(re.search(r"values\s*\((.*?)\)\s*;", b, re.S).group(1)))
    vals = vals.reshape(len(i1), len(i2)) if m2 else np.repeat(vals.reshape(len(i1), 1), 2, axis=1)
    return i1, i2, vals


def lookup(t, slew, load):
    i1, i2, v = t
    a = np.interp(slew, i1, np.arange(len(i1))); b = np.interp(load, i2, np.arange(len(i2)))
    ia, ib = int(min(a, len(i1) - 2)), int(min(b, len(i2) - 2))
    fa, fb = a - ia, b - ib
    return (v[ia, ib] * (1 - fa) * (1 - fb) + v[ia + 1, ib] * fa * (1 - fb) + v[ia, ib + 1] * (1 - fa) * fb + v[ia + 1, ib + 1] * fa * fb)


cells = {}
lib_body = next(blocks(lib_txt))[1]
for hdr, body in blocks(lib_body):
    m = re.search(r"cell\s*\(\s*\"?(\w+)\"?\s*\)\s*$", hdr)
    if not m:
        continue
    pins, arcs, seq = {}, [], bool(re.search(r"\b(ff|latch)\s*\(", body))
    for ph, pb in blocks(body):
        pm = re.search(r"\bpin\s*\(\s*\"?(\w+)\"?\s*\)\s*$", ph)
        if not pm:
            continue
        pn = pm.group(1)
        d = re.search(r"direction\s*:\s*\"?(\w+)", pb)
        cap = re.search(r"\bcapacitance\s*:\s*([\d.eE+-]+)", pb)
        pins[pn] = dict(dir=d.group(1) if d else "input", cap=float(cap.group(1)) if cap else 0.0)
        for th, tb in blocks(pb):
            if not th.startswith("timing"):
                continue
            rp = re.search(r"related_pin\s*:\s*\"([\w]+)\"", tb)
            tt = re.search(r"timing_type\s*:\s*\"?(\w+)", tb)
            ttype = tt.group(1) if tt else "combinational"
            if ttype.startswith("setup"):
                rt = table(tb, "rise_constraint")
                arcs.append(dict(to=pn, frm=rp.group(1), type="setup", setup=float(rt[2].max()) if rt else 0.3))
                continue
            if ttype.startswith(("hold", "recovery", "removal", "min_pulse", "clear", "preset", "skew", "non_seq")):
                continue
            arcs.append(dict(to=pn, frm=rp.group(1) if rp else None, type=ttype,
                             rise=table(tb, "cell_rise"), fall=table(tb, "cell_fall"),
                             trise=table(tb, "rise_transition"), tfall=table(tb, "fall_transition")))
    cells[m.group(1)] = dict(pins=pins, arcs=arcs, seq=seq)

# ---- netlist
mod = re.search(r"module\s+" + TOP + r"\b(.*?)endmodule", net_txt, re.S).group(1)
insts = []
for m in re.finditer(r"(gf180mcu_\w+)\s+(\S+)\s*\((.*?)\);", mod, re.S):
    conns = dict(re.findall(r"\.(\w+)\s*\(\s*([^()]*?)\s*\)", m.group(3)))
    insts.append((m.group(1), m.group(2), {k: v.strip() for k, v in conns.items()}))
# alias assigns
alias = dict((a.strip(), b.strip()) for a, b in re.findall(r"assign\s+(.*?)=\s*(.*?);", mod))
def canon(n):
    seen = 0
    while n in alias and seen < 50:
        n = alias[n]; seen += 1
    return n

load = collections.defaultdict(float); sinks = collections.defaultdict(list); driver = {}
for ct, nm, cn in insts:
    c = cells[ct]
    for p, net in cn.items():
        net = canon(net)
        if c["pins"].get(p, {}).get("dir") == "output":
            driver[net] = (nm, ct, p)
        else:
            load[net] += c["pins"].get(p, {}).get("cap", 0.0) + 0.005   # + 5 fF wire per sink (estimate)
            sinks[net].append((nm, ct, p))

arr = {}      # net -> (arrival ns, slew ns)
IN_SLEW = 0.3
order = {nm: (ct, cn) for ct, nm, cn in insts}
# sources: flop outputs (clk->Q) and primary inputs (0)
def net_arrival(net, stack=()):
    net = canon(net)
    if net in arr:
        return arr[net]
    if net not in driver or net in stack:
        arr[net] = (0.0, IN_SLEW); return arr[net]
    nm, ct, p = driver[net]
    c = cells[ct]; cn = order[nm][1]
    best = (0.0, IN_SLEW)
    for a in c["arcs"]:
        if a["to"] != p or a["type"] == "setup" or a.get("rise") is None:
            continue
        if c["seq"] and a["type"].startswith(("rising", "falling")):
            t_in, s_in = 0.0, IN_SLEW                     # clock edge at t = 0
        elif c["seq"]:
            continue                                      # async set/reset arcs ignored
        else:
            t_in, s_in = net_arrival(cn.get(a["frm"], "1'b0"), stack + (net,))
        L = load[net]
        d = max(lookup(a["rise"], s_in, L), lookup(a["fall"], s_in, L))
        s = max(lookup(a["trise"], s_in, L), lookup(a["tfall"], s_in, L)) if a["trise"] else IN_SLEW
        if t_in + d > best[0]:
            best = (t_in + d, s)
    arr[net] = best
    return best

worst = []
for ct, nm, cn in insts:
    c = cells[ct]
    if not c["seq"]:
        continue
    for a in c["arcs"]:
        if a["type"] == "setup" and a["to"] in cn:
            t, s = net_arrival(cn[a["to"]])
            worst.append((t + a["setup"], nm, a["to"]))
# outputs
for net in [canon(n) for n in re.findall(r"output\s+(?:\[[^\]]*\]\s*)?(\w+)", mod)]:
    pass
worst.sort(reverse=True)
print(f"cells: {len(insts)}  flops: {sum(cells[ct]['seq'] for ct, _, _ in insts)}")
print(f"worst reg/input -> reg (data arrival + setup): {worst[0][0]:.2f} ns at {worst[0][1]}.{worst[0][2]}")
print(f"slack at {PERIOD} ns: {PERIOD - worst[0][0]:.2f} ns   (estimate: no wire RC, ideal clock, 5 fF/sink)")
for w in worst[1:4]:
    print(f"  next: {w[0]:.2f} ns {w[1]}.{w[2]}")
