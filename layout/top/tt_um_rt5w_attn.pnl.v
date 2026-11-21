module tt_um_rt5w_attn (VAPWR,
    VDPWR,
    VGND,
    clk,
    ena,
    rst_n,
    ua,
    ui_in,
    uio_in,
    uio_oe,
    uio_out,
    uo_out);
 inout VAPWR;
 inout VDPWR;
 inout VGND;
 input clk;
 input ena;
 input rst_n;
 inout [7:0] ua;
 input [7:0] ui_in;
 input [7:0] uio_in;
 output [7:0] uio_oe;
 output [7:0] uio_out;
 output [7:0] uo_out;

 wire adc_ch0;
 wire adc_ch0_lv;
 wire adc_ch1;
 wire adc_ch1_lv;
 wire adc_ch2;
 wire adc_ch2_lv;
 wire adc_ch3;
 wire adc_ch3_lv;
 wire adc_lat;
 wire adc_lat_lv;
 wire adc_rst;
 wire adc_rst_lv;
 wire bias_en;
 wire bias_en_lv;
 wire cmp;
 wire cmp_lv;
 wire dac0;
 wire dac0_lv;
 wire dac1;
 wire dac1_lv;
 wire dac2;
 wire dac2_lv;
 wire dac3;
 wire dac3_lv;
 wire dac4;
 wire dac4_lv;
 wire dac5;
 wire dac5_lv;
 wire dac6;
 wire dac6_lv;
 wire dac7;
 wire dac7_lv;
 wire g0;
 wire g1;
 wire g2;
 wire g3;
 wire k0_0;
 wire k0_0_lv;
 wire k0_1;
 wire k0_1_lv;
 wire k0_2;
 wire k0_2_lv;
 wire k0_3;
 wire k0_3_lv;
 wire k1_0;
 wire k1_0_lv;
 wire k1_1;
 wire k1_1_lv;
 wire k1_2;
 wire k1_2_lv;
 wire k1_3;
 wire k1_3_lv;
 wire k2_0;
 wire k2_0_lv;
 wire k2_1;
 wire k2_1_lv;
 wire k2_2;
 wire k2_2_lv;
 wire k2_3;
 wire k2_3_lv;
 wire k3_0;
 wire k3_0_lv;
 wire k3_1;
 wire k3_1_lv;
 wire k3_2;
 wire k3_2_lv;
 wire k3_3;
 wire k3_3_lv;
 wire kbias;
 wire nbias;
 wire nc_pump_dn_0;
 wire nc_pump_up_0;
 wire nd0;
 wire nd1;
 wire nd2;
 wire nd3;
 wire ndac;
 wire ng;
 wire out0;
 wire out1;
 wire out2;
 wire out3;
 wire pg;
 wire pump_dn1;
 wire pump_dn1_lv;
 wire pump_dn2;
 wire pump_dn2_lv;
 wire pump_dn3;
 wire pump_dn3_lv;
 wire pump_up1;
 wire pump_up1_lv;
 wire pump_up2;
 wire pump_up2_lv;
 wire pump_up3;
 wire pump_up3_lv;
 wire q0_0;
 wire q0_0_lv;
 wire q0_1;
 wire q0_1_lv;
 wire q0_2;
 wire q0_2_lv;
 wire q0_3;
 wire q0_3_lv;
 wire q1_0;
 wire q1_0_lv;
 wire q1_1;
 wire q1_1_lv;
 wire q1_2;
 wire q1_2_lv;
 wire q1_3;
 wire q1_3_lv;
 wire q2_0;
 wire q2_0_lv;
 wire q2_1;
 wire q2_1_lv;
 wire q2_2;
 wire q2_2_lv;
 wire q2_3;
 wire q2_3_lv;
 wire q3_0;
 wire q3_0_lv;
 wire q3_1;
 wire q3_1_lv;
 wire q3_2;
 wire q3_2_lv;
 wire q3_3;
 wire q3_3_lv;
 wire row0;
 wire row1;
 wire row2;
 wire row3;
 wire vb;
 wire vb_probe_en;
 wire vb_probe_en_lv;
 wire vbn;
 wire vcas;
 wire vmid;
 wire vr;
 wire wsel0;
 wire wsel0_lv;
 wire wsel1;
 wire wsel10;
 wire wsel10_lv;
 wire wsel11;
 wire wsel11_lv;
 wire wsel12;
 wire wsel12_lv;
 wire wsel13;
 wire wsel13_lv;
 wire wsel14;
 wire wsel14_lv;
 wire wsel15;
 wire wsel15_lv;
 wire wsel16;
 wire wsel16_lv;
 wire wsel17;
 wire wsel17_lv;
 wire wsel18;
 wire wsel18_lv;
 wire wsel19;
 wire wsel19_lv;
 wire wsel1_lv;
 wire wsel2;
 wire wsel2_lv;
 wire wsel3;
 wire wsel3_lv;
 wire wsel4;
 wire wsel4_lv;
 wire wsel5;
 wire wsel5_lv;
 wire wsel6;
 wire wsel6_lv;
 wire wsel7;
 wire wsel7_lv;
 wire wsel8;
 wire wsel8_lv;
 wire wsel9;
 wire wsel9_lv;

 rt5w_array xarr (.nd0(nd0),
    .nd1(nd1),
    .nd2(nd2),
    .nd3(nd3),
    .ng(ng),
    .pg(pg),
    .pump_dn1(pump_dn1),
    .pump_dn2(pump_dn2),
    .pump_dn3(pump_dn3),
    .pump_up1(pump_up1),
    .pump_up2(pump_up2),
    .pump_up3(pump_up3),
    .q0_0(q0_0),
    .q0_1(q0_1),
    .q0_2(q0_2),
    .q0_3(q0_3),
    .q1_0(q1_0),
    .q1_1(q1_1),
    .q1_2(q1_2),
    .q1_3(q1_3),
    .q2_0(q2_0),
    .q2_1(q2_1),
    .q2_2(q2_2),
    .q2_3(q2_3),
    .q3_0(q3_0),
    .q3_1(q3_1),
    .q3_2(q3_2),
    .q3_3(q3_3),
    .row0(row0),
    .row1(row1),
    .row2(row2),
    .row3(row3),
    .vbn(vbn),
    .vdd(VAPWR),
    .vmid(vmid),
    .vss(VGND),
    .vw(ua[2]),
    .wsel0(wsel0),
    .wsel1(wsel1),
    .wsel10(wsel10),
    .wsel11(wsel11),
    .wsel12(wsel12),
    .wsel13(wsel13),
    .wsel14(wsel14),
    .wsel15(wsel15),
    .wsel16(wsel16),
    .wsel17(wsel17),
    .wsel18(wsel18),
    .wsel19(wsel19),
    .wsel2(wsel2),
    .wsel3(wsel3),
    .wsel4(wsel4),
    .wsel5(wsel5),
    .wsel6(wsel6),
    .wsel7(wsel7),
    .wsel8(wsel8),
    .wsel9(wsel9));
 rt5w_lsbank xbank (.adc_ch0(adc_ch0),
    .adc_ch0_lv(adc_ch0_lv),
    .adc_ch1(adc_ch1),
    .adc_ch1_lv(adc_ch1_lv),
    .adc_ch2(adc_ch2),
    .adc_ch2_lv(adc_ch2_lv),
    .adc_ch3(adc_ch3),
    .adc_ch3_lv(adc_ch3_lv),
    .adc_lat(adc_lat),
    .adc_lat_lv(adc_lat_lv),
    .adc_rst(adc_rst),
    .adc_rst_lv(adc_rst_lv),
    .bias_en(bias_en),
    .bias_en_lv(bias_en_lv),
    .dac0(dac0),
    .dac0_lv(dac0_lv),
    .dac1(dac1),
    .dac1_lv(dac1_lv),
    .dac2(dac2),
    .dac2_lv(dac2_lv),
    .dac3(dac3),
    .dac3_lv(dac3_lv),
    .dac4(dac4),
    .dac4_lv(dac4_lv),
    .dac5(dac5),
    .dac5_lv(dac5_lv),
    .dac6(dac6),
    .dac6_lv(dac6_lv),
    .dac7(dac7),
    .dac7_lv(dac7_lv),
    .k0_0(k0_0),
    .k0_0_lv(k0_0_lv),
    .k0_1(k0_1),
    .k0_1_lv(k0_1_lv),
    .k0_2(k0_2),
    .k0_2_lv(k0_2_lv),
    .k0_3(k0_3),
    .k0_3_lv(k0_3_lv),
    .k1_0(k1_0),
    .k1_0_lv(k1_0_lv),
    .k1_1(k1_1),
    .k1_1_lv(k1_1_lv),
    .k1_2(k1_2),
    .k1_2_lv(k1_2_lv),
    .k1_3(k1_3),
    .k1_3_lv(k1_3_lv),
    .k2_0(k2_0),
    .k2_0_lv(k2_0_lv),
    .k2_1(k2_1),
    .k2_1_lv(k2_1_lv),
    .k2_2(k2_2),
    .k2_2_lv(k2_2_lv),
    .k2_3(k2_3),
    .k2_3_lv(k2_3_lv),
    .k3_0(k3_0),
    .k3_0_lv(k3_0_lv),
    .k3_1(k3_1),
    .k3_1_lv(k3_1_lv),
    .k3_2(k3_2),
    .k3_2_lv(k3_2_lv),
    .k3_3(k3_3),
    .k3_3_lv(k3_3_lv),
    .pump_dn1(pump_dn1),
    .pump_dn1_lv(pump_dn1_lv),
    .pump_dn2(pump_dn2),
    .pump_dn2_lv(pump_dn2_lv),
    .pump_dn3(pump_dn3),
    .pump_dn3_lv(pump_dn3_lv),
    .pump_up1(pump_up1),
    .pump_up1_lv(pump_up1_lv),
    .pump_up2(pump_up2),
    .pump_up2_lv(pump_up2_lv),
    .pump_up3(pump_up3),
    .pump_up3_lv(pump_up3_lv),
    .q0_0(q0_0),
    .q0_0_lv(q0_0_lv),
    .q0_1(q0_1),
    .q0_1_lv(q0_1_lv),
    .q0_2(q0_2),
    .q0_2_lv(q0_2_lv),
    .q0_3(q0_3),
    .q0_3_lv(q0_3_lv),
    .q1_0(q1_0),
    .q1_0_lv(q1_0_lv),
    .q1_1(q1_1),
    .q1_1_lv(q1_1_lv),
    .q1_2(q1_2),
    .q1_2_lv(q1_2_lv),
    .q1_3(q1_3),
    .q1_3_lv(q1_3_lv),
    .q2_0(q2_0),
    .q2_0_lv(q2_0_lv),
    .q2_1(q2_1),
    .q2_1_lv(q2_1_lv),
    .q2_2(q2_2),
    .q2_2_lv(q2_2_lv),
    .q2_3(q2_3),
    .q2_3_lv(q2_3_lv),
    .q3_0(q3_0),
    .q3_0_lv(q3_0_lv),
    .q3_1(q3_1),
    .q3_1_lv(q3_1_lv),
    .q3_2(q3_2),
    .q3_2_lv(q3_2_lv),
    .q3_3(q3_3),
    .q3_3_lv(q3_3_lv),
    .vb_probe_en(vb_probe_en),
    .vb_probe_en_lv(vb_probe_en_lv),
    .vdd(VAPWR),
    .vddl(VDPWR),
    .vss(VGND),
    .wsel0(wsel0),
    .wsel0_lv(wsel0_lv),
    .wsel1(wsel1),
    .wsel10(wsel10),
    .wsel10_lv(wsel10_lv),
    .wsel11(wsel11),
    .wsel11_lv(wsel11_lv),
    .wsel12(wsel12),
    .wsel12_lv(wsel12_lv),
    .wsel13(wsel13),
    .wsel13_lv(wsel13_lv),
    .wsel14(wsel14),
    .wsel14_lv(wsel14_lv),
    .wsel15(wsel15),
    .wsel15_lv(wsel15_lv),
    .wsel16(wsel16),
    .wsel16_lv(wsel16_lv),
    .wsel17(wsel17),
    .wsel17_lv(wsel17_lv),
    .wsel18(wsel18),
    .wsel18_lv(wsel18_lv),
    .wsel19(wsel19),
    .wsel19_lv(wsel19_lv),
    .wsel1_lv(wsel1_lv),
    .wsel2(wsel2),
    .wsel2_lv(wsel2_lv),
    .wsel3(wsel3),
    .wsel3_lv(wsel3_lv),
    .wsel4(wsel4),
    .wsel4_lv(wsel4_lv),
    .wsel5(wsel5),
    .wsel5_lv(wsel5_lv),
    .wsel6(wsel6),
    .wsel6_lv(wsel6_lv),
    .wsel7(wsel7),
    .wsel7_lv(wsel7_lv),
    .wsel8(wsel8),
    .wsel8_lv(wsel8_lv),
    .wsel9(wsel9),
    .wsel9_lv(wsel9_lv));
 rt5w_bias xbias (.bias_en(bias_en),
    .iref(ua[0]),
    .kbias(kbias),
    .nbias(nbias),
    .nd0(nd0),
    .nd1(nd1),
    .nd2(nd2),
    .nd3(nd3),
    .ndac(ndac),
    .ng(ng),
    .pg(pg),
    .vbn(vbn),
    .vcas(vcas),
    .vdd(VAPWR),
    .vmid(vmid),
    .vr(vr),
    .vss(VGND));
 rt5w_digital xdig (.clk(clk),
    .ena(ena),
    .rst_n(rst_n),
    .bias_en(bias_en_lv),
    .vb_probe_en(vb_probe_en_lv),
    .adc_rst(adc_rst_lv),
    .adc_lat(adc_lat_lv),
    .adc_cmp(cmp_lv),
    .VPWR(VDPWR),
    .VGND(VGND),
    .adc_ch({adc_ch3_lv,
    adc_ch2_lv,
    adc_ch1_lv,
    adc_ch0_lv}),
    .adc_dac({dac7_lv,
    dac6_lv,
    dac5_lv,
    dac4_lv,
    dac3_lv,
    dac2_lv,
    dac1_lv,
    dac0_lv}),
    .k_code({k3_3_lv,
    k3_2_lv,
    k3_1_lv,
    k3_0_lv,
    k2_3_lv,
    k2_2_lv,
    k2_1_lv,
    k2_0_lv,
    k1_3_lv,
    k1_2_lv,
    k1_1_lv,
    k1_0_lv,
    k0_3_lv,
    k0_2_lv,
    k0_1_lv,
    k0_0_lv}),
    .pump_dn({pump_dn3_lv,
    pump_dn2_lv,
    pump_dn1_lv,
    nc_pump_dn_0}),
    .pump_up({pump_up3_lv,
    pump_up2_lv,
    pump_up1_lv,
    nc_pump_up_0}),
    .q_code({q3_3_lv,
    q3_2_lv,
    q3_1_lv,
    q3_0_lv,
    q2_3_lv,
    q2_2_lv,
    q2_1_lv,
    q2_0_lv,
    q1_3_lv,
    q1_2_lv,
    q1_1_lv,
    q1_0_lv,
    q0_3_lv,
    q0_2_lv,
    q0_1_lv,
    q0_0_lv}),
    .ui_in({ui_in[7],
    ui_in[6],
    ui_in[5],
    ui_in[4],
    ui_in[3],
    ui_in[2],
    ui_in[1],
    ui_in[0]}),
    .uio_in({uio_in[7],
    uio_in[6],
    uio_in[5],
    uio_in[4],
    uio_in[3],
    uio_in[2],
    uio_in[1],
    uio_in[0]}),
    .uio_oe({uio_oe[7],
    uio_oe[6],
    uio_oe[5],
    uio_oe[4],
    uio_oe[3],
    uio_oe[2],
    uio_oe[1],
    uio_oe[0]}),
    .uio_out({uio_out[7],
    uio_out[6],
    uio_out[5],
    uio_out[4],
    uio_out[3],
    uio_out[2],
    uio_out[1],
    uio_out[0]}),
    .uo_out({uo_out[7],
    uo_out[6],
    uo_out[5],
    uo_out[4],
    uo_out[3],
    uo_out[2],
    uo_out[1],
    uo_out[0]}),
    .wsel({wsel19_lv,
    wsel18_lv,
    wsel17_lv,
    wsel16_lv,
    wsel15_lv,
    wsel14_lv,
    wsel13_lv,
    wsel12_lv,
    wsel11_lv,
    wsel10_lv,
    wsel9_lv,
    wsel8_lv,
    wsel7_lv,
    wsel6_lv,
    wsel5_lv,
    wsel4_lv,
    wsel3_lv,
    wsel2_lv,
    wsel1_lv,
    wsel0_lv}));
 rt5w_kscale xk0 (.g(g0),
    .k0(k0_0),
    .k1(k0_1),
    .k2(k0_2),
    .k3(k0_3),
    .row(row0),
    .vdd(VAPWR),
    .vss(VGND));
 rt5w_kscale xk1 (.g(g1),
    .k0(k1_0),
    .k1(k1_1),
    .k2(k1_2),
    .k3(k1_3),
    .row(row1),
    .vdd(VAPWR),
    .vss(VGND));
 rt5w_kscale xk2 (.g(g2),
    .k0(k2_0),
    .k1(k2_1),
    .k2(k2_2),
    .k3(k2_3),
    .row(row2),
    .vdd(VAPWR),
    .vss(VGND));
 rt5w_kscale xk3 (.g(g3),
    .k0(k3_0),
    .k1(k3_1),
    .k2(k3_2),
    .k3(k3_3),
    .row(row3),
    .vdd(VAPWR),
    .vss(VGND));
 rt5w_lsdn xlsdn (.in(cmp),
    .out(cmp_lv),
    .vddl(VDPWR),
    .vss(VGND));
 rt5w_readout xro (.adc_ch0(adc_ch0),
    .adc_ch1(adc_ch1),
    .adc_ch2(adc_ch2),
    .adc_ch3(adc_ch3),
    .adc_lat(adc_lat),
    .adc_rst(adc_rst),
    .cmp(cmp),
    .dac0(dac0),
    .dac1(dac1),
    .dac2(dac2),
    .dac3(dac3),
    .dac4(dac4),
    .dac5(dac5),
    .dac6(dac6),
    .dac7(dac7),
    .ndac(ndac),
    .out0(out0),
    .out1(out1),
    .out2(out2),
    .out3(out3),
    .vcas(vcas),
    .vdd(VAPWR),
    .vr(vr),
    .vss(VGND));
 rt5w_softmax xsm (.g0(g0),
    .g1(g1),
    .g2(g2),
    .g3(g3),
    .kbias(kbias),
    .nbias(nbias),
    .out0(out0),
    .out1(out1),
    .out2(out2),
    .out3(out3),
    .vb(vb),
    .vcas(vcas),
    .vdd(VAPWR),
    .vr(vr),
    .vss(VGND));
 rt5w_vbbuf xvb (.en(vb_probe_en),
    .pad(ua[1]),
    .vb(vb),
    .vbn(vbn),
    .vdd(VAPWR),
    .vss(VGND));
