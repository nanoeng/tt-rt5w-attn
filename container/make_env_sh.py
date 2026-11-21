#!/usr/bin/env python3
"""Turn `pixi shell-hook --json` into a POSIX env file (plain `export K='V'` lines).
Unlike the bash hook it sources no package activation/completion scripts, so it works in sh/dash (Apptainer's
%environment), bash, zsh and VS Code terminals alike."""
import json
import shlex
import sys

d = json.load(sys.stdin)
lines = ["# generated from `pixi shell-hook --json` at image build time"]
for k, v in sorted(d["environment_variables"].items()):
    if k in ("PS1", "SHLVL", "_"):
        continue
    lines.append(f"export {k}={shlex.quote(v)}")
print("\n".join(lines))
