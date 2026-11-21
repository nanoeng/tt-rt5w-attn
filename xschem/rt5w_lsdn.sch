v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {3.3 V -> 1.8 V level shifter} -100 -400 0 0 0.4 0.4 {}
N 20 -10 20 10 {lab=vss}
C {gnd.sym} 20 10 0 0 {name=r1 lab=vss}
N 220 -10 220 10 {lab=vss}
C {gnd.sym} 220 10 0 0 {name=r2 lab=vss}
C {lab_pin.sym} 220 -40 0 0 {name=l3 sig_type=std_logic lab=vss}
C {lab_pin.sym} 20 -200 0 0 {name=l4 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 20 -40 0 0 {name=l5 sig_type=std_logic lab=vss}
C {lab_pin.sym} 220 -200 0 0 {name=l6 sig_type=std_logic lab=vddl}
C {lab_pin.sym} -80 -120 0 0 {name=l7 sig_type=std_logic lab=in}
C {lab_pin.sym} -20 -200 0 0 {name=l8 sig_type=std_logic lab=in}
C {lab_pin.sym} -20 -40 0 0 {name=l9 sig_type=std_logic lab=in}
C {lab_pin.sym} 220 -170 0 0 {name=l10 sig_type=std_logic lab=out}
C {lab_pin.sym} 220 -70 0 0 {name=l11 sig_type=std_logic lab=out}
C {lab_pin.sym} 280 -120 0 0 {name=l12 sig_type=std_logic lab=out}
C {lab_pin.sym} 20 -170 0 0 {name=l13 sig_type=std_logic lab=mid}
C {lab_pin.sym} 20 -70 0 0 {name=l14 sig_type=std_logic lab=mid}
C {lab_pin.sym} 180 -200 0 0 {name=l15 sig_type=std_logic lab=mid}
C {lab_pin.sym} 180 -40 0 0 {name=l16 sig_type=std_logic lab=mid}
C {lab_pin.sym} -80 -320 0 0 {name=l17 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 20 -230 0 0 {name=l18 sig_type=std_logic lab=vddl}
C {lab_pin.sym} 220 -230 0 0 {name=l19 sig_type=std_logic lab=vddl}
C {ipin.sym} -80 -120 0 0 {name=p20 lab=in}
C {opin.sym} 280 -120 0 0 {name=p21 lab=out}
C {iopin.sym} -80 -320 0 0 {name=p22 lab=vddl}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 0 -200 0 0 {name=Map L=0.5 W=1.68 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.4872 pd=3.94 nrd=0.1726 nrs=0.1726 sa=0 sb=0 sd=0 as=0.4872 ps=3.94}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 0 -40 0 0 {name=Man L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 200 -200 0 0 {name=Mbp L=0.5 W=1.68 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.4872 pd=3.94 nrd=0.1726 nrs=0.1726 sa=0 sb=0 sd=0 as=0.4872 ps=3.94}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 200 -40 0 0 {name=Mbn L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
