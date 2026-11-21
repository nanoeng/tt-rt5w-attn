/*
 * RT5W attention-head controller (digital half of tt_um_rt5w_attn)
 * SPDX-License-Identifier: Apache-2.0
 *
 * - SPI slave (mode 0, 16-bit frames: [15]=write, [14:8]=addr, [7:0]=data; MISO returns
 *   the addressed register during the data byte of a read frame).
 * - Pass FSM: WAKE (bias start-up) -> SETTLE (window) -> 4 x 8-bit SAR conversions -> DONE.
 * - SS-SGD (sign-sign, rev 3): after a calibration pass, rows 1..3 get one UP/DN pump
 *   pulse of PULSE_W cycles when their code differs from the target; equal -> no pulse;
 *   row 0 is pinned (never pumped) to fix the common mode.
 * - Weight-cell write/read select: one-hot wsel[19:0] connects ua[2] to one of 20 C_W cells (16 keys + 4 row trims).
 *   6x2 (20 Nov 2026): wsel leaves the controller as address + enable and q/k codes as a serial chain; both are
 *   decoded at 3.3 V by rt5w_hvif (sky130_fd_sc_hvl cells), so 30 instead of 74 lines cross the 1.8 -> 3.3 V shifters.
 * - SAR bit (ADCT clocks, default 16): adc_rst (1st clock) resets the integrator, the selected share and the DAC
 *   integrate, adc_lat (clock ADCT-1) fires the StrongARM latch, the bit is decided on the last clock from adc_cmp.
 *   adc_ch[3:0] is the one-hot channel select (0 outside conversions). All analog-facing strobes are registered.
 */
