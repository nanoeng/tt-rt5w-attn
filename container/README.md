# Portable toolchain: pixi lockfile, Docker/Podman image, Dev Container, Apptainer

One lockfile (`pixi.lock`) defines every tool version. Every other route is built from it:

| Route | Use it for | Command |
|---|---|---|
| **pixi, native** (no container) | Linux x86-64, Intel Macs, Apple Silicon under Rosetta | `pixi run emu` (also `rtl`, `rtl-vl`, `gl`, `corners`) |
| **Docker / Podman image** | any host, CI | `make image` and then `docker run --rm rt5w-tt make emu` |
| **Dev Container** | VS Code / GitHub Codespaces, teaching | "Reopen in Container" (uses `.devcontainer/devcontainer.json`) |
| **Apptainer `.sif`** | HPC (e.g. TACC), no root at run time | `make sif` and then `apptainer exec rt5w.sif make emu` |

## Locked versions (pixi.lock, conda-forge, 18 Nov 2026)

ngspice-41 + libngspice, Icarus Verilog 13.0, Verilator 5.054, Yosys 0.71, cocotb 2.1.0, PySpice 1.5 (PyPI wheel), PSY-TaLiRo 3.2.0 (GitHub tag v3.2.0, pinned by commit), RTAMT 0.3.5, pyserial 3.5, mpremote 1.29, MicroPython 1.29, GTKWave 3.3.121 (linux-64), Python 3.12.

gf180mcuD models: `google/globalfoundries-pdk-libs-gf180mcu_fd_pr` at commit `9f992d5a` (`scripts/fetch_pdk.sh`).

Changes from the hand-installed host this project used until now:
- ngspice 42 → 41;
- Icarus 12 → 13;
- Verilator 5.040 (built from source) → 5.054;
- Yosys 0.33 → 0.71.

Every suite passes on the locked versions.

## Platform notes

- **Platforms:** `linux-64` and `osx-64` only. conda-forge has no cocotb, Icarus, ngspice or Yosys builds for `linux-aarch64` or `osx-arm64` (checked Nov 2026). Apple Silicon runs the `osx-64` environment under Rosetta 2, or the amd64 image under Rosetta in Docker Desktop / OrbStack.
- **cocotb version string:** the conda-forge build reports `cocotb.__version__ == "0.0.0"` (a packaging quirk); it is the 2.1.0 package and works.
- **PSY-TaLiRo:** PyPI stops at 1.0.0, which does not import on numpy 2 (`np.float_`). v3.2.0 supports numpy ≥ 2 but is only on GitHub, so `pixi.toml` pins the v3.2.0 release commit; the lockfile records it, and building the image needs github.com once.
- **PySpice:** comes from PyPI (the conda-forge build stops at Python 3.10). `pixi_pypi_map.json` replaces pixi's online conda→PyPI name map, so locking works where `conda-mapping.prefix.dev` is blocked.
- **`env.sh`:** the image activates its environment through `/opt/rt5w/env.sh`, plain `export` lines generated from `pixi shell-hook --json`. It works in sh/dash (Apptainer), bash, zsh and VS Code terminals.

## Building behind a proxy, or without Docker Hub

```sh
# TLS-intercepting proxy: pass its CA as a BuildKit secret (it is not stored in any layer)
docker build --network host --secret id=ca,src=/path/ca.crt --build-arg HTTPS_PROXY=$HTTPS_PROXY -f container/Dockerfile -t rt5w-tt .
# no registry access: build an Ubuntu 24.04 base locally and point BASE at it
sudo debootstrap --variant=minbase --include=ca-certificates noble /tmp/noble http://archive.ubuntu.com/ubuntu/
sudo tar -C /tmp/noble -c . | docker import - localhost/ubuntu:24.04-debootstrap
docker build --build-arg BASE=localhost/ubuntu:24.04-debootstrap -f container/Dockerfile -t rt5w-tt .
```

## Hardware in the loop from a container or VM

Keep the TT demo board on the host and serve it over RFC 2217:

```sh
python3 hil/tools/rfc2217_bridge.py /dev/ttyACM0 -p 4000            # on the host (or: pixi run rfc2217 /dev/ttyACM0)
docker run --rm --add-host=host.docker.internal:host-gateway rt5w-tt \
  python examples/illustrated_transformer.py --backend hil --port rfc2217://host.docker.internal:4000
```

`--port` accepts any pyserial URL: `/dev/ttyACM0`, `COM5`, `rfc2217://host:port`, `socket://host:port`, `loop://`.

## Falsification (PSY-TaLiRo + RTAMT)

| What | Command | System under test |
|---|---|---|
| analog, ngspice CLI | `make falsify` (`ENGINE=ngspice CORNERS=tt,ss,ff,sf,fs BUDGET=40 ANNEAL=40`) | softmax core, transistor level, step transient |
| analog, PySpice | `make falsify ENGINE=pyspice` | same netlist on libngspice |
| digital, Icarus | `make falsify-rtl` (`FALSIFY_BUDGET=24`) | RTL + behavioural analog macro under cocotb |
| digital, Verilator | `make falsify-rtl-vl` | same |

In the image: `apptainer exec rt5w.sif make falsify` (or `docker run --rm rt5w-tt make falsify`).

## RTL + SPICE co-simulation

`make cosim` (Icarus) / `make cosim-vl` (Verilator): the controller RTL runs with `test/rt5w_analog_cosim.v`; cocotb
(`test/cosim_driver.py`) solves the array + softmax core in PySpice or ngspice (`rt5w/cosim.py`) at every analog event
(bias on, input change while biased) and feeds the shares and V_B back to the SAR comparator and the firmware's V_B
read. Tests in `test/test_cosim.py`. Options: `COSIM_ENGINE=pyspice|ngspice`, `COSIM_CORNER`, `COSIM_TEMP`,
`COSIM_BIAS_OFF` (bias while gated off, fraction of nominal; the gating switch is not drawn, default 1e-6),
`COSIM_WAKE` (register 0x07 used by the tests, default 255), `COSIM_FULL=1` (adds SS-SGD calibration).

## Waveforms

Mount your checkout (`-v "$PWD":/work -w /work`). The FST files land in your tree, so view them on the host in GTKWave or Surfer. For CI screenshots inside the image, `make waves` uses `xvfb-run`.
