# magic batch DRC (gf180mcuD tech, full rule style):
#   PDK_ROOT=... magic -dnull -noconsole -rcfile <pdk>/libs.tech/magic/gf180mcuD.magicrc magic_drc.tcl <gds> <top> <report>
set gds [lindex $argv end-2]
set top [lindex $argv end-1]
set rpt [lindex $argv end]
# as the TinyTapeout precheck (tt-support-tools/precheck/magic_drc.tcl): mask hints on, euclidean distances
gds maskhints yes
gds read $gds
load $top
select top cell
drc on
drc euclidean on
drc style drc(full)
drc check
drc catchup
set n [drc list count total]
set fp [open $rpt w]
puts $fp "TOTAL $n"
puts $fp "SCALE [cif scale out]"
foreach {why boxes} [drc listall why] {
    puts $fp "[llength $boxes]\t$why\t[lrange $boxes 0 2]"
}
close $fp
quit -noprompt
