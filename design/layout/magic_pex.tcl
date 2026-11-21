# C-only parasitic extraction (flat): magic -dnull -noconsole -rcfile <magicrc> magic_pex.tcl <gds> <cell> <out.spice>
set gds [lindex $argv end-2]
set top [lindex $argv end-1]
set out [lindex $argv end]
gds readonly true
gds read $gds
load $top
select top cell
port makeall
extract path [file dirname $out]
extract do local
extract do capacitance
extract do coupling
extract do resistance
extract all
ext2spice hierarchy off
ext2spice format ngspice
ext2spice scale off
ext2spice cthresh 0
ext2spice rthresh infinite
ext2spice subcircuit top on
ext2spice -o $out
quit -noprompt
