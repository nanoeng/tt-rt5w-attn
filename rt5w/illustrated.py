"""The Illustrated Transformer (Alammar, 2018) examples, compiled to RT5W passes.

The post gives numbers only for the "Thinking Machines" score/softmax figure (q1.k1 = 112, q1.k2 = 96, /8 -> 14, 12,
softmax 0.88 / 0.12). Its other examples are shown as attention heatmaps and words, so their vectors here are
ILLUSTRATIVE: small d_k = 4 embeddings chosen to reproduce the behaviour the post describes ("it" -> "The animal",
"je suis etudiant" -> "I am a student"). Every example is checked against the float reference
softmax(q K^T / sqrt(d_k)), so the chip result can be compared with what the post computes, not only with itself.

Examples
  E1 thinking_machines   score -> /sqrt(64) -> softmax for "Thinking" (exact numbers from the post)
  E2 matrix_form         Z = softmax(Q K^T / sqrt(d_k)) for both rows of "Thinking Machines"
  E3 it_animal           "The animal didn't cross the street because it was too tired": 11 keys -> tiles,
                         merged by log-sum-exp (V_B) and by a pivot token (codes only)
  E4 multi_head          two heads for "it" (one attends to "The animal", one to "tired"), time-shared on one head
  E5 decoder_masked      decoder self-attention with future positions masked, "I am a student"
  E6 enc_dec_attention   encoder-decoder attention: decoder queries over "je suis etudiant"
  E7 vocab_softmax       final linear + softmax over a toy 12-word vocabulary, tiled (the post's 10,000-word
                         vocabulary would need about 3,333 pivot passes per output word; it stays on the host)
"""
import math
import numpy as np

from .golden import encode_row, softmax, attention_row, merge_tiles_vb, merge_tiles_pivot, mask_leak_ok, Encoding
from .regmap import X_MAX, X_PER_QK

SENT = ["The", "animal", "didn't", "cross", "the", "street", "because", "it", "was", "too", "tired"]


def _keys_for_logits(q, z, d_k, seed):
    """Illustrative keys K (n x 4) with q . K_j / sqrt(d_k) = z_j exactly, random in the directions orthogonal to q."""
    rng = np.random.default_rng(seed)
    q = np.asarray(q, float)
    K = rng.normal(0, 0.5, (len(z), 4))
    K -= np.outer(K @ q / (q @ q), q)
    return K + np.outer(np.asarray(z) * math.sqrt(d_k) / (q @ q), q)


def _encode_global(q, K_all, d_k, groups, slots=4):
    """Encode several passes with ONE scale/offset (needed for cross-tile merging)."""
    q = np.asarray(q, float)
    beta = 15.0 / q.max()
    q_codes = np.clip(np.round(q * beta), 0, 15).astype(int)
    alpha = 1.0 / (X_PER_QK * beta * math.sqrt(d_k))
    span = K_all.max() - K_all.min()
    if alpha * span > 1.0:
        alpha = 1.0 / span
    b = 1.0 / alpha - K_all.max()
    out = []
    for idx in groups:
        k = np.zeros((slots, 4))
        k[:len(idx)] = np.clip(alpha * (K_all[idx] + b), 0, 1)
        x = np.clip(X_PER_QK * (k @ q_codes), 0, X_MAX)
        out.append(Encoding(q_codes, k, len(idx), alpha, beta, b, x))
    return out


def _shares(codes, n):
    c = np.asarray(codes[:n], float)
    return c / max(c.sum(), 1)


def _cmp(name, got, ref, labels):
    got, ref = np.asarray(got, float), np.asarray(ref, float)
    return dict(example=name, labels=labels, chip=[round(v, 4) for v in got], reference=[round(v, 4) for v in ref],
                max_abs_err=round(float(np.abs(got - ref).max()), 4), argmax_ok=bool(np.argmax(got) == np.argmax(ref)))


# ------------------------------------------------------------------------------------------------ examples
def e1_thinking_machines(be):
    q = np.ones(4)
    K = np.array([[28.0] * 4, [24.0] * 4])               # q.k1 = 112, q.k2 = 96 (the post's figure), d_k = 64
    ref, z = attention_row(q, K, d_k=64)                 # z = [14, 12] -> [0.881, 0.119]
    enc = encode_row(q, K, d_k=64)
    codes, lse = be.run(enc)
    r = _cmp("E1 thinking_machines", _shares(codes, 2), ref, ["Thinking", "Machines"])
    r.update(scores=list(map(float, q @ K.T)), scaled=list(map(float, z)), codes=codes, golden_codes=enc.golden_codes(),
             masked_slots_zero=codes[2] == 0 and codes[3] == 0, mask_bound_ok=mask_leak_ok(enc.x_expected))
    return r


