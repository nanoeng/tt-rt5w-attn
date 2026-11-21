# RT5W HIL and emulation frameworks: Illustrated-Transformer examples on every target (18 Nov 2026)

**Status.** All runs are simulation or emulation. No TT silicon or demo board was attached, so the real-board path was exercised only up to the serial link (a pseudo-terminal fake board), plus the firmware under the MicroPython interpreter.

**Tools.**
- ngspice-42 with the gf180mcu models;
- PySpice 1.5 on libngspice-42 (it misreads ngspice-42's `run` status; `op` is issued directly);
- Icarus 12;
- Verilator 5.040, built from source because cocotb 2.1 needs ≥ 5.036;
- cocotb 2.1;
- GTKWave 3.3;
- MicroPython 1.22.

## Architecture

**One firmware.** `hil/firmware/rt5w_fw.py`: a line protocol over USB serial. It runs unchanged in four places:
- on the TT demo board (MicroPython, `board_tt.py`);
- on the host against the virtual chip (`hil-sim`);
- behind a pseudo-terminal (`fake_board.py`), so the pyserial path can be tested;
- inside cocotb, through `cocotb.task.bridge`/`resume`, where its SPI bit-banging becomes pin activity on the RTL.

**One example suite.** `rt5w/illustrated.py` (E1–E7). Each example is checked against the float reference softmax(qKᵀ/√d_k), so a chip result is compared with what the post computes, not only with itself.

**Backends.** `ideal`, `behav` (optional Monte-Carlo die via `--seed`), `hil-sim`, `hil` (pyserial), `ngspice` (CLI) and `pyspice` (libngspice). Both SPICE engines use the subcircuits in `analog/rt5w_core.spice`.

## Mapping the post onto the chip

| Post step | Where it runs | Detail |
|---|---|---|
| q·k | chip | Keys k' = α(K + b) on C_W. The b·Σq term is common to all keys and cancels. |
| ÷√d_k | host-chosen key scale α | 0.3·α·β = 1/√d_k |
| softmax | chip | |
| −∞ mask | k = 0 plus the shift that puts max x at 18 | |
| more than 4 keys | tiles merged two ways | **log-sum-exp from V_B** (ua[1]), or a codes-only **pivot token** that is present in every tile |
| V, W^O, FFN, LayerNorm, vocabulary projection | host | |

**E1 uses the post's numbers:** 112 and 96, ÷8 → 14 and 12 → 0.88 / 0.12, giving codes [225, 30, 0, 0]. **E2–E7 are illustrative** d_k = 4 vectors built to reproduce what the post describes (it → animal, je suis étudiant → I am a student).

## Results (max |share error| across E1–E7; every argmax matches the reference)

| Target | Result |
|---|---|
| ideal / behav / hil-sim, nominal | ≤ 0.017 (quantisation only) |
| ngspice TT / ss −40 °C / ff 125 °C | 0.009 / 0.016 / 0.023 |
| PySpice TT | 0.009 (identical to the ngspice CLI) |
| RTL + firmware, Icarus | 8/8 cocotb tests (E1 codes [224, 31]: the RTL model stores keys as 8-bit codes) |
| RTL + firmware, Verilator 5.040 | 8/8, identical to Icarus, 5.7× faster (18 s vs 102 s) |
| Original unit suite on Verilator | 9/9 |
| Gate level | Icarus 9/9. Verilator 3/9: it mis-simulates the gf180 sequential UDP flip-flops, so keep gate-level on Icarus, as TinyTapeout's own flow does. |
| Monte-Carlo die (seed 3), untrimmed | max error 0.042, all argmax still correct |
| Same die after 8 SS-SGD epochs via CAL | median code error 4.38 → 0.88 LSB; max error 0.022 |
| Same die through the pseudo-terminal serial link | identical numbers |
| VBCAL on the virtual chip | slope 0.0338 V per e-fold |
| `pytest tests/` | 9/9 in 5 s |
| MicroPython self-test | pass |

## Findings

1. **VBCAL bug, fixed.** A constant V_B (open wire or dead probe) stored slope = 0, and every later PASS then divided by zero. VBCAL now rejects slopes outside 0.01–0.08 V/e-fold and keeps the defaults.
2. **What remains after trimming is the die's common softmax slope** (β spread ≈ 2.5 %). The row trims cannot correct it because row 0 is pinned. It needs a host-side gain calibration (a common α correction).
3. **Firmware-driven SS-SGD on the RTL** (4-clock pulses, measured asymmetric pump) brings the error 12.5 → 3.5–4.5 LSB and then dithers. This is consistent with open item O4 (pump asymmetry).
4. **Key-DAC resolution.** The MCP4725's 0.8 mV LSB is coarser than one pump step (0.14 mV), so writes are coarse and CAL passes do the fine tuning.
5. **SDK names unverified.** `board_tt.py` uses the `ttboard` SDK API names from memory. Check them against the firmware on your board; it is the only board-specific file.

## Running

| Command | What it runs |
|---|---|
| `make emu` | pytest: all Python backends, MicroPython, pseudo-terminal HIL |
| `make rtl` / `make rtl-vl` | cocotb on Icarus / Verilator |
| `make gl` | gate-level cocotb (Icarus) |
| `make waves` | FST traces + GTKWave PNGs (`waves/rt5w_illustrated.gtkw`) |
| `make corners` | examples on ngspice at ss/−40 °C and ff/125 °C |
| `make hil PORT=/dev/ttyACM0` | examples on the TT demo board |
