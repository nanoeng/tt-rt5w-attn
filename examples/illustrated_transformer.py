#!/usr/bin/env python3
"""Run the Illustrated-Transformer examples on any RT5W backend and compare with the float reference.

  python3 examples/illustrated_transformer.py --backend ideal
  python3 examples/illustrated_transformer.py --backend behav --seed 3        # one Monte-Carlo die
  python3 examples/illustrated_transformer.py --backend hil-sim               # HIL firmware vs virtual chip
  python3 examples/illustrated_transformer.py --backend hil --port /dev/ttyACM0   # TT demo board
  python3 examples/illustrated_transformer.py --backend ngspice --corner ss --temp -40
  python3 examples/illustrated_transformer.py --backend pyspice
The RTL (Icarus / Verilator + cocotb) runs the same examples: cd test && make -f Makefile.illustrated [SIM=verilator]
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rt5w.backends import get_backend          # noqa: E402
from rt5w.illustrated import run_all, calibrate  # noqa: E402

TOL = {"ideal": 0.02, "behav": 0.03, "hil-sim": 0.03, "hil": 0.06, "ngspice": 0.04, "pyspice": 0.04, "rtl": 0.02}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ideal", choices=list(TOL))
    ap.add_argument("--port")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--corner", default="tt")
    ap.add_argument("--temp", type=float, default=27)
    ap.add_argument("--calibrate", type=int, default=0, help="SS-SGD epochs on chip before the examples (hil, hil-sim)")
    ap.add_argument("--tol", type=float, help="override the share-error tolerance")
    ap.add_argument("--json")
    a = ap.parse_args()
    be = get_backend(a.backend, port=a.port, seed=a.seed, corner=a.corner, temp=a.temp)
    t = time.time()
    cal = None
    if a.calibrate:
        cal = calibrate(be, epochs=a.calibrate)
        print("SS-SGD median code MAE per epoch:", " ".join(f"{v:.2f}" for v in cal))
    res = run_all(be)
    be.close()
    tol = a.tol or TOL[a.backend]
    ok_all = True
    print(f"backend={a.backend} corner={a.corner} T={a.temp}  ({time.time() - t:.1f} s)")
    for r in res:
        ok = r["argmax_ok"] and r["max_abs_err"] <= tol
        ok_all &= ok
        extra = ""
        if "codes" in r:
            extra = f" codes={r['codes']} golden={r['golden_codes']}"
        if "top_word" in r:
            extra = f" 'it' -> {r['top_word']!r} (pivot {r['pivot']!r}, {r['passes_pivot']} passes)"
            if "lse_merge" in r:
                extra += f"; V_B merge err {r['lse_merge']['max_abs_err']}"
        if "word" in r:
            extra = f" next word {r['word']!r} in {r['passes']} passes"
        if "rows" in r:
            extra = " " + ", ".join(f"{x['query']}->{x['attends']}" for x in r["rows"])
        if "heads" in r:
            extra = " " + ", ".join(f"{k}: it->{v['top']}" for k, v in r["heads"].items())
        print(f"  {'PASS' if ok else 'FAIL'}  {r['example']:42s} max|err| {r['max_abs_err']:.4f}{extra}")
    if a.json:
        json.dump(dict(backend=a.backend, corner=a.corner, temp=a.temp, seed=a.seed, calibration=cal, results=res), open(a.json, "w"), indent=1, default=str)
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
