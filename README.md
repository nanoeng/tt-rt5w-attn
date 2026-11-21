![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg)

# RT5W: analog transformer attention head (Tiny Tapeout TTSKY26e, sky130A)

One row of self-attention, `softmax(q · K^T)` for 4 keys of dimension 4, computed by subthreshold transistor physics:
PMOS 1T + C_W score array, exponentiator / KCL softmax, 8-bit SAR readout and on-chip sign-sign SGD trims.
Analog hard macro on `tt_analog_6x2_3v3` (3.3 V on VAPWR) with a hardened 1.8 V SPI controller.

- Datasheet: [docs/info.md](docs/info.md)
- Submission files: `info.yaml`, `src/project.v` (macro interface), `gds/tt_um_rt5w_attn.gds`, `lef/tt_um_rt5w_attn.lef`
- Design sources: `design/blocks` (Python schematics, gm/ID-sized), `design/gmid` (LUTs), `design/layout` (generators,
  DRC/LVS/PEX), `design/tb` (ngspice testbenches), `netlist`, `netlist_pex`, `results`
- CI: `gds` (TT GDS packaging + official precheck + viewer), `docs` (datasheet), `test` (cocotb RTL);
  `ci` (full toolchain image, manual)

Sign-off (21 Nov 2026): magic DRC 0, full-chip LVS match, TT precheck pass (local), post-layout chain error
8 / 8 / 11 LSB at tt / ss / ff with the SAR run as one continuous transient.

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that makes it easier and cheaper to get designs manufactured on a real chip.
See https://tinytapeout.com.
