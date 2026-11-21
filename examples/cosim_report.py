#!/usr/bin/env python3
"""Readable report of an instrumented RTL + SPICE co-simulation (test/cosim_trace.json from `make cosim-trace`).

  python examples/cosim_report.py test/cosim_trace.json                 # text report
  python examples/cosim_report.py test/cosim_trace.json --csv out/      # + CSV files for plots

For every pass: example, query codes, keys, expected scores, golden codes, chip codes, LSE, FSM timeline relative to
START, SAR trials, V_B samples, SPICE transient (solve time, cached or not). Then the per-example results."""
import argparse
import csv
import json
import math
import os
from collections import Counter, defaultdict


def fsm_rel(p):
    f = p.get("fsm", [])
    if not f:
        return None, []
    t0 = f[0]["t_us"]
    return t0, [(s["state"], round(s["t_us"] - t0, 2)) for s in f]


def sar_by_ch(p):
    out = defaultdict(list)
    for s in p.get("sar", []):
        out[s["ch"]].append((s["dac"], s["cmp"], round(s["share_mlsb"] / 1000, 3)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace")
    ap.add_argument("--csv", help="directory for CSV exports")
    a = ap.parse_args()
    d = json.load(open(a.trace))
    m = d["meta"]
    print(f"co-simulation: {m['sim']} + {m['engine']}, {m['corner']} {m['temp']} C, bias off {m['bias_off']:g}, "
          f"WAKE {m['wake']}; {len(d['passes'])} passes, {m['transients']} SPICE transients, "
          f"{m['spice_seconds']} s in SPICE, {m['sim_time_ms']} ms simulated; VBCAL {m['vbcal']}")
    for p in d["passes"]:
        t0, rel = fsm_rel(p)
        spi = Counter(f"{s['op']} {s['reg']}" for s in p.get("spi", []))
        sp = p.get("spice", [])
        sar = sar_by_ch(p)
        print(f"\n[{p['index']:2d}] {p['example']}: q {p['q_codes']}  x {p['x_expected']}  golden {p['golden_codes']}"
              f"  -> codes {p['codes']}  LSE {p['lse']}")
        print(f"     keys k = {p['k']}")
        print(f"     SPI {sum(spi.values())} transactions: {dict(spi)}; key cells written {len(p.get('keys', []))}")
        print(f"     FSM (us from START): {rel}")
        for ch in sorted(sar):
            print(f"     SAR ch{ch}: " + " ".join(f"{dac}{'+' if c else '-'}" for dac, c, _ in sar[ch])
                  + f"   (SPICE share x255 at decision: {sar[ch][-1][2]})")
        for v in p.get("vb", []):
            print(f"     V_B sample {v['volts']} V at {round(v['t_us'] - t0, 2) if t0 else v['t_us']} us after START")
        for s in sp:
            print(f"     SPICE event at START{'+' + str(round(s['t_event_us'] - t0, 2)) if t0 else ''} us, "
                  f"from_off={s['from_off']}, {'cached' if s['cached'] else str(s['solve_s']) + ' s'}; "
                  f"final shares {s['shares'][-1]}, V_B {s['vb'][-1]}")
    print("\nresults")
    for r in d["results"] + [dict(d["e1_at_wake30"], example="E1 at WAKE 30")]:
        print(f"  {r['example']:42s} max|err| {r['max_abs_err']:<7} argmax_ok {r['argmax_ok']}")
    if a.csv:
        os.makedirs(a.csv, exist_ok=True)
        for p in d["passes"]:
            for k, s in enumerate(p.get("spice", [])):
                if s["cached"]:
                    continue
                path = os.path.join(a.csv, f"pass{p['index']:02d}_spice{k}.csv")
                with open(path, "w", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["t_us", "a0", "a1", "a2", "a3", "vb"])
                    for i, t in enumerate(s["t_us"]):
                        w.writerow([t] + s["shares"][i] + [s["vb"][i]])
        print(f"CSV written to {a.csv}")


if __name__ == "__main__":
    main()
