/*
 * RT5W analog macro for RTL + SPICE co-simulation (NOT for synthesis). Same module name and ports as
 * test/rt5w_analog_beh.v, so src/project.v is unchanged; the Makefile picks one or the other.
 *
 * Nothing analog is computed here. The cocotb driver (test/cosim_driver.py) watches bias_en, q_code, k_code,
 * the keys and the trims, solves the array + softmax core in ngspice / PySpice (rt5w/cosim.py) and writes the
 * SPICE shares into sh_mlsb* (share x 255000) and V_B into vb_uv. The comparator below is the ideal decision of
 * the (not yet drawn) SAR current DAC + comparator: 255*share + 0.5 > dac, as in the behavioural model.
 * The charge-pump trim stays behavioural (step sizes from sim/results/weight_cell.json); its voltage is passed to
 * SPICE as a row gate offset. Keys and the row-gain mismatch use the same backdoors as the behavioural model.
 */
`default_nettype none
`timescale 1ns/1ps

module rt5w_analog (
    input  wire        VDPWR, VGND,
    input  wire        bias_en,
    input  wire [15:0] q_code,
    input  wire [15:0] k_code,
    input  wire [3:0]  adc_ch,          // one-hot channel select
    input  wire        adc_rst,         // integrator reset strobe (model: no effect)
    input  wire        adc_lat,         // comparator latch strobe: adc_cmp is sampled here and held
    input  wire [7:0]  adc_dac,
    output reg         adc_cmp,
    input  wire [3:0]  pump_up,
    input  wire [3:0]  pump_dn,
    input  wire [19:0] wsel,            // one-hot cell select
    input  wire        vb_probe_en,
    inout  wire        iref, vb_probe, vw
);
    // decoded views of the one-hot selects (names kept for the Python harnesses)
    wire       adc_en  = |adc_ch;
    wire [1:0] adc_sel = adc_ch[3] ? 2'd3 : adc_ch[2] ? 2'd2 : adc_ch[1] ? 2'd1 : 2'd0;
    wire       wsel_en = |wsel;
    reg  [4:0] wsel_i;
    integer    wi;
    always @* begin wsel_i = 5'd0; for (wi = 0; wi < 20; wi = wi + 1) if (wsel[wi]) wsel_i = wi[4:0]; end
    reg        cmp_now;                 // continuous comparator decision; adc_cmp latches it on adc_lat
    initial adc_cmp = 1'b0;
    always @(posedge adc_lat) adc_cmp <= cmp_now;

    parameter integer STEP_UP_NV = 141;   // trim step per 50 ns of pulse, nV/1000 = 0.141 mV (as the behavioural model)
    parameter integer STEP_DN_NV = 120;

    reg  [127:0] kflat = 128'd0;                     // backdoor: k_jm at [8*(4j+m) +: 8]
    integer gam_ppm0 = 0, gam_ppm1 = 0, gam_ppm2 = 0, gam_ppm3 = 0;   // backdoor: row gain mismatch
    integer cmp_off_mlsb = 0;                        // backdoor: comparator offset (milli-LSB)
    integer vw_uv1 = 0, vw_uv2 = 0, vw_uv3 = 0;      // trim-cell voltages relative to mid (uV); row 0 has no pump
    integer sh_mlsb0 = 63750, sh_mlsb1 = 63750, sh_mlsb2 = 63750, sh_mlsb3 = 63750;   // from SPICE (cocotb)
    integer vb_uv = 0;                               // V_B from SPICE (cocotb)
    integer sh;
    real t_up [0:3]; real t_dn [0:3];

    always @* begin
        case (adc_sel) 2'd0: sh = sh_mlsb0; 2'd1: sh = sh_mlsb1; 2'd2: sh = sh_mlsb2; default: sh = sh_mlsb3; endcase
        cmp_now = adc_en && bias_en && ((sh + 500 + cmp_off_mlsb) > (adc_dac * 1000));
    end

    genvar r;
    generate for (r = 1; r < 4; r = r + 1) begin : g_pump
        always @(posedge pump_up[r]) t_up[r] = $realtime;
        always @(negedge pump_up[r]) begin
            if (r == 1) vw_uv1 = vw_uv1 + $rtoi(STEP_UP_NV * (($realtime - t_up[r]) / 50.0) + 0.5);
            if (r == 2) vw_uv2 = vw_uv2 + $rtoi(STEP_UP_NV * (($realtime - t_up[r]) / 50.0) + 0.5);
            if (r == 3) vw_uv3 = vw_uv3 + $rtoi(STEP_UP_NV * (($realtime - t_up[r]) / 50.0) + 0.5);
        end
        always @(posedge pump_dn[r]) t_dn[r] = $realtime;
        always @(negedge pump_dn[r]) begin
            if (r == 1) vw_uv1 = vw_uv1 - $rtoi(STEP_DN_NV * (($realtime - t_dn[r]) / 50.0) + 0.5);
            if (r == 2) vw_uv2 = vw_uv2 - $rtoi(STEP_DN_NV * (($realtime - t_dn[r]) / 50.0) + 0.5);
            if (r == 3) vw_uv3 = vw_uv3 - $rtoi(STEP_DN_NV * (($realtime - t_dn[r]) / 50.0) + 0.5);
        end
    end endgenerate
endmodule
