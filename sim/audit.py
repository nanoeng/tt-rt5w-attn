from rt5w_ng import *
import sys
def audit(x, **kw):
    r=softmax_op(x, nUT=37e-3, **kw); v=r['raw']; rows=[]
    for k in sorted(v):
        if k.startswith('@') and k.endswith('[gm]'):
            dv=k[1:-4]; idd=abs(v[f'@{dv}[id]'])
            if idd>0: rows.append((dv, idd, v[k]/idd, abs(v[f'@{dv}[vds]']), abs(v[f'@{dv}[vdsat]'])))
    return r, rows
if __name__=="__main__":
    for x in ([18,0,0,0],[0,0,0,0]):
        r,rows=audit(x); print(x, np.round(r['I']*1e9,2), 'VB',round(r['vb'],3))
        for dv,i,g,vds,vs in rows: print(f"  {dv:6s} I={i*1e9:8.2f}nA gm/ID={g:5.1f} Vds={vds:.2f} vdsat={vs:.3f}")
