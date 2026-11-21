"""results/pex/*.json -> LaTeX rows (schematic vs post-layout) for the deck."""
import json, os, sys
d = os.path.join(os.path.dirname(__file__), "..", "results", "pex")
def g(m, t, c):
    f = os.path.join(d, f"{m}_{t}_{c}.json")
    return json.load(open(f)) if os.path.exists(f) else None
L = []
for c, T in (("tt", "27"), ("ss", "$-40$"), ("ff", "125")):
    cells = []
    for t in ("keycell", "softmax", "readout", "chain"):
        s, p = g("sch", t, c), g("pex", t, c)
        if t == "keycell":
            f = lambda r: f"{1e3 * sum(r['nUT_fit']) / 4:.1f}" if r else "--"
        elif t == "softmax":
            f = lambda r: f"{r['err_cal']:.1f}" if r else "--"
        elif t == "readout":
            f = lambda r: f"{r['err_model']}" if r else "--"
        else:
            f = lambda r: f"{r['err']}" if r else "--"
        cells.append(f"{f(s)} / {f(p)}")
    L.append(f"{c} / {T}\\,\\textdegree C & " + " & ".join(cells) + r" \\")
out = sys.argv[1] if len(sys.argv) > 1 else "/dev/stdout"
open(out, "w").write("\n".join(L) + "\n")
