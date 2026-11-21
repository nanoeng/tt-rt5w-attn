v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Key cell: g = dcol + (h - w);  I_cell = I_Q * exp(-(h - w)/nU_T,p)} -260 -430 0 0 0.45 0.45 {}
N -200 60 -100 60 {lab=dcol}
N -100 60 -100 -120 {lab=dcol}
N 300 -120 300 60 {lab=w}
N 300 60 440 60 {lab=w}
N 620 -220 700 -220 {lab=row}
N 700 -220 700 -400 {lab=row}
N -140 -90 -140 -10 {lab=ta}
N -140 -10 20 -10 {lab=ta}
N 20 -10 20 -90 {lab=ta}
N 20 -90 140 -90 {lab=ta}
N -120 140 -120 20 {lab=vbn}
N -120 20 -20 20 {lab=vbn}
N -120 140 380 140 {lab=vbn}
N 380 140 380 20 {lab=vbn}
N -800 -330 -800 -290 {lab=wselb}
N -800 -290 -740 -290 {lab=wselb}
N -740 -290 -740 -180 {lab=wselb}
N -960 -310 -960 -360 {lab=wsel}
N -960 -360 -840 -360 {lab=wsel}
N -840 -360 -840 -260 {lab=wsel}
N -960 -310 -580 -310 {lab=wsel}
N -580 -310 -580 -180 {lab=wsel}
N -340 -150 -140 -150 {lab=nl}
N -140 -150 -140 -220 {lab=nl}
N -140 -220 -20 -220 {lab=nl}
N -20 -220 20 -220 {lab=nl}
N 20 -220 20 -250 {lab=nl}
N 20 -250 180 -250 {lab=nl}
N 100 -120 100 -150 {lab=g}
N 100 -150 140 -150 {lab=g}
N 140 -150 140 -220 {lab=g}
N 140 -220 220 -220 {lab=g}
N 220 -220 220 -150 {lab=g}
N 220 -150 340 -150 {lab=g}
N 340 -150 340 -250 {lab=g}
N 340 -250 580 -250 {lab=g}
N -800 -390 -800 -410 {lab=vdd}
C {vdd.sym} -800 -410 0 0 {name=r1 lab=vdd}
N -20 -280 -20 -300 {lab=vdd}
C {vdd.sym} -20 -300 0 0 {name=r2 lab=vdd}
N 220 -280 220 -300 {lab=vdd}
C {vdd.sym} 220 -300 0 0 {name=r3 lab=vdd}
N 620 -280 620 -300 {lab=vdd}
C {vdd.sym} 620 -300 0 0 {name=r4 lab=vdd}
N -800 -230 -800 -210 {lab=vss}
C {gnd.sym} -800 -210 0 0 {name=r5 lab=vss}
N -500 10 -500 30 {lab=vss}
C {gnd.sym} -500 30 0 0 {name=r6 lab=vss}
N -500 70 -500 90 {lab=vss}
C {gnd.sym} -500 90 0 0 {name=r7 lab=vss}
N 20 50 20 70 {lab=vss}
C {gnd.sym} 20 70 0 0 {name=r8 lab=vss}
N 420 50 420 70 {lab=vss}
C {gnd.sym} 420 70 0 0 {name=r9 lab=vss}
C {lab_pin.sym} -500 40 0 0 {name=l10 sig_type=std_logic lab=vss}
C {lab_pin.sym} -800 -260 0 0 {name=l11 sig_type=std_logic lab=vss}
C {lab_pin.sym} 340 -120 0 0 {name=l12 sig_type=std_logic lab=vss}
C {lab_pin.sym} 140 -120 0 0 {name=l13 sig_type=std_logic lab=vss}
C {lab_pin.sym} -140 -120 0 0 {name=l14 sig_type=std_logic lab=vss}
C {lab_pin.sym} -540 -180 0 0 {name=l15 sig_type=std_logic lab=vss}
C {lab_pin.sym} 220 -250 0 0 {name=l16 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 20 20 0 0 {name=l17 sig_type=std_logic lab=vss}
C {lab_pin.sym} -20 -250 0 0 {name=l18 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 420 20 0 0 {name=l19 sig_type=std_logic lab=vss}
C {lab_pin.sym} -700 -180 0 0 {name=l20 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 620 -250 0 0 {name=l21 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -800 -360 0 0 {name=l22 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -340 -120 0 0 {name=l23 sig_type=std_logic lab=vss}
C {lab_pin.sym} -340 -90 0 0 {name=l24 sig_type=std_logic lab=tb}
C {lab_pin.sym} 340 -90 0 0 {name=l25 sig_type=std_logic lab=tb}
C {lab_pin.sym} 420 -10 0 0 {name=l26 sig_type=std_logic lab=tb}
C {lab_pin.sym} -900 -100 0 0 {name=l27 sig_type=std_logic lab=vw}
C {lab_pin.sym} -700 -210 0 0 {name=l28 sig_type=std_logic lab=vw}
C {lab_pin.sym} -540 -150 0 0 {name=l29 sig_type=std_logic lab=vw}
C {lab_pin.sym} -700 -150 0 0 {name=l30 sig_type=std_logic lab=h}
C {lab_pin.sym} -540 -210 0 0 {name=l31 sig_type=std_logic lab=h}
C {lab_pin.sym} -540 40 0 0 {name=l32 sig_type=std_logic lab=h}
C {lab_pin.sym} -300 -120 0 0 {name=l33 sig_type=std_logic lab=h}
C {lab_pin.sym} 100 -120 0 0 {name=l34 sig_type=std_logic lab=g}
C {lab_pin.sym} -340 -150 0 0 {name=l35 sig_type=std_logic lab=nl}
C {lab_pin.sym} -140 -90 0 0 {name=l36 sig_type=std_logic lab=ta}
C {lab_pin.sym} -800 -330 0 0 {name=l37 sig_type=std_logic lab=wselb}
C {iopin.sym} -200 60 0 0 {name=p38 lab=dcol}
C {ipin.sym} 440 60 0 0 {name=p39 lab=w}
C {iopin.sym} -900 -100 0 0 {name=p40 lab=vw}
C {ipin.sym} -960 -310 0 0 {name=p41 lab=wsel}
C {ipin.sym} -120 140 0 0 {name=p42 lab=vbn}
C {iopin.sym} 700 -400 0 0 {name=p43 lab=row}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 0 -250 0 1 {name=Mp1 L=4 W=4.14 nf=1 mult=2 model=pfet_g5v0d10v5 spiceprefix=X ad=1.201 pd=8.86 nrd=0.07005 nrs=0.07005 sa=0 sb=0 sd=0 as=1.201 ps=8.86}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 200 -250 0 0 {name=Mp2 L=4 W=4.14 nf=1 mult=2 model=pfet_g5v0d10v5 spiceprefix=X ad=1.201 pd=8.86 nrd=0.07005 nrs=0.07005 sa=0 sb=0 sd=0 as=1.201 ps=8.86}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -120 -120 0 1 {name=M1 L=4 W=0.62 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1798 pd=1.82 nrd=0.4677 nrs=0.4677 sa=0 sb=0 sd=0 as=0.1798 ps=1.82}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 120 -120 0 0 {name=M2 L=4 W=0.62 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1798 pd=1.82 nrd=0.4677 nrs=0.4677 sa=0 sb=0 sd=0 as=0.1798 ps=1.82}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -320 -120 0 1 {name=M3 L=4 W=0.62 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1798 pd=1.82 nrd=0.4677 nrs=0.4677 sa=0 sb=0 sd=0 as=0.1798 ps=1.82}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 320 -120 0 0 {name=M4 L=4 W=0.62 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1798 pd=1.82 nrd=0.4677 nrs=0.4677 sa=0 sb=0 sd=0 as=0.1798 ps=1.82}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 0 20 0 0 {name=Mt1 L=4 W=2.24 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6496 pd=5.06 nrd=0.1295 nrs=0.1295 sa=0 sb=0 sd=0 as=0.6496 ps=5.06}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 400 20 0 0 {name=Mt2 L=4 W=2.24 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6496 pd=5.06 nrd=0.1295 nrs=0.1295 sa=0 sb=0 sd=0 as=0.6496 ps=5.06}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 600 -250 0 0 {name=Mc L=4 W=8.27 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=2.398 pd=17.12 nrd=0.03507 nrs=0.03507 sa=0 sb=0 sd=0 as=2.398 ps=17.12}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -520 40 0 0 {name=Cw L=10.4 W=10.4 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=3.016 pd=21.38 nrd=0.02788 nrs=0.02788 sa=0 sb=0 sd=0 as=3.016 ps=21.38}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -560 -180 0 0 {name=Mwn L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -720 -180 0 0 {name=Mwp L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -820 -360 0 0 {name=Mip L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -820 -260 0 0 {name=Min L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
