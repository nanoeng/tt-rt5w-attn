# RT5W verification entry points
#   make emu        Python emulation: ideal, behavioural, HIL-sim, ngspice, PySpice + MicroPython + pty HIL (pytest)
#   make rtl        cocotb: unit tests + Illustrated-Transformer firmware-in-the-loop on Icarus
#   make rtl-vl     the same on Verilator (needs >= 5.036 on PATH)
#   make gl         gate-level cocotb (Icarus, gf180 cells)
#   make waves      FST traces + GTKWave screenshots in waves/
#   make corners    Illustrated examples on ngspice at ss/-40 C and ff/125 C
#   make falsify    PSY-TaLiRo + RTAMT on the transistor-level softmax core (ENGINE=ngspice|pyspice, CORNERS=tt,ss,...)
#   make falsify-rtl / falsify-rtl-vl   PSY-TaLiRo on the RTL under cocotb (Icarus / Verilator)
#   make cosim-trace        instrumented co-sim of E1-E7 -> test/cosim_trace.json + examples/cosim_report.py
#   make cosim / cosim-vl   RTL (Icarus / Verilator) + analog macro in ngspice/PySpice, co-simulated under cocotb
#                           (COSIM_ENGINE=pyspice|ngspice COSIM_CORNER COSIM_TEMP COSIM_BIAS_OFF COSIM_WAKE COSIM_FULL=1)
#   make hil PORT=/dev/ttyACM0   examples on the TT demo board (any pyserial URL, e.g. rfc2217://host:4000)
#   make image / make sif         Docker image rt5w-tt / Apptainer rt5w.sif (see container/README.md)
# Physical design (pixi environments 'pd', 'layout', 'openroad'; PDK_ROOT / PDK = gf180mcuD):
#   make capture        xschem schematics from design/blocks/*.py: .sch/.sym, netlists, connectivity check, SVGs
#   make sims-analog    schematic testbenches vs the Python model (bias, IDAC, key cell, softmax, readout,
#                       V_B buffer, full chain) -> results/analog_sims.txt
#   make layout-blocks  PDK-pcell layouts of every leaf block (two-row + channel router) -> layout/gds/*.gds/.json
#   make drc-blocks / lvs-blocks   magic DRC and magic+netgen LVS of every block -> layout/gds/*.drc.txt, layout/lvs/
#   make harden         digital macro: yosys + OpenROAD + KLayout -> layout/gds/rt5w_ctrl.gds/.json
#   make floorplan      floorplanner page (layout/floorplan/floorplanner.html) + default/study floorplans
#   make layout-top FP=layout/floorplan/floorplan.json   top assembly + maze routing -> layout/gds/rt5w_analog.gds
#   make drc-top / lvs-top          the same checks on the assembled top
#   make verify-pd      all of the above in order, summary in results/pd_summary.md
PORT ?= /dev/ttyACM0
ENGINE ?= ngspice
CORNERS ?= tt
BUDGET ?= 40
ANNEAL ?= 0
.PHONY: emu rtl rtl-vl gl waves corners falsify falsify-rtl falsify-rtl-vl cosim cosim-vl cosim-trace hil image sif
.PHONY: capture sims-analog layout-blocks drc-blocks lvs-blocks harden floorplan layout-top drc-top lvs-top verify-pd
PIXI ?= pixi
export PDK_ROOT ?= /home/claude/ext/pdk
export PDK ?= sky130A
FP ?= layout/floorplan/floorplan.json
BLOCKS = rt5w_idac4 rt5w_coldiode rt5w_keycell rt5w_trimcell rt5w_pumpinv rt5w_kscale rt5w_softmax rt5w_bias rt5w_readout rt5w_vbbuf
emu:
	python3 -m pytest -q tests/
rtl:
	$(MAKE) -C test && $(MAKE) -C test -f Makefile.illustrated
rtl-vl:
	$(MAKE) -C test SIM=verilator && $(MAKE) -C test -f Makefile.illustrated SIM=verilator
gl:
	$(MAKE) -C test GATES=yes
waves:
	$(MAKE) -C test -f Makefile.illustrated WAVES=1 COCOTB_TEST_FILTER=it_e1 && cp test/sim_build/illustrated_icarus/tb.fst waves/illustrated_icarus.fst
	$(MAKE) -C test -f Makefile.illustrated SIM=verilator WAVES=1 COCOTB_TEST_FILTER=it_e1
	cd waves && GRAB=$$PWD/illustrated_icarus.png xvfb-run -a gtkwave -S rt5w_illustrated.tcl illustrated_icarus.fst
corners:
	python3 examples/illustrated_transformer.py --backend ngspice --corner ss --temp -40
	python3 examples/illustrated_transformer.py --backend ngspice --corner ff --temp 125
falsify:
	python3 examples/falsify_softmax.py --engine $(ENGINE) --corners $(CORNERS) --budget $(BUDGET) --anneal $(ANNEAL) --json sim/results/falsify_$(ENGINE).json
falsify-rtl:
	$(MAKE) -C test -f Makefile.falsify
falsify-rtl-vl:
	$(MAKE) -C test -f Makefile.falsify SIM=verilator
cosim:
	$(MAKE) -C test -f Makefile.cosim
cosim-vl:
	$(MAKE) -C test -f Makefile.cosim SIM=verilator
cosim-trace:
	$(MAKE) -C test -f Makefile.cosim COCOTB_TEST_MODULES=test_cosim_trace SIM_BUILD=sim_build/cosim_trace_$(or $(SIM),icarus)
	python3 examples/cosim_report.py test/cosim_trace.json
hil:
	python3 examples/illustrated_transformer.py --backend hil --port $(PORT) --calibrate 8
image:
	docker build -f container/Dockerfile -t rt5w-tt .
sif: image
	docker save rt5w-tt -o rt5w-tt.tar
	sed -e 's|^Bootstrap: docker$$|Bootstrap: docker-archive|' -e 's|^From: .*|From: rt5w-tt.tar|' container/rt5w.def > .rt5w-local.def
	apptainer build rt5w.sif .rt5w-local.def && rm -f rt5w-tt.tar .rt5w-local.def

# ------------------------------------------------------------------------------------------- physical design
capture:
	$(PIXI) run -e pd python design/capture.py
sims-analog:
	$(PIXI) run -e pd python design/verify.py sims
layout-blocks:
	USER=$${USER:-rt5w} $(PIXI) run -e layout python design/layout/blockgen.py
drc-blocks:
	for b in $(BLOCKS) rt5w_ctrl; do $(PIXI) run -e pd python design/layout/drc.py layout/gds/$$b.gds $$b; done
lvs-blocks:
	$(PIXI) run -e pd python design/layout/lvs.py $(BLOCKS)
harden:
	cd design/digital && PATH=$(CURDIR)/.pixi/envs/openroad/bin:$$PATH $(PIXI) run --manifest-path ../../pixi.toml -e layout python harden.py
floorplan:
	python3 design/layout/floorplan.py
layout-top:
	USER=$${USER:-rt5w} $(PIXI) run -e layout python design/layout/toplevel.py $(FP)
drc-top:
	$(PIXI) run -e pd python design/layout/drc.py layout/gds/rt5w_analog.gds rt5w_analog
lvs-top:
	$(PIXI) run -e pd python design/layout/lvs.py rt5w_analog
verify-pd:
	$(PIXI) run -e pd python design/verify.py all
