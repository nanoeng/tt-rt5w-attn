v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {V_B buffer: unity-gain two-stage Miller op amp, TG to ua[1]} -200 -620 0 0 0.5 0.5 {}
N -280 -140 -280 -110 {lab=vbn}
N -280 -110 -220 -110 {lab=vbn}
N -20 -410 -20 -290 {lab=d1}
N -20 -410 20 -410 {lab=d1}
N 20 -410 20 -440 {lab=d1}
N 20 -440 220 -440 {lab=d1}
N -380 -230 -380 -250 {lab=vdd}
C {vdd.sym} -380 -250 0 0 {name=r1 lab=vdd}
N -20 -470 -20 -490 {lab=vdd}
C {vdd.sym} -20 -490 0 0 {name=r2 lab=vdd}
N 260 -470 260 -490 {lab=vdd}
C {vdd.sym} 260 -490 0 0 {name=r3 lab=vdd}
N 420 -590 420 -610 {lab=vdd}
C {vdd.sym} 420 -610 0 0 {name=r4 lab=vdd}
N 580 -470 580 -490 {lab=vdd}
C {vdd.sym} 580 -490 0 0 {name=r5 lab=vdd}
N -380 -30 -380 -10 {lab=vss}
C {gnd.sym} -380 -10 0 0 {name=r6 lab=vss}
N -220 90 -220 110 {lab=vss}
C {gnd.sym} -220 110 0 0 {name=r7 lab=vss}
N 140 -50 140 -30 {lab=vss}
C {gnd.sym} 140 -30 0 0 {name=r8 lab=vss}
N 580 -50 580 -30 {lab=vss}
C {gnd.sym} 580 -30 0 0 {name=r9 lab=vss}
C {lab_pin.sym} 580 -80 0 0 {name=l10 sig_type=std_logic lab=vss}
C {lab_pin.sym} 140 -80 0 0 {name=l11 sig_type=std_logic lab=vss}
C {lab_pin.sym} -20 -440 0 0 {name=l12 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 420 -560 0 0 {name=l13 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 420 -300 0 0 {name=l14 sig_type=std_logic lab=o1}
C {lab_pin.sym} 820 -440 0 0 {name=l15 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -20 -260 0 0 {name=l16 sig_type=std_logic lab=vss}
C {lab_pin.sym} -380 -200 0 0 {name=l17 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 260 -440 0 0 {name=l18 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 580 -440 0 0 {name=l19 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -220 60 0 0 {name=l20 sig_type=std_logic lab=vss}
C {lab_pin.sym} -380 -60 0 0 {name=l21 sig_type=std_logic lab=vss}
C {lab_pin.sym} -220 -80 0 0 {name=l22 sig_type=std_logic lab=vss}
C {lab_pin.sym} 260 -260 0 0 {name=l23 sig_type=std_logic lab=vss}
C {lab_pin.sym} 820 -260 0 0 {name=l24 sig_type=std_logic lab=vss}
C {lab_pin.sym} -80 -260 0 0 {name=l25 sig_type=std_logic lab=vb}
C {lab_pin.sym} 220 -260 0 0 {name=l26 sig_type=std_logic lab=vb}
C {lab_pin.sym} -20 -230 0 0 {name=l27 sig_type=std_logic lab=tl}
C {lab_pin.sym} 140 -110 0 0 {name=l28 sig_type=std_logic lab=tl}
C {lab_pin.sym} 260 -230 0 0 {name=l29 sig_type=std_logic lab=tl}
C {lab_pin.sym} 820 -470 0 0 {name=l30 sig_type=std_logic lab=pad}
C {lab_pin.sym} 820 -230 0 0 {name=l31 sig_type=std_logic lab=pad}
C {lab_pin.sym} 920 -340 0 0 {name=l32 sig_type=std_logic lab=pad}
C {lab_pin.sym} -220 -50 0 0 {name=l33 sig_type=std_logic lab=tg}
C {lab_pin.sym} -220 30 0 0 {name=l34 sig_type=std_logic lab=tg}
C {lab_pin.sym} 100 -80 0 0 {name=l35 sig_type=std_logic lab=tg}
C {lab_pin.sym} 540 -80 0 0 {name=l36 sig_type=std_logic lab=tg}
C {lab_pin.sym} -380 -170 0 0 {name=l37 sig_type=std_logic lab=enb}
C {lab_pin.sym} -380 -90 0 0 {name=l38 sig_type=std_logic lab=enb}
C {lab_pin.sym} -180 60 0 0 {name=l39 sig_type=std_logic lab=enb}
C {lab_pin.sym} 780 -440 0 0 {name=l40 sig_type=std_logic lab=enb}
C {lab_pin.sym} 20 -260 0 0 {name=l41 sig_type=std_logic lab=bo}
C {lab_pin.sym} 380 -300 0 0 {name=l42 sig_type=std_logic lab=bo}
C {lab_pin.sym} 580 -410 0 0 {name=l43 sig_type=std_logic lab=bo}
C {lab_pin.sym} 580 -110 0 0 {name=l44 sig_type=std_logic lab=bo}
C {lab_pin.sym} 820 -410 0 0 {name=l45 sig_type=std_logic lab=bo}
C {lab_pin.sym} 820 -290 0 0 {name=l46 sig_type=std_logic lab=bo}
C {lab_pin.sym} -480 -130 0 0 {name=l47 sig_type=std_logic lab=en}
C {lab_pin.sym} -420 -200 0 0 {name=l48 sig_type=std_logic lab=en}
C {lab_pin.sym} -420 -60 0 0 {name=l49 sig_type=std_logic lab=en}
C {lab_pin.sym} -180 -80 0 0 {name=l50 sig_type=std_logic lab=en}
C {lab_pin.sym} 380 -560 0 0 {name=l51 sig_type=std_logic lab=en}
C {lab_pin.sym} 780 -260 0 0 {name=l52 sig_type=std_logic lab=en}
C {lab_pin.sym} 260 -410 0 0 {name=l53 sig_type=std_logic lab=o1}
C {lab_pin.sym} 260 -290 0 0 {name=l54 sig_type=std_logic lab=o1}
C {lab_pin.sym} 420 -530 0 0 {name=l55 sig_type=std_logic lab=o1}
C {lab_pin.sym} 420 -330 0 0 {name=l56 sig_type=std_logic lab=o1}
C {lab_pin.sym} 420 -270 0 0 {name=l57 sig_type=std_logic lab=o1}
C {lab_pin.sym} 540 -440 0 0 {name=l58 sig_type=std_logic lab=o1}
C {lab_pin.sym} -20 -410 0 0 {name=l59 sig_type=std_logic lab=d1}
C {ipin.sym} -80 -260 0 0 {name=p60 lab=vb}
C {ipin.sym} -280 -140 0 0 {name=p61 lab=vbn}
C {ipin.sym} -480 -130 0 0 {name=p62 lab=en}
C {opin.sym} 920 -340 0 0 {name=p63 lab=pad}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 0 -440 0 1 {name=Ml1 L=4 W=16.54 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=4.797 pd=33.66 nrd=0.01753 nrs=0.01753 sa=0 sb=0 sd=0 as=4.797 ps=33.66}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 240 -440 0 0 {name=Ml2 L=4 W=16.54 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=4.797 pd=33.66 nrd=0.01753 nrs=0.01753 sa=0 sb=0 sd=0 as=4.797 ps=33.66}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 0 -260 0 1 {name=Mi1 L=2 W=3.03 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.8787 pd=6.64 nrd=0.09571 nrs=0.09571 sa=0 sb=0 sd=0 as=0.8787 ps=6.64}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 240 -260 0 0 {name=Mi2 L=2 W=3.03 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.8787 pd=6.64 nrd=0.09571 nrs=0.09571 sa=0 sb=0 sd=0 as=0.8787 ps=6.64}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 120 -80 0 0 {name=Mt L=4 W=2.24 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6496 pd=5.06 nrd=0.1295 nrs=0.1295 sa=0 sb=0 sd=0 as=0.6496 ps=5.06}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 560 -440 0 0 {name=Mo L=0.5 W=3.6 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=1.044 pd=7.78 nrd=0.08056 nrs=0.08056 sa=0 sb=0 sd=0 as=1.044 ps=7.78}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 560 -80 0 0 {name=Mos L=4 W=2.24 nf=1 mult=32 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6496 pd=5.06 nrd=0.1295 nrs=0.1295 sa=0 sb=0 sd=0 as=0.6496 ps=5.06}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 400 -300 0 0 {name=Cc L=20 W=20 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=5.8 pd=40.58 nrd=0.0145 nrs=0.0145 sa=0 sb=0 sd=0 as=5.8 ps=40.58}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 400 -560 0 0 {name=Moff L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -200 -80 0 1 {name=Men1 L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -200 60 0 1 {name=Men2 L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -400 -200 0 0 {name=Minp L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -400 -60 0 0 {name=Minn L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 800 -260 0 0 {name=Mtgn L=0.5 W=4 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=1.16 pd=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0 as=1.16 ps=8.58}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 800 -440 0 0 {name=Mtgp L=0.5 W=8 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=2.32 pd=16.58 nrd=0.03625 nrs=0.03625 sa=0 sb=0 sd=0 as=2.32 ps=16.58}
