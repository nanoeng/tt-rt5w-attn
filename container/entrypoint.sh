#!/bin/bash
# Activate the baked pixi environment, then run the command (default: bash).
# shellcheck disable=SC1091
. /opt/rt5w/env.sh
export RT5W_PDK=/opt/rt5w/.pdk GF180_MODELS=/opt/rt5w/.pdk/gf180mcu_fd_pr/models/ngspice
exec "$@"
