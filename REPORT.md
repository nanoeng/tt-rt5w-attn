# RT5W TinyTapeout submission: re-assessment, corrections and verification (18 Nov 2026)

**Scope.** I rebuilt the TinyTapeout (gf180mcuD) submission files and checked them against three sources:
- the project's spec of record (the RT5W project docs);
- Alammar, *The Illustrated Transformer*;
- the Zero to ASIC post on the AI-co-designed OOK radio.

I also checked them against the current TinyTapeout template and precheck code (`ttgf-analog-template`, `tt-support-tools`, cloned 18 Nov 2026).

The earlier source tree (`rt5w_sota/…`) could not be reached from this session: the desktop bridge was offline, GitHub was not linked, and nothing was attached. **These files are therefore a rebuild, not a patch.** Diff them against the original tree before merging.

**Status.** Everything below is simulation (ngspice-42 with the gf180mcu_fd_pr models, Icarus 12 + cocotb 2.1, Yosys 0.33 with gf180mcu_fd_sc_mcu7t5v0). There is **no layout, GDS, DRC or LVS yet**, so the project cannot pass TinyTapeout precheck in its current form.

## 1. Corrections

| # | Item | Was (record) | Now | Source / evidence |
|---|---|---|---|---|
| C1 | Top module / template ports | `tt_um_attn_head`, no power ports | `tt_um_rt5w_attn` with `VGND`, `VDPWR`, `ua[7:0]` as in `ttgf-analog-template`; info.yaml passes TT `ProjectInfo` (require_pinout=True) | TT template; `project_info.py`. **Add your GitHub username to the name before submitting.** |
| C2 | Analog pins | ua0 TIA out, ua1 I_ref, ua2 V_B | ua0 I_REF, ua1 V_B (log-sum-exp, R7), ua2 V_W (weight write/read-back, leakage measurement) | TT: pins used in order, < 4 mA. Gives the observability Paper C needs (R6/R7) and a direct key-write path. |
| C3 | Clock | 50 MHz, 2500-cycle window | **20 MHz**, 1000-cycle window (same 50 µs) | Estimated worst unbuffered path 39.8 ns at ss/125 °C/3.0 V (`synth/sta_ss.txt`). The ZTA post notes that the 50 MHz pin guidance shapes designs. |
| C4 | START pin | (no synchroniser) | 2-FF synchroniser + edge detect | Found by cocotb: an asynchronous input fed the FSM directly. |
| C5 | SAR / counter critical paths | variable shifter, 16-bit zero-detect | one-hot SAR mask; borrow-bit counter | Timing at ss: 47.7 ns (shifter) → 39.8 ns (one-hot SAR + borrow counter). |
| C6 | Softmax core (rev 2b) | AGC/OTA loop; exponentiators on p-substrate; IC rule partly met | Tail-current KCL normalisation (no OTA); exponentiators in one DNWELL pocket (bulk = V_B); all biased devices at gm/ID ≥ 23.9 S/A; wide-swing cascode tail; keep-alive replica at matched V_DS | `sim/results/softmax_static.json`, `softmax_tran.json` |
| C7 | Masking (decoder) | — | Alammar sets masked scores to −inf. Here: k = 0 (x = 0) plus a host shift of max x to 18. Masked codes read 0 when max x > ln 510. Without the shift, masked tokens leak (test t04). | cocotb t03/t04 |
| C8 | 1/√d_k | folded into a gain | d_k = 4 → ½, folded into the query codes or a common array gain. A single host-calibrated scalar also absorbs the array's common gain error (g = 1.009). | `array_chain.json` |
| C9 | Thinking-Machines example | "illustrative" scores | Alammar's figure: 112, 96 → ÷8 → 14, 12 → 0.88/0.12. By shift invariance x = [18, 16, 0, 0]. Golden codes [225, 30, 0, 0]; RTL+model [225, 30, 0, 0]; transistor-level core [224, 31]; array → core chain [220, 35]. | t03; `softmax_static`; `array_chain` |
| C10 | Array multiplier | 4-T stacked translinear loop I_Q·I_K/I_ref | **The stacked loop fails at transistor level:** Q2's current enters Q1's diode, giving 2–19× errors. The record only closed it with ideal buffers. The row scale is redundant (it folds into V_w), so the proposed cell is a 1-T PMOS + floating C_W: I = I_Q·e^{−V_w/nU_T}. **This cell has its own open issue; see O1.** | `sim/tl_cell.py`, `array_chain.py` |
| C11 | Array current scale | LSB 0.5 µA, I_ref 5 µA → 682 µW array | I_Q LSB 8.25 nA, R_c 1.376 MΩ (x_max = 18): about 2.5 µA (~8 µW) | `array_chain.json` |
| C12 | Bias reference | 14 %/V supply sensitivity (FAIL) | Cascoded β-multiplier, K = 8, R = 170 k, new start-up: 0.498 µA, **0.063 %/V**, 3124 ppm/K (PTAT), corners ±1.6 %, starts from a 0 → 3.3 V ramp | `bias_idac.json` |
| C13 | Rev-3 trim pump at 20 MHz | 0.92 nA × 20 ns into 100 fF | 0.92 nA × 50 ns would triple the step. Charge sharing also gave 0.91 mV steps. Now **current-steered**, 3.7 nA into 1 pF: steps +0.141 / −0.120 mV (TT). | `weight_cell.json` |
| C14 | Transient integration | — | Gear integration for every transient. Trapezoidal integration rang on alternate samples and gave false settling, a repeat of the known pitfall. | `rt5w_ng.py` |

