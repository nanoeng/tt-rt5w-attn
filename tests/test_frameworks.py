"""Regression for the emulation and HIL frameworks (pytest -q tests/).
Every backend must run all Illustrated-Transformer examples; the RTL path is covered by cocotb (make rtl)."""
import os
import subprocess
import sys
import time

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from rt5w.backends import get_backend, HilBackend     # noqa: E402
from rt5w.illustrated import run_all, calibrate       # noqa: E402

TOL = dict(ideal=0.02, behav=0.02, **{"hil-sim": 0.02}, ngspice=0.03, pyspice=0.03)


@pytest.mark.parametrize("name", ["ideal", "behav", "hil-sim", "ngspice", "pyspice"])
def test_examples_nominal(name):
    be = get_backend(name)
    for r in run_all(be):
        assert r["argmax_ok"], r
        assert r["max_abs_err"] <= TOL[name], r


def test_toolchain_present():
    """Every simulator and library the frameworks rely on is installed and importable."""
    import shutil
    for exe in ("ngspice", "iverilog", "vvp", "verilator", "yosys", "cocotb-config", "micropython"):
        assert shutil.which(exe), exe
    import cocotb, cocotb_tools, PySpice, staliro, rtamt  # noqa: F401,E401
    from importlib.metadata import version
    assert version("psy-taliro").startswith("3."), version("psy-taliro")
    from PySpice.Spice.NgSpice.Shared import NgSpiceShared  # noqa: F401  (libngspice is found at import of an instance)


def test_falsify_engines_agree():
    """One softmax-core step transient: ngspice (CLI) and PySpice (libngspice) give the same STL robustness."""
    from rt5w import falsify as F
    a = F.evaluate([0, 0, 0, 0], [18, 16, 0, 0], 27, "tt", "ngspice")
    b = F.evaluate([0, 0, 0, 0], [18, 16, 0, 0], 27, "tt", "pyspice")
    for k in F.REQUIREMENTS:
        assert abs(a["rho"][k] - b["rho"][k]) <= 1e-4 * max(1.0, abs(a["rho"][k])), (k, a["rho"][k], b["rho"][k])
    assert a["rho"]["R3"] > 0                     # shares within 3 % of the golden softmax at readout


def test_falsify_campaign_smoke():
    """PSY-TaLiRo drives the SPICE model: a small UniformRandom campaign runs and reports every requirement."""
    from rt5w import falsify as F
    r = F.campaign("tt", "pyspice", budget=6, seed=3, log=lambda *a: None)
    assert r["n"] == 6 and set(r["rho_min"]) == set(F.REQUIREMENTS)
    assert sorted(r["held"] + r["falsified"]) == sorted(F.REQUIREMENTS)
    assert r["rho_min"]["R3"] > 0


def test_cosim_transient_settles_to_operating_point():
    """Co-simulation solver: the bias-on transient of the array + softmax settles to the .op of the same netlist."""
    from rt5w import cosim as C
    st = C.Cosim().blank_state()
    st.update(q=[15] * 4, ks=[15] * 4, k=[[255] * 4, [227, 227, 226, 226], [0] * 4, [0] * 4])
    t, sh, vb = C.simulate(st, st, True, "tt", "pyspice", off=1e-2)
    op, vb_op = C.operating_point(st)
    assert max(abs(sh[-1][j] - op[j]) for j in range(4)) < 0.5 / 255
    assert abs(vb[-1] - vb_op) < 2e-3


def test_thinking_machines_numbers():
    r = run_all(get_backend("ideal"))[0]
    assert r["scores"] == [112.0, 96.0] and r["scaled"] == [14.0, 12.0]
    assert r["codes"] == [225, 30, 0, 0] and r["masked_slots_zero"]


def test_calibration_fixes_mismatched_die():
    be = get_backend("hil-sim", seed=3)
    hist = calibrate(be, epochs=6)
    assert hist[-1] < 0.35 * hist[0], hist


def test_micropython_firmware():
    mp = subprocess.run(["micropython", "hil/tests/mp_selftest.py"], cwd=ROOT, capture_output=True, text=True)
    assert "SELFTEST PASS" in mp.stdout, mp.stdout + mp.stderr


def test_serial_hil_over_pty(tmp_path):
    link = str(tmp_path / "tty")
    p = subprocess.Popen([sys.executable, "hil/tests/fake_board.py", "--link", link], cwd=ROOT,
                         stdout=subprocess.PIPE, text=True)
    try:
        p.stdout.readline()
        be = HilBackend(link)
        assert be._cmd("VBCAL").startswith("OK")
        for r in run_all(be):
            assert r["argmax_ok"] and r["max_abs_err"] <= 0.02, r
        be.close()
    finally:
        p.kill()


def test_serial_hil_over_rfc2217(tmp_path):
    """Board (fake, on a pty) -> RFC 2217 bridge on TCP -> HIL backend via rfc2217:// URL (the container path)."""
    import socket
    link = str(tmp_path / "tty")
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    board = subprocess.Popen([sys.executable, "hil/tests/fake_board.py", "--link", link], cwd=ROOT,
                             stdout=subprocess.PIPE, text=True)
    board.stdout.readline()
    bridge = subprocess.Popen([sys.executable, "hil/tools/rfc2217_bridge.py", link, "-p", str(port), "--bind", "127.0.0.1"],
                              cwd=ROOT, stdout=subprocess.PIPE, text=True)
    try:
        bridge.stdout.readline()
        be = HilBackend(f"rfc2217://127.0.0.1:{port}")
        r = run_all(be)[0]
        assert r["codes"] == [225, 30, 0, 0], r
        be.close()
    finally:
        bridge.kill()
        board.kill()