def e2_matrix_form(be):
    X_q = [np.array([1.0, 1.0, 1.0, 1.0]), np.array([1.0, 0.8, 0.9, 1.0])]   # rows of Q (illustrative row 2)
    K = np.array([[28.0] * 4, [24.0] * 4])
    rows, refs = [], []
    for q in X_q:
        ref, _ = attention_row(q, K, d_k=64)
        codes, _ = be.run(encode_row(q, K, d_k=64))
        rows.append(_shares(codes, 2)); refs.append(ref)
    r = _cmp("E2 matrix_form", np.ravel(rows), np.ravel(refs), ["T.T", "T.M", "M.T", "M.M"])
    r["argmax_ok"] = all(np.argmax(a) == np.argmax(b) for a, b in zip(rows, refs))   # per query row
    r["passes"] = 2
    return r


def e3_it_animal(be):
    q = np.array([0.9, 0.3, 0.6, 0.2])                   # query of "it"
    z = np.array([1.0, 4.0, 0.3, 0.6, 0.8, 2.6, 0.4, 1.9, 0.5, 0.7, 1.6])   # illustrative logits (post: heatmap)
    K = _keys_for_logits(q, z, 4, seed=3)
    ref = softmax(z)
    # (a) log-sum-exp merge: tiles of 4 (3 passes), one global encoding
    groups = [list(range(0, 4)), list(range(4, 8)), list(range(8, 11))]
    encs = _encode_global(q, K, 4, groups)
    tiles = []
    for idx, enc in zip(groups, encs):
        codes, lse = be.run(enc)
        s = _shares(codes, len(idx))
        if not math.isfinite(lse):
            tiles = None
            break
        # the tile's LSE covers only its real slots: remove the masked slot (x = 0 -> e^0 = 1)
        if len(idx) < 4:
            lse = math.log(max(math.exp(lse) - (4 - len(idx)), 1e-12))
        tiles.append((s, lse))
    vb = merge_tiles_vb(tiles) if tiles else None
    # (b) pivot merge, codes only: tile 1 picks the pivot (its argmax); later tiles = pivot + 3 new tokens
    codes0, _ = be.run(encs[0])
    p = int(np.argmax(codes0[:4]))
    rel = {j: codes0[j] / max(codes0[p], 1) for j in range(4)}
    rest = [j for j in range(4, 11)]
    passes = 1
    for i in range(0, len(rest), 3):
        idx = [p] + rest[i:i + 3]
        enc = _encode_global(q, K, 4, [idx])[0]
        c, _ = be.run(enc)
        passes += 1
        for t, j in enumerate(idx[1:], start=1):
            rel[j] = c[t] / max(c[0], 1)
    piv = np.array([rel[j] for j in range(11)])
    piv = piv / piv.sum()
    r = _cmp("E3 it_animal (pivot merge)", piv, ref, SENT)
    r.update(pivot=SENT[p], passes_pivot=passes, top_word=SENT[int(np.argmax(piv))])
    if vb is not None:
        rv = _cmp("E3 it_animal (V_B log-sum-exp merge)", vb, ref, SENT)
        r["lse_merge"] = dict(chip=rv["chip"], max_abs_err=rv["max_abs_err"], argmax_ok=rv["argmax_ok"], passes=3)
    return r


def e4_multi_head(be):
    out = {}
    for h, (q, z, seed) in enumerate([(np.array([0.9, 0.3, 0.6, 0.2]),
                                       np.array([1.0, 4.0, 0.3, 0.6, 0.8, 2.6, 0.4, 1.9, 0.5, 0.7, 1.6]), 3),
                                      (np.array([0.2, 0.8, 0.4, 0.9]),
                                       np.array([0.4, 1.2, 0.2, 0.3, 0.5, 0.9, 0.6, 1.8, 0.7, 1.5, 3.9]), 11)]):
        K = _keys_for_logits(q, z, 4, seed=seed)
        groups = [[0, 1, 2, 3], [0, 4, 5, 6], [0, 7, 8, 9], [0, 10]]
        rel = {0: 1.0}
        for idx in groups:                      # pivot = "The" (always present) -> codes-only merge
            c, _ = be.run(_encode_global(q, K, 4, [idx])[0])
            for t, j in enumerate(idx[1:], start=1):
                rel[j] = c[t] / max(c[0], 1)
        p = np.array([rel[j] for j in range(11)]); p /= p.sum()
        out[f"head{h}"] = dict(top=SENT[int(np.argmax(p))], ref_top=SENT[int(np.argmax(softmax(z)))],
                               max_abs_err=round(float(np.abs(p - softmax(z)).max()), 4))
    ok = all(v["top"] == v["ref_top"] for v in out.values())
    return dict(example="E4 multi_head (2 heads, time-shared)", heads=out, argmax_ok=ok,
                max_abs_err=max(v["max_abs_err"] for v in out.values()), passes=8)


