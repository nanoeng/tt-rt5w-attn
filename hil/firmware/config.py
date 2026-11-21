# HIL wiring for the TT demo board. ua[1] and ua[2] are on the analog header of the TT carrier; wire them as below.
PROJECT = "tt_um_rt5w_attn"   # rename together with info.yaml top_module (add your GitHub username)
CLK_HZ = 20_000_000
VB_ADC_PIN = 26               # RP GP26/ADC0 <- ua[1] through a /2 divider (V_B up to ~2.4 V; ADC full scale 3.3 V)
VB_ADC_VREF = 3.3
VB_DIVIDER = 2.0
VW_DAC = "mcp4725"            # MCP4725 12-bit DAC on a PMOD/I2C -> ua[2] (0.8 mV LSB; one key step is 0.14 mV,
VW_DAC_VREF = 3.3             #   so writes are coarse: fine-tune keys with the on-chip pump + CAL passes)
MCP4725_ADDR = 0x60
I2C_ID, I2C_SCL, I2C_SDA = 0, 5, 4