## 2. Verification results

### Digital (`test/`, `synth/`)

- **Lint.** Verilator `-Wall`: clean.
- **Simulation.** cocotb on `tt_um_rt5w_attn` with the behavioural analog model: **9/9 pass at RTL and 9/9 at gate level** (gf180 cell functional models). The tests cover:
  - SPI register map and ID;
  - bias gating;
  - Thinking Machines;
  - masking with and without the shift;
  - 25 random QK vectors (≤ 1 LSB);
  - the settle window (a short window fails, the default passes);
  - weight-write lockout during a pass;
  - the START pin and OUT_SEL;
  - SS-SGD: row 0 is pinned, equal codes give no pulse, the sign rule is checked.
- **SS-SGD convergence.**
  - With symmetric steps the median error falls from 12.5 to 0.25 LSB in 6 epochs.
  - With the measured UP/DN asymmetry (16 %) it falls only from 12.5 to 3.75 LSB, so **asymmetry must be fixed** (O4).
- **Synthesis.** 1,144 cells, of which 265 are flip-flops; 36.6k µm² of cell area.
- **Timing (estimate).**
  - Worst path at ss/125 °C/3.0 V is 39.8 ns; at TT it is 20.6 ns.
  - At 20 MHz the ss slack is +10.2 ns.
  - This is my own liberty-table STA, with no wire RC and an ideal clock. Confirm it with OpenROAD/OpenSTA.

### Analog: softmax core (transistor level, ideal score current sources)

| Metric | Result | Record |
|---|---|---|
| Nominal (TT 27 °C) max / rms share error | 0.12 % / 0.04 % (≤ 1 LSB) | 0.41 % / 0.13 % |
| PVT (5 corners × −40/27/125 °C × 3.0/3.3/3.6 V), worst | 0.60 % max, 0.24 % rms, ≤ 2 LSB | 1.41 % |
| Monte Carlo (Pelgrom, 20 dies) | rms ≤ 0.39 %, max 1.75 %, ≤ 4 LSB | rms 2.92 % worst |
| β (log-domain slope), PVT / MC | 0.971–1.036 / 0.926–1.033 (1 die < 0.95) | failed 16/20 |
| AGC sum vs PTAT reference | −3.8 … +5.5 % (common mode, worst at ff 125 °C). The host renormalises by Σ codes. | 4.4 % |
| Settling, 48 transients (8 steps × 6 PVT) | **worst 17.6 µs**, all inside 50 µs; unchanged with R_c = 1.376 MΩ | 32.1–49 µs |
| Supply current | 1.17 µA at TT (0.9–1.6 µA over PVT) | — |

The window could drop to 500 cycles (25 µs), which would halve energy per decision.

### Analog: other blocks

