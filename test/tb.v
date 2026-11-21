`default_nettype none
`timescale 1ns / 1ps
/* Testbench wrapper (TinyTapeout style): instantiates tt_um_rt5w_attn with the analog behavioural model. */
module tb ();
  initial begin
    if ($test$plusargs("dump")) $dumpfile("tb.fst");
    if ($test$plusargs("dump")) $dumpvars(0, tb);
    #1;
  end
  reg clk, rst_n, ena;
  reg [7:0] ui_in, uio_in;
  wire [7:0] uo_out, uio_out, uio_oe;
  wire [7:0] ua;
  wire VPWR = 1'b1, VGND = 1'b0;
  tt_um_rt5w_attn user_project (
      .VGND(VGND), .VDPWR(VPWR), .VAPWR(VPWR),
      .ui_in(ui_in), .uo_out(uo_out), .uio_in(uio_in), .uio_out(uio_out), .uio_oe(uio_oe),
      .ua(ua), .ena(ena), .clk(clk), .rst_n(rst_n));
endmodule
