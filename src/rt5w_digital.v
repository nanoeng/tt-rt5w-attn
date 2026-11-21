/*
 * RT5W digital half, hardened with OpenROAD as one macro (digital/harden.py): the controller plus the TT pin
 * mapping, so the macro owns every TinyTapeout digital pin and every analog-macro control line.
 * SPDX-License-Identifier: Apache-2.0
 */
`default_nettype none

module rt5w_digital (
    input  wire [7:0]  ui_in,
    output wire [7:0]  uo_out,
    input  wire [7:0]  uio_in,
    output wire [7:0]  uio_out,
    output wire [7:0]  uio_oe,
    input  wire        ena,
    input  wire        clk,
    input  wire        rst_n,
    // to / from the analog macro
    output wire        bias_en,
    output wire        cfg_sdat,
    output wire        cfg_sclk,
    output wire [3:0]  adc_ch,
    output wire        adc_rst,
    output wire        adc_lat,
    output wire [7:0]  adc_dac,
    input  wire        adc_cmp,
    output wire [3:0]  pump_up,
    output wire [3:0]  pump_dn,
    output wire [4:0]  wsel_a,
    output wire        wsel_e,
    output wire        vb_probe_en
);
    wire busy, valid, miso;
    wire [7:0] result;

    rt5w_ctrl u_ctrl (
        .clk(clk), .rst_n(rst_n),
        .sck(ui_in[0]), .mosi(ui_in[1]), .cs_n(ui_in[2]), .miso(miso),
        .start_pin(ui_in[3]),
        .busy(busy), .valid(valid), .result(result),
        .bias_en(bias_en), .cfg_sdat(cfg_sdat), .cfg_sclk(cfg_sclk),
        .adc_ch(adc_ch), .adc_rst(adc_rst), .adc_lat(adc_lat), .adc_dac(adc_dac), .adc_cmp(adc_cmp),
        .pump_up(pump_up), .pump_dn(pump_dn), .wsel_a(wsel_a), .wsel_e(wsel_e),
        .vb_probe_en(vb_probe_en)
    );

    assign uo_out  = result;
    assign uio_out = {5'b00000, busy, valid, miso};
    assign uio_oe  = 8'b0000_0111;
    wire _unused = &{ena, uio_in, ui_in[7:4], 1'b0};
endmodule
