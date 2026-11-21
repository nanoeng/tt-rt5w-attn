v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {rt5w_analog: bias -> 4x4 array -> softmax -> readout;  V_B buffer;  ua0 I_u monitor, ua1 V_B, ua2 vw} -400 -1100 0 0 0.6 0.6 {}
N 0 -570 0 -590 {lab=vdd}
C {vdd.sym} 0 -590 0 0 {name=r1 lab=vdd}
N 600 -930 600 -950 {lab=vdd}
C {vdd.sym} 600 -950 0 0 {name=r2 lab=vdd}
N 900 -870 900 -890 {lab=vdd}
C {vdd.sym} 900 -890 0 0 {name=r3 lab=vdd}
N 900 -670 900 -690 {lab=vdd}
C {vdd.sym} 900 -690 0 0 {name=r4 lab=vdd}
N 900 -470 900 -490 {lab=vdd}
C {vdd.sym} 900 -490 0 0 {name=r5 lab=vdd}
N 900 -270 900 -290 {lab=vdd}
C {vdd.sym} 900 -290 0 0 {name=r6 lab=vdd}
N 1200 40 1200 20 {lab=vdd}
C {vdd.sym} 1200 20 0 0 {name=r7 lab=vdd}
N 1300 -510 1300 -530 {lab=vdd}
C {vdd.sym} 1300 -530 0 0 {name=r8 lab=vdd}
N 1800 -640 1800 -660 {lab=vdd}
C {vdd.sym} 1800 -660 0 0 {name=r9 lab=vdd}
N 0 -230 0 -210 {lab=vss}
C {gnd.sym} 0 -210 0 0 {name=r10 lab=vss}
N 600 130 600 150 {lab=vss}
C {gnd.sym} 600 150 0 0 {name=r11 lab=vss}
N 900 -730 900 -710 {lab=vss}
C {gnd.sym} 900 -710 0 0 {name=r12 lab=vss}
N 900 -530 900 -510 {lab=vss}
C {gnd.sym} 900 -510 0 0 {name=r13 lab=vss}
N 900 -330 900 -310 {lab=vss}
C {gnd.sym} 900 -310 0 0 {name=r14 lab=vss}
N 900 -130 900 -110 {lab=vss}
C {gnd.sym} 900 -110 0 0 {name=r15 lab=vss}
N 1200 160 1200 180 {lab=vss}
C {gnd.sym} 1200 180 0 0 {name=r16 lab=vss}
N 1300 -290 1300 -270 {lab=vss}
C {gnd.sym} 1300 -270 0 0 {name=r17 lab=vss}
N 1800 -160 1800 -140 {lab=vss}
C {gnd.sym} 1800 -140 0 0 {name=r18 lab=vss}
C {lab_pin.sym} -700 -900 0 0 {name=l19 sig_type=std_logic lab=bias_en}
C {lab_pin.sym} -100 -530 0 0 {name=l20 sig_type=std_logic lab=bias_en}
C {lab_pin.sym} 100 -530 0 0 {name=l21 sig_type=std_logic lab=nbias}
C {lab_pin.sym} 1200 -390 0 0 {name=l22 sig_type=std_logic lab=nbias}
C {lab_pin.sym} 100 -510 0 0 {name=l23 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 1200 -370 0 0 {name=l24 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 100 -490 0 0 {name=l25 sig_type=std_logic lab=nd0}
C {lab_pin.sym} 500 -570 0 0 {name=l26 sig_type=std_logic lab=nd0}
C {lab_pin.sym} 100 -470 0 0 {name=l27 sig_type=std_logic lab=nd1}
C {lab_pin.sym} 500 -550 0 0 {name=l28 sig_type=std_logic lab=nd1}
C {lab_pin.sym} 100 -450 0 0 {name=l29 sig_type=std_logic lab=nd2}
C {lab_pin.sym} 500 -530 0 0 {name=l30 sig_type=std_logic lab=nd2}
C {lab_pin.sym} 100 -430 0 0 {name=l31 sig_type=std_logic lab=nd3}
C {lab_pin.sym} 500 -510 0 0 {name=l32 sig_type=std_logic lab=nd3}
C {lab_pin.sym} 100 -410 0 0 {name=l33 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 1700 -520 0 0 {name=l34 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 100 -370 0 0 {name=l35 sig_type=std_logic lab=pg}
C {lab_pin.sym} 500 50 0 0 {name=l36 sig_type=std_logic lab=pg}
C {lab_pin.sym} 100 -350 0 0 {name=l37 sig_type=std_logic lab=ng}
C {lab_pin.sym} 500 70 0 0 {name=l38 sig_type=std_logic lab=ng}
C {lab_pin.sym} 100 -290 0 0 {name=l39 sig_type=std_logic lab=vmid}
C {lab_pin.sym} 500 90 0 0 {name=l40 sig_type=std_logic lab=vmid}
C {lab_pin.sym} 100 -270 0 0 {name=l41 sig_type=std_logic lab=ua0}
C {lab_pin.sym} 2300 -860 0 0 {name=l42 sig_type=std_logic lab=ua0}
C {lab_pin.sym} 700 -890 0 0 {name=l43 sig_type=std_logic lab=ua2}
C {lab_pin.sym} 2300 -780 0 0 {name=l44 sig_type=std_logic lab=ua2}
C {lab_pin.sym} 700 -870 0 0 {name=l45 sig_type=std_logic lab=row0}
C {lab_pin.sym} 1000 -830 0 0 {name=l46 sig_type=std_logic lab=row0}
C {lab_pin.sym} 700 -850 0 0 {name=l47 sig_type=std_logic lab=row1}
C {lab_pin.sym} 1000 -630 0 0 {name=l48 sig_type=std_logic lab=row1}
C {lab_pin.sym} 700 -830 0 0 {name=l49 sig_type=std_logic lab=row2}
C {lab_pin.sym} 1000 -430 0 0 {name=l50 sig_type=std_logic lab=row2}
C {lab_pin.sym} 700 -810 0 0 {name=l51 sig_type=std_logic lab=row3}
C {lab_pin.sym} 1000 -230 0 0 {name=l52 sig_type=std_logic lab=row3}
C {lab_pin.sym} -700 -860 0 0 {name=l53 sig_type=std_logic lab=q0_0}
C {lab_pin.sym} 500 -890 0 0 {name=l54 sig_type=std_logic lab=q0_0}
C {lab_pin.sym} -700 -820 0 0 {name=l55 sig_type=std_logic lab=q0_1}
C {lab_pin.sym} 500 -870 0 0 {name=l56 sig_type=std_logic lab=q0_1}
C {lab_pin.sym} -700 -780 0 0 {name=l57 sig_type=std_logic lab=q0_2}
C {lab_pin.sym} 500 -850 0 0 {name=l58 sig_type=std_logic lab=q0_2}
C {lab_pin.sym} -700 -740 0 0 {name=l59 sig_type=std_logic lab=q0_3}
C {lab_pin.sym} 500 -830 0 0 {name=l60 sig_type=std_logic lab=q0_3}
C {lab_pin.sym} -700 -700 0 0 {name=l61 sig_type=std_logic lab=q1_0}
C {lab_pin.sym} 500 -810 0 0 {name=l62 sig_type=std_logic lab=q1_0}
C {lab_pin.sym} -700 -660 0 0 {name=l63 sig_type=std_logic lab=q1_1}
C {lab_pin.sym} 500 -790 0 0 {name=l64 sig_type=std_logic lab=q1_1}
C {lab_pin.sym} -700 -620 0 0 {name=l65 sig_type=std_logic lab=q1_2}
C {lab_pin.sym} 500 -770 0 0 {name=l66 sig_type=std_logic lab=q1_2}
C {lab_pin.sym} -700 -580 0 0 {name=l67 sig_type=std_logic lab=q1_3}
C {lab_pin.sym} 500 -750 0 0 {name=l68 sig_type=std_logic lab=q1_3}
C {lab_pin.sym} -700 -540 0 0 {name=l69 sig_type=std_logic lab=q2_0}
C {lab_pin.sym} 500 -730 0 0 {name=l70 sig_type=std_logic lab=q2_0}
C {lab_pin.sym} -700 -500 0 0 {name=l71 sig_type=std_logic lab=q2_1}
C {lab_pin.sym} 500 -710 0 0 {name=l72 sig_type=std_logic lab=q2_1}
C {lab_pin.sym} -700 -460 0 0 {name=l73 sig_type=std_logic lab=q2_2}
C {lab_pin.sym} 500 -690 0 0 {name=l74 sig_type=std_logic lab=q2_2}
C {lab_pin.sym} -700 -420 0 0 {name=l75 sig_type=std_logic lab=q2_3}
C {lab_pin.sym} 500 -670 0 0 {name=l76 sig_type=std_logic lab=q2_3}
C {lab_pin.sym} -700 -380 0 0 {name=l77 sig_type=std_logic lab=q3_0}
C {lab_pin.sym} 500 -650 0 0 {name=l78 sig_type=std_logic lab=q3_0}
C {lab_pin.sym} -700 -340 0 0 {name=l79 sig_type=std_logic lab=q3_1}
C {lab_pin.sym} 500 -630 0 0 {name=l80 sig_type=std_logic lab=q3_1}
C {lab_pin.sym} -700 -300 0 0 {name=l81 sig_type=std_logic lab=q3_2}
C {lab_pin.sym} 500 -610 0 0 {name=l82 sig_type=std_logic lab=q3_2}
C {lab_pin.sym} -700 -260 0 0 {name=l83 sig_type=std_logic lab=q3_3}
C {lab_pin.sym} 500 -590 0 0 {name=l84 sig_type=std_logic lab=q3_3}
C {lab_pin.sym} -500 -580 0 0 {name=l85 sig_type=std_logic lab=wsel0}
C {lab_pin.sym} 500 -470 0 0 {name=l86 sig_type=std_logic lab=wsel0}
C {lab_pin.sym} -500 -540 0 0 {name=l87 sig_type=std_logic lab=wsel1}
C {lab_pin.sym} 500 -450 0 0 {name=l88 sig_type=std_logic lab=wsel1}
C {lab_pin.sym} -500 -500 0 0 {name=l89 sig_type=std_logic lab=wsel2}
C {lab_pin.sym} 500 -430 0 0 {name=l90 sig_type=std_logic lab=wsel2}
C {lab_pin.sym} -500 -460 0 0 {name=l91 sig_type=std_logic lab=wsel3}
C {lab_pin.sym} 500 -410 0 0 {name=l92 sig_type=std_logic lab=wsel3}
C {lab_pin.sym} -500 -420 0 0 {name=l93 sig_type=std_logic lab=wsel4}
C {lab_pin.sym} 500 -390 0 0 {name=l94 sig_type=std_logic lab=wsel4}
C {lab_pin.sym} -500 -380 0 0 {name=l95 sig_type=std_logic lab=wsel5}
C {lab_pin.sym} 500 -370 0 0 {name=l96 sig_type=std_logic lab=wsel5}
C {lab_pin.sym} -500 -340 0 0 {name=l97 sig_type=std_logic lab=wsel6}
C {lab_pin.sym} 500 -350 0 0 {name=l98 sig_type=std_logic lab=wsel6}
C {lab_pin.sym} -500 -300 0 0 {name=l99 sig_type=std_logic lab=wsel7}
C {lab_pin.sym} 500 -330 0 0 {name=l100 sig_type=std_logic lab=wsel7}
C {lab_pin.sym} -500 -260 0 0 {name=l101 sig_type=std_logic lab=wsel8}
C {lab_pin.sym} 500 -310 0 0 {name=l102 sig_type=std_logic lab=wsel8}
C {lab_pin.sym} -500 -220 0 0 {name=l103 sig_type=std_logic lab=wsel9}
C {lab_pin.sym} 500 -290 0 0 {name=l104 sig_type=std_logic lab=wsel9}
C {lab_pin.sym} -500 -180 0 0 {name=l105 sig_type=std_logic lab=wsel10}
C {lab_pin.sym} 500 -270 0 0 {name=l106 sig_type=std_logic lab=wsel10}
C {lab_pin.sym} -500 -140 0 0 {name=l107 sig_type=std_logic lab=wsel11}
C {lab_pin.sym} 500 -250 0 0 {name=l108 sig_type=std_logic lab=wsel11}
C {lab_pin.sym} -500 -100 0 0 {name=l109 sig_type=std_logic lab=wsel12}
C {lab_pin.sym} 500 -230 0 0 {name=l110 sig_type=std_logic lab=wsel12}
C {lab_pin.sym} -500 -60 0 0 {name=l111 sig_type=std_logic lab=wsel13}
C {lab_pin.sym} 500 -210 0 0 {name=l112 sig_type=std_logic lab=wsel13}
C {lab_pin.sym} -500 -20 0 0 {name=l113 sig_type=std_logic lab=wsel14}
C {lab_pin.sym} 500 -190 0 0 {name=l114 sig_type=std_logic lab=wsel14}
C {lab_pin.sym} -500 20 0 0 {name=l115 sig_type=std_logic lab=wsel15}
C {lab_pin.sym} 500 -170 0 0 {name=l116 sig_type=std_logic lab=wsel15}
C {lab_pin.sym} -500 60 0 0 {name=l117 sig_type=std_logic lab=wsel16}
C {lab_pin.sym} 500 -150 0 0 {name=l118 sig_type=std_logic lab=wsel16}
C {lab_pin.sym} -300 -900 0 0 {name=l119 sig_type=std_logic lab=wsel17}
C {lab_pin.sym} 500 -130 0 0 {name=l120 sig_type=std_logic lab=wsel17}
C {lab_pin.sym} -300 -860 0 0 {name=l121 sig_type=std_logic lab=wsel18}
C {lab_pin.sym} 500 -110 0 0 {name=l122 sig_type=std_logic lab=wsel18}
C {lab_pin.sym} -300 -820 0 0 {name=l123 sig_type=std_logic lab=wsel19}
C {lab_pin.sym} 500 -90 0 0 {name=l124 sig_type=std_logic lab=wsel19}
C {lab_pin.sym} -300 -780 0 0 {name=l125 sig_type=std_logic lab=pump_up1}
C {lab_pin.sym} 500 -70 0 0 {name=l126 sig_type=std_logic lab=pump_up1}
C {lab_pin.sym} -300 -740 0 0 {name=l127 sig_type=std_logic lab=pump_up2}
C {lab_pin.sym} 500 -50 0 0 {name=l128 sig_type=std_logic lab=pump_up2}
C {lab_pin.sym} -300 -700 0 0 {name=l129 sig_type=std_logic lab=pump_up3}
C {lab_pin.sym} 500 -30 0 0 {name=l130 sig_type=std_logic lab=pump_up3}
C {lab_pin.sym} -300 -660 0 0 {name=l131 sig_type=std_logic lab=pump_dn1}
C {lab_pin.sym} 500 -10 0 0 {name=l132 sig_type=std_logic lab=pump_dn1}
C {lab_pin.sym} -300 -620 0 0 {name=l133 sig_type=std_logic lab=pump_dn2}
C {lab_pin.sym} 500 10 0 0 {name=l134 sig_type=std_logic lab=pump_dn2}
C {lab_pin.sym} -300 -580 0 0 {name=l135 sig_type=std_logic lab=pump_dn3}
C {lab_pin.sym} 500 30 0 0 {name=l136 sig_type=std_logic lab=pump_dn3}
C {lab_pin.sym} 1100 80 0 0 {name=l137 sig_type=std_logic lab=vb}
C {lab_pin.sym} 1400 -470 0 0 {name=l138 sig_type=std_logic lab=vb}
C {lab_pin.sym} 1000 -810 0 0 {name=l139 sig_type=std_logic lab=g0}
C {lab_pin.sym} 1200 -470 0 0 {name=l140 sig_type=std_logic lab=g0}
C {lab_pin.sym} 1000 -610 0 0 {name=l141 sig_type=std_logic lab=g1}
C {lab_pin.sym} 1200 -450 0 0 {name=l142 sig_type=std_logic lab=g1}
C {lab_pin.sym} 1000 -410 0 0 {name=l143 sig_type=std_logic lab=g2}
C {lab_pin.sym} 1200 -430 0 0 {name=l144 sig_type=std_logic lab=g2}
C {lab_pin.sym} 1000 -210 0 0 {name=l145 sig_type=std_logic lab=g3}
C {lab_pin.sym} 1200 -410 0 0 {name=l146 sig_type=std_logic lab=g3}
C {lab_pin.sym} 1400 -450 0 0 {name=l147 sig_type=std_logic lab=out0}
C {lab_pin.sym} 1700 -600 0 0 {name=l148 sig_type=std_logic lab=out0}
C {lab_pin.sym} 1400 -430 0 0 {name=l149 sig_type=std_logic lab=out1}
C {lab_pin.sym} 1700 -580 0 0 {name=l150 sig_type=std_logic lab=out1}
C {lab_pin.sym} 1400 -410 0 0 {name=l151 sig_type=std_logic lab=out2}
C {lab_pin.sym} 1700 -560 0 0 {name=l152 sig_type=std_logic lab=out2}
C {lab_pin.sym} 1400 -390 0 0 {name=l153 sig_type=std_logic lab=out3}
C {lab_pin.sym} 1700 -540 0 0 {name=l154 sig_type=std_logic lab=out3}
C {lab_pin.sym} -700 -220 0 0 {name=l155 sig_type=std_logic lab=k0_0}
C {lab_pin.sym} 800 -830 0 0 {name=l156 sig_type=std_logic lab=k0_0}
C {lab_pin.sym} -700 -180 0 0 {name=l157 sig_type=std_logic lab=k0_1}
C {lab_pin.sym} 800 -810 0 0 {name=l158 sig_type=std_logic lab=k0_1}
C {lab_pin.sym} -700 -140 0 0 {name=l159 sig_type=std_logic lab=k0_2}
C {lab_pin.sym} 800 -790 0 0 {name=l160 sig_type=std_logic lab=k0_2}
C {lab_pin.sym} -700 -100 0 0 {name=l161 sig_type=std_logic lab=k0_3}
C {lab_pin.sym} 800 -770 0 0 {name=l162 sig_type=std_logic lab=k0_3}
C {lab_pin.sym} -700 -60 0 0 {name=l163 sig_type=std_logic lab=k1_0}
C {lab_pin.sym} 800 -630 0 0 {name=l164 sig_type=std_logic lab=k1_0}
C {lab_pin.sym} -700 -20 0 0 {name=l165 sig_type=std_logic lab=k1_1}
C {lab_pin.sym} 800 -610 0 0 {name=l166 sig_type=std_logic lab=k1_1}
C {lab_pin.sym} -700 20 0 0 {name=l167 sig_type=std_logic lab=k1_2}
C {lab_pin.sym} 800 -590 0 0 {name=l168 sig_type=std_logic lab=k1_2}
C {lab_pin.sym} -700 60 0 0 {name=l169 sig_type=std_logic lab=k1_3}
C {lab_pin.sym} 800 -570 0 0 {name=l170 sig_type=std_logic lab=k1_3}
C {lab_pin.sym} -500 -900 0 0 {name=l171 sig_type=std_logic lab=k2_0}
C {lab_pin.sym} 800 -430 0 0 {name=l172 sig_type=std_logic lab=k2_0}
C {lab_pin.sym} -500 -860 0 0 {name=l173 sig_type=std_logic lab=k2_1}
C {lab_pin.sym} 800 -410 0 0 {name=l174 sig_type=std_logic lab=k2_1}
C {lab_pin.sym} -500 -820 0 0 {name=l175 sig_type=std_logic lab=k2_2}
C {lab_pin.sym} 800 -390 0 0 {name=l176 sig_type=std_logic lab=k2_2}
C {lab_pin.sym} -500 -780 0 0 {name=l177 sig_type=std_logic lab=k2_3}
C {lab_pin.sym} 800 -370 0 0 {name=l178 sig_type=std_logic lab=k2_3}
C {lab_pin.sym} -500 -740 0 0 {name=l179 sig_type=std_logic lab=k3_0}
C {lab_pin.sym} 800 -230 0 0 {name=l180 sig_type=std_logic lab=k3_0}
C {lab_pin.sym} -500 -700 0 0 {name=l181 sig_type=std_logic lab=k3_1}
C {lab_pin.sym} 800 -210 0 0 {name=l182 sig_type=std_logic lab=k3_1}
C {lab_pin.sym} -500 -660 0 0 {name=l183 sig_type=std_logic lab=k3_2}
C {lab_pin.sym} 800 -190 0 0 {name=l184 sig_type=std_logic lab=k3_2}
C {lab_pin.sym} -500 -620 0 0 {name=l185 sig_type=std_logic lab=k3_3}
C {lab_pin.sym} 800 -170 0 0 {name=l186 sig_type=std_logic lab=k3_3}
C {lab_pin.sym} -300 -380 0 0 {name=l187 sig_type=std_logic lab=adc_rst}
C {lab_pin.sym} 1700 -380 0 0 {name=l188 sig_type=std_logic lab=adc_rst}
C {lab_pin.sym} -300 -340 0 0 {name=l189 sig_type=std_logic lab=adc_lat}
C {lab_pin.sym} 1700 -360 0 0 {name=l190 sig_type=std_logic lab=adc_lat}
C {lab_pin.sym} 1900 -600 0 0 {name=l191 sig_type=std_logic lab=cmp}
C {lab_pin.sym} 2300 -900 0 0 {name=l192 sig_type=std_logic lab=cmp}
C {lab_pin.sym} -300 -540 0 0 {name=l193 sig_type=std_logic lab=adc_ch0}
C {lab_pin.sym} 1700 -460 0 0 {name=l194 sig_type=std_logic lab=adc_ch0}
C {lab_pin.sym} -300 -500 0 0 {name=l195 sig_type=std_logic lab=adc_ch1}
C {lab_pin.sym} 1700 -440 0 0 {name=l196 sig_type=std_logic lab=adc_ch1}
C {lab_pin.sym} -300 -460 0 0 {name=l197 sig_type=std_logic lab=adc_ch2}
C {lab_pin.sym} 1700 -420 0 0 {name=l198 sig_type=std_logic lab=adc_ch2}
C {lab_pin.sym} -300 -420 0 0 {name=l199 sig_type=std_logic lab=adc_ch3}
C {lab_pin.sym} 1700 -400 0 0 {name=l200 sig_type=std_logic lab=adc_ch3}
C {lab_pin.sym} -300 -300 0 0 {name=l201 sig_type=std_logic lab=dac0}
C {lab_pin.sym} 1700 -340 0 0 {name=l202 sig_type=std_logic lab=dac0}
C {lab_pin.sym} -300 -260 0 0 {name=l203 sig_type=std_logic lab=dac1}
C {lab_pin.sym} 1700 -320 0 0 {name=l204 sig_type=std_logic lab=dac1}
C {lab_pin.sym} -300 -220 0 0 {name=l205 sig_type=std_logic lab=dac2}
C {lab_pin.sym} 1700 -300 0 0 {name=l206 sig_type=std_logic lab=dac2}
C {lab_pin.sym} -300 -180 0 0 {name=l207 sig_type=std_logic lab=dac3}
C {lab_pin.sym} 1700 -280 0 0 {name=l208 sig_type=std_logic lab=dac3}
C {lab_pin.sym} -300 -140 0 0 {name=l209 sig_type=std_logic lab=dac4}
C {lab_pin.sym} 1700 -260 0 0 {name=l210 sig_type=std_logic lab=dac4}
C {lab_pin.sym} -300 -100 0 0 {name=l211 sig_type=std_logic lab=dac5}
C {lab_pin.sym} 1700 -240 0 0 {name=l212 sig_type=std_logic lab=dac5}
C {lab_pin.sym} -300 -60 0 0 {name=l213 sig_type=std_logic lab=dac6}
C {lab_pin.sym} 1700 -220 0 0 {name=l214 sig_type=std_logic lab=dac6}
C {lab_pin.sym} -300 -20 0 0 {name=l215 sig_type=std_logic lab=dac7}
C {lab_pin.sym} 1700 -200 0 0 {name=l216 sig_type=std_logic lab=dac7}
C {lab_pin.sym} -300 20 0 0 {name=l217 sig_type=std_logic lab=vb_probe_en}
C {lab_pin.sym} 1100 120 0 0 {name=l218 sig_type=std_logic lab=vb_probe_en}
C {lab_pin.sym} 1300 80 0 0 {name=l219 sig_type=std_logic lab=ua1}
C {lab_pin.sym} 2300 -820 0 0 {name=l220 sig_type=std_logic lab=ua1}
C {lab_pin.sym} 100 -390 0 0 {name=l221 sig_type=std_logic lab=vbn}
C {lab_pin.sym} 500 -490 0 0 {name=l222 sig_type=std_logic lab=vbn}
C {lab_pin.sym} 1100 100 0 0 {name=l223 sig_type=std_logic lab=vbn}
C {lab_pin.sym} 100 -330 0 0 {name=l224 sig_type=std_logic lab=vcas}
C {lab_pin.sym} 1200 -330 0 0 {name=l225 sig_type=std_logic lab=vcas}
C {lab_pin.sym} 1700 -500 0 0 {name=l226 sig_type=std_logic lab=vcas}
C {lab_pin.sym} 100 -310 0 0 {name=l227 sig_type=std_logic lab=vr}
C {lab_pin.sym} 1200 -350 0 0 {name=l228 sig_type=std_logic lab=vr}
C {lab_pin.sym} 1700 -480 0 0 {name=l229 sig_type=std_logic lab=vr}
C {ipin.sym} -700 -900 0 0 {name=p230 lab=bias_en}
C {ipin.sym} -700 -860 0 0 {name=p231 lab=q0_0}
C {ipin.sym} -700 -820 0 0 {name=p232 lab=q0_1}
C {ipin.sym} -700 -780 0 0 {name=p233 lab=q0_2}
C {ipin.sym} -700 -740 0 0 {name=p234 lab=q0_3}
C {ipin.sym} -700 -700 0 0 {name=p235 lab=q1_0}
C {ipin.sym} -700 -660 0 0 {name=p236 lab=q1_1}
C {ipin.sym} -700 -620 0 0 {name=p237 lab=q1_2}
C {ipin.sym} -700 -580 0 0 {name=p238 lab=q1_3}
C {ipin.sym} -700 -540 0 0 {name=p239 lab=q2_0}
C {ipin.sym} -700 -500 0 0 {name=p240 lab=q2_1}
C {ipin.sym} -700 -460 0 0 {name=p241 lab=q2_2}
C {ipin.sym} -700 -420 0 0 {name=p242 lab=q2_3}
C {ipin.sym} -700 -380 0 0 {name=p243 lab=q3_0}
C {ipin.sym} -700 -340 0 0 {name=p244 lab=q3_1}
C {ipin.sym} -700 -300 0 0 {name=p245 lab=q3_2}
C {ipin.sym} -700 -260 0 0 {name=p246 lab=q3_3}
C {ipin.sym} -700 -220 0 0 {name=p247 lab=k0_0}
C {ipin.sym} -700 -180 0 0 {name=p248 lab=k0_1}
C {ipin.sym} -700 -140 0 0 {name=p249 lab=k0_2}
C {ipin.sym} -700 -100 0 0 {name=p250 lab=k0_3}
C {ipin.sym} -700 -60 0 0 {name=p251 lab=k1_0}
C {ipin.sym} -700 -20 0 0 {name=p252 lab=k1_1}
C {ipin.sym} -700 20 0 0 {name=p253 lab=k1_2}
C {ipin.sym} -700 60 0 0 {name=p254 lab=k1_3}
C {ipin.sym} -500 -900 0 0 {name=p255 lab=k2_0}
C {ipin.sym} -500 -860 0 0 {name=p256 lab=k2_1}
C {ipin.sym} -500 -820 0 0 {name=p257 lab=k2_2}
C {ipin.sym} -500 -780 0 0 {name=p258 lab=k2_3}
C {ipin.sym} -500 -740 0 0 {name=p259 lab=k3_0}
C {ipin.sym} -500 -700 0 0 {name=p260 lab=k3_1}
C {ipin.sym} -500 -660 0 0 {name=p261 lab=k3_2}
C {ipin.sym} -500 -620 0 0 {name=p262 lab=k3_3}
C {ipin.sym} -500 -580 0 0 {name=p263 lab=wsel0}
C {ipin.sym} -500 -540 0 0 {name=p264 lab=wsel1}
C {ipin.sym} -500 -500 0 0 {name=p265 lab=wsel2}
C {ipin.sym} -500 -460 0 0 {name=p266 lab=wsel3}
C {ipin.sym} -500 -420 0 0 {name=p267 lab=wsel4}
C {ipin.sym} -500 -380 0 0 {name=p268 lab=wsel5}
C {ipin.sym} -500 -340 0 0 {name=p269 lab=wsel6}
C {ipin.sym} -500 -300 0 0 {name=p270 lab=wsel7}
C {ipin.sym} -500 -260 0 0 {name=p271 lab=wsel8}
C {ipin.sym} -500 -220 0 0 {name=p272 lab=wsel9}
C {ipin.sym} -500 -180 0 0 {name=p273 lab=wsel10}
C {ipin.sym} -500 -140 0 0 {name=p274 lab=wsel11}
C {ipin.sym} -500 -100 0 0 {name=p275 lab=wsel12}
C {ipin.sym} -500 -60 0 0 {name=p276 lab=wsel13}
C {ipin.sym} -500 -20 0 0 {name=p277 lab=wsel14}
C {ipin.sym} -500 20 0 0 {name=p278 lab=wsel15}
C {ipin.sym} -500 60 0 0 {name=p279 lab=wsel16}
C {ipin.sym} -300 -900 0 0 {name=p280 lab=wsel17}
C {ipin.sym} -300 -860 0 0 {name=p281 lab=wsel18}
C {ipin.sym} -300 -820 0 0 {name=p282 lab=wsel19}
C {ipin.sym} -300 -780 0 0 {name=p283 lab=pump_up1}
C {ipin.sym} -300 -740 0 0 {name=p284 lab=pump_up2}
C {ipin.sym} -300 -700 0 0 {name=p285 lab=pump_up3}
C {ipin.sym} -300 -660 0 0 {name=p286 lab=pump_dn1}
C {ipin.sym} -300 -620 0 0 {name=p287 lab=pump_dn2}
C {ipin.sym} -300 -580 0 0 {name=p288 lab=pump_dn3}
C {ipin.sym} -300 -540 0 0 {name=p289 lab=adc_ch0}
C {ipin.sym} -300 -500 0 0 {name=p290 lab=adc_ch1}
C {ipin.sym} -300 -460 0 0 {name=p291 lab=adc_ch2}
C {ipin.sym} -300 -420 0 0 {name=p292 lab=adc_ch3}
C {ipin.sym} -300 -380 0 0 {name=p293 lab=adc_rst}
C {ipin.sym} -300 -340 0 0 {name=p294 lab=adc_lat}
C {ipin.sym} -300 -300 0 0 {name=p295 lab=dac0}
C {ipin.sym} -300 -260 0 0 {name=p296 lab=dac1}
C {ipin.sym} -300 -220 0 0 {name=p297 lab=dac2}
C {ipin.sym} -300 -180 0 0 {name=p298 lab=dac3}
C {ipin.sym} -300 -140 0 0 {name=p299 lab=dac4}
C {ipin.sym} -300 -100 0 0 {name=p300 lab=dac5}
C {ipin.sym} -300 -60 0 0 {name=p301 lab=dac6}
C {ipin.sym} -300 -20 0 0 {name=p302 lab=dac7}
C {ipin.sym} -300 20 0 0 {name=p303 lab=vb_probe_en}
C {opin.sym} 2300 -900 0 0 {name=p304 lab=cmp}
C {iopin.sym} 2300 -860 0 0 {name=p305 lab=ua0}
C {iopin.sym} 2300 -820 0 0 {name=p306 lab=ua1}
C {iopin.sym} 2300 -780 0 0 {name=p307 lab=ua2}
C {rt5w_bias.sym} 0 -400 0 0 {name=xbias}
C {rt5w_array.sym} 600 -400 0 0 {name=xarr}
C {rt5w_softmax.sym} 1300 -400 0 0 {name=xsm}
C {rt5w_kscale.sym} 900 -800 0 0 {name=xk0}
C {rt5w_kscale.sym} 900 -600 0 0 {name=xk1}
C {rt5w_kscale.sym} 900 -400 0 0 {name=xk2}
C {rt5w_kscale.sym} 900 -200 0 0 {name=xk3}
C {rt5w_readout.sym} 1800 -400 0 0 {name=xro}
C {rt5w_vbbuf.sym} 1200 100 0 0 {name=xvb}
