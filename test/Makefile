# cocotb Makefile (TinyTapeout layout). RTL: make [SIM=verilator] ; gate-level: make GATES=yes [SIM=verilator]
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(CURDIR)/../src
PROJECT_SOURCES = rt5w_digital.v rt5w_ctrl.v rt5w_hvif.v
ifneq ($(GATES),yes)
SIM_BUILD = sim_build/rtl_$(SIM)
VERILOG_SOURCES += $(CURDIR)/tt_um_rt5w_attn_beh.v $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
else
SIM_BUILD = sim_build/gl_$(SIM)
COMPILE_ARGS += -DGL_TEST -DFUNCTIONAL -DUNIT_DELAY=\#1
# post-route netlist of the hardened digital macro (design/digital/harden.py) + the PDK cell models
SC_VLOG ?= $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog
VERILOG_SOURCES += $(CURDIR)/tt_um_rt5w_attn_beh.v $(SRC_DIR)/rt5w_hvif.v $(CURDIR)/../design/digital/build/rt5w_digital.pnl.v \
                   $(CURDIR)/gl_nettype.v $(SC_VLOG)/primitives.v $(SC_VLOG)/sky130_fd_sc_hd.v
endif
VERILOG_SOURCES += $(CURDIR)/rt5w_analog_beh.v $(CURDIR)/tb.v
ifeq ($(SIM),icarus)
COMPILE_ARGS += -g2012
endif
ifeq ($(SIM),verilator)
EXTRA_ARGS += --timing -Wno-fatal -Wno-lint -Wno-style -Wno-REALCVT -Wno-MULTIDRIVEN
endif
TOPLEVEL = tb
COCOTB_TEST_MODULES = test_rt5w
include $(shell cocotb-config --makefiles)/Makefile.sim
