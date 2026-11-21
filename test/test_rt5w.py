# SPDX-License-Identifier: Apache-2.0
"""cocotb tests for tt_um_rt5w_attn (controller RTL + behavioural analog macro)."""
import math, random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer, RisingEdge, FallingEdge

CLK_NS = 50          # 20 MHz (timing estimate: 39.8 ns worst at ss 125C 3.0V, unbuffered)
SCK_HALF_NS = 500    # 1 MHz SPI (synchronised, needs SCK <= clk/8)
XMAX = 18.0
XS_DEN = 15 * 15 * 255 * 4


# ----------------------------------------------------------------------------- golden model
def scores(q, k, ks, gains=(1, 1, 1, 1)):
    return [min(XMAX, max(0.0, XMAX * ks[j] * sum(q[m] * k[j][m] for m in range(4)) / XS_DEN * gains[j]))
            for j in range(4)]


def softmax(x):
    m = max(x); e = [math.exp(v - m) for v in x]; s = sum(e)
    return [v / s for v in e]


def codes(x):
    return [min(255, int(math.floor(255 * a + 0.5))) for a in softmax(x)]


# ----------------------------------------------------------------------------- SPI helpers
async def spi_xfer(dut, word):
    """16-bit mode-0 frame; returns the 8 bits sampled during the data byte."""
    dut.ui_in.value = (dut.ui_in.value.to_unsigned() & ~0x07) | 0x04   # CS high
    await Timer(SCK_HALF_NS, "ns")
    ui = dut.ui_in.value.to_unsigned() & ~0x07                          # CS low, SCK low
    dut.ui_in.value = ui
    await Timer(SCK_HALF_NS, "ns")
    rd = 0
    for b in range(15, -1, -1):
        mosi = (word >> b) & 1
        dut.ui_in.value = ui | (mosi << 1)
        await Timer(SCK_HALF_NS, "ns")
        dut.ui_in.value = ui | (mosi << 1) | 1                          # SCK rise
        if b < 8:
            rd = (rd << 1) | (dut.uio_out.value.to_unsigned() & 1)
        await Timer(SCK_HALF_NS, "ns")
    dut.ui_in.value = ui | 0x04                                         # CS high
    await Timer(SCK_HALF_NS, "ns")
    return rd


async def wr(dut, addr, data):
    await spi_xfer(dut, 0x8000 | (addr << 8) | (data & 0xFF))


async def rd(dut, addr):
    return await spi_xfer(dut, (addr << 8))


async def reset(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.ena.value = 1; dut.ui_in.value = 0x04; dut.uio_in.value = 0; dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)


def ana(dut):
    return dut.user_project.u_ana


def load_keys(dut, k):
    v = 0
    for j in range(4):
        for m in range(4):
            v |= (k[j][m] & 0xFF) << (8 * (4 * j + m))
    ana(dut).kflat.value = v


async def load_qk(dut, q, ks):
    await wr(dut, 0x01, q[0] | (q[1] << 4)); await wr(dut, 0x02, q[2] | (q[3] << 4))
    await wr(dut, 0x03, ks[0] | (ks[1] << 4)); await wr(dut, 0x04, ks[2] | (ks[3] << 4))


async def run_pass(dut, cal=False, timeout_us=200):
    await wr(dut, 0x00, 0x02 | (0x08 if cal else 0x04))
    for _ in range(timeout_us * 20):
        await RisingEdge(dut.clk)
        if not (dut.uio_out.value.to_unsigned() >> 2) & 1:      # BUSY low
            break
    else:
        raise AssertionError("pass timeout")
    return [await rd(dut, 0x10 + j) for j in range(4)]


# ----------------------------------------------------------------------------- tests
@cocotb.test()
async def t01_id_and_registers(dut):
    await reset(dut)
    assert await rd(dut, 0x7F) == 0x5A
    assert await rd(dut, 0x05) == (1000 & 0xFF) and await rd(dut, 0x06) == (1000 >> 8)
    for a, v in ((0x01, 0xA5), (0x0C, 0x3C), (0x09, 0x2B), (0x08, 0x06)):
        await wr(dut, a, v)
        assert await rd(dut, a) == v, hex(a)
    assert await rd(dut, 0x10) == 0                              # results read-only, reset 0


