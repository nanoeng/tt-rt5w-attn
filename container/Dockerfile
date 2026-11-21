# RT5W TinyTapeout toolchain image: ngspice/libngspice + gf180mcuD models, Icarus, Verilator, Yosys, cocotb, PySpice,
# PSY-TaLiRo + RTAMT (STL falsification), MicroPython, mpremote, GTKWave (headless) -- all from the pixi lockfile,
# so every host gets the same versions.
#
#   docker build -f container/Dockerfile -t rt5w-tt .
#   docker run --rm rt5w-tt make emu                        # tests baked into the image
#   docker run --rm -v "$PWD":/work -w /work rt5w-tt make rtl   # your checkout, the image's tools
#
# Behind a TLS-intercepting proxy, pass its CA as a build secret (never baked into the image):
#   docker build --secret id=ca,src=/path/to/ca.crt --build-arg HTTPS_PROXY=... -f container/Dockerfile .
# Air-gapped / no Docker Hub: build any Ubuntu 24.04 rootfs locally and pass --build-arg BASE=<that image>.
ARG BASE=ubuntu:24.04
FROM ${BASE}

ARG PIXI_VERSION=0.84.2
ARG HTTPS_PROXY
ARG https_proxy
ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 PIXI_HOME=/opt/pixi PATH=/opt/pixi/bin:$PATH

# OS layer: only what conda-forge does not provide (TLS roots, git for the PDK fetch, a virtual X server for GTKWave)
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl git xvfb xauth \
 && rm -rf /var/lib/apt/lists/*

# pixi itself (static binary, pinned)
RUN --mount=type=secret,id=ca,required=false \
    if [ -f /run/secrets/ca ]; then export CURL_CA_BUNDLE=/run/secrets/ca; fi; \
    mkdir -p /opt/pixi/bin \
 && curl -fsSL "https://github.com/prefix-dev/pixi/releases/download/v${PIXI_VERSION}/pixi-x86_64-unknown-linux-musl.tar.gz" \
    | tar xz -C /opt/pixi/bin \
 && pixi --version

# toolchain from the lockfile (layer is reused until pixi.toml / pixi.lock change)
WORKDIR /opt/rt5w
COPY pixi.toml pixi.lock pixi_pypi_map.json ./
COPY container/make_env_sh.py container/make_env_sh.py
RUN --mount=type=secret,id=ca,required=false \
    if [ -f /run/secrets/ca ]; then export SSL_CERT_FILE=/run/secrets/ca GIT_SSL_CAINFO=/run/secrets/ca; fi; \
    pixi install --locked \
 && pixi shell-hook --locked --json > /tmp/hook.json \
 && .pixi/envs/default/bin/python container/make_env_sh.py < /tmp/hook.json > /opt/rt5w/env.sh \
 && rm /tmp/hook.json && pixi clean cache -y

# gf180mcuD device models at the pinned commit
COPY scripts/fetch_pdk.sh scripts/fetch_pdk.sh
RUN --mount=type=secret,id=ca,required=false \
    if [ -f /run/secrets/ca ]; then export GIT_SSL_CAINFO=/run/secrets/ca; fi; \
    RT5W_PDK=/opt/rt5w/.pdk sh scripts/fetch_pdk.sh

# the project itself (tests run against this copy by default; mount your checkout over /work to use the tools on it)
COPY . /opt/rt5w/repo
COPY container/entrypoint.sh /usr/local/bin/rt5w-entry
RUN chmod +x /usr/local/bin/rt5w-entry && mkdir -p /work
WORKDIR /opt/rt5w/repo
ENV RT5W_PDK=/opt/rt5w/.pdk GF180_MODELS=/opt/rt5w/.pdk/gf180mcu_fd_pr/models/ngspice
ENTRYPOINT ["/usr/local/bin/rt5w-entry"]
CMD ["bash"]
