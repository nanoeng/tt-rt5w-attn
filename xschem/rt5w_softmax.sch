v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Softmax core: I_out,j = 4 I_sum exp(x_j)/sum exp(x_k),  V_B = log-sum-exp} -200 -720 0 0 0.5 0.5 {}
N 320 70 320 130 {lab=tc}
N -20 70 -20 130 {lab=nbm}
N 180 -450 240 -450 {lab=out0}
N 240 -450 240 -560 {lab=out0}
N 240 -450 240 -350 {lab=out0}
N -120 -10 -60 -10 {lab=g0}
N -60 -10 -60 -120 {lab=g0}
N -60 -120 -60 -180 {lab=g0}
N -60 -180 -20 -180 {lab=g0}
N 480 -450 540 -450 {lab=out1}
N 540 -450 540 -560 {lab=out1}
N 540 -450 540 -350 {lab=out1}
N 180 -10 240 -10 {lab=g1}
N 240 -10 240 -120 {lab=g1}
N 240 -120 240 -180 {lab=g1}
N 240 -180 280 -180 {lab=g1}
N 780 -450 840 -450 {lab=out2}
N 840 -450 840 -560 {lab=out2}
N 840 -450 840 -350 {lab=out2}
N 480 -10 540 -10 {lab=g2}
N 540 -10 540 -120 {lab=g2}
N 540 -120 540 -180 {lab=g2}
N 540 -180 580 -180 {lab=g2}
N 1080 -450 1140 -450 {lab=out3}
N 1140 -450 1140 -560 {lab=out3}
N 1140 -450 1140 -350 {lab=out3}
N 780 -10 840 -10 {lab=g3}
N 840 -10 840 -120 {lab=g3}
N 840 -120 840 -180 {lab=g3}
N 840 -180 880 -180 {lab=g3}
N 20 40 20 100 {lab=vcas}
N 20 100 160 100 {lab=vcas}
N 160 100 160 40 {lab=vcas}
N 160 40 280 40 {lab=vcas}
N -40 -350 -40 -450 {lab=dp0}
N -40 -450 -20 -450 {lab=dp0}
N -20 -450 20 -450 {lab=dp0}
N 20 -450 20 -480 {lab=dp0}
N -40 -350 20 -350 {lab=dp0}
N 20 -350 20 -210 {lab=dp0}
N 20 -480 140 -480 {lab=dp0}
N 260 -350 260 -450 {lab=dp1}
N 260 -450 280 -450 {lab=dp1}
N 280 -450 320 -450 {lab=dp1}
N 320 -450 320 -480 {lab=dp1}
N 260 -350 320 -350 {lab=dp1}
N 320 -350 320 -210 {lab=dp1}
N 320 -480 440 -480 {lab=dp1}
N 560 -350 560 -450 {lab=dp2}
N 560 -450 580 -450 {lab=dp2}
N 580 -450 620 -450 {lab=dp2}
N 620 -450 620 -480 {lab=dp2}
N 560 -350 620 -350 {lab=dp2}
N 620 -350 620 -210 {lab=dp2}
N 620 -480 740 -480 {lab=dp2}
N 860 -350 860 -450 {lab=dp3}
N 860 -450 880 -450 {lab=dp3}
N 880 -450 920 -450 {lab=dp3}
N 920 -450 920 -480 {lab=dp3}
N 860 -350 920 -350 {lab=dp3}
N 920 -350 920 -210 {lab=dp3}
N 920 -480 1040 -480 {lab=dp3}
N 20 -150 20 -130 {lab=vb}
N 320 -150 320 -130 {lab=vb}
N 320 10 320 -130 {lab=vb}
N 620 -150 620 -130 {lab=vb}
N 740 40 740 -130 {lab=vb}
N 920 -150 920 -130 {lab=vb}
N 20 -130 320 -130 {lab=vb}
N 320 -130 620 -130 {lab=vb}
N 620 -130 740 -130 {lab=vb}
N 740 -130 920 -130 {lab=vb}
N 920 -130 1000 -130 {lab=vb}
N -20 -510 -20 -530 {lab=vdd}
C {vdd.sym} -20 -530 0 0 {name=r1 lab=vdd}
N 180 -510 180 -530 {lab=vdd}
C {vdd.sym} 180 -530 0 0 {name=r2 lab=vdd}
N 280 -510 280 -530 {lab=vdd}
C {vdd.sym} 280 -530 0 0 {name=r3 lab=vdd}
N 480 -510 480 -530 {lab=vdd}
C {vdd.sym} 480 -530 0 0 {name=r4 lab=vdd}
N 580 -510 580 -530 {lab=vdd}
C {vdd.sym} 580 -530 0 0 {name=r5 lab=vdd}
N 780 -510 780 -530 {lab=vdd}
C {vdd.sym} 780 -530 0 0 {name=r6 lab=vdd}
N 880 -510 880 -530 {lab=vdd}
C {vdd.sym} 880 -530 0 0 {name=r7 lab=vdd}
N 1080 -510 1080 -530 {lab=vdd}
C {vdd.sym} 1080 -530 0 0 {name=r8 lab=vdd}
N -140 -40 -140 -20 {lab=vss}
C {gnd.sym} -140 -20 0 0 {name=r9 lab=vss}
N -40 -290 -40 -270 {lab=vss}
C {gnd.sym} -40 -270 0 0 {name=r10 lab=vss}
N -20 190 -20 210 {lab=vss}
C {gnd.sym} -20 210 0 0 {name=r11 lab=vss}
N 160 -40 160 -20 {lab=vss}
C {gnd.sym} 160 -20 0 0 {name=r12 lab=vss}
N 240 -290 240 -270 {lab=vss}
C {gnd.sym} 240 -270 0 0 {name=r13 lab=vss}
N 260 -290 260 -270 {lab=vss}
C {gnd.sym} 260 -270 0 0 {name=r14 lab=vss}
N 320 190 320 210 {lab=vss}
C {gnd.sym} 320 210 0 0 {name=r15 lab=vss}
N 460 -40 460 -20 {lab=vss}
C {gnd.sym} 460 -20 0 0 {name=r16 lab=vss}
N 540 -290 540 -270 {lab=vss}
C {gnd.sym} 540 -270 0 0 {name=r17 lab=vss}
N 560 -290 560 -270 {lab=vss}
C {gnd.sym} 560 -270 0 0 {name=r18 lab=vss}
N 620 190 620 210 {lab=vss}
C {gnd.sym} 620 210 0 0 {name=r19 lab=vss}
N 760 -40 760 -20 {lab=vss}
C {gnd.sym} 760 -20 0 0 {name=r20 lab=vss}
N 780 10 780 30 {lab=vss}
C {gnd.sym} 780 30 0 0 {name=r21 lab=vss}
N 780 70 780 90 {lab=vss}
C {gnd.sym} 780 90 0 0 {name=r22 lab=vss}
N 840 -290 840 -270 {lab=vss}
C {gnd.sym} 840 -270 0 0 {name=r23 lab=vss}
N 860 -290 860 -270 {lab=vss}
C {gnd.sym} 860 -270 0 0 {name=r24 lab=vss}
N 1140 -290 1140 -270 {lab=vss}
C {gnd.sym} 1140 -270 0 0 {name=r25 lab=vss}
C {lab_pin.sym} 1140 -320 0 0 {name=l26 sig_type=std_logic lab=vss}
C {lab_pin.sym} -20 -480 0 0 {name=l27 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 240 -320 0 0 {name=l28 sig_type=std_logic lab=vss}
C {lab_pin.sym} 560 -320 0 0 {name=l29 sig_type=std_logic lab=vss}
C {lab_pin.sym} 860 -320 0 0 {name=l30 sig_type=std_logic lab=vss}
C {lab_pin.sym} 540 -320 0 0 {name=l31 sig_type=std_logic lab=vss}
C {lab_pin.sym} -20 160 0 0 {name=l32 sig_type=std_logic lab=vss}
C {lab_pin.sym} -40 -320 0 0 {name=l33 sig_type=std_logic lab=vss}
C {lab_pin.sym} 880 -480 0 0 {name=l34 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 780 -480 0 0 {name=l35 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1080 -480 0 0 {name=l36 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 260 -320 0 0 {name=l37 sig_type=std_logic lab=vss}
C {lab_pin.sym} 840 -320 0 0 {name=l38 sig_type=std_logic lab=vss}
C {lab_pin.sym} 780 40 0 0 {name=l39 sig_type=std_logic lab=vss}
C {lab_pin.sym} 920 -180 0 0 {name=l40 sig_type=std_logic lab=vss}
C {lab_pin.sym} 180 -480 0 0 {name=l41 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 480 -480 0 0 {name=l42 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 20 -180 0 0 {name=l43 sig_type=std_logic lab=vss}
C {lab_pin.sym} 280 -480 0 0 {name=l44 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 580 -480 0 0 {name=l45 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 320 160 0 0 {name=l46 sig_type=std_logic lab=vss}
C {lab_pin.sym} -20 40 0 0 {name=l47 sig_type=std_logic lab=vss}
C {lab_pin.sym} 320 -180 0 0 {name=l48 sig_type=std_logic lab=vss}
C {lab_pin.sym} 620 -180 0 0 {name=l49 sig_type=std_logic lab=vss}
C {lab_pin.sym} 320 40 0 0 {name=l50 sig_type=std_logic lab=vss}
C {lab_pin.sym} 620 160 0 0 {name=l51 sig_type=std_logic lab=vss}
C {lab_pin.sym} -120 0 0 0 {name=l52 sig_type=std_logic lab=nbias}
C {lab_pin.sym} -20 10 0 0 {name=l53 sig_type=std_logic lab=nbias}
C {lab_pin.sym} 20 160 0 0 {name=l54 sig_type=std_logic lab=nbias}
C {lab_pin.sym} 280 160 0 0 {name=l55 sig_type=std_logic lab=nbias}
C {lab_pin.sym} -240 40 0 0 {name=l56 sig_type=std_logic lab=vr}
C {lab_pin.sym} -120 -70 0 0 {name=l57 sig_type=std_logic lab=vr}
C {lab_pin.sym} 180 -70 0 0 {name=l58 sig_type=std_logic lab=vr}
C {lab_pin.sym} 480 -70 0 0 {name=l59 sig_type=std_logic lab=vr}
C {lab_pin.sym} 780 -70 0 0 {name=l60 sig_type=std_logic lab=vr}
C {lab_pin.sym} -80 -320 0 0 {name=l61 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 200 -320 0 0 {name=l62 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 220 -320 0 0 {name=l63 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 500 -320 0 0 {name=l64 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 520 -320 0 0 {name=l65 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 580 160 0 0 {name=l66 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 620 130 0 0 {name=l67 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 640 100 0 0 {name=l68 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 800 -320 0 0 {name=l69 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 820 -320 0 0 {name=l70 sig_type=std_logic lab=kbias}
C {lab_pin.sym} 1100 -320 0 0 {name=l71 sig_type=std_logic lab=kbias}
C {lab_pin.sym} -40 -350 0 0 {name=l72 sig_type=std_logic lab=dp0}
C {lab_pin.sym} 260 -350 0 0 {name=l73 sig_type=std_logic lab=dp1}
C {lab_pin.sym} 560 -350 0 0 {name=l74 sig_type=std_logic lab=dp2}
C {lab_pin.sym} 860 -350 0 0 {name=l75 sig_type=std_logic lab=dp3}
C {lab_pin.sym} -20 70 0 0 {name=l76 sig_type=std_logic lab=nbm}
C {lab_pin.sym} 320 70 0 0 {name=l77 sig_type=std_logic lab=tc}
C {ipin.sym} -60 -120 0 0 {name=p78 lab=g0}
C {opin.sym} 240 -560 0 0 {name=p79 lab=out0}
C {ipin.sym} 240 -120 0 0 {name=p80 lab=g1}
C {opin.sym} 540 -560 0 0 {name=p81 lab=out1}
C {ipin.sym} 540 -120 0 0 {name=p82 lab=g2}
C {opin.sym} 840 -560 0 0 {name=p83 lab=out2}
C {ipin.sym} 840 -120 0 0 {name=p84 lab=g3}
C {opin.sym} 1140 -560 0 0 {name=p85 lab=out3}
C {ipin.sym} -120 0 0 0 {name=p86 lab=nbias}
C {ipin.sym} 160 100 0 0 {name=p87 lab=vcas}
C {ipin.sym} 640 100 0 0 {name=p88 lab=kbias}
C {ipin.sym} -240 40 0 0 {name=p89 lab=vr}
C {opin.sym} 1000 -130 0 0 {name=p90 lab=vb}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 0 -480 0 1 {name=Mp0 L=4 W=15.11 nf=1 mult=4 model=pfet_g5v0d10v5 spiceprefix=X ad=4.382 pd=30.8 nrd=0.01919 nrs=0.01919 sa=0 sb=0 sd=0 as=4.382 ps=30.8}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 160 -480 0 0 {name=Mo0 L=4 W=15.11 nf=1 mult=16 model=pfet_g5v0d10v5 spiceprefix=X ad=4.382 pd=30.8 nrd=0.01919 nrs=0.01919 sa=0 sb=0 sd=0 as=4.382 ps=30.8}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -60 -320 0 0 {name=Mk0 L=1 W=2.38 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6902 pd=5.34 nrd=0.1218 nrs=0.1218 sa=0 sb=0 sd=0 as=0.6902 ps=5.34}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 220 -320 0 0 {name=Mr0 L=1 W=2.38 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6902 pd=5.34 nrd=0.1218 nrs=0.1218 sa=0 sb=0 sd=0 as=0.6902 ps=5.34}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 0 -180 0 0 {name=Me0 L=2 W=7.15 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=2.074 pd=14.88 nrd=0.04056 nrs=0.04056 sa=0 sb=0 sd=0 as=2.074 ps=14.88}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} -120 -40 0 0 {name=Rc0 L=244 model=res_xhigh_po_0p35 spiceprefix=X mult=1}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 300 -480 0 1 {name=Mp1 L=4 W=15.11 nf=1 mult=4 model=pfet_g5v0d10v5 spiceprefix=X ad=4.382 pd=30.8 nrd=0.01919 nrs=0.01919 sa=0 sb=0 sd=0 as=4.382 ps=30.8}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 460 -480 0 0 {name=Mo1 L=4 W=15.11 nf=1 mult=16 model=pfet_g5v0d10v5 spiceprefix=X ad=4.382 pd=30.8 nrd=0.01919 nrs=0.01919 sa=0 sb=0 sd=0 as=4.382 ps=30.8}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 240 -320 0 0 {name=Mk1 L=1 W=2.38 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6902 pd=5.34 nrd=0.1218 nrs=0.1218 sa=0 sb=0 sd=0 as=0.6902 ps=5.34}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 520 -320 0 0 {name=Mr1 L=1 W=2.38 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6902 pd=5.34 nrd=0.1218 nrs=0.1218 sa=0 sb=0 sd=0 as=0.6902 ps=5.34}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 300 -180 0 0 {name=Me1 L=2 W=7.15 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=2.074 pd=14.88 nrd=0.04056 nrs=0.04056 sa=0 sb=0 sd=0 as=2.074 ps=14.88}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 180 -40 0 0 {name=Rc1 L=244 model=res_xhigh_po_0p35 spiceprefix=X mult=1}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 600 -480 0 1 {name=Mp2 L=4 W=15.11 nf=1 mult=4 model=pfet_g5v0d10v5 spiceprefix=X ad=4.382 pd=30.8 nrd=0.01919 nrs=0.01919 sa=0 sb=0 sd=0 as=4.382 ps=30.8}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 760 -480 0 0 {name=Mo2 L=4 W=15.11 nf=1 mult=16 model=pfet_g5v0d10v5 spiceprefix=X ad=4.382 pd=30.8 nrd=0.01919 nrs=0.01919 sa=0 sb=0 sd=0 as=4.382 ps=30.8}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 540 -320 0 0 {name=Mk2 L=1 W=2.38 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6902 pd=5.34 nrd=0.1218 nrs=0.1218 sa=0 sb=0 sd=0 as=0.6902 ps=5.34}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 820 -320 0 0 {name=Mr2 L=1 W=2.38 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6902 pd=5.34 nrd=0.1218 nrs=0.1218 sa=0 sb=0 sd=0 as=0.6902 ps=5.34}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 600 -180 0 0 {name=Me2 L=2 W=7.15 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=2.074 pd=14.88 nrd=0.04056 nrs=0.04056 sa=0 sb=0 sd=0 as=2.074 ps=14.88}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 480 -40 0 0 {name=Rc2 L=244 model=res_xhigh_po_0p35 spiceprefix=X mult=1}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 900 -480 0 1 {name=Mp3 L=4 W=15.11 nf=1 mult=4 model=pfet_g5v0d10v5 spiceprefix=X ad=4.382 pd=30.8 nrd=0.01919 nrs=0.01919 sa=0 sb=0 sd=0 as=4.382 ps=30.8}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 1060 -480 0 0 {name=Mo3 L=4 W=15.11 nf=1 mult=16 model=pfet_g5v0d10v5 spiceprefix=X ad=4.382 pd=30.8 nrd=0.01919 nrs=0.01919 sa=0 sb=0 sd=0 as=4.382 ps=30.8}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 840 -320 0 0 {name=Mk3 L=1 W=2.38 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6902 pd=5.34 nrd=0.1218 nrs=0.1218 sa=0 sb=0 sd=0 as=0.6902 ps=5.34}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 1120 -320 0 0 {name=Mr3 L=1 W=2.38 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6902 pd=5.34 nrd=0.1218 nrs=0.1218 sa=0 sb=0 sd=0 as=0.6902 ps=5.34}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 900 -180 0 0 {name=Me3 L=2 W=7.15 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=2.074 pd=14.88 nrd=0.04056 nrs=0.04056 sa=0 sb=0 sd=0 as=2.074 ps=14.88}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 780 -40 0 0 {name=Rc3 L=244 model=res_xhigh_po_0p35 spiceprefix=X mult=1}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 300 40 0 0 {name=Mcas L=1 W=0.62 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1798 pd=1.82 nrd=0.4677 nrs=0.4677 sa=0 sb=0 sd=0 as=0.1798 ps=1.82}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 300 160 0 0 {name=Mtail L=4 W=2.24 nf=1 mult=16 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6496 pd=5.06 nrd=0.1295 nrs=0.1295 sa=0 sb=0 sd=0 as=0.6496 ps=5.06}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 0 40 0 1 {name=Mbc L=1 W=0.62 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.1798 pd=1.82 nrd=0.4677 nrs=0.4677 sa=0 sb=0 sd=0 as=0.1798 ps=1.82}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 0 160 0 1 {name=Mbias L=4 W=2.24 nf=1 mult=4 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6496 pd=5.06 nrd=0.1295 nrs=0.1295 sa=0 sb=0 sd=0 as=0.6496 ps=5.06}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 600 160 0 0 {name=Mkb L=1 W=2.38 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6902 pd=5.34 nrd=0.1218 nrs=0.1218 sa=0 sb=0 sd=0 as=0.6902 ps=5.34}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 760 40 0 0 {name=Cb L=15 W=15 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=4.35 pd=30.58 nrd=0.01933 nrs=0.01933 sa=0 sb=0 sd=0 as=4.35 ps=30.58}
