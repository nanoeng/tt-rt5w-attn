"""Differential coupling of the readout integration node pair in the PEX netlist: C(int, X) - C(intr, X) per net X
(int / intr identified structurally: the gates of the StrongARM input pair, W4.21/L1)."""
import re, collections, sys
f = sys.argv[1] if len(sys.argv) > 1 else 'netlist_pex/rt5w_readout.spice'
devs, caps = [], collections.defaultdict(float)
for l in open(f):
    t = l.split()
    if not t: continue
    if t[0].startswith('X') and len(t) > 5:
        p = dict(x.split('=') for x in t[6:] if '=' in x); devs.append((t[1], t[2], t[3], p.get('w'), p.get('l')))
    elif t[0].startswith('C'):
        m = re.match(r'([\d.eE+-]+)([fpa]?)', t[3]); s = {'f': 1, 'p': 1e3, 'a': 1e-3, '': 1e15}[m.group(2)]
        caps[(t[1], t[2])] += float(m.group(1)) * s
ins = [d for d in devs if d[3] == '4.21' and d[4] == '1']
tail = collections.Counter(d[2] for d in ins).most_common(1)[0][0]
g = sorted({d[1] for d in ins if d[2] == tail})
def nb(n):
    d = collections.defaultdict(float)
    for (a, b), v in caps.items():
        if a == n: d[b] += v
        elif b == n: d[a] += v
    return d
A, B = nb(g[0]), nb(g[1])
print('nodes', g, 'tot %.1f / %.1f fF' % (sum(A.values()), sum(B.values())))
diff = {k: A.get(k, 0) - B.get(k, 0) for k in set(A) | set(B) if k not in g}
for k in sorted(diff, key=lambda k: -abs(diff[k]))[:12]: print('  %-22s %+6.2f  (%.2f / %.2f)' % (k, diff[k], A.get(k, 0), B.get(k, 0)))
# switching nets during a conversion: comparator internals and the clocks
xa = [d[0] for d in ins if d[1] == g[0]][0]; xb = [d[0] for d in ins if d[1] == g[1]][0]
print('xa/xb', xa, xb)
for lab, n in (('int-xa', (g[0], xa)), ('intr-xb', (g[1], xb)), ('int-xb', (g[0], xb)), ('intr-xa', (g[1], xa)),
               ('int-rst', (g[0], 'adc_rst')), ('intr-rst', (g[1], 'adc_rst')), ('int-lat', (g[0], 'adc_lat')),
               ('intr-lat', (g[1], 'adc_lat')), ('int-cmp', (g[0], 'cmp')), ('intr-cmp', (g[1], 'cmp')),
               ('int-tail', (g[0], tail)), ('intr-tail', (g[1], tail))):
    print('  %-9s %.2f fF' % (lab, nb(n[0]).get(n[1], 0)))
