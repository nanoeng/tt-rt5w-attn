# MicroPython entry point: line protocol over USB serial (see rt5w_fw.py for the command set).
import sys
from rt5w_fw import Rt5wFirmware, Protocol
from board_tt import TTBoard

proto = Protocol(Rt5wFirmware(TTBoard()))
print("RT5W HIL ready")
while True:
    line = sys.stdin.readline()
    if line:
        print(proto.handle(line))
