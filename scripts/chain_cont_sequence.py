import sys, os
sys.path[:0]=['design/tb','design','design/blocks']
import tb_chain
seq=[int(x) for x in os.environ.get("SEQ","3,3,3").split(",")]
T_CLK=tb_chain.T_CLK
def sar(adct):
    P=adct*T_CLK; L=[]
    def st(ch,trial):
        o=[f"alter Vch{j} dc = {3.3 if j==ch else 0}" for j in range(4)]
        for kk in range(8): o+=[f"let d{kk} = 3.3*(floor({trial}/{2**kk}) - 2*floor({trial}/{2**(kk+1)}))", f"alter Vd{kk} dc = d{kk}"]
        return o
    n=len(seq)*8
    L+=["let code = 0","let trial = 128"]+st(seq[0],"trial")
    for m in range(1,n+1): L.append(f"stop when time = {m*P+2e-9:.4e}")
    L.append(f"tran 2n {n*P+4e-9:.4e}")
    for m in range(n):
        i,b=m//8,7-m%8
        L+=["let c = v(cmp)[length(v(cmp))-1]","if c > 1.65","let code = trial","end"]
        if b==0: L+=[f"let code_{i} = code",f"print code_{i}","let code = 0"]
        if m<n-1:
            ni,nb=(m+1)//8,7-(m+1)%8
            L+=[f"let trial = code + {2**nb}"]+st(seq[ni],"trial")+["resume"]
    return "\n".join(L)
tb_chain._sar_cont=sar
import sim
_r=sim.run
def r2(*a,**kw):
    v,t,o=_r(*a,**kw); print('codes',[int(round(v[f'code_{i}'])) for i in range(len(seq))]); v.update({f'code_{c}':0 for c in range(4) if f'code_{c}' not in v}); return v,t,o
sim.run=r2
c,T,i=sys.argv[1],float(sys.argv[2]),int(sys.argv[3]); q,k,ks=tb_chain.VECTORS[i]
print('seq',seq,'model',tb_chain.model_codes(q,k,ks)[0]); tb_chain.run(q,k,ks,c,T)
