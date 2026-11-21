set_thread_count [exec nproc]
read_lef /home/claude/ext/pdk/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__min.tlef
read_liberty /home/claude/ext/pdk/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_lef /home/claude/rt5w_sky/tt/layout/lef/rt5w_array.lef
read_lef /home/claude/rt5w_sky/tt/layout/lef/rt5w_bias.lef
read_lef /home/claude/rt5w_sky/tt/layout/lef/rt5w_digital.lef
read_lef /home/claude/rt5w_sky/tt/layout/lef/rt5w_kscale.lef
read_lef /home/claude/rt5w_sky/tt/layout/lef/rt5w_lsbank.lef
read_lef /home/claude/rt5w_sky/tt/layout/lef/rt5w_lsdn.lef
read_lef /home/claude/rt5w_sky/tt/layout/lef/rt5w_readout.lef
read_lef /home/claude/rt5w_sky/tt/layout/lef/rt5w_softmax.lef
read_lef /home/claude/rt5w_sky/tt/layout/lef/rt5w_vbbuf.lef
read_verilog /home/claude/rt5w_sky/tt/layout/top/tt_um_rt5w_attn.v
link_design tt_um_rt5w_attn
read_def -floorplan_initialize /home/claude/ext/tt/tt-support-tools/tech/sky130A/def/analog/tt_analog_6x2_3v3.def
set block [ord::get_db_block]
set tech [ord::get_db_tech]
make_tracks li1 -x_offset 0.23 -x_pitch 0.46 -y_offset 0.17 -y_pitch 0.34
make_tracks met1 -x_offset 0.17 -x_pitch 0.34 -y_offset 0.17 -y_pitch 0.34
make_tracks met2 -x_offset 0.115 -x_pitch 0.23 -y_offset 0.115 -y_pitch 0.23
make_tracks met3 -x_offset 0.17 -x_pitch 0.34 -y_offset 0.17 -y_pitch 0.34
make_tracks met4 -x_offset 0.23 -x_pitch 0.46 -y_offset 0.23 -y_pitch 0.46
set i [$block findInst xarr]
$i setLocation [expr int(1.84 * 1000)] [expr int(6.0 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xbank]
$i setLocation [expr int(2.0 * 1000)] [expr int(152.3 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xdig]
$i setLocation [expr int(2.0 * 1000)] [expr int(172.76 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xbias]
$i setLocation [expr int(554.0 * 1000)] [expr int(3.0 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xk0]
$i setLocation [expr int(554.0 * 1000)] [expr int(178.0 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xk1]
$i setLocation [expr int(627.0 * 1000)] [expr int(178.0 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xro]
$i setLocation [expr int(703.0 * 1000)] [expr int(3.0 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xvb]
$i setLocation [expr int(703.0 * 1000)] [expr int(133.0 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xk2]
$i setLocation [expr int(703.0 * 1000)] [expr int(178.0 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xk3]
$i setLocation [expr int(776.0 * 1000)] [expr int(178.0 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xsm]
$i setLocation [expr int(905.0 * 1000)] [expr int(4.0 * 1000)]
$i setPlacementStatus FIRM
set i [$block findInst xlsdn]
$i setLocation [expr int(875.0 * 1000)] [expr int(140.0 * 1000)]
$i setPlacementStatus FIRM
set m4 [$tech findLayer met4]
set bt [$block findBTerm VAPWR]
if {$bt eq "NULL"} { set n [$block findNet VAPWR]; set bt [odb::dbBTerm_create $n VAPWR] }
set bp [odb::dbBPin_create $bt]
odb::dbBox_create $bp $m4 [expr int(545.5 * 1000)] 5000 [expr int((545.5 + 2.0) * 1000)] 220760
$bp setPlacementStatus FIRM
set bt [$block findBTerm VGND]
if {$bt eq "NULL"} { set n [$block findNet VGND]; set bt [odb::dbBTerm_create $n VGND] }
set bp [odb::dbBPin_create $bt]
odb::dbBox_create $bp $m4 [expr int(548.5 * 1000)] 5000 [expr int((548.5 + 2.0) * 1000)] 220760
$bp setPlacementStatus FIRM
set bt [$block findBTerm VDPWR]
if {$bt eq "NULL"} { set n [$block findNet VDPWR]; set bt [odb::dbBTerm_create $n VDPWR] }
set bp [odb::dbBPin_create $bt]
odb::dbBox_create $bp $m4 [expr int(551.5 * 1000)] 5000 [expr int((551.5 + 2.0) * 1000)] 220760
$bp setPlacementStatus FIRM
create_ndr -name PWR -spacing {met1 0.14 met2 0.14 met3 0.3 met4 0.3} -width {met1 0.5 met2 0.5 met3 1.0 met4 1.0}
# foreach n {VAPWR VGND VDPWR} { assign_ndr -ndr PWR -net $n }   ;# off: see notes
set_routing_layers -signal met1-met4
pin_access -bottom_routing_layer met1 -top_routing_layer met4 -verbose 3
set_global_routing_layer_adjustment met1-met4 0.3
set_global_routing_layer_adjustment met5 1.0
set_routing_layers -signal met1-met4 -clock met1-met4
