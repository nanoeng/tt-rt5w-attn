v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {8 x 1.8 V -> 3.3 V level shifters} -100 -300 0 0 0.4 0.4 {}
N 0 -50 0 -70 {lab=vdd}
C {vdd.sym} 0 -70 0 0 {name=r1 lab=vdd}
N 500 -50 500 -70 {lab=vdd}
C {vdd.sym} 500 -70 0 0 {name=r2 lab=vdd}
N 1000 -50 1000 -70 {lab=vdd}
C {vdd.sym} 1000 -70 0 0 {name=r3 lab=vdd}
N 1500 -50 1500 -70 {lab=vdd}
C {vdd.sym} 1500 -70 0 0 {name=r4 lab=vdd}
N 2000 -50 2000 -70 {lab=vdd}
C {vdd.sym} 2000 -70 0 0 {name=r5 lab=vdd}
N 2500 -50 2500 -70 {lab=vdd}
C {vdd.sym} 2500 -70 0 0 {name=r6 lab=vdd}
N 3000 -50 3000 -70 {lab=vdd}
C {vdd.sym} 3000 -70 0 0 {name=r7 lab=vdd}
N 3500 -50 3500 -70 {lab=vdd}
C {vdd.sym} 3500 -70 0 0 {name=r8 lab=vdd}
N 0 50 0 70 {lab=vss}
C {gnd.sym} 0 70 0 0 {name=r9 lab=vss}
N 500 50 500 70 {lab=vss}
C {gnd.sym} 500 70 0 0 {name=r10 lab=vss}
N 1000 50 1000 70 {lab=vss}
C {gnd.sym} 1000 70 0 0 {name=r11 lab=vss}
N 1500 50 1500 70 {lab=vss}
C {gnd.sym} 1500 70 0 0 {name=r12 lab=vss}
N 2000 50 2000 70 {lab=vss}
C {gnd.sym} 2000 70 0 0 {name=r13 lab=vss}
N 2500 50 2500 70 {lab=vss}
C {gnd.sym} 2500 70 0 0 {name=r14 lab=vss}
N 3000 50 3000 70 {lab=vss}
C {gnd.sym} 3000 70 0 0 {name=r15 lab=vss}
N 3500 50 3500 70 {lab=vss}
C {gnd.sym} 3500 70 0 0 {name=r16 lab=vss}
C {lab_pin.sym} -400 600 0 0 {name=l17 sig_type=std_logic lab=in0}
C {lab_pin.sym} -100 -10 0 0 {name=l18 sig_type=std_logic lab=in0}
C {lab_pin.sym} 100 -10 0 0 {name=l19 sig_type=std_logic lab=out0}
C {lab_pin.sym} 4400 600 0 0 {name=l20 sig_type=std_logic lab=out0}
C {lab_pin.sym} -400 640 0 0 {name=l21 sig_type=std_logic lab=in1}
C {lab_pin.sym} 400 -10 0 0 {name=l22 sig_type=std_logic lab=in1}
C {lab_pin.sym} 600 -10 0 0 {name=l23 sig_type=std_logic lab=out1}
C {lab_pin.sym} 4400 640 0 0 {name=l24 sig_type=std_logic lab=out1}
C {lab_pin.sym} -400 680 0 0 {name=l25 sig_type=std_logic lab=in2}
C {lab_pin.sym} 900 -10 0 0 {name=l26 sig_type=std_logic lab=in2}
C {lab_pin.sym} 1100 -10 0 0 {name=l27 sig_type=std_logic lab=out2}
C {lab_pin.sym} 4400 680 0 0 {name=l28 sig_type=std_logic lab=out2}
C {lab_pin.sym} -400 720 0 0 {name=l29 sig_type=std_logic lab=in3}
C {lab_pin.sym} 1400 -10 0 0 {name=l30 sig_type=std_logic lab=in3}
C {lab_pin.sym} 1600 -10 0 0 {name=l31 sig_type=std_logic lab=out3}
C {lab_pin.sym} 4400 720 0 0 {name=l32 sig_type=std_logic lab=out3}
C {lab_pin.sym} -400 760 0 0 {name=l33 sig_type=std_logic lab=in4}
C {lab_pin.sym} 1900 -10 0 0 {name=l34 sig_type=std_logic lab=in4}
C {lab_pin.sym} 2100 -10 0 0 {name=l35 sig_type=std_logic lab=out4}
C {lab_pin.sym} 4400 760 0 0 {name=l36 sig_type=std_logic lab=out4}
C {lab_pin.sym} -400 800 0 0 {name=l37 sig_type=std_logic lab=in5}
C {lab_pin.sym} 2400 -10 0 0 {name=l38 sig_type=std_logic lab=in5}
C {lab_pin.sym} 2600 -10 0 0 {name=l39 sig_type=std_logic lab=out5}
C {lab_pin.sym} 4400 800 0 0 {name=l40 sig_type=std_logic lab=out5}
C {lab_pin.sym} -400 840 0 0 {name=l41 sig_type=std_logic lab=in6}
C {lab_pin.sym} 2900 -10 0 0 {name=l42 sig_type=std_logic lab=in6}
C {lab_pin.sym} 3100 -10 0 0 {name=l43 sig_type=std_logic lab=out6}
C {lab_pin.sym} 4400 840 0 0 {name=l44 sig_type=std_logic lab=out6}
C {lab_pin.sym} -400 880 0 0 {name=l45 sig_type=std_logic lab=in7}
C {lab_pin.sym} 3400 -10 0 0 {name=l46 sig_type=std_logic lab=in7}
C {lab_pin.sym} 3600 -10 0 0 {name=l47 sig_type=std_logic lab=out7}
C {lab_pin.sym} 4400 880 0 0 {name=l48 sig_type=std_logic lab=out7}
C {lab_pin.sym} -400 1200 0 0 {name=l49 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 100 10 0 0 {name=l50 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 600 10 0 0 {name=l51 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 1100 10 0 0 {name=l52 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 1600 10 0 0 {name=l53 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 2100 10 0 0 {name=l54 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 2600 10 0 0 {name=l55 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 3100 10 0 0 {name=l56 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 3600 10 0 0 {name=l57 sig_type=std_logic lab=vddl}
C {ipin.sym} -400 600 0 0 {name=p58 lab=in0}
C {opin.sym} 4400 600 0 0 {name=p59 lab=out0}
C {ipin.sym} -400 640 0 0 {name=p60 lab=in1}
C {opin.sym} 4400 640 0 0 {name=p61 lab=out1}
C {ipin.sym} -400 680 0 0 {name=p62 lab=in2}
C {opin.sym} 4400 680 0 0 {name=p63 lab=out2}
C {ipin.sym} -400 720 0 0 {name=p64 lab=in3}
C {opin.sym} 4400 720 0 0 {name=p65 lab=out3}
C {ipin.sym} -400 760 0 0 {name=p66 lab=in4}
C {opin.sym} 4400 760 0 0 {name=p67 lab=out4}
C {ipin.sym} -400 800 0 0 {name=p68 lab=in5}
C {opin.sym} 4400 800 0 0 {name=p69 lab=out5}
C {ipin.sym} -400 840 0 0 {name=p70 lab=in6}
C {opin.sym} 4400 840 0 0 {name=p71 lab=out6}
C {ipin.sym} -400 880 0 0 {name=p72 lab=in7}
C {opin.sym} 4400 880 0 0 {name=p73 lab=out7}
C {iopin.sym} -400 1200 0 0 {name=p74 lab=vddl}
C {rt5w_lsup.sym} 0 0 0 0 {name=xl0}
C {rt5w_lsup.sym} 500 0 0 0 {name=xl1}
C {rt5w_lsup.sym} 1000 0 0 0 {name=xl2}
C {rt5w_lsup.sym} 1500 0 0 0 {name=xl3}
C {rt5w_lsup.sym} 2000 0 0 0 {name=xl4}
C {rt5w_lsup.sym} 2500 0 0 0 {name=xl5}
C {rt5w_lsup.sym} 3000 0 0 0 {name=xl6}
C {rt5w_lsup.sym} 3500 0 0 0 {name=xl7}
