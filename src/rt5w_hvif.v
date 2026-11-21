/*
 * rt5w_hvif: 3.3 V interface between the level shifters and the analog macro (sky130_fd_sc_hvl cells, 6x2).
 *  - configuration chain: 32 flip-flops clocked by cfg_sclk, {k_code, q_code} = chain (first bit shifted in ends
 *    at bit 31); the outputs move only while the controller is idle
 *  - cell select decoder: wsel = one-hot(wsel_a) when wsel_e, else 0 (addresses >= 20 select nothing)
 * This RTL is the simulation model and the reference of the gate netlist (design/layout/hvif.py).
 * SPDX-License-Identifier: Apache-2.0
 */
`default_nettype none
module rt5w_hvif (
    input  wire        cfg_sdat,
    input  wire        cfg_sclk,
    input  wire [4:0]  wsel_a,
    input  wire        wsel_e,
    output wire [15:0] q_code,
    output wire [15:0] k_code,
    output wire [19:0] wsel
);
    reg [31:0] chain;
    always @(posedge cfg_sclk) chain <= {chain[30:0], cfg_sdat};
    assign {k_code, q_code} = chain;
    assign wsel = wsel_e ? (20'd1 << wsel_a) : 20'd0;
endmodule