def e5_decoder_masked(be):
    words = ["<s>", "I", "am", "a"]
    z_full = np.array([[2.0, 0, 0, 0], [0.5, 2.5, 0, 0], [0.3, 1.2, 2.2, 0], [0.2, 0.6, 1.5, 2.4]])
    res, errs, leak = [], [], True
    for t in range(4):                          # step t sees positions 0..t; t+1.. are masked (-inf -> k = 0)
        q = np.array([0.7, 0.5, 0.9, 0.4])
        K = _keys_for_logits(q, z_full[t, :t + 1], 4, seed=20 + t)
        enc = encode_row(q, K, d_k=4)
        codes, _ = be.run(enc)
        ref = softmax(z_full[t, :t + 1])
        got = _shares(codes, t + 1)
        errs.append(float(np.abs(got - ref).max()))
        leak &= all(c == 0 for c in codes[t + 1:]) or not mask_leak_ok(enc.x_expected)
        res.append(dict(step=t, query=words[t], chip=[round(v, 3) for v in got], reference=[round(v, 3) for v in ref],
                        masked_codes=codes[t + 1:]))
    return dict(example="E5 decoder_masked", steps=res, max_abs_err=round(max(errs), 4),
                masked_zero_when_bound_holds=leak, argmax_ok=all(np.argmax(r["chip"]) == np.argmax(r["reference"]) for r in res))


def e6_enc_dec(be):
    src = ["je", "suis", "etudiant"]
    tgt = ["I", "am", "a", "student"]
    align = np.array([[3.0, 0.5, 0.2], [0.4, 3.2, 0.6], [0.2, 0.9, 2.6], [0.1, 0.4, 3.4]])
    q = np.array([0.6, 0.9, 0.5, 0.8])
    res, errs = [], []
    for i, w in enumerate(tgt):
        K = _keys_for_logits(q, align[i], 4, seed=40 + i)   # keys/values from the encoder stack
        codes, _ = be.run(encode_row(q, K, d_k=4))
        got, ref = _shares(codes, 3), softmax(align[i])
        errs.append(float(np.abs(got - ref).max()))
        res.append(dict(query=w, attends=src[int(np.argmax(got))], ref_attends=src[int(np.argmax(ref))],
                        chip=[round(v, 3) for v in got]))
    return dict(example="E6 enc_dec_attention", rows=res, max_abs_err=round(max(errs), 4),
                argmax_ok=all(r["attends"] == r["ref_attends"] for r in res))


def e7_vocab(be):
    vocab = ["a", "am", "I", "thanks", "student", "<eos>", "je", "suis", "the", "it", "was", "cross"]
    logits = np.array([0.5, 0.8, 1.0, 0.2, 4.5, 1.6, 0.1, 0.3, 0.9, 0.4, 0.6, 0.2])   # decoder output "student"
    q = np.array([1.0, 0.7, 0.8, 0.6])
    K = _keys_for_logits(q, logits, 4, seed=7)          # rows of the output projection, as keys
    rel, passes = {0: 1.0}, 0
    for i in range(1, 12, 3):
        idx = [0] + list(range(i, min(i + 3, 12)))
        c, _ = be.run(_encode_global(q, K, 4, [idx])[0])
        passes += 1
        for t, j in enumerate(idx[1:], start=1):
            rel[j] = c[t] / max(c[0], 1)
    p = np.array([rel[j] for j in range(12)]); p /= p.sum()
    ref = softmax(logits)
    r = _cmp("E7 vocab_softmax (12 words, pivot tiles)", p, ref, vocab)
    r.update(passes=passes, word=vocab[int(np.argmax(p))], passes_for_10000_words=math.ceil(9999 / 3))
    return r


EXAMPLES = [e1_thinking_machines, e2_matrix_form, e3_it_animal, e4_multi_head, e5_decoder_masked, e6_enc_dec, e7_vocab]


def calibration_set(n=24, seed=0):
    """Random calibration vectors (keys of similar size so every row matters), as in rev-3 SS-SGD."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        q = rng.integers(8, 16, 4)
        K = rng.uniform(0.6, 1.0, (4, 4))
        out.append(Encoding(q, K, 4, 1, 1, 0, np.clip(X_PER_QK * (K @ q), 0, X_MAX)))
    return out


def calibrate(be, epochs=8, seed=0):
    """On-chip SS-SGD over the calibration set; returns median code MAE per epoch (epoch 0 = before)."""
    cal = calibration_set(seed=seed)
    hist = []
    for ep in range(epochs + 1):
        maes = []
        for enc in cal:
            if ep == 0:
                codes, _ = be.run(enc)
            else:
                codes, _ = be.calibrate(enc)
            maes.append(np.abs(np.array(codes) - np.array(enc.golden_codes())).mean())
        hist.append(float(np.median(maes)))
    return hist


def run_all(be):
    return [f(be) for f in EXAMPLES]
