import struct
from smbus2 import SMBus

# OctoQuad default settings
I2C_ADDR = 0x30
I2C_BUS = 1
channels = [0,0,0,0,0,0,0,0]
def read_octoquad():
    with SMBus(I2C_BUS) as bus:
        # Read 4 bytes starting at Register 0x00 (Channel 0 Position)
        # OctoQuad uses Little Endian format
        pos_data = bus.read_i2c_block_data(I2C_ADDR, 0x00, 4)
        position = struct.unpack('<i', bytes(pos_data))[0]

        # Read 2 bytes starting at Register 0x20 (Channel 0 Velocity)
        vel_data = bus.read_i2c_block_data(I2C_ADDR, 0x20, 2)
        velocity = struct.unpack('<h', bytes(vel_data))[0]
        # Read all 8 channels (32 bytes total) starting from register 0x00
        all_data = bus.read_i2c_block_data(I2C_ADDR, 0x00, 32)

# Unpack into a list of 8 integers
# '<8i' means 8 little-endian signed integers
        positions = struct.unpack('<8i', bytes(all_data))

        for i, val in enumerate(positions):
            channels[i] = val

        return position, velocity

try:
   while True:
        read_octoquad()
        print(channels)
except Exception as e:
    print(f"Error reading from OctoQuad: {e}")
