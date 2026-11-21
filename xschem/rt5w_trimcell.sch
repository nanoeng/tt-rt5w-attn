v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Row trim cell: w written from vw, then +/- one pump step per clock} -360 -420 0 0 0.45 0.45 {}
N -100 -300 -100 -260 {lab=pg}
N -100 -260 -20 -260 {lab=pg}
N -80 -180 -80 -140 {lab=up_b}
N -80 -140 -20 -140 {lab=up_b}
N 120 -180 120 -140 {lab=up}
N 120 -140 180 -140 {lab=up}
N -80 0 -80 40 {lab=dn}
N -80 40 -20 40 {lab=dn}
N 120 0 120 40 {lab=dn_b}
N 120 40 180 40 {lab=dn_b}
N -100 200 -100 160 {lab=ng}
N -100 160 -20 160 {lab=ng}
N 20 -230 20 -170 {lab=pu}
N 20 -170 220 -170 {lab=pu}
N 220 -110 220 10 {lab=vmid}
N 220 -110 220 -60 {lab=vmid}
N 220 -60 320 -60 {lab=vmid}
N 20 70 20 130 {lab=nd}
N 20 70 220 70 {lab=nd}
N -680 20 -680 -90 {lab=vw}
N -680 -90 -460 -90 {lab=vw}
N -680 20 -300 20 {lab=vw}
N -300 20 -300 -30 {lab=vw}
N -600 -230 -600 -190 {lab=wselb}
N -600 -190 -500 -190 {lab=wselb}
N -500 -190 -500 -60 {lab=wselb}
N -760 -210 -760 -260 {lab=wsel}
N -760 -260 -640 -260 {lab=wsel}
N -640 -260 -640 -160 {lab=wsel}
N -760 -210 -340 -210 {lab=wsel}
N -340 -210 -340 -60 {lab=wsel}
N -600 -290 -600 -310 {lab=vdd}
C {vdd.sym} -600 -310 0 0 {name=r1 lab=vdd}
N 20 -290 20 -310 {lab=vdd}
C {vdd.sym} 20 -310 0 0 {name=r2 lab=vdd}
N -600 -130 -600 -110 {lab=vss}
C {gnd.sym} -600 -110 0 0 {name=r3 lab=vss}
N -140 70 -140 90 {lab=vss}
C {gnd.sym} -140 90 0 0 {name=r4 lab=vss}
N -140 130 -140 150 {lab=vss}
C {gnd.sym} -140 150 0 0 {name=r5 lab=vss}
N 20 190 20 210 {lab=vss}
C {gnd.sym} 20 210 0 0 {name=r6 lab=vss}
C {lab_pin.sym} 220 -140 0 0 {name=l7 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -600 -160 0 0 {name=l8 sig_type=std_logic lab=vss}
C {lab_pin.sym} 20 -260 0 0 {name=l9 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 20 -140 0 0 {name=l10 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -460 -60 0 0 {name=l11 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 220 40 0 0 {name=l12 sig_type=std_logic lab=vss}
C {lab_pin.sym} -300 -60 0 0 {name=l13 sig_type=std_logic lab=vss}
C {lab_pin.sym} -600 -260 0 0 {name=l14 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 20 40 0 0 {name=l15 sig_type=std_logic lab=vss}
C {lab_pin.sym} 20 160 0 0 {name=l16 sig_type=std_logic lab=vss}
C {lab_pin.sym} -140 100 0 0 {name=l17 sig_type=std_logic lab=vss}
C {lab_pin.sym} -460 -30 0 0 {name=l18 sig_type=std_logic lab=w}
C {lab_pin.sym} -300 -90 0 0 {name=l19 sig_type=std_logic lab=w}
C {lab_pin.sym} -180 100 0 0 {name=l20 sig_type=std_logic lab=w}
C {lab_pin.sym} 20 -110 0 0 {name=l21 sig_type=std_logic lab=w}
C {lab_pin.sym} 20 10 0 0 {name=l22 sig_type=std_logic lab=w}
C {lab_pin.sym} 120 -60 0 0 {name=l23 sig_type=std_logic lab=w}
C {lab_pin.sym} 20 70 0 0 {name=l24 sig_type=std_logic lab=nd}
C {lab_pin.sym} 20 -230 0 0 {name=l25 sig_type=std_logic lab=pu}
C {lab_pin.sym} -600 -230 0 0 {name=l26 sig_type=std_logic lab=wselb}
C {iopin.sym} -680 20 0 0 {name=p27 lab=vw}
C {ipin.sym} -760 -210 0 0 {name=p28 lab=wsel}
C {ipin.sym} -100 -300 0 0 {name=p29 lab=pg}
C {ipin.sym} -100 200 0 0 {name=p30 lab=ng}
C {ipin.sym} -80 -180 0 0 {name=p31 lab=up_b}
C {ipin.sym} 120 -180 0 0 {name=p32 lab=up}
C {ipin.sym} -80 0 0 0 {name=p33 lab=dn}
C {ipin.sym} 120 0 0 0 {name=p34 lab=dn_b}
C {iopin.sym} 320 -60 0 0 {name=p35 lab=vmid}
C {opin.sym} 120 -60 0 0 {name=p36 lab=w}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 0 -260 0 0 {name=Mpu L=4 W=1.47 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.4263 pd=3.52 nrd=0.1973 nrs=0.1973 sa=0 sb=0 sd=0 as=0.4263 ps=3.52}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 0 -140 0 0 {name=Msu L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} 200 -140 0 0 {name=Msub L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 0 40 0 0 {name=Msd L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 200 40 0 0 {name=Msdb L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} 0 160 0 0 {name=Mnd L=1 W=2.37 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.6873 pd=5.32 nrd=0.1224 nrs=0.1224 sa=0 sb=0 sd=0 as=0.6873 ps=5.32}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -160 100 0 0 {name=Cw L=10.4 W=10.4 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=3.016 pd=21.38 nrd=0.02788 nrs=0.02788 sa=0 sb=0 sd=0 as=3.016 ps=21.38}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -320 -60 0 0 {name=Mwn L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -480 -60 0 0 {name=Mwp L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/pfet_g5v0d10v5.sym} -620 -260 0 0 {name=Mip L=0.5 W=0.84 nf=1 mult=1 model=pfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -620 -160 0 0 {name=Min L=0.5 W=0.84 nf=1 mult=1 model=nfet_g5v0d10v5 spiceprefix=X ad=0.2436 pd=2.26 nrd=0.3452 nrs=0.3452 sa=0 sb=0 sd=0 as=0.2436 ps=2.26}
