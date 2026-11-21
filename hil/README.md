# RT5W hardware-in-the-loop (HIL) and emulation

One firmware, one example suite, every target:

```
                         rt5w/illustrated.py  (E1-E7 from "The Illustrated Transformer")
                                     |
                       rt5w/backends: run(encoding) -> codes, log-sum-exp
   +---------+--------+-------------+---------------+--------------------+----------------------+
   | ideal   | behav  | hil-sim     | hil           | ngspice / pyspice  | rtl (cocotb)         |
   | golden  | Python | firmware vs | firmware on   | transistor level,  | firmware-in-the-loop |
   | maths   | model  | virtual chip| TT demo board | gf180mcuD          | Icarus / Verilator   |
   +---------+--------+-------------+---------------+--------------------+----------------------+
                               hil/firmware/rt5w_fw.py (MicroPython + CPython)
```

## Board setup (TT demo board, RP2040 or RP2350)

1. Flash the TinyTapeout MicroPython firmware for your board.
2. Copy the files: `mpremote cp hil/firmware/rt5w_fw.py hil/firmware/board_tt.py hil/firmware/config.py hil/firmware/main.py :`
3. Wiring (edit `config.py` to match):

   | Chip pin | Connect to | Notes |
   |---|---|---|
   | `ua[1]` V_B | RP GP26/ADC0 through a ÷2 divider | Log-sum-exp readout. Only needed for VBCAL and V_B tile merging; the pivot merge needs no ADC. |
   | `ua[2]` V_W | MCP4725 DAC (I²C on a PMOD) | Key writes. 0.8 mV per DAC LSB against 0.14 mV per pump step, so fine-tune with CAL passes. |
   | `ua[0]` I_REF | SMU, or leave open | Bias sweeps only. |

4. `board_tt.py` is the only file that touches the `ttboard` SDK. Check the names (`DemoBoard`, `RPMode.ASIC_RP_CONTROL`, `ui_in`, `uio_out`, `clock_project_PWM`) against your SDK version.
5. Run: `make hil PORT=/dev/ttyACM0`, which runs the 7 examples after 8 calibration epochs.
6. **From a container, a VM or another PC:** on the machine with the board, run `python3 hil/tools/rfc2217_bridge.py /dev/ttyACM0 -p 4000`, then use `PORT=rfc2217://<that-host>:4000`. Any pyserial URL works (`socket://`, `loop://`); see `container/README.md`.

## Line protocol

The full command list is in the header of `rt5w_fw.py`: `ID`, `W`, `R`, `WIN`, `KEY`, `KEYS`, `Q`, `PASS`, `CAL`, `VBCAL`. Replies start with `OK` or `ERR`. The firmware never stops on a bad line, and VBCAL refuses a dead or saturated probe.

## Without hardware

| Command | What it tests |
|---|---|
| `python3 examples/illustrated_transformer.py --backend hil-sim [--seed N] [--calibrate 8]` | Firmware against the virtual chip, in process. |
| `python3 hil/tests/fake_board.py --seed 3 &` then `--backend hil --port /tmp/rt5w_hil_tty` | The real pyserial path through a pseudo-terminal. |
| `micropython hil/tests/mp_selftest.py` | The firmware under the MicroPython interpreter. |
| `make rtl` / `make rtl-vl` | The same firmware driving the RTL in Icarus or Verilator (cocotb `bridge`/`resume`). |
| `make waves` | FST traces plus `waves/rt5w_illustrated.gtkw` for GTKWave. |
