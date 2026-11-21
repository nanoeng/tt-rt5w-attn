"""Readout (mux + current DAC + integrating StrongARM) vs the Python model's ADC (rt5w/analog_model.py):
code = floor(255 a + 0.5) with a = I_out / (16 I_u).  The SAR algorithm of rt5w_ctrl.v runs inside the ngspice
control loop: per bit, adc_rst (1 clock), integrate (ADCT-2 clocks), adc_lat (1 clock), read cmp, keep or drop.
The circuit's own transfer is floor(16 I / I_u) (DAC LSB I_u/16), i.e. the model's 255 vs the DAC's 256 steps."""
import numpy as np

import sim
import tech
from units import SM_P

T_CLK = 50e-9


def _sar_control(currents, ch, adct):
    t_rst, t_lat = T_CLK, (adct - 1) * T_CLK
    t_end = adct * T_CLK
    L = []
    for n, i_in in enumerate(currents):
        L += [f"alter Iin{ch} dc = {i_in / 4:.6e}", "let code = 0"]
        for b in range(7, -1, -1):
            L.append(f"let trial = code + {2 ** b}")
            for k in range(8):
                L += [f"let d{k} = 3.3*(floor(trial/{2 ** k}) - 2*floor(trial/{2 ** (k + 1)}))",
                      f"alter Vd{k} dc = d{k}"]
            L += [f"tran 10n {t_end:.3e}", "let c = v(cmp)[length(v(cmp))-1]",
                  "if c > 1.65", "let code = trial", "end", "destroy all"]
        L.append(f"let code_{n} = code\nprint code_{n}")
    return "\n".join(L), t_rst, t_lat, t_end


def run(corner="tt", temp=27.0, codes=None, ch=0, adct=16):
    t = tech.measure(corner, temp)
    iu = t["I_u"]
    codes = np.array(codes if codes is not None else [0, 1, 2, 7, 31, 64, 100, 127, 128, 180, 254, 255])
    currents = (codes + 0.5) * iu / 16       # mid-step inputs (the circuit's ideal code is `codes`)
    a = currents / (16 * iu)                 # the share the softmax mirrors would deliver
    ctl, t_rst, t_lat, t_end = _sar_control(currents, ch, adct)
    L = ["Vdd vdd 0 3.3", "Vss vss 0 0", f"Vr vr 0 {t['vr']:.4f}", f"Vvc vcas 0 {t['vcas']:.4f}", f"Indac vdd ndac {iu:.6e}",
         f"Vrst adc_rst 0 PWL(0 3.3 {t_rst:.3e} 3.3 {t_rst + 1e-9:.3e} 0)",
         f"Vlat adc_lat 0 PWL(0 0 {t_lat:.3e} 0 {t_lat + 1e-9:.3e} 3.3)"]
    for j in range(4):
        # softmax-like PMOS output (x4 mirror, Mp m=4 : Mo m=16 of an ideal reference): finite compliance, as on chip
        L += [f"Iin{j} pd{j} 0 {2 * iu:.6e}",
              f"XMp{j} pd{j} pd{j} vdd vdd sky130_fd_pr__pfet_g5v0d10v5 L={SM_P['L']} W={SM_P['W']} nf=1 m=4",
              f"XMo{j} o{j} pd{j} vdd vdd sky130_fd_pr__pfet_g5v0d10v5 L={SM_P['L']} W={SM_P['W']} nf=1 m=16",
              f"Vch{j} adc_ch{j} 0 {3.3 if j == ch else 0}"]
    L += [f"Vd{k} dac{k} 0 0" for k in range(8)]
    L.append(sim.inst("Xr", "rt5w_readout", **{**{p: p for p in sim.ports("rt5w_readout")},
                                                **{f"out{j}": f"o{j}" for j in range(4)}}))
    vals, _, out = sim.run("\n".join(L), ctl, corner, temp, blocks=["rt5w_readout"], timeout=3600)
    got = np.array([int(round(vals[f"code_{n}"])) for n in range(len(codes))])
    circuit = np.minimum(255, np.floor(16 * currents / iu + 1e-9)).astype(int)
    model = np.minimum(255, np.floor(255 * a + 0.5)).astype(int)
    return dict(codes=codes, got=got, circuit=circuit, model=model,
                err_model=int(np.abs(got - model).max()), err_ideal=int(np.abs(got - circuit).max()))


if __name__ == "__main__":
    for c, T in (("tt", 27), ("ss", -40), ("ff", 125)):
        r = run(c, T)
        print(f"{c:8s} {T:5.0f} C: model codes {[int(v) for v in r['model']]}\n{'':17s}SPICE codes {[int(v) for v in r['got']]}"
              f"  | max |err| vs model {r['err_model']} LSB, vs ideal 256-step DAC {r['err_ideal']} LSB")