@cocotb.test()
async def t02_bias_gating(dut):
    await reset(dut)
    assert int(ana(dut).bias_en.value) == 0, "bias must be gated off when idle (default)"
    load_keys(dut, [[255] * 4, [0] * 4, [0] * 4, [0] * 4]); await load_qk(dut, [15] * 4, [15] * 4)
    await wr(dut, 0x00, 0x06)
    await ClockCycles(dut.clk, 20)
    assert int(ana(dut).bias_en.value) == 1
    while (dut.uio_out.value.to_unsigned() >> 2) & 1:
        await RisingEdge(dut.clk)
    await ClockCycles(dut.clk, 2)
    assert int(ana(dut).bias_en.value) == 0
    await wr(dut, 0x00, 0x01)                                    # force on
    assert int(ana(dut).bias_en.value) == 1


@cocotb.test()
async def t03_thinking_machines(dut):
    """Alammar's 'Thinking Machines' figure: q1.k1 = 112, q1.k2 = 96, /sqrt(64) -> 14, 12 -> 0.88 / 0.12.
    Shift invariance: the host shifts the top score to X_MAX = 18 -> x = [18, 16]; two masked tokens at x = 0."""
    await reset(dut)
    k = [[255] * 4, [227, 227, 226, 226], [0] * 4, [0] * 4]       # x1 = 18*906/1020 = 15.99
    load_keys(dut, k); await load_qk(dut, [15] * 4, [15] * 4)
    got = await run_pass(dut)
    exp = codes(scores([15] * 4, k, [15] * 4))
    dut._log.info(f"Thinking Machines: codes {got}, golden {exp}, shares {[round(c/255,3) for c in got]}")
    assert got == exp
    assert abs(got[0] / 255 - 0.88) < 0.01 and abs(got[1] / 255 - 0.12) < 0.01
    assert got[2] == 0 and got[3] == 0, "masked tokens must read 0 (max x > ln 510)"


@cocotb.test()
async def t04_masking_needs_shift(dut):
    """Without the host shift the masked tokens leak (Lite C finding): x=[3,2,0,0] -> masked codes ~9."""
    await reset(dut)
    k = [[43, 42, 42, 43], [28, 28, 29, 28], [0] * 4, [0] * 4]
    load_keys(dut, k); await load_qk(dut, [15] * 4, [15] * 4)
    got = await run_pass(dut)
    exp = codes(scores([15] * 4, k, [15] * 4))
    dut._log.info(f"unshifted: {got} golden {exp}")
    assert got == exp and got[2] > 0


@cocotb.test()
async def t05_random_vectors(dut):
    await reset(dut)
    rnd = random.Random(11)
    for n in range(25):
        q = [rnd.randrange(16) for _ in range(4)]
        ks = [rnd.randrange(16) for _ in range(4)]
        k = [[rnd.randrange(256) for _ in range(4)] for _ in range(4)]
        load_keys(dut, k); await load_qk(dut, q, ks)
        got = await run_pass(dut)
        exp = codes(scores(q, k, ks))
        assert max(abs(a - b) for a, b in zip(got, exp)) <= 1, (n, got, exp)
        assert 252 <= sum(got) <= 258


@cocotb.test()
async def t06_settle_window(dut):
    """A window shorter than the analog settling gives wrong codes; the default (1000 cycles = 50 us) is exact."""
    await reset(dut)
    k = [[255] * 4, [227, 227, 226, 226], [0] * 4, [0] * 4]
    load_keys(dut, k); await load_qk(dut, [15] * 4, [15] * 4)
    exp = codes(scores([15] * 4, k, [15] * 4))
    await wr(dut, 0x05, 20); await wr(dut, 0x06, 0); await wr(dut, 0x07, 1)
    short = await run_pass(dut)
    await wr(dut, 0x05, 1000 & 0xFF); await wr(dut, 0x06, 1000 >> 8); await wr(dut, 0x07, 30)
    full = await run_pass(dut)
    dut._log.info(f"short window {short}, full window {full}, golden {exp}")
    assert short != exp and full == exp


@cocotb.test()
async def t07_write_lockout(dut):
    await reset(dut)
    await wr(dut, 0x09, 0x20 | 7)
    assert int(ana(dut).wsel_en.value) == 1 and int(ana(dut).wsel.value) == (1 << 7)
    await wr(dut, 0x00, 0x06)
    await ClockCycles(dut.clk, 30)
    assert int(ana(dut).wsel_en.value) == 0, "weight write switch must open during a pass"


@cocotb.test()
async def t08_start_pin_and_out_sel(dut):
    await reset(dut)
    k = [[255] * 4, [227, 227, 226, 226], [0] * 4, [0] * 4]
    load_keys(dut, k); await load_qk(dut, [15] * 4, [15] * 4)
    ui = dut.ui_in.value.to_unsigned()
    dut.ui_in.value = ui | 0x08
    await ClockCycles(dut.clk, 4)
    dut.ui_in.value = ui
    for _ in range(200 * 20):                                    # poll VALID (uio_out[1])
        await RisingEdge(dut.clk)
        if (dut.uio_out.value.to_unsigned() >> 1) & 1:
            break
    else:
        raise AssertionError('VALID never rose')
    exp = codes(scores([15] * 4, k, [15] * 4))
    for j in range(4):
        await wr(dut, 0x0B, j)
        await ClockCycles(dut.clk, 2)
        assert dut.uo_out.value.to_unsigned() == exp[j]


