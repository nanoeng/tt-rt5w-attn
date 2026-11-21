"""Run the sky130 PSY-TaLiRo campaigns (rt5w/falsify_sky130.py) and write results/falsify_sky130/<sut>_<corner>_<engine>.json.
usage: python examples/falsify_sky130.py softmax|chain CORNER [ENGINE] [BUDGET] [ANNEAL]"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rt5w import falsify_sky130 as F

sut, corner = sys.argv[1], sys.argv[2]
engine = sys.argv[3] if len(sys.argv) > 3 else "ngspice"
budget = int(sys.argv[4]) if len(sys.argv) > 4 else (30 if sut == "softmax" else 24)
anneal = int(sys.argv[5]) if len(sys.argv) > 5 else (10 if sut == "softmax" else 8)
log = lambda m: print(m, flush=True)   # noqa: E731
r = (F.campaign_softmax if sut == "softmax" else F.campaign_chain)(corner, engine, budget, anneal, log=log)
r["netlist"] = os.environ.get("RT5W_NETLIST", "netlist")
r["date"] = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
out = os.path.join("results", "falsify_sky130", f"{sut}_{corner}_{engine}.json")
json.dump(r, open(out, "w"), indent=1, default=float)
keys = ("rho_norm", "falsified", "held") if sut == "softmax" else ("rho_min_dc", "rho_min_cont", "falsified_dc", "falsified_cont")
print("RESULT", sut, corner, engine, r["n"], "samples", r["seconds"], "s", {k: r[k] for k in keys}, flush=True)
