v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Column diode: carries I_Q,c, sets the column line dcol} -100 -170 0 0 0.4 0.4 {}
N -20 0 -20 30 {lab=dcol}
N -20 30 20 30 {lab=dcol}
N 20 30 20 60 {lab=dcol}
N 20 60 60 60 {lab=dcol}
N 20 -30 20 -50 {lab=vdd}
C {vdd.sym} 20 -50 0 0 {name=r1 lab=vdd}
C {lab_pin.sym} 20 0 0 0 {name=l2 sig_type=std_logic lab=vdd}
C {iopin.sym} 60 60 0 0 {name=p3 lab=dcol}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 0 0 0 0 {name=Md L=4 W=8.27 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=2.398 pd=17.12 nrd=0.03507 nrs=0.03507 sa=0 sb=0 sd=0 as=2.398 ps=17.12}
