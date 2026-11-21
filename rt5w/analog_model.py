"""Behavioural model of the RT5W analog macro, parameterised from the ngspice results (sim/results/*.json).
Same equations as test/rt5w_analog_beh.v, plus optional die-level non-idealities for Monte-Carlo emulation."""
import math
import numpy as np

from .regmap import X_MAX, X_PER_QK

PARAMS = dict(
    nUT_p=0.0528,          # PMOS array n*U_T (V): sky130 key-cell in-cell slope, tt 27 C (design/tb/tech.py nUT_p_cell)
    w_ref=2.27,            # row trim reference = column-line level at I_u (sky130 tt); h = w_ref - nUT_p ln k
    vb0=1.298, vb_slope=0.0342,   # V_B at LSE = ln 4, slope per e-fold     softmax_static (TT)
    tau_us=3.2,            # share settling time constant: 17.6 us worst to 0.5 LSB ~ 5.5 tau
    step_up_mV=0.141, step_dn_mV=0.120,   # trim pump steps per 50 ns clock (weight_cell.json, TT)
    sigma_row_gain=0.0044, # array row-gain sigma (MC)
    sigma_softmax_beta=0.025,  # softmax slope spread over MC dies (0.926-1.033)
    sum_err=0.0,           # AGC common-mode sum error (ratiometric ADC sees it; host renormalises)
)


class AnalogModel:
    def __init__(self, seed=None, params=None, ideal=False):
        self.p = dict(PARAMS, **(params or {}))
        rng = np.random.default_rng(seed)
        self.ideal = ideal or seed is None
        self.row_gain = np.ones(4) if self.ideal else 1 + rng.normal(0, self.p["sigma_row_gain"], 4)
        self.beta = 1.0 if self.ideal else 1 + rng.normal(0, self.p["sigma_softmax_beta"])
        self.k = np.zeros((4, 4))          # keys (cells 0..15)
        self.vw_trim = np.zeros(4)         # row trim voltages (mV), row 0 pinned

    # writes ----------------------------------------------------------------------------------------
    def write_cell_voltage(self, cell, v_w_pin):
        dh = v_w_pin - self.p["w_ref"]                   # h - w
        k = math.exp(-dh / self.p["nUT_p"]) if dh < 0.6 else 0.0
        if cell < 16:
            self.k[cell // 4, cell % 4] = min(k, 1.0)

    def pump(self, up_mask, dn_mask, clocks=1):
        for r in range(1, 4):
            if (up_mask >> r) & 1:
                self.vw_trim[r] += self.p["step_up_mV"] * clocks
            if (dn_mask >> r) & 1:
                self.vw_trim[r] -= self.p["step_dn_mV"] * clocks

    # evaluation ------------------------------------------------------------------------------------
    def scores(self, q_codes):
        g = self.row_gain * np.exp(self.vw_trim / (self.p["nUT_p"] * 1e3))
        return np.clip(X_PER_QK * (self.k @ np.asarray(q_codes, float)) * g, 0, X_MAX)

    def evaluate(self, q_codes, window_us=50.0):
        x = self.scores(q_codes) * self.beta
        e = np.exp(x - x.max())
        a = e / e.sum()
        settle = 1 - math.exp(-window_us / self.p["tau_us"])
        a = 0.25 + (a - 0.25) * settle
        codes = [int(min(255, math.floor(255 * v * (1 + self.p["sum_err"]) + 0.5))) for v in a]
        lse = math.log(np.exp(x - x.max()).sum()) + x.max()
        v_b = self.p["vb0"] + self.p["vb_slope"] * (lse - math.log(4.0))
        return codes, v_b, x
