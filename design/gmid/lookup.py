"""gm/ID look-up (Jespers & Murmann, "Systematic Design of Analog CMOS Circuits Using Pre-Computed Lookup Tables",
CUP 2017): every quantity is read from the characterisation tables (techsweep.py) at a chosen gm/ID, L and V_DS.

    lut = Lut("n")                          # sky130 nfet_g5v0d10v5, tt, 27 C
    lut.at(gm_id=20, L=4, vds=1.0)          # dict: id_w [A/um], gm_gds, ft, vgs, vth, cgg_w ...
    lut.size(i_d=125e-9, gm_id=20, L=4)     # -> W (um) and the operating point
Width scaling: I_D, g_m, g_ds and capacitances are proportional to W (W = 10 um in the table); gm/ID, gm/gds and
f_T are width independent (the method's premise; checked against a direct simulation in check_lut.py)."""
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


class Lut:
    def __init__(self, kind="n", corner="tt", temp=27):
        d = np.load(os.path.join(HERE, f"lut_{kind}_{corner}_{int(temp)}.npz"))
        self.kind, self.corner, self.temp = kind, corner, temp
        self.L, self.VGS, self.VDS, self.W = d["L"], d["VGS"], d["VDS"], float(d["W"])
        self.t = {k: d[k] for k in ("id", "gm", "gds", "gmbs", "cgg", "cgs", "cgd", "vth")}

    def _slice(self, L, vds):
        """Tables at one (L, VDS) as functions of VGS; L interpolated linearly in log L."""
        iv = np.interp(vds, self.VDS, np.arange(len(self.VDS)))
        i0 = int(np.floor(iv)); fv = iv - i0; i1 = min(i0 + 1, len(self.VDS) - 1)
        il = np.interp(np.log(L), np.log(self.L), np.arange(len(self.L)))
        l0 = int(np.floor(il)); fl = il - l0; l1 = min(l0 + 1, len(self.L) - 1)
        out = {}
        for k, a in self.t.items():
            v = lambda li: (1 - fv) * a[li, i0] + fv * a[li, i1]   # noqa: E731
            out[k] = (1 - fl) * v(l0) + fl * v(l1)
        return out

    ID_MIN = 1e-11      # A/um: below this the model's gm/ID is set by junction/GIDL leakage, not by the channel

    def _branch(self, L, vds):
        s = self._slice(L, vds)
        gmid = s["gm"] / np.maximum(s["id"], 1e-30)
        ok = (s["id"] / self.W) >= self.ID_MIN
        return s, gmid, ok

    def at(self, gm_id, L, vds):
        """Operating point at gm/ID on the strong-inversion side of the weak-inversion plateau (the last V_GS where
        gm/ID still reaches the target; unique because gm/ID falls monotonically from there)."""
        s, gmid, ok = self._branch(L, vds)
        idx = np.where(ok & (gmid >= gm_id))[0]
        if len(idx) == 0:
            raise ValueError(f"gm/ID {gm_id} above the plateau {self.max_gm_id(L, vds):.1f} S/A at L={L} um")
        k = idx[-1]
        if k + 1 >= len(self.VGS):
            raise ValueError("gm/ID reached at the end of the V_GS sweep")
        f = (gmid[k] - gm_id) / (gmid[k] - gmid[k + 1])
        vgs = float(self.VGS[k] + f * (self.VGS[k + 1] - self.VGS[k]))
        q = {kk: float(np.interp(vgs, self.VGS, v)) for kk, v in s.items()}
        return dict(gm_id=gm_id, L=L, vds=vds, vgs=vgs, vth=q["vth"], id_w=q["id"] / self.W,
                    gm_gds=q["gm"] / q["gds"], ft=q["gm"] / (2 * np.pi * q["cgg"]), cgg_w=q["cgg"] / self.W,
                    gmb_gm=q["gmbs"] / q["gm"], vov=vgs - q["vth"])

    def gm_id_at_density(self, idw, L, vds=1.0):
        """gm/ID at a current density I_D/W (A/um)."""
        s, gmid, ok = self._branch(L, vds)
        return float(np.interp(np.log(idw), np.log(np.maximum(s["id"] / self.W, 1e-30)), gmid))

    def wi_target(self, L, vds=1.0, frac=0.9):
        """Weak-inversion design point: 90 % of gm/ID in deep weak inversion (1 nA/um). The 5 V nfet model's
        gm/ID keeps creeping up into the leakage region, so its maximum is not a usable plateau."""
        return frac * self.gm_id_at_density(1e-9, L, vds)

    def max_gm_id(self, L, vds):
        """Weak-inversion plateau: max gm/ID over channel-dominated currents (id/W >= ID_MIN)."""
        s, gmid, ok = self._branch(L, vds)
        return float(np.max(gmid[ok]))

    def size(self, i_d, gm_id, L, vds=None, w_min=0.42, w_grid=0.01):
        vds = vds if vds is not None else 1.0
        op = self.at(gm_id, L, vds)
        W = max(w_min, round(i_d / op["id_w"] / w_grid) * w_grid)
        op.update(W=W, i_d=i_d, gm=gm_id * i_d, gds=gm_id * i_d / op["gm_gds"], cgg=op["cgg_w"] * W)
        return op
