import sys, json
sys.path[:0]=['design/tb','design','design/blocks']
import tb_chain
c,T=sys.argv[1],float(sys.argv[2]); out=[]
for q,k,ks in tb_chain.VECTORS:
    r=tb_chain.run(q,k,ks,c,T); out.append(dict(q=q,ks=ks,model=r['model'],spice=r['spice'],err=r['err'])); print(c,q,ks,r['model'],r['spice'],r['err'],flush=True)
import os; m='pexcont' if os.environ.get('RT5W_NETLIST')=='netlist_pex' else 'schcont'
json.dump(dict(vectors=out,err=max(v['err'] for v in out),mode=m,corner=c),open(f'results/pex/{m}_chain_{c}.json','w'),indent=1)