- **Array chain** (array → softmax at TT, host-calibrated common gain):
  - held-out max share error 1.48 %, median 0.33 %, ≤ 4 codes;
  - product law over PVT: mean +0.8…+3.2 %, max 5.7 %;
  - Monte Carlo row-gain σ 0.44 %.
  - *These numbers assume perfect floating-gate coupling (O1).*
- **IDAC (4-bit thermometer):** INL 0.12 LSB, DNL 0.08 LSB (Monte Carlo, 20 dies), monotonic, gain +3.8 %. Simulated at a 10 nA LSB; re-run at 8.25 nA.
- **Weight cell:**
  - droop at TT 27 °C is 6–12 µV/ms;
  - **at 60 °C it is 0.09–1.1 mV/ms, and at 85–125 °C 0.45–5 mV/ms**.

## 3. Open before tape-out (most severe first)

1. **O1: array floating-gate coupling.** The coupling ratio α = C_W/(C_W + C_gg) is 0.45 for the 640 µm² cell, 0.90 for W/L 40/1 and 0.95 for W/L 20/1. As a result the cell computes I_Q^α·k, not I_Q·k. Small cells restore α but bring back per-cell mismatch (σ_VT ≈ 1.5 mV, about 3.5 %). The write switch also injects −19 mV onto 1 pF. Options:
   - C_W ≫ C_gg with small cells plus a host-side q pre-distortion;
   - an active (buffered) gate offset;
   - keys as current DACs with a working translinear multiplier, which the record also lacks.
2. **O2: area does not close.**
   - The controller alone is 36.6k µm² of cells (about 55–60k µm² placed).
   - The analog core is another ≥ 20–30k µm²: exponentiators about 1k, PMOS mirrors about 2k, array 10k+, R_c 4 × ~3k, 20 C_W cells × 1 pF.
   - The 2x2 tile is 231.4k µm², so it may fit, but only after layout.
   - Remove registers you don't need (row codes 0x03/0x04 are now spare).
3. **O3: not designed yet.**
   - the SAR current DAC and current comparator (behavioural only);
   - the V_B probe buffer;
   - the column write-reference switch;
   - the pump bias / v_mid replica;
   - real V_R / V_cas generators;
   - the cascode bias currents in the reference.
4. **O4: pump UP/DN asymmetry** (−13 … +16 %). Add dummy switches, or separate UP and DN pulse-width registers.
5. **O5: hot leakage.** Above about 40 °C, keys and trims need refresh. Specify 0–40 °C or add a refresh FSM.
6. **O6: layout flow.** Following the ZTA post:
   - Run full PVT plus Monte Carlo after extraction, not only TT.
   - **Make LVS fail on any device-property mismatch.**
   - Benchmark the power grid (IR/EM; supply current is µA-level, so this is easy).
   - Verify every floorplan rule rather than trusting it.
7. **O7: TT GF specifics to confirm with TinyTapeout.** MIM sits under the top metal (`Metal5` is forbidden; Metal4 is the project top), so plan MOS caps. The availability of `ppolyf_u_3k` also needs confirming.

## 4. Files

| Path | Contents |
|---|---|
| `info.yaml`, `docs/info.md` | Corrected submission metadata and datasheet. |
| `src/project.v`, `src/rt5w_ctrl.v` | Top module and controller. |
| `analog/rt5w_core.spice` | Analog subcircuits of record. Ideal elements are marked. |
| `test/` | cocotb tests, tb, behavioural analog model, Makefile (`make`, `make GATES=yes`). |
| `synth/` | Yosys scripts, gate-level netlists, `mini_sta.py`, timing reports. |
| `sim/` | ngspice generators and sweeps (`softmax_static`, `softmax_tran`, `array_chain`, `bias_idac`, `weight_cell`, `tl_cell`) and `results/*.json`. |
| `ext_cells/` | gf180mcu_fd_sc_mcu7t5v0 functional models (Apache-2.0) used for gate-level simulation. |

## 5. HIL and emulation frameworks (added 18 Nov 2026)

See `HIL_EMULATION.md` and `hil/README.md`. The Illustrated-Transformer examples E1–E7 run on the ideal, behavioural, HIL-sim, real-HIL (serial), ngspice, PySpice and RTL targets (cocotb on Icarus and Verilator), all through one firmware.
