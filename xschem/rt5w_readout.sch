v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Readout: one-hot mux -> int, 8-bit binary current DAC (unit I_u/16), integrating StrongARM comparator} -1000 -1150 0 0 0.5 0.5 {}
N 180 -10 180 170 {lab=nd2}
N 3320 -50 3320 30 {lab=n_cmp}
N 3620 -50 3620 30 {lab=n_cmpb}
N -380 -930 -380 -980 {lab=out0}
N -380 -980 -280 -980 {lab=out0}
N -280 -980 -280 -930 {lab=out0}
N -280 -930 -180 -930 {lab=out0}
N -380 -670 -380 -720 {lab=out1}
N -380 -720 -280 -720 {lab=out1}
N -280 -720 -280 -670 {lab=out1}
N -280 -670 -180 -670 {lab=out1}
N -380 -410 -380 -460 {lab=out2}
N -380 -460 -280 -460 {lab=out2}
N -280 -460 -280 -410 {lab=out2}
N -280 -410 -180 -410 {lab=out2}
N -380 -150 -380 -200 {lab=out3}
N -380 -200 -280 -200 {lab=out3}
N -280 -200 -280 -150 {lab=out3}
N -280 -150 -180 -150 {lab=out3}
N 420 -10 420 170 {lab=sk0}
N 420 -10 540 -10 {lab=sk0}
N 660 -10 660 170 {lab=sk1}
N 660 -10 780 -10 {lab=sk1}
N 900 -10 900 170 {lab=sk2}
N 900 -10 1020 -10 {lab=sk2}
N 1140 -10 1140 170 {lab=sk3}
N 1140 -10 1260 -10 {lab=sk3}
N 1380 -10 1380 170 {lab=sk4}
N 1380 -10 1500 -10 {lab=sk4}
N 1620 -10 1620 170 {lab=sk5}
N 1620 -10 1740 -10 {lab=sk5}
N 1860 -10 1860 170 {lab=sk6}
N 1860 -10 1980 -10 {lab=sk6}
N 2100 -10 2100 170 {lab=sk7}
N 2100 -10 2220 -10 {lab=sk7}
N 2580 90 2580 170 {lab=tl}
N 2580 170 2720 170 {lab=tl}
N 2720 170 2720 90 {lab=tl}
N 2720 90 2820 90 {lab=tl}
N -1000 -900 -740 -900 {lab=adc_ch0}
N -740 -900 -740 -960 {lab=adc_ch0}
N -740 -900 -740 -840 {lab=adc_ch0}
N -740 -900 -580 -900 {lab=adc_ch0}
N -580 -900 -580 -960 {lab=adc_ch0}
N -580 -900 -580 -840 {lab=adc_ch0}
N -1000 -640 -740 -640 {lab=adc_ch1}
N -740 -640 -740 -700 {lab=adc_ch1}
N -740 -640 -740 -580 {lab=adc_ch1}
N -740 -640 -580 -640 {lab=adc_ch1}
N -580 -640 -580 -700 {lab=adc_ch1}
N -580 -640 -580 -580 {lab=adc_ch1}
N -1000 -380 -740 -380 {lab=adc_ch2}
N -740 -380 -740 -440 {lab=adc_ch2}
N -740 -380 -740 -320 {lab=adc_ch2}
N -740 -380 -580 -380 {lab=adc_ch2}
N -580 -380 -580 -440 {lab=adc_ch2}
N -580 -380 -580 -320 {lab=adc_ch2}
N -1000 -120 -740 -120 {lab=adc_ch3}
N -740 -120 -740 -180 {lab=adc_ch3}
N -740 -120 -740 -60 {lab=adc_ch3}
N -740 -120 -580 -120 {lab=adc_ch3}
N -580 -120 -580 -180 {lab=adc_ch3}
N -580 -120 -580 -60 {lab=adc_ch3}
N -1400 -650 -1400 -670 {lab=vdd}
C {vdd.sym} -1400 -670 0 0 {name=r1 lab=vdd}
N -1080 -650 -1080 -670 {lab=vdd}
C {vdd.sym} -1080 -670 0 0 {name=r2 lab=vdd}
N -860 -990 -860 -1010 {lab=vdd}
C {vdd.sym} -860 -1010 0 0 {name=r3 lab=vdd}
N -860 -730 -860 -750 {lab=vdd}
C {vdd.sym} -860 -750 0 0 {name=r4 lab=vdd}
N -860 -470 -860 -490 {lab=vdd}
C {vdd.sym} -860 -490 0 0 {name=r5 lab=vdd}
N -860 -210 -860 -230 {lab=vdd}
C {vdd.sym} -860 -230 0 0 {name=r6 lab=vdd}
N -700 -990 -700 -1010 {lab=vdd}
C {vdd.sym} -700 -1010 0 0 {name=r7 lab=vdd}
N -700 -730 -700 -750 {lab=vdd}
C {vdd.sym} -700 -750 0 0 {name=r8 lab=vdd}
N -700 -470 -700 -490 {lab=vdd}
C {vdd.sym} -700 -490 0 0 {name=r9 lab=vdd}
N -700 -210 -700 -230 {lab=vdd}
C {vdd.sym} -700 -230 0 0 {name=r10 lab=vdd}
N -540 -990 -540 -1010 {lab=vdd}
C {vdd.sym} -540 -1010 0 0 {name=r11 lab=vdd}
N -540 -730 -540 -750 {lab=vdd}
C {vdd.sym} -540 -750 0 0 {name=r12 lab=vdd}
N -540 -470 -540 -490 {lab=vdd}
C {vdd.sym} -540 -490 0 0 {name=r13 lab=vdd}
N -540 -210 -540 -230 {lab=vdd}
C {vdd.sym} -540 -230 0 0 {name=r14 lab=vdd}
N 420 -750 420 -770 {lab=vdd}
C {vdd.sym} 420 -770 0 0 {name=r15 lab=vdd}
N 540 -70 540 -90 {lab=vdd}
C {vdd.sym} 540 -90 0 0 {name=r16 lab=vdd}
N 660 -750 660 -770 {lab=vdd}
C {vdd.sym} 660 -770 0 0 {name=r17 lab=vdd}
N 780 -70 780 -90 {lab=vdd}
C {vdd.sym} 780 -90 0 0 {name=r18 lab=vdd}
N 900 -750 900 -770 {lab=vdd}
C {vdd.sym} 900 -770 0 0 {name=r19 lab=vdd}
N 1020 -70 1020 -90 {lab=vdd}
C {vdd.sym} 1020 -90 0 0 {name=r20 lab=vdd}
N 1140 -750 1140 -770 {lab=vdd}
C {vdd.sym} 1140 -770 0 0 {name=r21 lab=vdd}
N 1240 -1080 1240 -1100 {lab=vdd}
C {vdd.sym} 1240 -1100 0 0 {name=r22 lab=vdd}
N 1260 -70 1260 -90 {lab=vdd}
C {vdd.sym} 1260 -90 0 0 {name=r23 lab=vdd}
N 1380 -750 1380 -770 {lab=vdd}
C {vdd.sym} 1380 -770 0 0 {name=r24 lab=vdd}
N 1500 -70 1500 -90 {lab=vdd}
C {vdd.sym} 1500 -90 0 0 {name=r25 lab=vdd}
N 1560 -1080 1560 -1100 {lab=vdd}
C {vdd.sym} 1560 -1100 0 0 {name=r26 lab=vdd}
N 1620 -750 1620 -770 {lab=vdd}
C {vdd.sym} 1620 -770 0 0 {name=r27 lab=vdd}
N 1740 -70 1740 -90 {lab=vdd}
C {vdd.sym} 1740 -90 0 0 {name=r28 lab=vdd}
N 1860 -750 1860 -770 {lab=vdd}
C {vdd.sym} 1860 -770 0 0 {name=r29 lab=vdd}
N 1980 -70 1980 -90 {lab=vdd}
C {vdd.sym} 1980 -90 0 0 {name=r30 lab=vdd}
N 2100 -750 2100 -770 {lab=vdd}
C {vdd.sym} 2100 -770 0 0 {name=r31 lab=vdd}
N 2220 -70 2220 -90 {lab=vdd}
C {vdd.sym} 2220 -90 0 0 {name=r32 lab=vdd}
N 2420 -270 2420 -290 {lab=vdd}
C {vdd.sym} 2420 -290 0 0 {name=r33 lab=vdd}
N 2420 -110 2420 -130 {lab=vdd}
C {vdd.sym} 2420 -130 0 0 {name=r34 lab=vdd}
N 2480 -620 2480 -640 {lab=vdd}
C {vdd.sym} 2480 -640 0 0 {name=r35 lab=vdd}
N 2580 -270 2580 -290 {lab=vdd}
C {vdd.sym} 2580 -290 0 0 {name=r36 lab=vdd}
N 2820 -270 2820 -290 {lab=vdd}
C {vdd.sym} 2820 -290 0 0 {name=r37 lab=vdd}
N 2980 -270 2980 -290 {lab=vdd}
C {vdd.sym} 2980 -290 0 0 {name=r38 lab=vdd}
N 2980 -110 2980 -130 {lab=vdd}
C {vdd.sym} 2980 -130 0 0 {name=r39 lab=vdd}
N 3320 -270 3320 -290 {lab=vdd}
C {vdd.sym} 3320 -290 0 0 {name=r40 lab=vdd}
N 3440 -270 3440 -290 {lab=vdd}
C {vdd.sym} 3440 -290 0 0 {name=r41 lab=vdd}
N 3620 -270 3620 -290 {lab=vdd}
C {vdd.sym} 3620 -290 0 0 {name=r42 lab=vdd}
N 3740 -270 3740 -290 {lab=vdd}
C {vdd.sym} 3740 -290 0 0 {name=r43 lab=vdd}
N -1560 -350 -1560 -330 {lab=vss}
C {gnd.sym} -1560 -330 0 0 {name=r44 lab=vss}
N -1560 -290 -1560 -270 {lab=vss}
C {gnd.sym} -1560 -270 0 0 {name=r45 lab=vss}
N -1400 -290 -1400 -270 {lab=vss}
C {gnd.sym} -1400 -270 0 0 {name=r46 lab=vss}
N -1240 -350 -1240 -330 {lab=vss}
C {gnd.sym} -1240 -330 0 0 {name=r47 lab=vss}
N -1240 -290 -1240 -270 {lab=vss}
C {gnd.sym} -1240 -270 0 0 {name=r48 lab=vss}
N -1080 -290 -1080 -270 {lab=vss}
C {gnd.sym} -1080 -270 0 0 {name=r49 lab=vss}
N -540 -810 -540 -790 {lab=vss}
C {gnd.sym} -540 -790 0 0 {name=r50 lab=vss}
N -540 -550 -540 -530 {lab=vss}
C {gnd.sym} -540 -530 0 0 {name=r51 lab=vss}
N -540 -290 -540 -270 {lab=vss}
C {gnd.sym} -540 -270 0 0 {name=r52 lab=vss}
N -540 -30 -540 -10 {lab=vss}
C {gnd.sym} -540 -10 0 0 {name=r53 lab=vss}
N 180 230 180 250 {lab=vss}
C {gnd.sym} 180 250 0 0 {name=r54 lab=vss}
N 420 -550 420 -530 {lab=vss}
C {gnd.sym} 420 -530 0 0 {name=r55 lab=vss}
N 420 -210 420 -190 {lab=vss}
C {gnd.sym} 420 -190 0 0 {name=r56 lab=vss}
N 420 230 420 250 {lab=vss}
C {gnd.sym} 420 250 0 0 {name=r57 lab=vss}
N 540 -210 540 -190 {lab=vss}
C {gnd.sym} 540 -190 0 0 {name=r58 lab=vss}
N 660 -550 660 -530 {lab=vss}
C {gnd.sym} 660 -530 0 0 {name=r59 lab=vss}
N 660 -210 660 -190 {lab=vss}
C {gnd.sym} 660 -190 0 0 {name=r60 lab=vss}
N 660 230 660 250 {lab=vss}
C {gnd.sym} 660 250 0 0 {name=r61 lab=vss}
N 780 -210 780 -190 {lab=vss}
C {gnd.sym} 780 -190 0 0 {name=r62 lab=vss}
N 900 -550 900 -530 {lab=vss}
C {gnd.sym} 900 -530 0 0 {name=r63 lab=vss}
N 900 -210 900 -190 {lab=vss}
C {gnd.sym} 900 -190 0 0 {name=r64 lab=vss}
N 900 230 900 250 {lab=vss}
C {gnd.sym} 900 250 0 0 {name=r65 lab=vss}
N 920 -1020 920 -1000 {lab=vss}
C {gnd.sym} 920 -1000 0 0 {name=r66 lab=vss}
N 1020 -210 1020 -190 {lab=vss}
C {gnd.sym} 1020 -190 0 0 {name=r67 lab=vss}
N 1140 -550 1140 -530 {lab=vss}
C {gnd.sym} 1140 -530 0 0 {name=r68 lab=vss}
N 1140 -210 1140 -190 {lab=vss}
C {gnd.sym} 1140 -190 0 0 {name=r69 lab=vss}
N 1140 230 1140 250 {lab=vss}
C {gnd.sym} 1140 250 0 0 {name=r70 lab=vss}
N 1260 -210 1260 -190 {lab=vss}
C {gnd.sym} 1260 -190 0 0 {name=r71 lab=vss}
N 1380 -550 1380 -530 {lab=vss}
C {gnd.sym} 1380 -530 0 0 {name=r72 lab=vss}
N 1380 -210 1380 -190 {lab=vss}
C {gnd.sym} 1380 -190 0 0 {name=r73 lab=vss}
N 1380 230 1380 250 {lab=vss}
C {gnd.sym} 1380 250 0 0 {name=r74 lab=vss}
N 1400 -1020 1400 -1000 {lab=vss}
C {gnd.sym} 1400 -1000 0 0 {name=r75 lab=vss}
N 1500 -210 1500 -190 {lab=vss}
C {gnd.sym} 1500 -190 0 0 {name=r76 lab=vss}
N 1620 -550 1620 -530 {lab=vss}
C {gnd.sym} 1620 -530 0 0 {name=r77 lab=vss}
N 1620 -210 1620 -190 {lab=vss}
C {gnd.sym} 1620 -190 0 0 {name=r78 lab=vss}
N 1620 230 1620 250 {lab=vss}
C {gnd.sym} 1620 250 0 0 {name=r79 lab=vss}
N 1740 -210 1740 -190 {lab=vss}
C {gnd.sym} 1740 -190 0 0 {name=r80 lab=vss}
N 1860 -550 1860 -530 {lab=vss}
C {gnd.sym} 1860 -530 0 0 {name=r81 lab=vss}
N 1860 -210 1860 -190 {lab=vss}
C {gnd.sym} 1860 -190 0 0 {name=r82 lab=vss}
N 1860 230 1860 250 {lab=vss}
C {gnd.sym} 1860 250 0 0 {name=r83 lab=vss}
N 1980 -210 1980 -190 {lab=vss}
C {gnd.sym} 1980 -190 0 0 {name=r84 lab=vss}
N 2100 -550 2100 -530 {lab=vss}
C {gnd.sym} 2100 -530 0 0 {name=r85 lab=vss}
N 2100 -210 2100 -190 {lab=vss}
C {gnd.sym} 2100 -190 0 0 {name=r86 lab=vss}
N 2100 230 2100 250 {lab=vss}
C {gnd.sym} 2100 250 0 0 {name=r87 lab=vss}
N 2220 -210 2220 -190 {lab=vss}
C {gnd.sym} 2220 -190 0 0 {name=r88 lab=vss}
N 2640 -620 2640 -600 {lab=vss}
C {gnd.sym} 2640 -600 0 0 {name=r89 lab=vss}
N 2720 230 2720 250 {lab=vss}
C {gnd.sym} 2720 250 0 0 {name=r90 lab=vss}
N 3320 90 3320 110 {lab=vss}
C {gnd.sym} 3320 110 0 0 {name=r91 lab=vss}
N 3620 90 3620 110 {lab=vss}
C {gnd.sym} 3620 110 0 0 {name=r92 lab=vss}
C {lab_pin.sym} -860 -840 0 0 {name=l93 sig_type=std_logic lab=vss}
C {lab_pin.sym} -1080 -480 0 0 {name=l94 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 900 200 0 0 {name=l95 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2680 -620 0 0 {name=l96 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2720 200 0 0 {name=l97 sig_type=std_logic lab=vss}
C {lab_pin.sym} 900 -720 0 0 {name=l98 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -860 -700 0 0 {name=l99 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 2580 -80 0 0 {name=l100 sig_type=std_logic lab=vss}
C {lab_pin.sym} -1080 -620 0 0 {name=l101 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -540 -440 0 0 {name=l102 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -700 -60 0 0 {name=l103 sig_type=std_logic lab=vss}
C {lab_pin.sym} 660 -40 0 0 {name=l104 sig_type=std_logic lab=vss}
C {lab_pin.sym} -1560 -320 0 0 {name=l105 sig_type=std_logic lab=vss}
C {lab_pin.sym} -1400 -320 0 0 {name=l106 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2580 -240 0 0 {name=l107 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -380 -380 0 0 {name=l108 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -540 -960 0 0 {name=l109 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -700 -580 0 0 {name=l110 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1860 -720 0 0 {name=l111 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 2100 -400 0 0 {name=l112 sig_type=std_logic lab=vss}
C {lab_pin.sym} 120 -620 0 0 {name=l113 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1620 -400 0 0 {name=l114 sig_type=std_logic lab=vss}
C {lab_pin.sym} 900 -40 0 0 {name=l115 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2420 -80 0 0 {name=l116 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 2100 200 0 0 {name=l117 sig_type=std_logic lab=vss}
C {lab_pin.sym} -860 -440 0 0 {name=l118 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 2100 -720 0 0 {name=l119 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -540 -580 0 0 {name=l120 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2100 -240 0 0 {name=l121 sig_type=std_logic lab=vss}
C {lab_pin.sym} 3620 -240 0 0 {name=l122 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 2220 -240 0 0 {name=l123 sig_type=std_logic lab=vss}
C {lab_pin.sym} 760 -1050 0 0 {name=l124 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 2580 60 0 0 {name=l125 sig_type=std_logic lab=vss}
C {lab_pin.sym} -700 -320 0 0 {name=l126 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1140 -40 0 0 {name=l127 sig_type=std_logic lab=vss}
C {lab_pin.sym} -700 -960 0 0 {name=l128 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -180 -640 0 0 {name=l129 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1620 200 0 0 {name=l130 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1140 -580 0 0 {name=l131 sig_type=std_logic lab=vss}
C {lab_pin.sym} 3740 -240 0 0 {name=l132 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 540 -40 0 0 {name=l133 sig_type=std_logic lab=vss}
C {lab_pin.sym} -860 -580 0 0 {name=l134 sig_type=std_logic lab=vss}
C {lab_pin.sym} 660 -400 0 0 {name=l135 sig_type=std_logic lab=vss}
C {lab_pin.sym} 600 -1050 0 0 {name=l136 sig_type=std_logic lab=vss}
C {lab_pin.sym} 900 -240 0 0 {name=l137 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1860 200 0 0 {name=l138 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2980 -80 0 0 {name=l139 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 3320 60 0 0 {name=l140 sig_type=std_logic lab=vss}
C {lab_pin.sym} 180 -40 0 0 {name=l141 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2220 -40 0 0 {name=l142 sig_type=std_logic lab=vss}
C {lab_pin.sym} -380 -900 0 0 {name=l143 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 900 -400 0 0 {name=l144 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1740 -240 0 0 {name=l145 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1860 -580 0 0 {name=l146 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2820 -80 0 0 {name=l147 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1860 -240 0 0 {name=l148 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2520 -620 0 0 {name=l149 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -700 -700 0 0 {name=l150 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1240 -1050 0 0 {name=l151 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1380 200 0 0 {name=l152 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1020 -400 0 0 {name=l153 sig_type=std_logic lab=vss}
C {lab_pin.sym} -1400 -620 0 0 {name=l154 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 280 -1050 0 0 {name=l155 sig_type=std_logic lab=vss}
C {lab_pin.sym} 3320 -240 0 0 {name=l156 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1980 -240 0 0 {name=l157 sig_type=std_logic lab=vss}
C {lab_pin.sym} 780 -240 0 0 {name=l158 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1740 -40 0 0 {name=l159 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1080 -1050 0 0 {name=l160 sig_type=std_logic lab=vss}
C {lab_pin.sym} -860 -960 0 0 {name=l161 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1380 -580 0 0 {name=l162 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1380 -240 0 0 {name=l163 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1620 -720 0 0 {name=l164 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1140 -400 0 0 {name=l165 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1860 -40 0 0 {name=l166 sig_type=std_logic lab=vss}
C {lab_pin.sym} 540 -400 0 0 {name=l167 sig_type=std_logic lab=vss}
C {lab_pin.sym} -860 -60 0 0 {name=l168 sig_type=std_logic lab=vss}
C {lab_pin.sym} -700 -840 0 0 {name=l169 sig_type=std_logic lab=vss}
C {lab_pin.sym} 420 200 0 0 {name=l170 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1500 -240 0 0 {name=l171 sig_type=std_logic lab=vss}
C {lab_pin.sym} -700 -180 0 0 {name=l172 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1260 -40 0 0 {name=l173 sig_type=std_logic lab=vss}
C {lab_pin.sym} 420 -720 0 0 {name=l174 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1980 -40 0 0 {name=l175 sig_type=std_logic lab=vss}
C {lab_pin.sym} 780 -40 0 0 {name=l176 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1140 -720 0 0 {name=l177 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 2820 60 0 0 {name=l178 sig_type=std_logic lab=vss}
C {lab_pin.sym} 420 -580 0 0 {name=l179 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1560 -1050 0 0 {name=l180 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1380 -40 0 0 {name=l181 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2220 -400 0 0 {name=l182 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1140 -240 0 0 {name=l183 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1500 -40 0 0 {name=l184 sig_type=std_logic lab=vss}
C {lab_pin.sym} -1240 -320 0 0 {name=l185 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1020 -240 0 0 {name=l186 sig_type=std_logic lab=vss}
C {lab_pin.sym} -540 -840 0 0 {name=l187 sig_type=std_logic lab=vss}
C {lab_pin.sym} -540 -180 0 0 {name=l188 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 2360 -620 0 0 {name=l189 sig_type=std_logic lab=vss}
C {lab_pin.sym} 540 -240 0 0 {name=l190 sig_type=std_logic lab=vss}
C {lab_pin.sym} -380 -120 0 0 {name=l191 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 660 -720 0 0 {name=l192 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 3620 -80 0 0 {name=l193 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1740 -400 0 0 {name=l194 sig_type=std_logic lab=vss}
C {lab_pin.sym} 660 -240 0 0 {name=l195 sig_type=std_logic lab=vss}
C {lab_pin.sym} 440 -1050 0 0 {name=l196 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -1080 -320 0 0 {name=l197 sig_type=std_logic lab=vss}
C {lab_pin.sym} 3320 -80 0 0 {name=l198 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2100 -580 0 0 {name=l199 sig_type=std_logic lab=vss}
C {lab_pin.sym} 180 200 0 0 {name=l200 sig_type=std_logic lab=vss}
C {lab_pin.sym} -860 -180 0 0 {name=l201 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1620 -580 0 0 {name=l202 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1020 -40 0 0 {name=l203 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1620 -240 0 0 {name=l204 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1860 -400 0 0 {name=l205 sig_type=std_logic lab=vss}
C {lab_pin.sym} 3440 -240 0 0 {name=l206 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -540 -320 0 0 {name=l207 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2420 -240 0 0 {name=l208 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1260 -400 0 0 {name=l209 sig_type=std_logic lab=vss}
C {lab_pin.sym} 120 -1050 0 0 {name=l210 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1140 200 0 0 {name=l211 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1980 -400 0 0 {name=l212 sig_type=std_logic lab=vss}
C {lab_pin.sym} 780 -400 0 0 {name=l213 sig_type=std_logic lab=vss}
C {lab_pin.sym} -180 -380 0 0 {name=l214 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1400 -1050 0 0 {name=l215 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1380 -400 0 0 {name=l216 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1500 -400 0 0 {name=l217 sig_type=std_logic lab=vss}
C {lab_pin.sym} 420 -240 0 0 {name=l218 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2100 -40 0 0 {name=l219 sig_type=std_logic lab=vss}
C {lab_pin.sym} -860 -320 0 0 {name=l220 sig_type=std_logic lab=vss}
C {lab_pin.sym} 3620 60 0 0 {name=l221 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1620 -40 0 0 {name=l222 sig_type=std_logic lab=vss}
C {lab_pin.sym} 660 200 0 0 {name=l223 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1260 -240 0 0 {name=l224 sig_type=std_logic lab=vss}
C {lab_pin.sym} -540 -60 0 0 {name=l225 sig_type=std_logic lab=vss}
C {lab_pin.sym} -540 -700 0 0 {name=l226 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1380 -720 0 0 {name=l227 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 2820 -240 0 0 {name=l228 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 660 -580 0 0 {name=l229 sig_type=std_logic lab=vss}
C {lab_pin.sym} -380 -640 0 0 {name=l230 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 920 -1050 0 0 {name=l231 sig_type=std_logic lab=vss}
C {lab_pin.sym} 2980 -240 0 0 {name=l232 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 420 -400 0 0 {name=l233 sig_type=std_logic lab=vss}
C {lab_pin.sym} -180 -900 0 0 {name=l234 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -700 -440 0 0 {name=l235 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -180 -120 0 0 {name=l236 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 420 -40 0 0 {name=l237 sig_type=std_logic lab=vss}
C {lab_pin.sym} 900 -580 0 0 {name=l238 sig_type=std_logic lab=vss}
C {lab_pin.sym} -700 -930 0 0 {name=l239 sig_type=std_logic lab=gs0}
C {lab_pin.sym} -700 -870 0 0 {name=l240 sig_type=std_logic lab=gs0}
C {lab_pin.sym} -220 -900 0 0 {name=l241 sig_type=std_logic lab=gs0}
C {lab_pin.sym} -860 -930 0 0 {name=l242 sig_type=std_logic lab=gd0}
C {lab_pin.sym} -860 -870 0 0 {name=l243 sig_type=std_logic lab=gd0}
C {lab_pin.sym} -340 -900 0 0 {name=l244 sig_type=std_logic lab=gd0}
C {lab_pin.sym} -700 -670 0 0 {name=l245 sig_type=std_logic lab=gs1}
C {lab_pin.sym} -700 -610 0 0 {name=l246 sig_type=std_logic lab=gs1}
C {lab_pin.sym} -220 -640 0 0 {name=l247 sig_type=std_logic lab=gs1}
C {lab_pin.sym} -860 -670 0 0 {name=l248 sig_type=std_logic lab=gd1}
C {lab_pin.sym} -860 -610 0 0 {name=l249 sig_type=std_logic lab=gd1}
C {lab_pin.sym} -340 -640 0 0 {name=l250 sig_type=std_logic lab=gd1}
C {lab_pin.sym} -700 -410 0 0 {name=l251 sig_type=std_logic lab=gs2}
C {lab_pin.sym} -700 -350 0 0 {name=l252 sig_type=std_logic lab=gs2}
C {lab_pin.sym} -220 -380 0 0 {name=l253 sig_type=std_logic lab=gs2}
C {lab_pin.sym} -860 -410 0 0 {name=l254 sig_type=std_logic lab=gd2}
C {lab_pin.sym} -860 -350 0 0 {name=l255 sig_type=std_logic lab=gd2}
C {lab_pin.sym} -340 -380 0 0 {name=l256 sig_type=std_logic lab=gd2}
C {lab_pin.sym} -700 -150 0 0 {name=l257 sig_type=std_logic lab=gs3}
C {lab_pin.sym} -700 -90 0 0 {name=l258 sig_type=std_logic lab=gs3}
C {lab_pin.sym} -220 -120 0 0 {name=l259 sig_type=std_logic lab=gs3}
C {lab_pin.sym} -860 -150 0 0 {name=l260 sig_type=std_logic lab=gd3}
C {lab_pin.sym} -860 -90 0 0 {name=l261 sig_type=std_logic lab=gd3}
C {lab_pin.sym} -340 -120 0 0 {name=l262 sig_type=std_logic lab=gd3}
C {lab_pin.sym} -1600 -320 0 0 {name=l263 sig_type=std_logic lab=vcas}
C {lab_pin.sym} 120 -60 0 0 {name=l264 sig_type=std_logic lab=vcas}
C {lab_pin.sym} 220 -40 0 0 {name=l265 sig_type=std_logic lab=vcas}
C {lab_pin.sym} 20 -480 0 0 {name=l266 sig_type=std_logic lab=adc_rst}
C {lab_pin.sym} 80 -620 0 0 {name=l267 sig_type=std_logic lab=adc_rst}
C {lab_pin.sym} 2320 -620 0 0 {name=l268 sig_type=std_logic lab=adc_rst}
C {lab_pin.sym} 380 -40 0 0 {name=l269 sig_type=std_logic lab=gon0}
C {lab_pin.sym} 420 -370 0 0 {name=l270 sig_type=std_logic lab=gon0}
C {lab_pin.sym} 420 -270 0 0 {name=l271 sig_type=std_logic lab=gon0}
C {lab_pin.sym} 500 -40 0 0 {name=l272 sig_type=std_logic lab=gof0}
C {lab_pin.sym} 540 -370 0 0 {name=l273 sig_type=std_logic lab=gof0}
C {lab_pin.sym} 540 -270 0 0 {name=l274 sig_type=std_logic lab=gof0}
C {lab_pin.sym} 620 -40 0 0 {name=l275 sig_type=std_logic lab=gon1}
C {lab_pin.sym} 660 -370 0 0 {name=l276 sig_type=std_logic lab=gon1}
C {lab_pin.sym} 660 -270 0 0 {name=l277 sig_type=std_logic lab=gon1}
C {lab_pin.sym} 740 -40 0 0 {name=l278 sig_type=std_logic lab=gof1}
C {lab_pin.sym} 780 -370 0 0 {name=l279 sig_type=std_logic lab=gof1}
C {lab_pin.sym} 780 -270 0 0 {name=l280 sig_type=std_logic lab=gof1}
C {lab_pin.sym} 860 -40 0 0 {name=l281 sig_type=std_logic lab=gon2}
C {lab_pin.sym} 900 -370 0 0 {name=l282 sig_type=std_logic lab=gon2}
C {lab_pin.sym} 900 -270 0 0 {name=l283 sig_type=std_logic lab=gon2}
C {lab_pin.sym} 980 -40 0 0 {name=l284 sig_type=std_logic lab=gof2}
C {lab_pin.sym} 1020 -370 0 0 {name=l285 sig_type=std_logic lab=gof2}
C {lab_pin.sym} 1020 -270 0 0 {name=l286 sig_type=std_logic lab=gof2}
C {lab_pin.sym} 1100 -40 0 0 {name=l287 sig_type=std_logic lab=gon3}
C {lab_pin.sym} 1140 -370 0 0 {name=l288 sig_type=std_logic lab=gon3}
C {lab_pin.sym} 1140 -270 0 0 {name=l289 sig_type=std_logic lab=gon3}
C {lab_pin.sym} 1220 -40 0 0 {name=l290 sig_type=std_logic lab=gof3}
C {lab_pin.sym} 1260 -370 0 0 {name=l291 sig_type=std_logic lab=gof3}
C {lab_pin.sym} 1260 -270 0 0 {name=l292 sig_type=std_logic lab=gof3}
C {lab_pin.sym} 1340 -40 0 0 {name=l293 sig_type=std_logic lab=gon4}
C {lab_pin.sym} 1380 -370 0 0 {name=l294 sig_type=std_logic lab=gon4}
C {lab_pin.sym} 1380 -270 0 0 {name=l295 sig_type=std_logic lab=gon4}
C {lab_pin.sym} 1460 -40 0 0 {name=l296 sig_type=std_logic lab=gof4}
C {lab_pin.sym} 1500 -370 0 0 {name=l297 sig_type=std_logic lab=gof4}
C {lab_pin.sym} 1500 -270 0 0 {name=l298 sig_type=std_logic lab=gof4}
C {lab_pin.sym} 1580 -40 0 0 {name=l299 sig_type=std_logic lab=gon5}
C {lab_pin.sym} 1620 -370 0 0 {name=l300 sig_type=std_logic lab=gon5}
C {lab_pin.sym} 1620 -270 0 0 {name=l301 sig_type=std_logic lab=gon5}
C {lab_pin.sym} 1700 -40 0 0 {name=l302 sig_type=std_logic lab=gof5}
C {lab_pin.sym} 1740 -370 0 0 {name=l303 sig_type=std_logic lab=gof5}
C {lab_pin.sym} 1740 -270 0 0 {name=l304 sig_type=std_logic lab=gof5}
C {lab_pin.sym} 1820 -40 0 0 {name=l305 sig_type=std_logic lab=gon6}
C {lab_pin.sym} 1860 -370 0 0 {name=l306 sig_type=std_logic lab=gon6}
C {lab_pin.sym} 1860 -270 0 0 {name=l307 sig_type=std_logic lab=gon6}
C {lab_pin.sym} 1940 -40 0 0 {name=l308 sig_type=std_logic lab=gof6}
C {lab_pin.sym} 1980 -370 0 0 {name=l309 sig_type=std_logic lab=gof6}
C {lab_pin.sym} 1980 -270 0 0 {name=l310 sig_type=std_logic lab=gof6}
C {lab_pin.sym} 2060 -40 0 0 {name=l311 sig_type=std_logic lab=gon7}
C {lab_pin.sym} 2100 -370 0 0 {name=l312 sig_type=std_logic lab=gon7}
C {lab_pin.sym} 2100 -270 0 0 {name=l313 sig_type=std_logic lab=gon7}
C {lab_pin.sym} 2180 -40 0 0 {name=l314 sig_type=std_logic lab=gof7}
C {lab_pin.sym} 2220 -370 0 0 {name=l315 sig_type=std_logic lab=gof7}
C {lab_pin.sym} 2220 -270 0 0 {name=l316 sig_type=std_logic lab=gof7}
C {lab_pin.sym} 2420 -50 0 0 {name=l317 sig_type=std_logic lab=xa}
C {lab_pin.sym} 2580 -50 0 0 {name=l318 sig_type=std_logic lab=xa}
C {lab_pin.sym} 2580 30 0 0 {name=l319 sig_type=std_logic lab=xa}
C {lab_pin.sym} 2820 -50 0 0 {name=l320 sig_type=std_logic lab=xb}
C {lab_pin.sym} 2820 30 0 0 {name=l321 sig_type=std_logic lab=xb}
C {lab_pin.sym} 2980 -50 0 0 {name=l322 sig_type=std_logic lab=xb}
C {lab_pin.sym} -900 -960 0 0 {name=l323 sig_type=std_logic lab=chb0}
C {lab_pin.sym} -900 -840 0 0 {name=l324 sig_type=std_logic lab=chb0}
C {lab_pin.sym} -540 -930 0 0 {name=l325 sig_type=std_logic lab=chb0}
C {lab_pin.sym} -540 -870 0 0 {name=l326 sig_type=std_logic lab=chb0}
C {lab_pin.sym} -900 -700 0 0 {name=l327 sig_type=std_logic lab=chb1}
C {lab_pin.sym} -900 -580 0 0 {name=l328 sig_type=std_logic lab=chb1}
C {lab_pin.sym} -540 -670 0 0 {name=l329 sig_type=std_logic lab=chb1}
C {lab_pin.sym} -540 -610 0 0 {name=l330 sig_type=std_logic lab=chb1}
C {lab_pin.sym} -900 -440 0 0 {name=l331 sig_type=std_logic lab=chb2}
C {lab_pin.sym} -900 -320 0 0 {name=l332 sig_type=std_logic lab=chb2}
C {lab_pin.sym} -540 -410 0 0 {name=l333 sig_type=std_logic lab=chb2}
C {lab_pin.sym} -540 -350 0 0 {name=l334 sig_type=std_logic lab=chb2}
C {lab_pin.sym} -900 -180 0 0 {name=l335 sig_type=std_logic lab=chb3}
C {lab_pin.sym} -900 -60 0 0 {name=l336 sig_type=std_logic lab=chb3}
C {lab_pin.sym} -540 -150 0 0 {name=l337 sig_type=std_logic lab=chb3}
C {lab_pin.sym} -540 -90 0 0 {name=l338 sig_type=std_logic lab=chb3}
C {lab_pin.sym} -1440 -620 0 0 {name=l339 sig_type=std_logic lab=pb1}
C {lab_pin.sym} -1120 -620 0 0 {name=l340 sig_type=std_logic lab=pb1}
C {lab_pin.sym} -1080 -590 0 0 {name=l341 sig_type=std_logic lab=pb1}
C {lab_pin.sym} -1080 -510 0 0 {name=l342 sig_type=std_logic lab=pb1}
C {lab_pin.sym} 1200 -1050 0 0 {name=l343 sig_type=std_logic lab=pm}
C {lab_pin.sym} 1240 -1020 0 0 {name=l344 sig_type=std_logic lab=pm}
C {lab_pin.sym} 1400 -1080 0 0 {name=l345 sig_type=std_logic lab=pm}
C {lab_pin.sym} 1520 -1050 0 0 {name=l346 sig_type=std_logic lab=pm}
C {lab_pin.sym} 380 -240 0 0 {name=l347 sig_type=std_logic lab=dacb0}
C {lab_pin.sym} 420 -690 0 0 {name=l348 sig_type=std_logic lab=dacb0}
C {lab_pin.sym} 420 -610 0 0 {name=l349 sig_type=std_logic lab=dacb0}
C {lab_pin.sym} 500 -400 0 0 {name=l350 sig_type=std_logic lab=dacb0}
C {lab_pin.sym} 620 -240 0 0 {name=l351 sig_type=std_logic lab=dacb1}
C {lab_pin.sym} 660 -690 0 0 {name=l352 sig_type=std_logic lab=dacb1}
C {lab_pin.sym} 660 -610 0 0 {name=l353 sig_type=std_logic lab=dacb1}
C {lab_pin.sym} 740 -400 0 0 {name=l354 sig_type=std_logic lab=dacb1}
C {lab_pin.sym} 860 -240 0 0 {name=l355 sig_type=std_logic lab=dacb2}
C {lab_pin.sym} 900 -690 0 0 {name=l356 sig_type=std_logic lab=dacb2}
C {lab_pin.sym} 900 -610 0 0 {name=l357 sig_type=std_logic lab=dacb2}
C {lab_pin.sym} 980 -400 0 0 {name=l358 sig_type=std_logic lab=dacb2}
C {lab_pin.sym} 1100 -240 0 0 {name=l359 sig_type=std_logic lab=dacb3}
C {lab_pin.sym} 1140 -690 0 0 {name=l360 sig_type=std_logic lab=dacb3}
C {lab_pin.sym} 1140 -610 0 0 {name=l361 sig_type=std_logic lab=dacb3}
C {lab_pin.sym} 1220 -400 0 0 {name=l362 sig_type=std_logic lab=dacb3}
C {lab_pin.sym} 1340 -240 0 0 {name=l363 sig_type=std_logic lab=dacb4}
C {lab_pin.sym} 1380 -690 0 0 {name=l364 sig_type=std_logic lab=dacb4}
C {lab_pin.sym} 1380 -610 0 0 {name=l365 sig_type=std_logic lab=dacb4}
C {lab_pin.sym} 1460 -400 0 0 {name=l366 sig_type=std_logic lab=dacb4}
C {lab_pin.sym} 1580 -240 0 0 {name=l367 sig_type=std_logic lab=dacb5}
C {lab_pin.sym} 1620 -690 0 0 {name=l368 sig_type=std_logic lab=dacb5}
C {lab_pin.sym} 1620 -610 0 0 {name=l369 sig_type=std_logic lab=dacb5}
C {lab_pin.sym} 1700 -400 0 0 {name=l370 sig_type=std_logic lab=dacb5}
C {lab_pin.sym} 1820 -240 0 0 {name=l371 sig_type=std_logic lab=dacb6}
C {lab_pin.sym} 1860 -690 0 0 {name=l372 sig_type=std_logic lab=dacb6}
C {lab_pin.sym} 1860 -610 0 0 {name=l373 sig_type=std_logic lab=dacb6}
C {lab_pin.sym} 1940 -400 0 0 {name=l374 sig_type=std_logic lab=dacb6}
C {lab_pin.sym} 2060 -240 0 0 {name=l375 sig_type=std_logic lab=dacb7}
C {lab_pin.sym} 2100 -690 0 0 {name=l376 sig_type=std_logic lab=dacb7}
C {lab_pin.sym} 2100 -610 0 0 {name=l377 sig_type=std_logic lab=dacb7}
C {lab_pin.sym} 2180 -400 0 0 {name=l378 sig_type=std_logic lab=dacb7}
C {lab_pin.sym} 80 -1050 0 0 {name=l379 sig_type=std_logic lab=cgp}
C {lab_pin.sym} 400 -1050 0 0 {name=l380 sig_type=std_logic lab=cgp}
C {lab_pin.sym} 720 -1050 0 0 {name=l381 sig_type=std_logic lab=cgp}
C {lab_pin.sym} 760 -1020 0 0 {name=l382 sig_type=std_logic lab=cgp}
C {lab_pin.sym} 920 -1080 0 0 {name=l383 sig_type=std_logic lab=cgp}
C {lab_pin.sym} 240 -1050 0 0 {name=l384 sig_type=std_logic lab=cgn}
C {lab_pin.sym} 560 -1050 0 0 {name=l385 sig_type=std_logic lab=cgn}
C {lab_pin.sym} 1040 -1050 0 0 {name=l386 sig_type=std_logic lab=cgn}
C {lab_pin.sym} 1080 -1080 0 0 {name=l387 sig_type=std_logic lab=cgn}
C {lab_pin.sym} 1560 -1020 0 0 {name=l388 sig_type=std_logic lab=cgn}
C {lab_pin.sym} 300 -650 0 0 {name=l389 sig_type=std_logic lab=dac0}
C {lab_pin.sym} 380 -720 0 0 {name=l390 sig_type=std_logic lab=dac0}
C {lab_pin.sym} 380 -580 0 0 {name=l391 sig_type=std_logic lab=dac0}
C {lab_pin.sym} 380 -400 0 0 {name=l392 sig_type=std_logic lab=dac0}
C {lab_pin.sym} 500 -240 0 0 {name=l393 sig_type=std_logic lab=dac0}
C {lab_pin.sym} 540 -650 0 0 {name=l394 sig_type=std_logic lab=dac1}
C {lab_pin.sym} 620 -720 0 0 {name=l395 sig_type=std_logic lab=dac1}
C {lab_pin.sym} 620 -580 0 0 {name=l396 sig_type=std_logic lab=dac1}
C {lab_pin.sym} 620 -400 0 0 {name=l397 sig_type=std_logic lab=dac1}
C {lab_pin.sym} 740 -240 0 0 {name=l398 sig_type=std_logic lab=dac1}
C {lab_pin.sym} 780 -650 0 0 {name=l399 sig_type=std_logic lab=dac2}
C {lab_pin.sym} 860 -720 0 0 {name=l400 sig_type=std_logic lab=dac2}
C {lab_pin.sym} 860 -580 0 0 {name=l401 sig_type=std_logic lab=dac2}
C {lab_pin.sym} 860 -400 0 0 {name=l402 sig_type=std_logic lab=dac2}
C {lab_pin.sym} 980 -240 0 0 {name=l403 sig_type=std_logic lab=dac2}
C {lab_pin.sym} 1020 -650 0 0 {name=l404 sig_type=std_logic lab=dac3}
C {lab_pin.sym} 1100 -720 0 0 {name=l405 sig_type=std_logic lab=dac3}
C {lab_pin.sym} 1100 -580 0 0 {name=l406 sig_type=std_logic lab=dac3}
C {lab_pin.sym} 1100 -400 0 0 {name=l407 sig_type=std_logic lab=dac3}
C {lab_pin.sym} 1220 -240 0 0 {name=l408 sig_type=std_logic lab=dac3}
C {lab_pin.sym} 1260 -650 0 0 {name=l409 sig_type=std_logic lab=dac4}
C {lab_pin.sym} 1340 -720 0 0 {name=l410 sig_type=std_logic lab=dac4}
C {lab_pin.sym} 1340 -580 0 0 {name=l411 sig_type=std_logic lab=dac4}
C {lab_pin.sym} 1340 -400 0 0 {name=l412 sig_type=std_logic lab=dac4}
C {lab_pin.sym} 1460 -240 0 0 {name=l413 sig_type=std_logic lab=dac4}
C {lab_pin.sym} 1500 -650 0 0 {name=l414 sig_type=std_logic lab=dac5}
C {lab_pin.sym} 1580 -720 0 0 {name=l415 sig_type=std_logic lab=dac5}
C {lab_pin.sym} 1580 -580 0 0 {name=l416 sig_type=std_logic lab=dac5}
C {lab_pin.sym} 1580 -400 0 0 {name=l417 sig_type=std_logic lab=dac5}
C {lab_pin.sym} 1700 -240 0 0 {name=l418 sig_type=std_logic lab=dac5}
C {lab_pin.sym} 1740 -650 0 0 {name=l419 sig_type=std_logic lab=dac6}
C {lab_pin.sym} 1820 -720 0 0 {name=l420 sig_type=std_logic lab=dac6}
C {lab_pin.sym} 1820 -580 0 0 {name=l421 sig_type=std_logic lab=dac6}
C {lab_pin.sym} 1820 -400 0 0 {name=l422 sig_type=std_logic lab=dac6}
C {lab_pin.sym} 1940 -240 0 0 {name=l423 sig_type=std_logic lab=dac6}
C {lab_pin.sym} 1980 -650 0 0 {name=l424 sig_type=std_logic lab=dac7}
C {lab_pin.sym} 2060 -720 0 0 {name=l425 sig_type=std_logic lab=dac7}
C {lab_pin.sym} 2060 -580 0 0 {name=l426 sig_type=std_logic lab=dac7}
C {lab_pin.sym} 2060 -400 0 0 {name=l427 sig_type=std_logic lab=dac7}
C {lab_pin.sym} 2180 -240 0 0 {name=l428 sig_type=std_logic lab=dac7}
C {lab_pin.sym} 3280 60 0 0 {name=l429 sig_type=std_logic lab=cmpb}
C {lab_pin.sym} 3400 -240 0 0 {name=l430 sig_type=std_logic lab=cmpb}
C {lab_pin.sym} 3620 -210 0 0 {name=l431 sig_type=std_logic lab=cmpb}
C {lab_pin.sym} 3620 -110 0 0 {name=l432 sig_type=std_logic lab=cmpb}
C {lab_pin.sym} 3740 -210 0 0 {name=l433 sig_type=std_logic lab=cmpb}
C {lab_pin.sym} 440 -1080 0 0 {name=l434 sig_type=std_logic lab=intr}
C {lab_pin.sym} 600 -1020 0 0 {name=l435 sig_type=std_logic lab=intr}
C {lab_pin.sym} 2360 -650 0 0 {name=l436 sig_type=std_logic lab=intr}
C {lab_pin.sym} 2520 -590 0 0 {name=l437 sig_type=std_logic lab=intr}
C {lab_pin.sym} 2680 -650 0 0 {name=l438 sig_type=std_logic lab=intr}
C {lab_pin.sym} 2780 60 0 0 {name=l439 sig_type=std_logic lab=intr}
C {lab_pin.sym} 2460 -240 0 0 {name=l440 sig_type=std_logic lab=adc_lat}
C {lab_pin.sym} 2460 -80 0 0 {name=l441 sig_type=std_logic lab=adc_lat}
C {lab_pin.sym} 2580 260 0 0 {name=l442 sig_type=std_logic lab=adc_lat}
C {lab_pin.sym} 2680 200 0 0 {name=l443 sig_type=std_logic lab=adc_lat}
C {lab_pin.sym} 2940 -240 0 0 {name=l444 sig_type=std_logic lab=adc_lat}
C {lab_pin.sym} 2940 -80 0 0 {name=l445 sig_type=std_logic lab=adc_lat}
C {lab_pin.sym} 3320 -210 0 0 {name=l446 sig_type=std_logic lab=cmp}
C {lab_pin.sym} 3320 -110 0 0 {name=l447 sig_type=std_logic lab=cmp}
C {lab_pin.sym} 3340 -360 0 0 {name=l448 sig_type=std_logic lab=cmp}
C {lab_pin.sym} 3440 -210 0 0 {name=l449 sig_type=std_logic lab=cmp}
C {lab_pin.sym} 3580 60 0 0 {name=l450 sig_type=std_logic lab=cmp}
C {lab_pin.sym} 3700 -240 0 0 {name=l451 sig_type=std_logic lab=cmp}
C {lab_pin.sym} 2420 -210 0 0 {name=l452 sig_type=std_logic lab=oa}
C {lab_pin.sym} 2580 -210 0 0 {name=l453 sig_type=std_logic lab=oa}
C {lab_pin.sym} 2580 -110 0 0 {name=l454 sig_type=std_logic lab=oa}
C {lab_pin.sym} 2780 -240 0 0 {name=l455 sig_type=std_logic lab=oa}
C {lab_pin.sym} 2780 -80 0 0 {name=l456 sig_type=std_logic lab=oa}
C {lab_pin.sym} 3280 -240 0 0 {name=l457 sig_type=std_logic lab=oa}
C {lab_pin.sym} 3280 -80 0 0 {name=l458 sig_type=std_logic lab=oa}
C {lab_pin.sym} 2620 -240 0 0 {name=l459 sig_type=std_logic lab=ob}
C {lab_pin.sym} 2620 -80 0 0 {name=l460 sig_type=std_logic lab=ob}
C {lab_pin.sym} 2820 -210 0 0 {name=l461 sig_type=std_logic lab=ob}
C {lab_pin.sym} 2820 -110 0 0 {name=l462 sig_type=std_logic lab=ob}
C {lab_pin.sym} 2980 -210 0 0 {name=l463 sig_type=std_logic lab=ob}
C {lab_pin.sym} 3580 -240 0 0 {name=l464 sig_type=std_logic lab=ob}
C {lab_pin.sym} 3580 -80 0 0 {name=l465 sig_type=std_logic lab=ob}
C {lab_pin.sym} -1280 -320 0 0 {name=l466 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -1120 -480 0 0 {name=l467 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -1080 -450 0 0 {name=l468 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -1080 -350 0 0 {name=l469 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -860 -810 0 0 {name=l470 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -860 -550 0 0 {name=l471 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -860 -290 0 0 {name=l472 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -860 -30 0 0 {name=l473 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -700 -810 0 0 {name=l474 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -700 -550 0 0 {name=l475 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -700 -290 0 0 {name=l476 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -700 -30 0 0 {name=l477 sig_type=std_logic lab=pcas}
C {lab_pin.sym} -1120 -320 0 0 {name=l478 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 40 120 0 0 {name=l479 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 180 -70 0 0 {name=l480 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 220 200 0 0 {name=l481 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 380 200 0 0 {name=l482 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 620 200 0 0 {name=l483 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 860 200 0 0 {name=l484 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 880 -1050 0 0 {name=l485 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 1100 200 0 0 {name=l486 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 1340 200 0 0 {name=l487 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 1360 -1050 0 0 {name=l488 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 1580 200 0 0 {name=l489 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 1820 200 0 0 {name=l490 sig_type=std_logic lab=ndac}
C {lab_pin.sym} 2060 200 0 0 {name=l491 sig_type=std_logic lab=ndac}
C {lab_pin.sym} -440 -660 0 0 {name=l492 sig_type=std_logic lab=vr}
C {lab_pin.sym} -380 -870 0 0 {name=l493 sig_type=std_logic lab=vr}
C {lab_pin.sym} -380 -610 0 0 {name=l494 sig_type=std_logic lab=vr}
C {lab_pin.sym} -380 -350 0 0 {name=l495 sig_type=std_logic lab=vr}
C {lab_pin.sym} -380 -90 0 0 {name=l496 sig_type=std_logic lab=vr}
C {lab_pin.sym} 120 -1020 0 0 {name=l497 sig_type=std_logic lab=vr}
C {lab_pin.sym} 120 -590 0 0 {name=l498 sig_type=std_logic lab=vr}
C {lab_pin.sym} 280 -1080 0 0 {name=l499 sig_type=std_logic lab=vr}
C {lab_pin.sym} 440 -1020 0 0 {name=l500 sig_type=std_logic lab=vr}
C {lab_pin.sym} 600 -1080 0 0 {name=l501 sig_type=std_logic lab=vr}
C {lab_pin.sym} 760 -1080 0 0 {name=l502 sig_type=std_logic lab=vr}
C {lab_pin.sym} 1080 -1020 0 0 {name=l503 sig_type=std_logic lab=vr}
C {lab_pin.sym} 2360 -590 0 0 {name=l504 sig_type=std_logic lab=vr}
C {lab_pin.sym} 2520 -650 0 0 {name=l505 sig_type=std_logic lab=vr}
C {lab_pin.sym} 2680 -590 0 0 {name=l506 sig_type=std_logic lab=vr}
C {lab_pin.sym} -180 -870 0 0 {name=l507 sig_type=std_logic lab=int}
C {lab_pin.sym} -180 -610 0 0 {name=l508 sig_type=std_logic lab=int}
C {lab_pin.sym} -180 -350 0 0 {name=l509 sig_type=std_logic lab=int}
C {lab_pin.sym} -180 -90 0 0 {name=l510 sig_type=std_logic lab=int}
C {lab_pin.sym} 120 -1080 0 0 {name=l511 sig_type=std_logic lab=int}
C {lab_pin.sym} 120 -650 0 0 {name=l512 sig_type=std_logic lab=int}
C {lab_pin.sym} 280 -1020 0 0 {name=l513 sig_type=std_logic lab=int}
C {lab_pin.sym} 420 -70 0 0 {name=l514 sig_type=std_logic lab=int}
C {lab_pin.sym} 660 -70 0 0 {name=l515 sig_type=std_logic lab=int}
C {lab_pin.sym} 900 -70 0 0 {name=l516 sig_type=std_logic lab=int}
C {lab_pin.sym} 1140 -70 0 0 {name=l517 sig_type=std_logic lab=int}
C {lab_pin.sym} 1380 -70 0 0 {name=l518 sig_type=std_logic lab=int}
C {lab_pin.sym} 1620 -70 0 0 {name=l519 sig_type=std_logic lab=int}
C {lab_pin.sym} 1860 -70 0 0 {name=l520 sig_type=std_logic lab=int}
C {lab_pin.sym} 2100 -70 0 0 {name=l521 sig_type=std_logic lab=int}
C {lab_pin.sym} 2620 60 0 0 {name=l522 sig_type=std_logic lab=int}
C {lab_pin.sym} -1440 -320 0 0 {name=l523 sig_type=std_logic lab=vcl}
C {lab_pin.sym} -1400 -590 0 0 {name=l524 sig_type=std_logic lab=vcl}
C {lab_pin.sym} -1400 -350 0 0 {name=l525 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 420 -430 0 0 {name=l526 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 540 -430 0 0 {name=l527 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 660 -430 0 0 {name=l528 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 780 -430 0 0 {name=l529 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 900 -430 0 0 {name=l530 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 1020 -430 0 0 {name=l531 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 1140 -430 0 0 {name=l532 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 1260 -430 0 0 {name=l533 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 1380 -430 0 0 {name=l534 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 1500 -430 0 0 {name=l535 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 1620 -430 0 0 {name=l536 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 1740 -430 0 0 {name=l537 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 1860 -430 0 0 {name=l538 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 1980 -430 0 0 {name=l539 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 2100 -430 0 0 {name=l540 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 2220 -430 0 0 {name=l541 sig_type=std_logic lab=vcl}
C {lab_pin.sym} 3320 -50 0 0 {name=l542 sig_type=std_logic lab=n_cmp}
C {lab_pin.sym} 3620 -50 0 0 {name=l543 sig_type=std_logic lab=n_cmpb}
C {lab_pin.sym} 180 -10 0 0 {name=l544 sig_type=std_logic lab=nd2}
C {lab_pin.sym} 420 -10 0 0 {name=l545 sig_type=std_logic lab=sk0}
C {lab_pin.sym} 660 -10 0 0 {name=l546 sig_type=std_logic lab=sk1}
C {lab_pin.sym} 900 -10 0 0 {name=l547 sig_type=std_logic lab=sk2}
C {lab_pin.sym} 1140 -10 0 0 {name=l548 sig_type=std_logic lab=sk3}
C {lab_pin.sym} 1380 -10 0 0 {name=l549 sig_type=std_logic lab=sk4}
C {lab_pin.sym} 1620 -10 0 0 {name=l550 sig_type=std_logic lab=sk5}
C {lab_pin.sym} 1860 -10 0 0 {name=l551 sig_type=std_logic lab=sk6}
C {lab_pin.sym} 2100 -10 0 0 {name=l552 sig_type=std_logic lab=sk7}
C {lab_pin.sym} 2580 90 0 0 {name=l553 sig_type=std_logic lab=tl}
C {ipin.sym} -280 -980 0 0 {name=p554 lab=out0}
C {ipin.sym} -1000 -900 0 0 {name=p555 lab=adc_ch0}
C {ipin.sym} -280 -720 0 0 {name=p556 lab=out1}
C {ipin.sym} -1000 -640 0 0 {name=p557 lab=adc_ch1}
C {ipin.sym} -280 -460 0 0 {name=p558 lab=out2}
C {ipin.sym} -1000 -380 0 0 {name=p559 lab=adc_ch2}
C {ipin.sym} -280 -200 0 0 {name=p560 lab=out3}
C {ipin.sym} -1000 -120 0 0 {name=p561 lab=adc_ch3}
C {ipin.sym} 300 -650 0 0 {name=p562 lab=dac0}
C {ipin.sym} 540 -650 0 0 {name=p563 lab=dac1}
C {ipin.sym} 780 -650 0 0 {name=p564 lab=dac2}
C {ipin.sym} 1020 -650 0 0 {name=p565 lab=dac3}
C {ipin.sym} 1260 -650 0 0 {name=p566 lab=dac4}
C {ipin.sym} 1500 -650 0 0 {name=p567 lab=dac5}
C {ipin.sym} 1740 -650 0 0 {name=p568 lab=dac6}
C {ipin.sym} 1980 -650 0 0 {name=p569 lab=dac7}
C {ipin.sym} 40 120 0 0 {name=p570 lab=ndac}
C {ipin.sym} 120 -60 0 0 {name=p571 lab=vcas}
C {ipin.sym} -440 -660 0 0 {name=p572 lab=vr}
C {ipin.sym} 20 -480 0 0 {name=p573 lab=adc_rst}
C {ipin.sym} 2580 260 0 0 {name=p574 lab=adc_lat}
C {opin.sym} 3340 -360 0 0 {name=p575 lab=cmp}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -200 -900 0 0 {name=Mcs0 L=0.5 W=4.2 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=1.218 pd=8.98 nrd=0.06905 nrs=0.06905 sa=0 sb=0 sd=0 as=1.218 ps=8.98}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -360 -900 0 1 {name=Mcd0 L=0.5 W=4.2 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=1.218 pd=8.98 nrd=0.06905 nrs=0.06905 sa=0 sb=0 sd=0 as=1.218 ps=8.98}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -560 -960 0 0 {name=Mib0p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -560 -840 0 0 {name=Mib0n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -720 -960 0 0 {name=Mgs0p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -720 -840 0 0 {name=Mgs0n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -880 -960 0 0 {name=Mgd0p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -880 -840 0 0 {name=Mgd0n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -200 -640 0 0 {name=Mcs1 L=0.5 W=4.2 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=1.218 pd=8.98 nrd=0.06905 nrs=0.06905 sa=0 sb=0 sd=0 as=1.218 ps=8.98}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -360 -640 0 1 {name=Mcd1 L=0.5 W=4.2 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=1.218 pd=8.98 nrd=0.06905 nrs=0.06905 sa=0 sb=0 sd=0 as=1.218 ps=8.98}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -560 -700 0 0 {name=Mib1p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -560 -580 0 0 {name=Mib1n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -720 -700 0 0 {name=Mgs1p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -720 -580 0 0 {name=Mgs1n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -880 -700 0 0 {name=Mgd1p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -880 -580 0 0 {name=Mgd1n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -200 -380 0 0 {name=Mcs2 L=0.5 W=4.2 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=1.218 pd=8.98 nrd=0.06905 nrs=0.06905 sa=0 sb=0 sd=0 as=1.218 ps=8.98}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -360 -380 0 1 {name=Mcd2 L=0.5 W=4.2 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=1.218 pd=8.98 nrd=0.06905 nrs=0.06905 sa=0 sb=0 sd=0 as=1.218 ps=8.98}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -560 -440 0 0 {name=Mib2p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -560 -320 0 0 {name=Mib2n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -720 -440 0 0 {name=Mgs2p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -720 -320 0 0 {name=Mgs2n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -880 -440 0 0 {name=Mgd2p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -880 -320 0 0 {name=Mgd2n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -200 -120 0 0 {name=Mcs3 L=0.5 W=4.2 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=1.218 pd=8.98 nrd=0.06905 nrs=0.06905 sa=0 sb=0 sd=0 as=1.218 ps=8.98}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -360 -120 0 1 {name=Mcd3 L=0.5 W=4.2 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=1.218 pd=8.98 nrd=0.06905 nrs=0.06905 sa=0 sb=0 sd=0 as=1.218 ps=8.98}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -560 -180 0 0 {name=Mib3p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -560 -60 0 0 {name=Mib3n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -720 -180 0 0 {name=Mgs3p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -720 -60 0 0 {name=Mgs3n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -880 -180 0 0 {name=Mgd3p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -880 -60 0 0 {name=Mgd3n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -1100 -620 0 0 {name=Mpb1 L=0.5 W=0.42 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -1100 -480 0 0 {name=Mpb2 L=0.5 W=0.42 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -1100 -320 0 0 {name=Mpbn L=2 W=4.68 nf=1 mult=16 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -1260 -320 0 0 {name=Cpc L=6 W=6 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=1.74 pd=12.58 nrd=0.04833 nrs=0.04833 sa=0 sb=0 sd=0 as=1.74 ps=12.58}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -1420 -620 0 0 {name=Mvp L=0.5 W=0.42 nf=1 mult=16 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -1420 -320 0 0 {name=Mvl L=2 W=0.58 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1682 pd=1.74 nrd=0.5 nrs=0.5 sa=0 sb=0 sd=0 as=0.1682 ps=1.74}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -1580 -320 0 0 {name=Cvc L=6 W=6 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=1.74 pd=12.58 nrd=0.04833 nrs=0.04833 sa=0 sb=0 sd=0 as=1.74 ps=12.58}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 100 -620 0 0 {name=Mrst L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 100 -1050 0 0 {name=Mcu L=0.5 W=0.42 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 260 -1050 0 0 {name=Mcl L=0.5 W=0.42 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 420 -1050 0 0 {name=Mcur L=0.5 W=0.42 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 580 -1050 0 0 {name=Mclr L=0.5 W=0.42 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 740 -1050 0 0 {name=Mru L=0.5 W=0.42 nf=1 mult=8 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 900 -1050 0 0 {name=Mku L=2 W=4.68 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1060 -1050 0 0 {name=Mrl L=0.5 W=0.42 nf=1 mult=8 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 1220 -1050 0 0 {name=Mpm L=0.5 W=0.42 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1380 -1050 0 0 {name=Mku2 L=2 W=4.68 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 1540 -1050 0 0 {name=Mpm2 L=0.5 W=0.42 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2340 -620 0 0 {name=Mrstr L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 2500 -620 0 0 {name=Mdcs L=0.5 W=4.2 nf=1 mult=4 model=pfet_g5v0d10v5 spiceprefix=X ad=1.218 pd=8.98 nrd=0.06905 nrs=0.06905 sa=0 sb=0 sd=0 as=1.218 ps=8.98}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2660 -620 0 0 {name=Mdsw L=1 W=0.42 nf=1 mult=34 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 200 -40 0 1 {name=Mdc L=1 W=0.42 nf=1 mult=2 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 200 200 0 1 {name=Mdd L=2 W=4.74 nf=1 mult=16 model=nfet_g5v0d10v5 spiceprefix=X ad=1.375 pd=10.06 nrd=0.06118 nrs=0.06118 sa=0 sb=0 sd=0 as=1.375 ps=10.06}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 400 -720 0 0 {name=Mdi0p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 400 -580 0 0 {name=Mdi0n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 400 -40 0 0 {name=Mon0 L=1 W=0.42 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 520 -40 0 0 {name=Mof0 L=1 W=0.42 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 400 -400 0 0 {name=Mgn0p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 400 -240 0 0 {name=Mgn0n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 520 -400 0 0 {name=Mgf0p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 520 -240 0 0 {name=Mgf0n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 400 200 0 0 {name=Mu0 L=2 W=4.68 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 640 -720 0 0 {name=Mdi1p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 640 -580 0 0 {name=Mdi1n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 640 -40 0 0 {name=Mon1 L=1 W=0.42 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 760 -40 0 0 {name=Mof1 L=1 W=0.42 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 640 -400 0 0 {name=Mgn1p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 640 -240 0 0 {name=Mgn1n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 760 -400 0 0 {name=Mgf1p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 760 -240 0 0 {name=Mgf1n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 640 200 0 0 {name=Mu1 L=2 W=4.68 nf=1 mult=2 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 880 -720 0 0 {name=Mdi2p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 880 -580 0 0 {name=Mdi2n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 880 -40 0 0 {name=Mon2 L=1 W=0.42 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1000 -40 0 0 {name=Mof2 L=1 W=0.42 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 880 -400 0 0 {name=Mgn2p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 880 -240 0 0 {name=Mgn2n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1000 -400 0 0 {name=Mgf2p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1000 -240 0 0 {name=Mgf2n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 880 200 0 0 {name=Mu2 L=2 W=4.68 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 1120 -720 0 0 {name=Mdi3p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1120 -580 0 0 {name=Mdi3n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1120 -40 0 0 {name=Mon3 L=1 W=0.42 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1240 -40 0 0 {name=Mof3 L=1 W=0.42 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1120 -400 0 0 {name=Mgn3p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1120 -240 0 0 {name=Mgn3n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1240 -400 0 0 {name=Mgf3p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1240 -240 0 0 {name=Mgf3n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1120 200 0 0 {name=Mu3 L=2 W=4.68 nf=1 mult=8 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 1360 -720 0 0 {name=Mdi4p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1360 -580 0 0 {name=Mdi4n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1360 -40 0 0 {name=Mon4 L=1 W=0.42 nf=1 mult=2 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1480 -40 0 0 {name=Mof4 L=1 W=0.42 nf=1 mult=2 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1360 -400 0 0 {name=Mgn4p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1360 -240 0 0 {name=Mgn4n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1480 -400 0 0 {name=Mgf4p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1480 -240 0 0 {name=Mgf4n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1360 200 0 0 {name=Mu4 L=2 W=4.68 nf=1 mult=16 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 1600 -720 0 0 {name=Mdi5p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1600 -580 0 0 {name=Mdi5n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1600 -40 0 0 {name=Mon5 L=1 W=0.42 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1720 -40 0 0 {name=Mof5 L=1 W=0.42 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1600 -400 0 0 {name=Mgn5p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1600 -240 0 0 {name=Mgn5n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1720 -400 0 0 {name=Mgf5p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1720 -240 0 0 {name=Mgf5n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1600 200 0 0 {name=Mu5 L=2 W=4.68 nf=1 mult=32 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 1840 -720 0 0 {name=Mdi6p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1840 -580 0 0 {name=Mdi6n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1840 -40 0 0 {name=Mon6 L=1 W=0.42 nf=1 mult=8 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1960 -40 0 0 {name=Mof6 L=1 W=0.42 nf=1 mult=8 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1840 -400 0 0 {name=Mgn6p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1840 -240 0 0 {name=Mgn6n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1960 -400 0 0 {name=Mgf6p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1960 -240 0 0 {name=Mgf6n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1840 200 0 0 {name=Mu6 L=2 W=4.68 nf=1 mult=64 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 2080 -720 0 0 {name=Mdi7p L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2080 -580 0 0 {name=Mdi7n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2080 -40 0 0 {name=Mon7 L=1 W=0.42 nf=1 mult=16 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2200 -40 0 0 {name=Mof7 L=1 W=0.42 nf=1 mult=16 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2080 -400 0 0 {name=Mgn7p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2080 -240 0 0 {name=Mgn7n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2200 -400 0 0 {name=Mgf7p L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2200 -240 0 0 {name=Mgf7n L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2080 200 0 0 {name=Mu7 L=2 W=4.68 nf=1 mult=128 model=nfet_g5v0d10v5 spiceprefix=X ad=1.357 pd=9.94 nrd=0.06197 nrs=0.06197 sa=0 sb=0 sd=0 as=1.357 ps=9.94}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2700 200 0 0 {name=Mtl L=0.5 W=0.57 nf=1 mult=2 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1653 pd=1.72 nrd=0.5088 nrs=0.5088 sa=0 sb=0 sd=0 as=0.1653 ps=1.72}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2600 60 0 1 {name=M1a L=1 W=4.21 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=1.221 pd=9 nrd=0.06888 nrs=0.06888 sa=0 sb=0 sd=0 as=1.221 ps=9}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2800 60 0 0 {name=M1b L=1 W=4.21 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=1.221 pd=9 nrd=0.06888 nrs=0.06888 sa=0 sb=0 sd=0 as=1.221 ps=9}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2600 -80 0 1 {name=M2a L=0.5 W=0.57 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1653 pd=1.72 nrd=0.5088 nrs=0.5088 sa=0 sb=0 sd=0 as=0.1653 ps=1.72}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 2800 -80 0 0 {name=M2b L=0.5 W=0.57 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1653 pd=1.72 nrd=0.5088 nrs=0.5088 sa=0 sb=0 sd=0 as=0.1653 ps=1.72}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 2600 -240 0 1 {name=M3a L=0.5 W=0.57 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1653 pd=1.72 nrd=0.5088 nrs=0.5088 sa=0 sb=0 sd=0 as=0.1653 ps=1.72}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 2800 -240 0 0 {name=M3b L=0.5 W=0.57 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1653 pd=1.72 nrd=0.5088 nrs=0.5088 sa=0 sb=0 sd=0 as=0.1653 ps=1.72}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 2440 -240 0 1 {name=Mra L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 2960 -240 0 0 {name=Mrb L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 2440 -80 0 1 {name=Mrxa L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 2960 -80 0 0 {name=Mrxb L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 3300 -240 0 0 {name=Mp_cmpa L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 3420 -240 0 0 {name=Mp_cmpb L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 3300 -80 0 0 {name=Mn_cmpa L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 3300 60 0 0 {name=Mn_cmpb L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 3600 -240 0 0 {name=Mp_cmpba L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 3720 -240 0 0 {name=Mp_cmpbb L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 3600 -80 0 0 {name=Mn_cmpba L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 3600 60 0 0 {name=Mn_cmpbb L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
