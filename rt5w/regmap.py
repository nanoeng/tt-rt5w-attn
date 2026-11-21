"""Register map of tt_um_rt5w_attn (src/rt5w_ctrl.v). MicroPython-compatible (no f-strings in hot paths, no typing)."""
CTRL, Q01, Q23, K01, K23, WIN_L, WIN_H, WAKE, ADCT, WSEL, PULSE, OUT_SEL = 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B
TGT0, RES0, STATUS, NPASS, LASTUPD, ID = 0x0C, 0x10, 0x14, 0x15, 0x16, 0x7F
ID_VALUE = 0x5A
CTRL_BIAS_FORCE, CTRL_GATE, CTRL_START, CTRL_CAL, CTRL_VBPROBE = 0x01, 0x02, 0x04, 0x08, 0x10
STATUS_BUSY, STATUS_VALID, STATUS_CAL = 0x02, 0x04, 0x08
WSEL_EN = 0x20
N_CELLS = 20          # 0..15 keys k[r][c] at 4*r + c, 16..19 row trims
CLK_HZ = 20000000
DEFAULT_WIN = 1000    # 50 us at 20 MHz
X_MAX = 18.0          # score full scale (e-folds)
X_PER_QK = 0.3        # x_j = 0.3 * sum_c q_c * k_jc   (q codes 0..15, k in (0, 1]); 0.3 = 18 / (4 * 15)
