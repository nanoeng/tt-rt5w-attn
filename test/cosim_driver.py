# SPDX-License-Identifier: Apache-2.0
"""cocotb side of the RTL + SPICE co-simulation.

The RTL (src/project.v + src/rt5w_ctrl.v) runs in Icarus or Verilator with test/rt5w_analog_cosim.v as the analog
macro. This driver
  - watches the macro's inputs (bias_en, q_code, k_code, keys, trims, row mismatch) and records an analog event when
    the bias turns on or an input changes while biased (rt5w.cosim.Cosim.event);
  - every SAMPLE_NS while biased, takes the SPICE solution at the current simulation time (shares and V_B, transient
    from the event, held after the horizon) and writes it into the macro (sh_mlsb*, vb_uv), where the comparator of
    the SAR reads it.
A SPICE transient runs only when the simulation first needs the shares after an event (the simulator waits for it;
simulated time does not advance). Identical events are cached.
Environment: COSIM_ENGINE (pyspice | ngspice), COSIM_CORNER, COSIM_TEMP, COSIM_BIAS_OFF (fraction of nominal bias
while gated off; the gating switch is not drawn yet, default 1e-6)."""
import os
import sys

import cocotb
from cocotb.triggers import First, Timer
from cocotb.utils import get_sim_time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# COSIM_PDK: sky130 (default; the TTSKY26e macro, rt5w/cosim_sky130.py) or gf180 (the 19 Nov version, rt5w/cosim.py)
if os.environ.get("COSIM_PDK", "sky130") == "sky130":
    from rt5w.cosim_sky130 import Cosim  # noqa: E402
else:
    from rt5w.cosim import Cosim  # noqa: E402

SAMPLE_NS = 100


def _sint(h):
    """Signed value of a Verilog integer: cocotb gives a Python int (Icarus) or a LogicArray (Verilator)."""
    v = h.value
    if isinstance(v, int):
        return v - (1 << 32) if v >= (1 << 31) else v
    return v.to_signed()


def env_cosim():
    return Cosim(corner=os.environ.get("COSIM_CORNER", "tt"), temp=float(os.environ.get("COSIM_TEMP", "27")),
                 engine=os.environ.get("COSIM_ENGINE", "pyspice"),
                 off=float(os.environ.get("COSIM_BIAS_OFF", "1e-6")))


class AnalogCosimDriver:
    def __init__(self, dut, cosim=None):
        self.ana = dut.user_project.u_ana
        self.cs = cosim or env_cosim()
        self.last = None

    def state(self):
        a = self.ana
        q = a.q_code.value.to_unsigned()
        ks = a.k_code.value.to_unsigned()
        kf = a.kflat.value.to_unsigned()
        trim = [0.0] + [_sint(getattr(a, f"vw_uv{r}")) * 1e-3 for r in (1, 2, 3)]   # mV
        gam = [_sint(getattr(a, f"gam_ppm{r}")) * 1e-6 for r in range(4)]
        st = self.cs.blank_state()
        st.update(q=[(q >> (4 * m)) & 15 for m in range(4)], ks=[(ks >> (4 * j)) & 15 for j in range(4)],
                  k=[[(kf >> (8 * (4 * j + m))) & 0xFF for m in range(4)] for j in range(4)], trim_mv=trim, gamma=gam)
        return st

    def now_s(self):
        return get_sim_time("ns") * 1e-9

    def start(self):
        cocotb.start_soon(self._watch())
        cocotb.start_soon(self._drive())
        return self

    async def _watch(self):
        a = self.ana
        was = 0
        sigs = [a.bias_en, a.q_code, a.k_code, a.kflat, a.vw_uv1, a.vw_uv2, a.vw_uv3,
                a.gam_ppm0, a.gam_ppm1, a.gam_ppm2, a.gam_ppm3]
        while True:
            await First(*[s.value_change for s in sigs])
            b = int(a.bias_en.value)
            if b:
                st = self.state()
                key = Cosim._key(st)
                if not was or key != self.last:
                    self.cs.event(st, True, self.now_s(), bool(was))
                    self.last = key
            elif was:
                self.cs.event(None, False, self.now_s(), True)
            was = b

    async def _drive(self):
        a = self.ana
        while True:
            await Timer(SAMPLE_NS, "ns")
            if not int(a.bias_en.value):
                continue
            r = self.cs.sample(self.now_s())
            if r is None:
                continue
            shares, vb = r
            for j in range(4):
                getattr(a, f"sh_mlsb{j}").value = int(round(shares[j] * 255000))
            a.vb_uv.value = int(round(vb * 1e6))

    def vb_now(self):
        r = self.cs.sample(self.now_s())
        return None if r is None else r[1]
