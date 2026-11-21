import sys; sys.path.insert(0,'design'); sys.path.insert(0,'design/tb')
import os; os.environ['RT5W_NETLIST']='netlist_exp'
import importlib, sim, tech
from units import SM_P
c=sys.argv[1]; T=float(sys.argv[2])
t=tech.measure(c,T); iu=t['I_u']
ports=sim.ports('rt5w_readout'); print(ports[-3:])
L=["Vdd vdd 0 3.3","Vss vss 0 0",f"Vr vr 0 {t['vr']:.4f}",f"Vvc vcas 0 {t['vcas']:.4f}",f"Indac vdd ndac {iu:.6e}",
   "Vrst adc_rst 0 0","Vlat adc_lat 0 0","Vf intf vr 0"]
for j in range(4):
    L+=[f"Iin{j} pd{j} 0 {iu/4*16:.6e}",
        f"XMp{j} pd{j} pd{j} vdd vdd sky130_fd_pr__pfet_g5v0d10v5 L={SM_P['L']} W={SM_P['W']} nf=1 m=4",
        f"XMo{j} o{j} pd{j} vdd vdd sky130_fd_pr__pfet_g5v0d10v5 L={SM_P['L']} W={SM_P['W']} nf=1 m=16",
        f"Vch{j} adc_ch{j} 0 0"]
L+=[f"Vd{k} dac{k} 0 0" for k in range(8)]
conn={p:p for p in ports}; conn.update({f"out{j}":f"o{j}" for j in range(4)}); conn['int']='intf'
L.append(sim.inst("Xr","rt5w_readout",**conn))
ctl=["op","let i0=i(Vf)","print i0","alter Vch0 dc=3.3","op","let ish=i(Vf)","print ish","alter Vch0 dc=0"]
ctl+=[f"alter Vd{k} dc=3.3" for k in range(8)]+["op","let idac=i(Vf)","print idac"]
vals,_,out=sim.run("\n".join(L),"\n".join(ctl),c,T,blocks=["rt5w_readout"],timeout=600)
i0,ish,idac=vals['i0'],vals['ish'],vals['idac']
print(c,'share gain',(ish-i0)/(16*iu),'dac gain',-(idac-i0)/(255*iu/16),'i0',i0)
