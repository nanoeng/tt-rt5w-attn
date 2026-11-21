"""Replace the HVI layer (75/20) of every cell of a GDS by the HVI that magic regenerates for that cell
(magic GDS round trip with `gds maskhints no`). Magic 8.3.568 (TT precheck CI, ttsky26e) checks hvi.5 on the
mask-hint part of HVI only (drawn HVI minus what magic regenerates), per cell: drawn HVI that differs from the
regenerated shape leaves sub-0.7 um hint slivers next to sibling cells -> false hvi.5 errors (876 on 21 Nov).
With HVI equal to magic's own output there are no hints. All other layers stay as drawn.
usage: hvi_from_magic.py in.gds magic_rewrite.gds out.gds"""
import sys
import klayout.db as pya

src, mag, out = sys.argv[1:4]
ly = pya.Layout(); ly.read(src)
lm = pya.Layout(); lm.read(mag)
HVI = (75, 20)
li = ly.layer(*HVI)
lim = lm.find_layer(*HVI)
by_name = {c.name: c for c in lm.each_cell()}
miss, n = [], 0
for c in ly.each_cell():
    m = by_name.get(c.name)
    if m is None:
        if not c.shapes(li).is_empty():
            miss.append(c.name)
        continue
    c.shapes(li).clear()
    if lim is not None:
        for s in m.shapes(lim).each():
            c.shapes(li).insert(s)
            n += 1
# KLayout FEOL (foundry rules) on top of magic's output: per cell, close sub-0.7 um HVI gaps (hvi.2a), cover every
# nwell that touches HVI (MR_nwell.CON.1); the additions touch the regenerated HVI, so each is a single hint piece.
lnw = ly.find_layer(64, 20)
for c in ly.each_cell():
    r = pya.Region(c.shapes(li)).merged()
    if r.is_empty():
        continue
    add = r.sized(350).sized(-350) - r
    if lnw is not None:
        nw = pya.Region(c.shapes(lnw)).merged()
        add += nw.interacting(nw & r) - r
    add = add.merged()
    if not add.is_empty():
        c.shapes(li).insert(add)
# cross-cell gaps: the same closing / nwell cover on the flattened chip, as flat shapes in the top cell
top = ly.top_cell()
r = pya.Region(top.begin_shapes_rec(li)).merged()
add = r.sized(350).sized(-350) - r
if lnw is not None:
    nw = pya.Region(top.begin_shapes_rec(lnw)).merged()
    add += nw.interacting(nw & r) - r
add = add.merged()
top.shapes(li).insert(add)
print(f"top-level HVI fill: {add.count()} polygons")
if miss:
    raise SystemExit(f"cells with HVI but not in the magic rewrite: {miss[:10]}")
ly.write(out)
print(f"HVI replaced from {mag}: {n} shapes")
