import sys, os, json, numpy as np
sys.path[:0]=['design/tb','design','design/blocks']
import sim, tech
from units import SM_P
T_CLK=50e-9
def per_bit(b, adct, sched):
    return min(adct, sched.get(b, adct))
def pwl_sched(nconv, adct, sched):
    starts=[]; t=0.0; lens=[]
    for i in range(nconv):
        for b in range(7,-1,-1):
            n=per_bit(b,adct,sched); starts.append(t); lens.append(n); t+=n*T_CLK
    return starts, lens, t
def pwl(points):
    return "PWL(" + " ".join(f"{a:.4e} {b}" for a,b in points) + ")"
def run(c,T,codes,adct=16,sched=None):
    sched=sched or {}
    t=tech.measure(c,T); iu=t['I_u']
    cur=[(x+0.5)*iu/16 for x in codes]
    starts,lens,tend=pwl_sched(len(codes),adct,sched)
    rp=[(0,3.3)]; lp=[(0,0)]
    for s,n in zip(starts,lens):
        rp += [(s,3.3),(s+T_CLK,3.3),(s+T_CLK+1e-9,0),(s+n*T_CLK-1e-9,0)] if s>0 else [(T_CLK,3.3),(T_CLK+1e-9,0),(n*T_CLK-1e-9,0)]
        lp += [(s+(n-1)*T_CLK,0),(s+(n-1)*T_CLK+1e-9,3.3),(s+n*T_CLK-1e-9,3.3),(s+n*T_CLK,0)]
    # rp: rising at each new start
    rp2=[(0,3.3)]
    for s,n in zip(starts,lens):
        if s>0: rp2 += [(s-1e-9,0),(s,3.3)]
        rp2 += [(s+T_CLK,3.3),(s+T_CLK+1e-9,0)]
    L=["Vdd vdd 0 3.3","Vss vss 0 0",f"Vr vr 0 {t['vr']:.4f}",f"Vvc vcas 0 {t['vcas']:.4f}",f"Indac vdd ndac {iu:.6e}",
       f"Vrst adc_rst 0 {pwl(rp2)}", f"Vlat adc_lat 0 {pwl(lp)}"]
    for j in range(4):
        L+=[f"Iin{j} pd{j} 0 {(cur[0]/4 if j==0 else 2*iu):.6e}",
            f"XMp{j} pd{j} pd{j} vdd vdd sky130_fd_pr__pfet_g5v0d10v5 L={SM_P['L']} W={SM_P['W']} nf=1 m=4",
            f"XMo{j} o{j} pd{j} vdd vdd sky130_fd_pr__pfet_g5v0d10v5 L={SM_P['L']} W={SM_P['W']} nf=1 m=16",
            f"Vch{j} adc_ch{j} 0 {3.3 if j==0 else 0}"]
    L+=[f"Vd{k} dac{k} 0 0" for k in range(8)]
    L+= [x for x in os.environ.get("EXTRA","").split(";") if x.strip()]
    L.append(sim.inst("Xr","rt5w_readout",**{**{p:p for p in sim.ports("rt5w_readout")},**{f"out{j}":f"o{j}" for j in range(4)}}))
    def st(trial,i):
        o=[f"alter Iin0 dc = {cur[i]/4:.6e}"]
        for kk in range(8): o+=[f"let d{kk} = 3.3*(floor({trial}/{2**kk}) - 2*floor({trial}/{2**(kk+1)}))", f"alter Vd{kk} dc = d{kk}"]
        return o
    n=len(codes)*8
    C=["let code = 0","let trial = 128"]+st("trial",0)
    ends=[s+l*T_CLK for s,l in zip(starts,lens)]
    for e in ends: C.append(f"stop when time = {e+2e-9:.4e}")
    C.append(f"tran 2n {tend+4e-9:.4e}")
    for m in range(n):
        i,b=m//8,7-m%8
        C+=["let c = v(cmp)[length(v(cmp))-1]","if c > 1.65","let code = trial","end"]
        if b==0: C+=[f"let code_{i} = code",f"print code_{i}","let code = 0"]
        if m<n-1:
            ni,nb=(m+1)//8,7-(m+1)%8
            C+=[f"let trial = code + {2**nb}"]+st("trial",ni)+["resume"]
    W=os.environ.get("WAVE")
    NODES=["v(cmp)","v(xr.int)","v(xr.intr)","v(o0)","v(pd0)","v(ndac)","v(xr.sk7)","v(xr.sk6)","v(xr.pcas)","v(vr)","v(xr.cgp)","v(xr.cgn)"]
    if W:
        C.insert(0,"save "+" ".join(NODES)); C.append("wrdata __DATA__ "+" ".join(NODES))
    v,tab,o=sim.run("\n".join(L),"\n".join(C),c,T,blocks=["rt5w_readout"],timeout=3600,options=os.environ.get("OPTS",""))
    if W:
        np.save(W, tab); json.dump(dict(starts=starts,lens=lens,T=T_CLK,nodes=NODES),open(W+".json","w"))
    return [int(round(v[f"code_{i}"])) for i in range(len(codes))]
codes=[int(x) for x in os.environ.get("CODES","200,200,91,91,7,255,128,127,64").split(",")]
sched=eval(os.environ.get("SCHED","{}"))
c=sys.argv[1]; T=float(sys.argv[2])
print(c,'sched',sched,'in ',codes); print(c,'out',run(c,T,codes,sched=sched))
