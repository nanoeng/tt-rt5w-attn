v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {1.8 V -> 3.3 V level shifter} -100 -400 0 0 0.4 0.4 {}
N 220 -230 220 -250 {lab=vdd}
C {vdd.sym} 220 -250 0 0 {name=r1 lab=vdd}
N 420 -230 420 -250 {lab=vdd}
C {vdd.sym} 420 -250 0 0 {name=r2 lab=vdd}
N 620 -230 620 -250 {lab=vdd}
C {vdd.sym} 620 -250 0 0 {name=r3 lab=vdd}
N 20 -10 20 10 {lab=vss}
C {gnd.sym} 20 10 0 0 {name=r4 lab=vss}
N 220 -10 220 10 {lab=vss}
C {gnd.sym} 220 10 0 0 {name=r5 lab=vss}
N 420 -10 420 10 {lab=vss}
C {gnd.sym} 420 10 0 0 {name=r6 lab=vss}
N 620 -10 620 10 {lab=vss}
C {gnd.sym} 620 10 0 0 {name=r7 lab=vss}
C {lab_pin.sym} 20 -200 0 0 {name=l8 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 420 -200 0 0 {name=l9 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 220 -40 0 0 {name=l10 sig_type=std_logic lab=vss}
C {lab_pin.sym} 20 -40 0 0 {name=l11 sig_type=std_logic lab=vss}
C {lab_pin.sym} 420 -40 0 0 {name=l12 sig_type=std_logic lab=vss}
C {lab_pin.sym} 620 -40 0 0 {name=l13 sig_type=std_logic lab=vss}
C {lab_pin.sym} 620 -200 0 0 {name=l14 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 220 -200 0 0 {name=l15 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 20 -170 0 0 {name=l16 sig_type=std_logic lab=inb}
C {lab_pin.sym} 20 -70 0 0 {name=l17 sig_type=std_logic lab=inb}
C {lab_pin.sym} 380 -40 0 0 {name=l18 sig_type=std_logic lab=inb}
C {lab_pin.sym} -80 -320 0 0 {name=l19 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 20 -230 0 0 {name=l20 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 180 -200 0 0 {name=l21 sig_type=std_logic lab=xb}
C {lab_pin.sym} 420 -170 0 0 {name=l22 sig_type=std_logic lab=xb}
C {lab_pin.sym} 420 -70 0 0 {name=l23 sig_type=std_logic lab=xb}
C {lab_pin.sym} 620 -170 0 0 {name=l24 sig_type=std_logic lab=out}
C {lab_pin.sym} 620 -70 0 0 {name=l25 sig_type=std_logic lab=out}
C {lab_pin.sym} 680 -120 0 0 {name=l26 sig_type=std_logic lab=out}
C {lab_pin.sym} -80 -120 0 0 {name=l27 sig_type=std_logic lab=in}
C {lab_pin.sym} -20 -200 0 0 {name=l28 sig_type=std_logic lab=in}
C {lab_pin.sym} -20 -40 0 0 {name=l29 sig_type=std_logic lab=in}
C {lab_pin.sym} 180 -40 0 0 {name=l30 sig_type=std_logic lab=in}
C {lab_pin.sym} 220 -170 0 0 {name=l31 sig_type=std_logic lab=xa}
C {lab_pin.sym} 220 -70 0 0 {name=l32 sig_type=std_logic lab=xa}
C {lab_pin.sym} 380 -200 0 0 {name=l33 sig_type=std_logic lab=xa}
C {lab_pin.sym} 580 -200 0 0 {name=l34 sig_type=std_logic lab=xa}
C {lab_pin.sym} 580 -40 0 0 {name=l35 sig_type=std_logic lab=xa}
C {ipin.sym} -80 -120 0 0 {name=p36 lab=in}
C {opin.sym} 680 -120 0 0 {name=p37 lab=out}
C {iopin.sym} -80 -320 0 0 {name=p38 lab=vddl}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 0 -200 0 0 {name=Mip L=0.5 W=1.68 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.4872 pd=3.94 nrd=0.1726 nrs=0.1726 sa=0 sb=0 sd=0 as=0.4872 ps=3.94}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 0 -40 0 0 {name=Min L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 200 -200 0 0 {name=Mpa L=1 W=0.42 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 400 -200 0 0 {name=Mpb L=1 W=0.42 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.1218 pd=1.42 nrd=0.6905 nrs=0.6905 sa=0 sb=0 sd=0 as=0.1218 ps=1.42}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 200 -40 0 0 {name=Mna L=0.5 W=2.5 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.725 pd=5.58 nrd=0.116 nrs=0.116 sa=0 sb=0 sd=0 as=0.725 ps=5.58}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 400 -40 0 0 {name=Mnb L=0.5 W=2.5 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.725 pd=5.58 nrd=0.116 nrs=0.116 sa=0 sb=0 sd=0 as=0.725 ps=5.58}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 600 -200 0 0 {name=Mop L=0.5 W=1.68 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.4872 pd=3.94 nrd=0.1726 nrs=0.1726 sa=0 sb=0 sd=0 as=0.4872 ps=3.94}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 600 -40 0 0 {name=Mon L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
