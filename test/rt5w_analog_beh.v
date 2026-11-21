/*
 * Behavioural model of the RT5W analog macro for RTL / cocotb simulation (NOT for synthesis).
 * Numbers come from the ngspice characterisation in sim/results (JSON):
 *   x_j   = clip(XS * ks_j * sum_m q_m k_jm * g_j, 0, 18)   (scores in e-folds of n*U_T)
 *   a_j   = softmax(x)_j   (+ per-row gain mismatch gamma_j, settling tau)
 *   cmp   = 255*a_sel + 0.5 + cmp_off  >  dac      (SAR yields round(255 a))
 *   pump  : V_w step +STEP_UP / -STEP_DN mV per 50 ns of pulse (one 20 MHz clock);  g_j = exp(V_w,j / nUT)
 * Keys k_jm (8-bit) and mismatch are set through backdoor regs (kflat, gam_ppm*).
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

    parameter real XMAX     = 18.0;
    parameter real NUT_MV   = 52.8;     // PMOS array n*U_T: sky130 key-cell schematic (design/tb/tech.py, tt 27 C)
    parameter real STEP_UP  = 0.141;    // mV per 50 ns pulse: steered pump, 3.7 nA into 1 pF (sim/results/weight_cell.json, TT)
    parameter real STEP_DN  = 0.120;    // 16 % UP/DN asymmetry at TT (worst measured)
    parameter real TAU_NS   = 6000.0;   // share settling time constant (see softmax_tran)
    parameter real XS_DEN   = 15.0*15.0*255.0*4.0;  // full-scale product

    reg  [127:0] kflat = 128'd0;                    // backdoor: k_jm at [8*(4j+m) +: 8]
    integer gam_ppm0 = 0, gam_ppm1 = 0, gam_ppm2 = 0, gam_ppm3 = 0;   // backdoor: row gain mismatch
    integer cmp_off_mlsb = 0;                       // backdoor: comparator offset (milli-LSB)
    real vw0 = 0.0, vw1 = 0.0, vw2 = 0.0, vw3 = 0.0; // trim-cell voltages relative to mid (mV)
    real t_on;                                      // time of last bias/input change
    real x0, x1, x2, x3, a0, a1, a2, a3, ssum, m, settle, sh, sh2, settle2;
    real t_up [0:3]; real t_dn [0:3];

    function real clip(input real v); clip = (v < 0.0) ? 0.0 : ((v > XMAX) ? XMAX : v); endfunction
    function real kk(input integer j, input integer mm); kk = kflat[8*(4*j+mm) +: 8]; endfunction
    function real qq(input integer mm); qq = q_code[4*mm +: 4]; endfunction
    function real ks(input integer j); ks = k_code[4*j +: 4]; endfunction
    function real score(input integer j);
        integer mm; real acc;
        begin acc = 0.0; for (mm = 0; mm < 4; mm = mm + 1) acc = acc + qq(mm) * kk(j, mm);
              score = XMAX * ks(j) * acc / XS_DEN; end
    endfunction

    always @(posedge bias_en or q_code or k_code or kflat) t_on = $realtime;

    // explicit sensitivity: signals read inside functions are not in @* for every simulator
    always @(q_code or k_code or kflat or vw0 or vw1 or vw2 or vw3 or gam_ppm0 or gam_ppm1 or gam_ppm2 or gam_ppm3) begin
        x0 = clip(score(0) * (1.0 + gam_ppm0 * 1e-6) * $exp(vw0 / NUT_MV));
        x1 = clip(score(1) * (1.0 + gam_ppm1 * 1e-6) * $exp(vw1 / NUT_MV));
        x2 = clip(score(2) * (1.0 + gam_ppm2 * 1e-6) * $exp(vw2 / NUT_MV));
        x3 = clip(score(3) * (1.0 + gam_ppm3 * 1e-6) * $exp(vw3 / NUT_MV));
        m = x0; if (x1 > m) m = x1; if (x2 > m) m = x2; if (x3 > m) m = x3;
        a0 = $exp(x0 - m); a1 = $exp(x1 - m); a2 = $exp(x2 - m); a3 = $exp(x3 - m);
        ssum = a0 + a1 + a2 + a3; a0 = a0 / ssum; a1 = a1 / ssum; a2 = a2 / ssum; a3 = a3 / ssum;
    end

    // comparator: re-evaluated when its inputs change and on a 20 ns tick (settling advances in time)
    reg tick = 0; always #20 tick = ~tick;
    always @(tick or adc_dac or adc_sel or adc_en or bias_en or a0 or a1 or a2 or a3) begin
        settle2 = bias_en ? (1.0 - $exp(-($realtime - t_on) / TAU_NS)) : 0.0;
        case (adc_sel) 2'd0: sh = a0; 2'd1: sh = a1; 2'd2: sh = a2; default: sh = a3; endcase
        sh2 = 0.25 + (sh - 0.25) * settle2;      // unsettled share still moving from uniform (0.25)
        cmp_now = adc_en && bias_en && ((255.0 * sh2 + 0.5 + cmp_off_mlsb * 1e-3) > adc_dac);
    end

    // charge pumps: step per 20 ns of pulse; row 0 has no pump in silicon (ignored here too)
    genvar r;
    generate for (r = 1; r < 4; r = r + 1) begin : g_pump
        always @(posedge pump_up[r]) t_up[r] = $realtime;
        always @(negedge pump_up[r]) begin
            if (r == 1) vw1 = vw1 + STEP_UP * (($realtime - t_up[r]) / 50.0);
            if (r == 2) vw2 = vw2 + STEP_UP * (($realtime - t_up[r]) / 50.0);
            if (r == 3) vw3 = vw3 + STEP_UP * (($realtime - t_up[r]) / 50.0);
        end
        always @(posedge pump_dn[r]) t_dn[r] = $realtime;
        always @(negedge pump_dn[r]) begin
            if (r == 1) vw1 = vw1 - STEP_DN * (($realtime - t_dn[r]) / 50.0);
            if (r == 2) vw2 = vw2 - STEP_DN * (($realtime - t_dn[r]) / 50.0);
            if (r == 3) vw3 = vw3 - STEP_DN * (($realtime - t_dn[r]) / 50.0);
        end
    end endgenerate

endmodule