`default_nettype none

module rt5w_ctrl (
    input  wire        clk,
    input  wire        rst_n,
    // SPI
    input  wire        sck,
    input  wire        mosi,
    input  wire        cs_n,
    output wire        miso,
    // direct strobes
    input  wire        start_pin,
    // status
    output wire        busy,
    output wire        valid,
    output wire [7:0]  result,          // code selected by OUT_SEL
    // to analog macro
    output wire        bias_en,
    output wire        cfg_sdat,        // 3.3 V configuration chain (32 bits {k23,k01,q23,q01}, MSB first)
    output wire        cfg_sclk,        //   q/k IDAC codes live in the chain (rt5w_hvif), not on 32 wires
    output wire [3:0]  adc_ch,          // one-hot channel select
    output reg         adc_rst,         // integrator reset (first clock of a bit)
    output reg         adc_lat,         // comparator latch strobe (clock ADCT-1 of a bit)
    output reg  [7:0]  adc_dac,
    input  wire        adc_cmp,         // 1: I_share > I_dac (held by the SR latch after adc_lat)
    output wire [3:0]  pump_up,
    output wire [3:0]  pump_dn,
    output wire [4:0]  wsel_a,          // cell select address, decoded to one-hot on the 3.3 V side
    output wire        wsel_e,          //   enable; drops one cycle before the address changes (break-before-make)
    output wire        vb_probe_en
);
    // ------------------------------------------------------------------ SPI (2-FF synchronised)
    reg [2:0] sck_s, cs_s; reg [1:0] mosi_s;
    always @(posedge clk or negedge rst_n)
        if (!rst_n) begin sck_s <= 3'b000; cs_s <= 3'b111; mosi_s <= 2'b00; end
        else begin sck_s <= {sck_s[1:0], sck}; cs_s <= {cs_s[1:0], cs_n}; mosi_s <= {mosi_s[0], mosi}; end
    wire sck_rise = (sck_s[2:1] == 2'b01);
    wire sck_fall = (sck_s[2:1] == 2'b10);
    wire cs_act   = ~cs_s[1];
    wire cs_start = (cs_s[2:1] == 2'b10);

    reg [4:0]  bitcnt;
    /* verilator lint_off UNUSEDSIGNAL */
    reg [15:0] shreg;   // bit 15 shifts out unused
    /* verilator lint_on UNUSEDSIGNAL */
    reg [7:0]  miso_sh;
    reg        wr_stb;
    reg [6:0]  wr_addr; reg [7:0] wr_data;
    wire [7:0] rd_data;

    always @(posedge clk or negedge rst_n)
        if (!rst_n) begin bitcnt <= 0; shreg <= 0; miso_sh <= 0; wr_stb <= 0; wr_addr <= 0; wr_data <= 0; end
        else begin
            wr_stb <= 1'b0;
            if (cs_start) begin bitcnt <= 0; miso_sh <= 8'h00; end
            else if (cs_act && sck_rise) begin
                shreg  <= {shreg[14:0], mosi_s[1]};
                bitcnt <= bitcnt + 1'b1;
                if (bitcnt == 5'd15) begin
                    if (shreg[14]) begin wr_stb <= 1'b1; wr_addr <= shreg[13:7]; wr_data <= {shreg[6:0], mosi_s[1]}; end
                end
            end else if (cs_act && sck_fall) begin
                if (bitcnt == 5'd8) miso_sh <= rd_data;              // address captured -> load data
                else if (bitcnt > 5'd8) miso_sh <= {miso_sh[6:0], 1'b0};
            end
        end
    // address of the current frame is in shreg[6:0] once 8 bits are in (bit 15 = R/W)
    wire [6:0] rd_addr = shreg[6:0];
    assign miso = cs_act ? miso_sh[7] : 1'b0;

    // ------------------------------------------------------------------ registers
    reg [7:0] ctrl;          // 0x00: [0] bias_force [1] gate_after_pass [2] start [3] cal_pass [4] vb_probe [5] cont
    reg [7:0] q01, q23;      // 0x01,0x02
    reg [7:0] k01, k23;      // 0x03,0x04
    reg [15:0] win;          // 0x05/0x06 settle window (cycles), default 1000 = 50 us @ 20 MHz
    reg [7:0] wake;          // 0x07 bias wake-up (cycles x4), default 30 -> 121 cycles = 6 us @ 20 MHz
    reg [4:0] adct;          // 0x08 SAR bit time (cycles), default 16, minimum 4
    reg [5:0] wselr;         // 0x09: [5] enable [4:0] cell
    reg [3:0] pulse_w;       // 0x0A pump pulse width (cycles), default 1
    reg [1:0] out_sel;       // 0x0B
    reg [7:0] tgt [0:3];     // 0x0C..0x0F SS-SGD targets
    reg [7:0] res [0:3];     // 0x10..0x13 results (RO)
    reg [7:0] npass;         // 0x15 pass counter (RO)
    reg [3:0] last_up, last_dn; // 0x16 (RO) last update {dn,up}
    reg       valid_r, cal_mode;

    localparam S_IDLE = 3'd0, S_WAKE = 3'd1, S_SETTLE = 3'd2, S_CONV = 3'd3, S_UPD = 3'd4, S_DONE = 3'd5;
    reg [2:0] st;

    wire start_req = (wr_stb && wr_addr == 7'h00 && (wr_data[2] | wr_data[3]));
    reg  [2:0] start_s;      // 2-FF synchroniser + edge detect (asynchronous pin)
    always @(posedge clk or negedge rst_n) if (!rst_n) start_s <= 3'b000; else start_s <= {start_s[1:0], start_pin};
    wire start_pin_rise = start_s[1] & ~start_s[2];
    wire start_now = start_req || start_pin_rise;
    reg  start_pend, start_cal;          // a start that waits for the configuration chain
    wire cfg_ok;
    wire start_go = (st == S_IDLE) && (start_now || start_pend) && cfg_ok;
    wire start_cal_v = start_now ? (start_req ? wr_data[3] : 1'b0) : start_cal;
    always @(posedge clk or negedge rst_n)
        if (!rst_n) begin start_pend <= 1'b0; start_cal <= 1'b0; end
        else if (start_go) start_pend <= 1'b0;
        else if (st == S_IDLE && start_now) begin start_pend <= 1'b1; start_cal <= start_cal_v; end

    integer i;
    always @(posedge clk or negedge rst_n)
        if (!rst_n) begin
            ctrl <= 8'h02; q01 <= 0; q23 <= 0; k01 <= 0; k23 <= 0; win <= 16'd1000; wake <= 8'd30; adct <= 5'd16;
            wselr <= 0; pulse_w <= 4'd1; out_sel <= 0;
            for (i = 0; i < 4; i = i + 1) tgt[i] <= 0;
        end else if (wr_stb) begin
            case (wr_addr)
                7'h00: ctrl <= {wr_data[7:4], 2'b00, wr_data[1:0]};   // start bits self-clear
                7'h01: q01 <= wr_data; 7'h02: q23 <= wr_data;
                7'h03: k01 <= wr_data; 7'h04: k23 <= wr_data;
                7'h05: win[7:0] <= wr_data; 7'h06: win[15:8] <= wr_data;
                7'h07: wake <= wr_data; 7'h08: adct <= (wr_data[4:0] < 5'd4) ? 5'd4 : wr_data[4:0];
                7'h09: wselr <= wr_data[5:0];
                7'h0A: pulse_w <= (wr_data[3:0] == 0) ? 4'd1 : wr_data[3:0];
                7'h0B: out_sel <= wr_data[1:0];
                7'h0C: tgt[0] <= wr_data; 7'h0D: tgt[1] <= wr_data; 7'h0E: tgt[2] <= wr_data; 7'h0F: tgt[3] <= wr_data;
                default: ;
            endcase
        end

    reg [7:0] rd_mux;
    always @(*) begin
        case (rd_addr)
            7'h00: rd_mux = ctrl; 7'h01: rd_mux = q01; 7'h02: rd_mux = q23; 7'h03: rd_mux = k01; 7'h04: rd_mux = k23;
            7'h05: rd_mux = win[7:0]; 7'h06: rd_mux = win[15:8]; 7'h07: rd_mux = wake; 7'h08: rd_mux = {3'b000, adct};
            7'h09: rd_mux = {2'b00, wselr}; 7'h0A: rd_mux = {4'h0, pulse_w}; 7'h0B: rd_mux = {6'h00, out_sel};
            7'h0C: rd_mux = tgt[0]; 7'h0D: rd_mux = tgt[1]; 7'h0E: rd_mux = tgt[2]; 7'h0F: rd_mux = tgt[3];
            7'h10: rd_mux = res[0]; 7'h11: rd_mux = res[1]; 7'h12: rd_mux = res[2]; 7'h13: rd_mux = res[3];
            7'h14: rd_mux = {4'h0, cal_mode, valid_r, (st != S_IDLE), 1'b0};
            7'h15: rd_mux = npass; 7'h16: rd_mux = {last_dn, last_up};
            7'h7F: rd_mux = 8'h5A;   // ID
            default: rd_mux = 8'h00;
        endcase
    end
    assign rd_data = rd_mux;

    // ------------------------------------------------------------------ pass FSM + SAR + SS-SGD
    reg [16:0] cnt;           // down-counter; bit 16 (borrow) ends the interval -> no wide zero-detect
    reg [7:0]  mask;          // SAR one-hot bit under test (no variable shifter on the critical path)
    reg [4:0]  tcnt;
    reg [1:0]  adc_sel;
    reg [3:0]  up_r, dn_r;
    reg [3:0]  pcnt;

    always @(posedge clk or negedge rst_n)
        if (!rst_n) begin
            st <= S_IDLE; cnt <= 0; mask <= 0; tcnt <= 0; adc_sel <= 0; adc_dac <= 0; valid_r <= 0; cal_mode <= 0;
            adc_rst <= 1'b0; adc_lat <= 1'b0;
            up_r <= 0; dn_r <= 0; pcnt <= 0; npass <= 0; last_up <= 0; last_dn <= 0;
            for (i = 0; i < 4; i = i + 1) res[i] <= 0;
        end else case (st)
            S_IDLE: if (start_go) begin
                        cal_mode <= start_cal_v;
                        valid_r <= 1'b0; cnt <= {7'd0, wake, 2'b00}; st <= S_WAKE;
                    end
            S_WAKE:   if (cnt[16]) begin cnt <= {1'b0, win}; st <= S_SETTLE; end else cnt <= cnt - 1'b1;
            S_SETTLE: if (cnt[16]) begin adc_sel <= 0; mask <= 8'h80; adc_dac <= 8'h80; tcnt <= adct; st <= S_CONV;
                                         adc_rst <= 1'b1; end
                      else cnt <= cnt - 1'b1;
            S_CONV: begin
                adc_rst <= 1'b0;
                adc_lat <= (tcnt == 5'd3);                  // high during the clock where tcnt == 2
                if (tcnt != 1) tcnt <= tcnt - 1'b1;
                else begin
                    tcnt <= adct;
                    adc_rst <= 1'b1;                         // next bit (or next channel) starts with a reset
                    // decide current bit: keep it if I_share > I_dac
                    if (mask[0]) begin
                        res[adc_sel] <= adc_cmp ? adc_dac : (adc_dac & 8'hFE);
                        if (adc_sel == 2'd3) begin
                            adc_rst <= 1'b0;
                            npass <= npass + 1'b1;
                            if (cal_mode) st <= S_UPD; else begin valid_r <= 1'b1; st <= S_DONE; end
                        end else begin adc_sel <= adc_sel + 1'b1; adc_dac <= 8'h80; mask <= 8'h80; end
                    end else begin
                        adc_dac <= (adc_cmp ? adc_dac : (adc_dac & ~mask)) | {1'b0, mask[7:1]};
                        mask <= {1'b0, mask[7:1]};
                    end
                end
            end
            S_UPD: begin   // sign-sign rule, row 0 pinned, equal codes -> no pulse
                if (pcnt == 0 && up_r == 0 && dn_r == 0 && !valid_r) begin
                    for (i = 1; i < 4; i = i + 1) begin
                        up_r[i] <= (res[i] < tgt[i]);
                        dn_r[i] <= (res[i] > tgt[i]);
                    end
                    up_r[0] <= 1'b0; dn_r[0] <= 1'b0;
                    pcnt <= pulse_w; valid_r <= 1'b1;     // valid marks "update issued"
                end else if (pcnt != 0) begin
                    pcnt <= pcnt - 1'b1;
                    if (pcnt == 1) begin last_up <= up_r; last_dn <= dn_r; up_r <= 0; dn_r <= 0; st <= S_DONE; end
                end
            end
            S_DONE: begin st <= S_IDLE; end
            default: st <= S_IDLE;
        endcase

    wire passing = (st == S_WAKE) || (st == S_SETTLE) || (st == S_CONV) || (st == S_UPD);
    assign bias_en  = ctrl[0] | passing | ~ctrl[1];   // pumps are biased too (S_UPD)
    assign adc_ch   = (st == S_CONV) ? (4'b0001 << adc_sel) : 4'b0000;
    assign pump_up  = (st == S_UPD && pcnt != 0) ? {up_r[3:1], 1'b0} : 4'b0000;
    assign pump_dn  = (st == S_UPD && pcnt != 0) ? {dn_r[3:1], 1'b0} : 4'b0000;
    // 3.3 V configuration chain: shifted only while idle; a pass waits until it is clean. 3 clocks per bit:
    // data, sclk rise (the chain captures), sclk fall -> setup and hold of one clock at the 3.3 V flops.
    reg        cfg_dirty, cfg_busy, sclk_r, sdat_r;
    reg [1:0]  cfg_ph;
    reg [5:0]  cfg_n;
    wire [31:0] cfg_word = {k23, k01, q23, q01};   // shifted straight from the registers (a write during the
                                                    // shift sets cfg_dirty again -> the chain is re-sent)
    wire cfg_wr = wr_stb && (wr_addr >= 7'h01) && (wr_addr <= 7'h04);
    assign cfg_ok = !cfg_busy && !cfg_dirty && !cfg_wr;
    always @(posedge clk or negedge rst_n)
        if (!rst_n) begin
            cfg_dirty <= 1'b1; cfg_busy <= 1'b0; sclk_r <= 1'b0; sdat_r <= 1'b0; cfg_ph <= 0; cfg_n <= 0;
        end else begin
            if (cfg_wr) cfg_dirty <= 1'b1;
            if (!cfg_busy) begin
                if (cfg_dirty && !cfg_wr && st == S_IDLE) begin
                    cfg_n <= 6'd32; cfg_ph <= 0; cfg_busy <= 1'b1; cfg_dirty <= 1'b0;
                end
            end else case (cfg_ph)
                2'd0: if (cfg_n == 0) cfg_busy <= 1'b0;
                      else begin sdat_r <= cfg_word[cfg_n[4:0] - 5'd1]; cfg_n <= cfg_n - 1'b1; cfg_ph <= 2'd1; end
                2'd1: begin sclk_r <= 1'b1; cfg_ph <= 2'd2; end
                default: begin sclk_r <= 1'b0; cfg_ph <= 2'd0; end
            endcase
        end
    assign cfg_sdat = sdat_r;
    assign cfg_sclk = sclk_r;
    // cell select: enable off for a clock before the address moves, address settles a clock before enable returns
    reg [4:0] wsel_aq;
    reg       wsel_eq;
    wire wsel_want = wselr[5] & ~passing & (wselr[4:0] < 5'd20);   // never write a cell during a pass
    always @(posedge clk or negedge rst_n)
        if (!rst_n) begin wsel_aq <= 5'd0; wsel_eq <= 1'b0; end
        else if (wselr[4:0] != wsel_aq) begin wsel_eq <= 1'b0; if (!wsel_eq) wsel_aq <= wselr[4:0]; end
        else wsel_eq <= wsel_want;
    assign wsel_a = wsel_aq;
    assign wsel_e = wsel_eq;
    assign vb_probe_en = ctrl[4];
    assign busy     = (st != S_IDLE) | start_pend;
    assign valid    = valid_r;
    assign result   = res[out_sel];
endmodule
