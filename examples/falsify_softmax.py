#!/usr/bin/env python3
"""PSY-TaLiRo falsification of the RT5W softmax core (transistor level, gf180mcuD) against nine STL requirements.

  python examples/falsify_softmax.py                                   # tt, ngspice, 40 random + 0 annealing samples
  python examples/falsify_softmax.py --engine pyspice --corner ss --budget 40 --anneal 100
  python examples/falsify_softmax.py --corners tt,ss,ff,sf,fs --json results/falsify.json
  python examples/falsify_softmax.py --check 0,0,0,0:18,16,0,0 --temp 27     # one transient, robustness per requirement

Exit code: 0 always for a campaign (falsified requirements are findings, not tool errors); 1 on a tool error.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from rt5w import falsify as F  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--engine", choices=["ngspice", "pyspice"], default="ngspice")
    ap.add_argument("--corner", default="tt", choices=["tt", "ss", "ff", "sf", "fs"])
    ap.add_argument("--corners", help="comma list; overrides --corner")
    ap.add_argument("--budget", type=int, default=40, help="UniformRandom samples per corner")
    ap.add_argument("--anneal", type=int, default=0, help="DualAnnealing samples per corner (after the random phase)")
    ap.add_argument("--seed", type=int, default=1, help="> 0 (PSY-TaLiRo)")
    ap.add_argument("--reqs", help="comma list of requirements (default: all nine)")
    ap.add_argument("--check", help="xa:xb, e.g. 0,0,0,0:18,16,0,0 -> one transient, no search")
    ap.add_argument("--temp", type=float, default=27.0, help="temperature for --check")
    ap.add_argument("--json", help="write the full result (incl. every sample) here")
    a = ap.parse_args()
    reqs = a.reqs.split(",") if a.reqs else None

    print("STL requirements (RTAMT syntax), T0 = step + 50 us window:")
    for k in (reqs or F.REQUIREMENTS):
        f, s, w = F.REQUIREMENTS[k]
        print(f"  {k:4s} {f:48s} s={s:<8.4g} {w}")

    if a.check:
        xa, xb = ([float(v) for v in part.split(",")] for part in a.check.split(":"))
        r = F.evaluate(xa, xb, a.temp, a.corner, a.engine, reqs)
        print(f"\n{a.engine} {a.corner} {a.temp:g} C  step {xa} -> {xb}")
        print(f"final codes {r['final_codes']}  golden {r['golden_codes']}")
        for k, v in r["rho"].items():
            print(f"  {k:4s} rho {v:+.5f}  rho/s {v / F.REQUIREMENTS[k][1]:+8.3f}  {'holds' if v >= 0 else 'FALSIFIED'}")
        out = r
    else:
        corners = a.corners.split(",") if a.corners else [a.corner]
        out = []
        for c in corners:
            print(f"\ncampaign: corner {c}, engine {a.engine}, UniformRandom {a.budget} + DualAnnealing {a.anneal}, "
                  f"x_a, x_b in [0,18]^4, T in [-40,125] C")
            r = F.campaign(c, a.engine, a.budget, a.anneal, a.seed, reqs)
            print(f"  {r['n']} transients in {r['seconds']} s")
            for k, v in r["rho_min"].items():
                tag = "holds" if v >= 0 else "FALSIFIED"
                line = f"  {k:4s} rho_min {v:+.5f}  ({v / F.REQUIREMENTS[k][1]:+8.3f} s)  {tag}"
                if v < 0:
                    ce = r["counterexamples"][k]
                    line += (f"   e.g. {[round(x, 1) for x in ce['xa']]} -> {[round(x, 1) for x in ce['xb']]}"
                             f" at {ce['temp']:.0f} C")
                print(line)
            print(f"  held: {r['held']}   falsified: {r['falsified']}")
            out.append(r)
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        json.dump(out, open(a.json, "w"), indent=1)
        print(f"wrote {a.json}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
