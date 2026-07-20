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

def read_ads1015_a0():
    with SMBus(I2C_BUS) as bus:
        # Write to config register to select channel A0
        bus.write_i2c_block_data(ADS_ADDRESS, POINTER_CONFIG, [CONFIG_HIGH, CONFIG_LOW])
        time.sleep(0.05) # Wait for conversion to settle
        
        # Read 2 bytes from the conversion register
        data = bus.read_i2c_block_data(ADS_ADDRESS, POINTER_CONVERSION, 2)
        
        # Convert the data (ADS1015 is 12-bit, left-justified in 16-bit register)
        raw_adc = (data[0] << 8) | data[1]
        raw_adc >>= 4
        
        # Handle 12-bit two's complement for negative values (if any)
        if raw_adc > 0x7FF:
            raw_adc -= 0x1000
            
        # Calculate voltage based on the +/-6.144V Full Scale Range
        voltage = raw_adc * (6.144 / 2047.0)
        return raw_adc, voltage

print("Reading ADS1015 directly via SMBus...")
try:
    while True:
        raw, volt = read_ads1015_a0()
        print(f"Raw: {raw:<6} Voltage: {volt:.4f}V")
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nStopped.")
