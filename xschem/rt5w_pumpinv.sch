v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Pump strobe inverters} -100 -260 0 0 0.4 0.4 {}
N 20 -150 20 -170 {lab=vdd}
C {vdd.sym} 20 -170 0 0 {name=r1 lab=vdd}
N 220 -150 220 -170 {lab=vdd}
C {vdd.sym} 220 -170 0 0 {name=r2 lab=vdd}
N 20 70 20 90 {lab=vss}
C {gnd.sym} 20 90 0 0 {name=r3 lab=vss}
N 220 70 220 90 {lab=vss}
C {gnd.sym} 220 90 0 0 {name=r4 lab=vss}
C {lab_pin.sym} 20 -120 0 0 {name=l5 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 220 -120 0 0 {name=l6 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 220 40 0 0 {name=l7 sig_type=std_logic lab=vss}
C {lab_pin.sym} 20 40 0 0 {name=l8 sig_type=std_logic lab=vss}
C {lab_pin.sym} 20 -90 0 0 {name=l9 sig_type=std_logic lab=upb}
C {lab_pin.sym} 20 10 0 0 {name=l10 sig_type=std_logic lab=upb}
C {lab_pin.sym} 60 -40 0 0 {name=l11 sig_type=std_logic lab=upb}
C {lab_pin.sym} -80 -40 0 0 {name=l12 sig_type=std_logic lab=up}
C {lab_pin.sym} -20 -120 0 0 {name=l13 sig_type=std_logic lab=up}
C {lab_pin.sym} -20 40 0 0 {name=l14 sig_type=std_logic lab=up}
C {lab_pin.sym} 220 -90 0 0 {name=l15 sig_type=std_logic lab=dnb}
C {lab_pin.sym} 220 10 0 0 {name=l16 sig_type=std_logic lab=dnb}
C {lab_pin.sym} 260 -40 0 0 {name=l17 sig_type=std_logic lab=dnb}
C {lab_pin.sym} 120 -40 0 0 {name=l18 sig_type=std_logic lab=dn}
C {lab_pin.sym} 180 -120 0 0 {name=l19 sig_type=std_logic lab=dn}
C {lab_pin.sym} 180 40 0 0 {name=l20 sig_type=std_logic lab=dn}
C {ipin.sym} -80 -40 0 0 {name=p21 lab=up}
C {ipin.sym} 120 -40 0 0 {name=p22 lab=dn}
C {opin.sym} 60 -40 0 0 {name=p23 lab=upb}
C {opin.sym} 260 -40 0 0 {name=p24 lab=dnb}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 0 -120 0 0 {name=Mupp L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 0 40 0 0 {name=Mupn L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 200 -120 0 0 {name=Mdnp L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 200 40 0 0 {name=Mdnn L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
