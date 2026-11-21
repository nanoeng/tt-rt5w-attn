"""Transistor-level backend: column IDACs -> PMOS array -> softmax core, gf180mcuD, from analog/rt5w_core.spice.
Engines: 'ngspice' (CLI subprocess) or 'pyspice' (PySpice NgSpiceShared / libngspice).
IDEAL in this netlist (as in rt5w_core.spice): V_R, V_cas, tail/keep-alive bias currents, IDAC unit feed,
key storage (ideal series offset instead of the floating C_W: open item O1), and the readout ADC
(codes = round(255 * I_j / sum I), the host-side renormalisation)."""
import math
import os
import re
import subprocess
import tempfile

import numpy as np

from . import Backend, ROOT

MODELS = os.environ.get("GF180_MODELS", os.path.join(ROOT, ".pdk", "gf180mcu_fd_pr", "models", "ngspice"))
CORE = os.path.join(ROOT, "analog", "rt5w_core.spice")
IQ_LSB = 8.25e-9
NUT_P = 0.0398
CORNER_LIB = {"tt": "typical", "ss": "ss", "ff": "ff", "sf": "sf", "fs": "fs"}


def netlist(q_codes, k, corner="tt", temp=27):
    ptat = (temp + 273.15) / 300.15
    L = ["* rt5w array + softmax (backend)", f".include {MODELS}/design.ngspice",
         f".lib {MODELS}/sm141064.ngspice {CORNER_LIB[corner]}", f".include {CORE}", f".temp {temp}",
         # ideal-offset cell: same device as rt5w_cell, key as a series gate offset
         ".subckt cell_ideal vdd dcol row vw=0",
         "Mc row fg vdd vdd pmos_3p3 w=20u l=4u m=8",
         "Vw fg dcol {vw}", ".ends",
         "Vdd vdd 0 3.3", "Vr vr 0 1.65", "Vcas vcas 0 1.05", "Vhi hi 0 3.3", "Vlo lo 0 0",
         f"Ib vdd nbias {125e-9 * ptat:.5e}", f"Ik vdd kbias {5e-9 * ptat:.5e}"]
    for c in range(4):
        th = ["hi" if u < q_codes[c] else "lo" for u in range(15)]
        L += [f"Ilsb{c} vdd nd{c} {IQ_LSB * ptat:.5e}", f"Xi{c} dcol{c} nd{c} 0 {' '.join(th)} rt5w_idac4",
              f"Xd{c} vdd dcol{c} rt5w_coldiode"]
        for r in range(4):
            kk = float(k[r][c])
            vw = 1.0 if kk < 1e-3 else -NUT_P * ptat * math.log(kk)   # PTAT write keeps k over temperature
            L.append(f"Xc{r}{c} vdd dcol{c} g{r} cell_ideal vw={vw:.6f}")
    L += ["Xsm vdd 0 g0 g1 g2 g3 vb o0 o1 o2 o3 nbias kbias vr vcas rt5w_softmax"]
    L += [f"Vo{j} o{j} 0 2.78" for j in range(4)]
    return "\n".join(L)


_NG = None


def shared_ngspice():
    """One libngspice instance per process: PySpice 1.5 re-declares its cffi structs on every NgSpiceShared()."""
    global _NG
    if _NG is None:
        import logging
        from PySpice.Spice.NgSpice.Shared import NgSpiceShared

        class _Quiet(NgSpiceShared):                 # keep ngspice's console chatter out of the report
            def send_char(self, message, ngspice_id):
                return 0

        logging.getLogger("PySpice").setLevel(logging.ERROR)
        _NG = _Quiet(send_data=False)
    return _NG


def _parse(txt):
    return {m.group(1).lower(): float(m.group(2)) for m in re.finditer(r"^\s*([\w\(\)#\.]+)\s*=\s*([-+0-9.eE]+)", txt, re.M)}


class SpiceBackend(Backend):
    def __init__(self, engine="ngspice", corner="tt", temp=27):
        self.name, self.corner, self.temp = engine, corner, temp
        self._ng = None
        if engine == "pyspice":
            self._ng = shared_ngspice()
        # V_B calibration, exactly as the firmware's VBCAL: all-zero scores and one score at 18
        z = np.zeros((4, 4))
        one = z.copy(); one[0] = 1.0
        _, v0 = self._op([15] * 4, z)
        _, v1 = self._op([15] * 4, one)
        self.vb0, self.vb_slope = v0, (v1 - v0) / (math.log(math.exp(18) + 3) - math.log(4))

    def _op(self, q, k):
        nl = netlist(q, k, self.corner, self.temp)
        if self.name == "ngspice":
            body = nl + "\n.control\nop\nprint i(vo0) i(vo1) i(vo2) i(vo3) v(vb)\n.endc\n.end\n"
            with tempfile.NamedTemporaryFile("w", suffix=".sp", delete=False) as f:
                f.write(body)
            r = subprocess.run(["ngspice", "-b", f.name], capture_output=True, text=True, timeout=300)
            os.unlink(f.name)
            v = _parse(r.stdout)
            I = np.array([v[f"i(vo{j})"] for j in range(4)])
            return I, v["v(vb)"]
        ng = self._ng
        ng.destroy()
        ng.load_circuit(nl + "\n.end\n")
        ng._ngspice_shared.ngSpice_Command(b"op")      # PySpice 1.5 misreads ngspice-42's 'run' status
        p = ng.plot(None, ng.last_plot)
        I = np.array([float(np.real(p[f"vo{j}#branch"]._data[0])) for j in range(4)])
        return I, float(np.real(p["vb"]._data[0]))

    def run(self, enc):
        I, vb = self._op(enc.q_codes, enc.k)
        a = I / I.sum()
        codes = [int(min(255, math.floor(255 * v + 0.5))) for v in a]
        return codes, math.log(4) + (vb - self.vb0) / self.vb_slope
