/*
 * Copyright (c) 2026 RT5W authors
 * SPDX-License-Identifier: Apache-2.0
 *
 * Behavioural top for simulation only (cocotb, test/Makefile); src/project.v is the interface of the hard macro.
 * tt_um_rt5w_attn: 4x4 analog attention head (QK^T + softmax) with on-die SS-SGD trim.
 * sky130A (TTSKY26e), tt_analog_6x2_3v3: VDPWR = 1.8 V digital, VAPWR = 3.3 V analog, 3 analog pins.
 * 1.8 V -> 3.3 V: 30 level shifters; static q/k codes cross serially (cfg_sdat/cfg_sclk) and the one-hot cell select
 * as a 5-bit address + enable, both rebuilt in rt5w_hvif on the 3.3 V side.
 *
 *  ui_in[0] SCK   ui_in[1] MOSI   ui_in[2] CS_n   ui_in[3] START (rising edge = inference pass)
 *  uo_out[7:0]    8-bit softmax code of the token chosen by OUT_SEL (reg 0x0B)
 *  uio[0] MISO (out)  uio[1] VALID (out)  uio[2] BUSY (out)  uio[7:3] unused (inputs)
 *  ua[0] I_REF   bias current inject / measure (beta-multiplier output, H1/H2 sweeps)
 *  ua[1] V_B     log-sum-exp node through the probe buffer (R7, tile merging)
 *  ua[2] V_W     weight write / read-back (key + trim C_W cells, leakage measurement)
 */
`default_nettype none

module tt_um_rt5w_attn (
    input  wire       VGND,
    input  wire       VDPWR,    // 1.8 V digital
    input  wire       VAPWR,    // 3.3 V analog
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    inout  wire [7:0] ua,       // only ua[2:0] are bonded (analog_pins: 3)
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);
    wire        bias_en, adc_rst, adc_lat, adc_cmp, vb_probe_en;
    wire [15:0] q_code, k_code;
    wire        cfg_sdat, cfg_sclk, wsel_e;
    wire [4:0]  wsel_a;
    wire [3:0]  adc_ch;
    wire [7:0]  adc_dac;
    wire [3:0]  pump_up, pump_dn;
    wire [19:0] wsel;

    // Digital half: hardened macro (OpenROAD, design/digital/harden.py) = controller + TT pin mapping
    rt5w_digital u_dig (
        .ui_in(ui_in), .uo_out(uo_out), .uio_in(uio_in), .uio_out(uio_out), .uio_oe(uio_oe),
        .ena(ena), .clk(clk), .rst_n(rst_n),
        .bias_en(bias_en), .cfg_sdat(cfg_sdat), .cfg_sclk(cfg_sclk),
        .adc_ch(adc_ch), .adc_rst(adc_rst), .adc_lat(adc_lat), .adc_dac(adc_dac), .adc_cmp(adc_cmp),
        .pump_up(pump_up), .pump_dn(pump_dn), .wsel_a(wsel_a), .wsel_e(wsel_e), .vb_probe_en(vb_probe_en)
    );

    // 3.3 V interface (behind the level shifters): configuration chain + cell-select decoder
    rt5w_hvif u_hvif (
        .cfg_sdat(cfg_sdat), .cfg_sclk(cfg_sclk), .wsel_a(wsel_a), .wsel_e(wsel_e),
        .q_code(q_code), .k_code(k_code), .wsel(wsel)
    );

    // Analog hard macro (transistor level: analog/rt5w_core.spice). For RTL simulation the
    // behavioural model test/rt5w_analog_beh.v is compiled instead of the GDS view.
    rt5w_analog u_ana (
        .VDPWR(VAPWR), .VGND(VGND),      // the analog core runs on VAPWR
        .bias_en(bias_en), .q_code(q_code), .k_code(k_code),
        .adc_ch(adc_ch), .adc_rst(adc_rst), .adc_lat(adc_lat), .adc_dac(adc_dac), .adc_cmp(adc_cmp),
        .pump_up(pump_up), .pump_dn(pump_dn), .wsel(wsel),
        .vb_probe_en(vb_probe_en),
        .iref(ua[0]), .vb_probe(ua[1]), .vw(ua[2])
    );

endmodule
