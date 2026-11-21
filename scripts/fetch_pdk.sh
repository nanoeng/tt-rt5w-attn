#!/usr/bin/env sh
# Fetch the gf180mcuD primitive device models (ngspice) at the pinned commit into $RT5W_PDK (default: ./.pdk).
# Pinned to the commit every RT5W result was simulated with (2026-11-18).
set -eu
PDK_DIR="${RT5W_PDK:-$(cd "$(dirname "$0")/.." && pwd)/.pdk}"
REPO="https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_pr.git"
COMMIT="9f992d5a9186d1f7820c58f039c484ad35b2edea"
DEST="$PDK_DIR/gf180mcu_fd_pr"
if [ -f "$DEST/models/ngspice/sm141064.ngspice" ] && [ "$(git -C "$DEST" rev-parse HEAD 2>/dev/null)" = "$COMMIT" ]; then
  echo "gf180mcu_fd_pr already at $COMMIT"; exit 0
fi
rm -rf "$DEST"; mkdir -p "$PDK_DIR"
git init -q "$DEST"
git -C "$DEST" remote add origin "$REPO"
git -C "$DEST" fetch -q --depth 1 origin "$COMMIT"
git -C "$DEST" checkout -q FETCH_HEAD
git -C "$DEST" sparse-checkout set models/ngspice >/dev/null 2>&1 || true
echo "gf180mcu_fd_pr $COMMIT -> $DEST"
