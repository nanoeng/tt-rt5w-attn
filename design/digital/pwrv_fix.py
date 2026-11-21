"""Post-process OpenROAD's power-aware netlist for LVS: VPWR / VGND as module ports, and supply pins on every cell
that was inserted after the global connections (CTS buffers, fill / decap). Idempotent.
    python design/digital/pwrv_fix.py design/digital/build/rt5w_digital.pwr.v"""
import re
import sys

SUP = {"VGND": "VGND", "VNB": "VGND", "VPB": "VPWR", "VPWR": "VPWR"}


def fix(path):
    t = open(path).read()
    n = 0

    def cell(m):
        nonlocal n
        c, inst, body = m.group(1), m.group(2), m.group(3)
        used = set(re.findall(r"\.(\w+)\(", body))
        pins = ("VGND", "VPWR") if c.endswith("tapvpwrvgnd_1") else tuple(SUP)
        add = [f".{k}({SUP[k]})" for k in pins if k not in used]
        if not add:
            return m.group(0)
        n += 1
        return f"\n {c} {inst} ({body.rstrip()}{', ' if body.strip() else ''}{', '.join(add)});"

    t = re.sub(r"\n\s*(sky130_fd_sc_hd__\w+)\s+(\S+)\s*\((.*?)\);", cell, t, flags=re.S)
    m = re.match(r"(\s*module\s+\w+\s*\()(.*?)(\);)", t, re.S)
    ports = [p.strip() for p in m.group(2).split(",")]
    if "VPWR" not in ports:
        t = m.group(1) + "VPWR,\n    VGND,\n    " + m.group(2).lstrip() + m.group(3) + "\n inout VPWR;\n inout VGND;" + t[m.end():]
    open(path, "w").write(t)
    return n


if __name__ == "__main__":
    print("supply pins added on", fix(sys.argv[1]), "instances")
