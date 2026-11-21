# TT demo board adapter (MicroPython, tt-micropython-firmware / ttboard SDK). Copy rt5w_fw.py, board_tt.py, config.py
# and main.py to the board (e.g. `mpremote cp *.py :`). The SDK names below match ttboard 2024-2026 releases
# (DemoBoard.get(), shuttle.<project>.enable(), ui_in/uo_out/uio_out, clock_project_PWM); check them against the
# firmware version on your board -- this is the only file that touches board APIs.
import time
from machine import Pin, ADC, I2C
from ttboard.demoboard import DemoBoard
from ttboard.mode import RPMode
import config as C


class TTBoard:
    def __init__(self):
        self.tt = DemoBoard.get()
        self.tt.mode = RPMode.ASIC_RP_CONTROL
        getattr(self.tt.shuttle, C.PROJECT).enable()
        self.tt.clock_project_PWM(C.CLK_HZ)
        self.tt.reset_project(True)
        time.sleep_ms(2)
        self.tt.reset_project(False)
        self.ui = 0x04                                    # CS_N high, SCK low
        self.tt.ui_in.value = self.ui
        self.adc = ADC(Pin(C.VB_ADC_PIN)) if C.VB_ADC_PIN is not None else None
        self.dac = I2C(C.I2C_ID, scl=Pin(C.I2C_SCL), sda=Pin(C.I2C_SDA), freq=400000) if C.VW_DAC == "mcp4725" else None

    # bit-banged SPI mode 0 on ui[0]=SCK, ui[1]=MOSI, ui[2]=CS_N; MISO on uio[0]. ~50 kHz: well under clk/8.
    def xfer16(self, word):
        tt, ui, rd = self.tt, self.ui & ~0x07, 0
        tt.ui_in.value = ui
        for b in range(15, -1, -1):
            m = ((word >> b) & 1) << 1
            tt.ui_in.value = ui | m
            tt.ui_in.value = ui | m | 1
            if b < 8:
                rd = (rd << 1) | (tt.uio_out.value & 1)
        tt.ui_in.value = ui | 0x04
        return rd

    def start(self, level):
        self.ui = (self.ui | 0x08) if level else (self.ui & ~0x08)
        self.tt.ui_in.value = self.ui

    def sleep_us(self, us):
        time.sleep_us(int(us))

    def vw_set(self, volts):                              # ua[2] key-write voltage
        if self.dac is None:
            raise RuntimeError("no V_W DAC configured (config.VW_DAC)")
        code = max(0, min(4095, int(volts / C.VW_DAC_VREF * 4095 + 0.5)))
        self.dac.writeto(C.MCP4725_ADDR, bytes([(code >> 8) & 0x0F, code & 0xFF]))

    def vb_read(self):                                    # ua[1] log-sum-exp probe
        if self.adc is None:
            return None
        n = 16
        acc = 0
        for _ in range(n):
            acc += self.adc.read_u16()
        return acc / n / 65535 * C.VB_ADC_VREF * C.VB_DIVIDER
