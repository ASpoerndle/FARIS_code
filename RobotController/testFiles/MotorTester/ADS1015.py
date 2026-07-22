
import time
from smbus2 import SMBus
class GripperADS():
    # ADS1015 Constants
    I2CBUS = 1
    I2CADDRESS = 0x48
    CONVERSIONREGISTER = 0x00
    CONFIGREGISTER = 0x01

    # Config register values for Single-ended A0, +/-6.144V range, 1600 SPS
    # OS[15]=1 (Start conversion), MUX[14:12]=100 (A0), PGA[11:9]=000 (+/-6.144V), MODE[8]=0 (Continuous)
    CONFIG_HIGH = 0xC4
    CONFIG_LOW = 0x83
    def getGripperVoltage(self):
        with SMBus(GripperADS.I2CBUS) as bus: #check bus 1 because thats where the ADS1015 is
            bus.write_i2c_block_data(GripperADS.I2CADDRESS, GripperADS.CONFIGREGISTER, [GripperADS.CONFIG_HIGH, GripperADS.CONFIG_LOW])
            #input the bus address for the ADS (0x48), which register you wanna cess (config), and set a high and low config
            time.sleep(0.05)
            data = bus.read_i2c_block_data(GripperADS.I2CADDRESS, GripperADS.CONVERSIONREGISTER, 2)
            #access bus 1, access the conversion register, bring back 2 bytes

            raw_adc = (data[0] << 8) | data[1]

            raw_adc >>= 4
            if raw_adc > 0x7FF:
                raw_adc -= 0x1000

                # Calculate voltage based on the +/-6.144V Full Scale Range
            voltage = raw_adc * (6.144 / 2047.0)
            return voltage
