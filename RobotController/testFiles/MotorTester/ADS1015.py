
import time
from smbus2 import SMBus

# ADS1015 Constants
I2C_BUS = 1
ADS_ADDRESS = 0x48
POINTER_CONVERSION = 0x00
POINTER_CONFIG = 0x01

# Config register values for Single-ended A0, +/-6.144V range, 1600 SPS
# OS[15]=1 (Start conversion), MUX[14:12]=100 (A0), PGA[11:9]=000 (+/-6.144V), MODE[8]=0 (Continuous)
CONFIG_HIGH = 0xC4
CONFIG_LOW = 0x83

with SMBus(I2C_BUS) as bus: #check bus 1 because thats where the ADS1015 is
    bus.write_i2c_block_data(ADS_ADDRESS, POINTER_CONFIG, [CONFIG_HIGH, CONFIG_LOW])
    #input the bus address for the ADS (0x48), which register you wanna cess (config), and set a high and low config
    time.sleep(0.05)
    data = bus.read_i2c_block_data(ADS_ADDRESS, POINTER_CONVERSION, 2)
    #access bus 1, access the conversion register, bring back 2 bytes
    print(data[0])
    raw_adc = (data[0] << 8) | data[1]
    
    raw_adc >>= 4
