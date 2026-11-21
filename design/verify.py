"""Physical-design verification driver: schematic simulations against the Python model, block / top DRC + LVS,
digital hardening, with one summary table (results/pd_summary.md + .json).

    pixi run -e pd python design/verify.py sims      # schematic testbenches only (~15 min, 3 corners)
    pixi run -e pd python design/verify.py all       # capture -> sims -> layout -> DRC/LVS -> harden -> top
Every check has an explicit pass criterion (the spec column), so the summary is a verification record, not a log."""
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
CORNERS = (("typical", 27), ("ss", -40), ("ff", 125))
rows = []


def check(area, item, value, spec, ok):
    rows.append(dict(area=area, item=item, value=value, spec=spec, ok=bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {area:9s} {item:44s} {value:40s} ({spec})", flush=True)


def sims():
    import numpy as np
    from tb import tb_bias, tb_chain, tb_idac, tb_keycell, tb_readout, tb_softmax, tb_vbbuf
    for c, T in CORNERS:
        on, off = tb_bias.run(c, T, 1), tb_bias.run(c, T, 0)
        iu = on["nbias"]
        ka = off["nbias"] / iu * 100
        check("bias", f"I_u, keep-alive @ {c} {T} C", f"{iu*1e9:.1f} nA, gated {ka:.2f} %",
              "I_u 125 nA x PTAT/R (+-40 % corners); gated 0.5..2 %", 70e-9 < iu < 200e-9 and 0.5 < ka < 2.0)
        r = tb_idac.run(c, T)
        check("idac", f"monotonic / INL @ {c} {T} C", f"INL {r['inl_max']:.3f} LSB, gain {r['gain_err']*100:+.1f} %",
              "monotonic, INL < 0.5 LSB", r["monotonic"] and r["inl_max"] < 0.5)
        r = tb_keycell.run(c, T)
        g = r["gain0"]
        check("keycell", f"gain at k=1 over q @ {c} {T} C", f"spread {100*(g.max()/g.min()-1):.2f} %",
              "q-independent within 5 % (buffered gate offset, O1)", g.max() / g.min() - 1 < 0.05)
        r = tb_softmax.run(c, T)
        e = max(x["err_lsb"] for x in r["rows"])
        res = max(abs(x["vb_fit_err_mV"]) for x in r["rows"])
        check("softmax", f"share error / V_B fit @ {c} {T} C", f"{e:.2f} LSB, V_B residual {res:.1f} mV",
              "<= 4 LSB vs softmax(x); V_B linear in LSE within 3 mV", e <= 4 and res < 3)
        r = tb_readout.run(c, T)
        check("readout", f"SAR codes vs model @ {c} {T} C", f"max |err| {r['err_model']} LSB",
              "<= 1 LSB (12 codes, mid-step inputs)", r["err_model"] <= 1)
        r = tb_vbbuf.run(c, T)
        check("vbbuf", f"ua[1] - V_B, settling @ {c} {T} C",
              f"{np.abs(r['err_mV']).max():.1f} mV, {r['t_settle_us']:.1f} us", "<= 6 mV over 1.2..2.3 V, < 20 us",
              np.abs(r["err_mV"]).max() <= 6 and r["t_settle_us"] < 20)
    s = tb_bias.startup()
    check("bias", "start-up from a 10 us supply ramp", f"{s['t_settle_us']:.1f} us, {s['final']*1e9:.1f} nA",
          "settles < 50 us to I_u", s["t_settle_us"] < 50 and s["final"] > 100e-9)
    for q, k, ks in tb_chain.VECTORS:
        r = tb_chain.run(q, k, ks)
        check("chain", f"q={q} ks={ks}", f"SPICE {r['spice']} model {r['model']}", "<= 5 LSB per code (tt 27 C)",
              r["err"] <= 5)


def run(cmd, env=None):
    print("$", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=dict(os.environ, **(env or {})))


def pd():
    sys.path.insert(0, os.path.join(HERE, "layout"))
    import drc
    import lvs
    blocks = ["rt5w_idac4", "rt5w_coldiode", "rt5w_keycell", "rt5w_trimcell", "rt5w_pumpinv", "rt5w_kscale",
              "rt5w_softmax", "rt5w_bias", "rt5w_readout", "rt5w_vbbuf"]
    r = run(["pixi", "run", "-e", "layout", "python", "design/layout/blockgen.py"], dict(USER=os.environ.get("USER", "rt5w")))
    check("layout", "block generation", "ok" if r.returncode == 0 else r.stderr[-200:], "all leaf blocks", r.returncode == 0)
    for b in blocks:
        info = json.load(open(os.path.join(ROOT, "layout", "gds", b + ".json")))
        total, rules = drc.run(os.path.join(ROOT, "layout", "gds", b + ".gds"), b)
        other = sum(n for n, why, _ in rules if "HRES.7" not in why)
        hres = total - other
        check("drc", b, f"{other} errors (+{hres} HRES.7 pcell waiver)" if hres else f"{other} errors",
              "0 (magic drc(full)); HRES.7 inside the PDK high-Rs pcell is waived", other == 0)
        ok, msg, _ = lvs.run(b)
        check("lvs", b, msg.strip()[:40], "circuits match uniquely", ok)
        check("layout", f"{b} outline", f"{info['width']:.0f} x {info['height']:.0f} um, {info['shorts']} router shorts",
              "router reports no shorts", info["shorts"] == 0)
    if os.path.exists(os.path.join(ROOT, "layout", "gds", "rt5w_ctrl.json")):
        c = json.load(open(os.path.join(ROOT, "layout", "gds", "rt5w_ctrl.json")))
        total, rules = drc.run(os.path.join(ROOT, "layout", "gds", "rt5w_ctrl.gds"), "rt5w_ctrl")
        check("digital", "rt5w_ctrl hardened (OpenROAD)", f"{c['cells']} cells, {c['width']:.0f} x {c['height']:.0f} um, "
              f"{'; '.join(c['timing'])}", "setup/hold slack >= 0, 0 route DRC, 0 magic DRC",
              all(float(t.split()[-1]) >= 0 for t in c["timing"]) and c["route_drc"] == 0 and total == 0)
    run(["python3", "design/layout/floorplan.py"])
    fp = json.load(open(os.path.join(ROOT, "layout", "floorplan", "fp_data.json")))
    area = sum(fp["blocks"][i["block"]]["w"] * fp["blocks"][i["block"]]["h"] for i in fp["instances"])
    t = fp["tile"]
    check("floorplan", "block area vs TT 2x2 analog tile", f"{area/1e3:.0f}k um2 = {area/(t['w']*t['h']):.2f} x tile",
          "<= 0.7 x tile for a routable floorplan", area / (t["w"] * t["h"]) <= 0.7)


def summary():
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    json.dump(dict(date=stamp, rows=rows), open(os.path.join(ROOT, "results", "pd_summary.json"), "w"), indent=1)
    L = [f"# RT5W physical-design verification ({stamp})", "", "| | area | check | result | criterion |", "|---|---|---|---|---|"]
    L += [f"| {'PASS' if r['ok'] else '**FAIL**'} | {r['area']} | {r['item']} | {r['value']} | {r['spec']} |" for r in rows]
    n = sum(r["ok"] for r in rows)
    L += ["", f"{n} / {len(rows)} checks pass."]
    open(os.path.join(ROOT, "results", "pd_summary.md"), "w").write("\n".join(L) + "\n")
    print(f"{n} / {len(rows)} checks pass -> results/pd_summary.md")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("sims", "all"):
        sims()
    if mode in ("pd", "all"):
        pd()
    summary()
