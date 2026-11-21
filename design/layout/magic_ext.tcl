# magic extraction for LVS: magic -dnull -noconsole -rcfile <magicrc> magic_ext.tcl <gds> <top> <out.spice>
set gds [lindex $argv end-2]
set top [lindex $argv end-1]
set out [lindex $argv end]
gds read $gds
load $top
select top cell
# sky130: GDS text labels are plain labels; make them ports so the extracted top subckt has its pin list
port makeall
extract path [file dirname $out]
extract do local
extract all
ext2spice lvs
ext2spice -o $out
quit -noprompt
