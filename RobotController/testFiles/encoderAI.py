import struct
from smbus2 import SMBus

# OctoQuad default settings
I2C_ADDR = 0x30
I2C_BUS = 1
positions = [0,0,0,0,0,0,0,0]
velocities = [0,0,0,0,0,0,0,0]
def read_octoquad():
    with SMBus(I2C_BUS) as bus:
        # Read all 8 channels (32 bytes total) starting from register 0x00
        all_positions = bus.read_i2c_block_data(I2C_ADDR, 0x00, 32)
        all_velocities = bus.read_i2c_block_data(I2C_ADDR, 0x20,16)
        
        # Unpack into a list of 8 integers
        # '<8i' means 8 little-endian signed integers
        velocities = struct.unpack('<8h', bytes(all_velocities))
        positions = struct.unpack('<8i', bytes(all_positions))
        
        # for i, val in enumerate(positions):
        #     channels[i] = val

        # return position, velocity
#Ideal position is -13
try:
   while True:
        read_octoquad()
        print(positions)
        print(velocities)
except Exception as e:
    print(f"Error reading from OctoQuad: {e}")
