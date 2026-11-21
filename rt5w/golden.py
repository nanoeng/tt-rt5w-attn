"""Illustrated-Transformer reference maths (Alammar 2018) and its mapping onto one RT5W pass.

Chip function (one pass, one query row, 4 key slots):
    x_j  = clip(0.3 * sum_c q_c k_jc, 0, 18)          q_c: 4-bit codes, k_jc in [0, 1] (C_W keys)
    a_j  = softmax(x)_j ;  code_j = round(255 a_j) ;  V_B = V_B0 - nU_T ln(sum_j e^{x_j})
Host responsibilities (what the post's steps map to):
    step 1  Q, K, V projections ............ host (trained weights)
    step 2  q . k_j ........................ chip (array, KCL)            -> encode_row()
    step 3  / sqrt(d_k) .................... folded into the key scale alpha
    step 4  softmax ........................ chip (exponentiators + KCL)
    mask    -inf ........................... k = 0 (x = 0) + shift max x to 18
    >4 keys ................................ tiles merged by log-sum-exp (V_B) or by a pivot token (codes only)
    step 5-6, W^O, FFN, LayerNorm, vocab ... host
"""
import math
import numpy as np

from .regmap import X_MAX, X_PER_QK

LN510 = math.log(510.0)


def softmax(z):
    z = np.asarray(z, dtype=float)
    e = np.exp(z - z.max())
    return e / e.sum()


def attention_row(q, K, d_k=None, mask=None):
    """Reference: softmax(q K^T / sqrt(d_k)) with optional boolean mask (True = masked -> -inf)."""
    K = np.atleast_2d(np.asarray(K, float))
    d_k = d_k or K.shape[1]
    z = K @ np.asarray(q, float) / math.sqrt(d_k)
    if mask is not None:
        z = np.where(np.asarray(mask, bool), -np.inf, z)
    return softmax(z), z


class Encoding:
    """One pass worth of chip inputs plus what the host needs to decode it."""
    def __init__(self, q_codes, k, n_real, alpha, beta, b, x_expected):
        self.q_codes, self.k, self.n_real = list(q_codes), np.asarray(k, float), n_real
        self.alpha, self.beta, self.b, self.x_expected = alpha, beta, b, np.asarray(x_expected, float)

    def golden_codes(self):
        a = softmax(self.x_expected)
        return [int(min(255, math.floor(255 * v + 0.5))) for v in a]


def encode_row(q, K, d_k=None, slots=4):
    """Map a query q (>= 0, length 4) and up to `slots` keys K (signed) onto one chip pass.
    Signed keys use the rev-3 offset coding k' = alpha (K + b): the extra term alpha b sum(q) is common to all
    keys and cancels in the softmax. alpha is set so that 0.3 * alpha * beta = 1/sqrt(d_k) (the post's step 3);
    b is then as large as k' <= 1 allows, which pushes max x towards 18 (masked slots get k' = 0 -> x = 0)."""
    q = np.asarray(q, float)
    K = np.atleast_2d(np.asarray(K, float))
    n, d = K.shape
    assert d == 4 and n <= slots and (q >= 0).all(), "chip: d = 4, non-negative query (ReLU on W_Q, rev 3 option A)"
    d_k = d_k or d
    beta = 15.0 / q.max() if q.max() > 0 else 1.0
    q_codes = np.clip(np.round(q * beta), 0, 15).astype(int)
    alpha = 1.0 / (X_PER_QK * beta * math.sqrt(d_k))
    span = K.max() - K.min()
    if alpha * span > 1.0:                         # logit range does not fit: compress (reported)
        alpha = 1.0 / span
    b = 1.0 / alpha - K.max()                      # top key element -> k' = 1
    k = np.zeros((slots, 4))
    k[:n] = np.clip(alpha * (K + b), 0.0, 1.0)
    x = np.clip(X_PER_QK * (k @ q_codes), 0, X_MAX)
    return Encoding(q_codes, k, n, alpha, beta, b, x)


def mask_leak_ok(x):
    """Masked slots (x = 0) read code 0 iff max x > ln 510."""
    return float(np.max(x)) > LN510


def merge_tiles_vb(tiles):
    """Online-softmax merge of tiles using each tile's log-sum-exp (V_B readout). tiles: [(shares, lse)]."""
    L = np.array([t[1] for t in tiles])
    w = softmax(L)
    return np.concatenate([np.asarray(s, float) * wi for (s, _), wi in zip(tiles, w)])


def merge_tiles_pivot(tiles):
    """Codes-only merge: every tile carries the same pivot token in slot 0, so share_j / share_pivot = e^{x_j - x_p}.
    tiles: list of share vectors (slot 0 = pivot). Returns probabilities over [pivot] + all other slots."""
    rel = [1.0]
    for s in tiles:
        s = np.asarray(s, float)
        p = max(s[0], 1e-6)
        rel += list(s[1:] / p)
    rel = np.array(rel)
    return rel / rel.sum()