@cocotb.test()
async def t09_ss_sgd_trims_row_gain(dut):
    """Rev-3 sign-sign rule on chip: rows 1..3 carry gain errors; targets are golden codes.
    Row 0 must never be pumped; equal codes give no pulse; the median code error must fall."""
    await reset(dut)
    a = ana(dut)
    a.gam_ppm1.value = 40000; a.gam_ppm2.value = -35000; a.gam_ppm3.value = 25000
    rnd = random.Random(5)
    cal = []
    for _ in range(12):
        q = [rnd.randrange(8, 16) for _ in range(4)]
        k = [[rnd.randrange(80, 256) for _ in range(4)] for _ in range(4)]
        cal.append((q, k, codes(scores(q, k, [15] * 4))))

    async def epoch(update):
        errs = []
        for q, k, tgt in cal:
            load_keys(dut, k); await load_qk(dut, q, [15] * 4)
            for j in range(4):
                await wr(dut, 0x0C + j, tgt[j])
            got = await run_pass(dut, cal=update)
            errs.append(sum(abs(g - t) for g, t in zip(got, tgt)) / 4)
            if update:
                upd = await rd(dut, 0x16)
                assert upd & 0x11 == 0, "row 0 pinned"
                for j in range(1, 4):
                    up, dn = (upd >> j) & 1, (upd >> (4 + j)) & 1
                    assert up == (got[j] < tgt[j]) and dn == (got[j] > tgt[j])
        return sorted(errs)[len(errs) // 2]

    await wr(dut, 0x0A, 4)                                       # 4-clock pulses (eta ~ 2 %)
    e0 = await epoch(False)
    for _ in range(6):
        await epoch(True)
    e1 = await epoch(False)
    dut._log.info(f"SS-SGD median MAE {e0:.2f} -> {e1:.2f} LSB; trims (mV) "
                  f"{float(a.vw1.value):.2f} {float(a.vw2.value):.2f} {float(a.vw3.value):.2f}")
    assert e1 < e0 and float(a.vw0.value) == 0.0
    assert float(a.vw1.value) < 0 < float(a.vw2.value)          # trims oppose the injected errors


@cocotb.test()
async def t10_hvif_break_before_make_and_chain(dut):
    """6x2 interface: the cell-select address only moves while its enable is low, and the 3.3 V chain reproduces
    the q/k registers before a pass starts."""
    await reset(dut)
    dig = dut.user_project.u_dig if hasattr(dut, "user_project") else dut
    bad = []

    async def watch():
        pa, pe = None, None
        while True:
            await RisingEdge(dut.clk)
            await Timer(1, "ns")
            a, e = int(dig.wsel_a.value), int(dig.wsel_e.value)
            if pa is not None and a != pa and (pe == 1 or e == 1):
                bad.append((pa, a, pe, e))
            pa, pe = a, e
    w = cocotb.start_soon(watch())
    for cell in (3, 17, 4, 19, 0, 25, 8):
        await wr(dut, 0x09, 0x20 | cell)
        await ClockCycles(dut.clk, 6)
        want = (1 << cell) if cell < 20 else 0
        assert int(ana(dut).wsel.value) == want, (cell, hex(int(ana(dut).wsel.value)))
    w.kill()
    assert not bad, f"address moved while enabled: {bad[:4]}"
    await wr(dut, 0x09, 0x00)
    for v in ((0x12, 0x34, 0x56, 0x78), (0xA5, 0x5A, 0xFF, 0x01)):
        for a, d in zip((0x01, 0x02, 0x03, 0x04), v):
            await wr(dut, a, d)
        await wr(dut, 0x00, 0x06)                             # start: waits for the chain (32 bits x 3 clocks)
        await ClockCycles(dut.clk, 150)
        q = v[0] | (v[1] << 8)
        k = v[2] | (v[3] << 8)
        assert int(ana(dut).q_code.value) == q and int(ana(dut).k_code.value) == k, \
            (hex(int(ana(dut).q_code.value)), hex(int(ana(dut).k_code.value)))
        while int(dut.uio_out.value) & 0x4:                  # BUSY
            await ClockCycles(dut.clk, 50)
