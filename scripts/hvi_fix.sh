#!/bin/sh
# HVI clean-up of the merged chip for magic >= 8.3.568 (TT precheck CI for ttsky26e), 21 Nov 2026.
# 1) magic GDS round trip without mask hints -> HVI exactly as magic regenerates it, per cell;
# 2) scripts/hvi_from_magic.py puts that HVI into the merged GDS (all other layers unchanged) and adds the
#    KLayout-FEOL closings (hvi.2a, MR_nwell.CON.1) per cell and flat at the top.
# usage: scripts/hvi_fix.sh in.gds out.gds   (MAGIC=path/to/magic 8.3.568 recommended; PDK_ROOT set)
set -e
IN=$(readlink -f "$1"); OUT=$(readlink -f "$2"); TMP=$(mktemp -d)
MAGIC=${MAGIC:-magic}
cat > "$TMP/rw.tcl" <<TCL
gds maskhints no
gds read $IN
load tt_um_rt5w_attn
gds write $TMP/rw.gds
quit -noprompt
TCL
"$MAGIC" -noconsole -dnull -rcfile "$PDK_ROOT/sky130A/libs.tech/magic/sky130A.magicrc" "$TMP/rw.tcl" > "$TMP/rw.log" 2>&1
python "$(dirname "$0")/hvi_from_magic.py" "$IN" "$TMP/rw.gds" "$OUT"
rm -rf "$TMP"
