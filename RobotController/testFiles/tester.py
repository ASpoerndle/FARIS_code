import board
import Jetson.GPIO as GPIO
import time
import sys
import smbus2
from smbus2 import i2c_msg # Atomic I2C fix
import struct
import busio

#----------------------------------------------------------------
#                       CONSTANTS & SETUP
#----------------------------------------------------------------
OCTOQUAD_I2C_ADDR = 0x30
I2C_BUS_NUM = 1
bus = smbus2.SMBus(I2C_BUS_NUM)

# Register Addresses
OCTOQUAD_REG_CHIP_ID = 0x00
OCTOQUAD_REG_FW_MAJ  = 0x01
OCTOQUAD_REG_CMD     = 0x04
OCTOQUAD_REG_ENC0    = 0x1C  # Data starts here for all modes
OCTOQUAD_REG_VEL0    = 0x3C

# Command IDs
CMD_SET_PARAM        = 0x01
CMD_SAVE_PARAMS      = 0x03

# Parameter IDs
PARAM_BANK_MODE      = 0x02
PARAM_PULSE_WIDTH    = 0x04
PARAM_WRAP_TRACK     = 0x05

#----------------------------------------------------------------
#                      HELPER FUNCTIONS
#----------------------------------------------------------------

def init_hardware():
    """Configures the OctoQuad once based on spec 3.0C"""
    print("Configuring OctoQuad hardware...")
    
    # 1. Set Bank Mode: Bank 1 (0-3) = Absolute/PWM, Bank 2 (4-7) = Quad
    # [Cmd, ParamID, Value]
    bus.write_i2c_block_data(OCTOQUAD_I2C_ADDR, OCTOQUAD_REG_CMD, [CMD_SET_PARAM, PARAM_BANK_MODE, 2])
    
    # 2. Set Min/Max for Absolute Channels (Default 1us to 1024us)
    # Necessary for correct degree math and velocity
    for ch in range(4):
        # [Cmd, ParamID, Channel, Min_L, Min_H, Max_L, Max_H]
        bus.write_i2c_block_data(OCTOQUAD_I2C_ADDR, OCTOQUAD_REG_CMD, [CMD_SET_PARAM, PARAM_PULSE_WIDTH, ch, 1, 0, 0, 4])
    
    # 3. Save to Flash
    bus.write_byte_data(OCTOQUAD_I2C_ADDR, OCTOQUAD_REG_CMD, CMD_SAVE_PARAMS)
    time.sleep(0.1)
    print("Hardware ready.")

def read_octoquad_data():
    """Uses atomic I2C transactions to prevent data byte-shifting"""
    # Read 32 bytes (8 channels * 4 bytes each)
    write = i2c_msg.write(OCTOQUAD_I2C_ADDR, [OCTOQUAD_REG_ENC0])
    read = i2c_msg.read(OCTOQUAD_I2C_ADDR, 32)
    bus.i2c_rdwr(write, read)
    
    # Unpack as 8 signed 32-bit integers
    return struct.unpack('<8i', bytes(list(read)))

def get_degrees(channel, counts_list):
    raw = counts_list[channel]
    if channel <= 3:
        # Absolute Mode (1-1024 range)
        return ((raw - 1)/341.0) * 360.0
    else:
        # Relative Mode (8192 ticks/rev)
        return (raw / 8192.0) * 360.0

#----------------------------------------------------------------
#                            MAIN
#----------------------------------------------------------------

# 1. Verify Chip
chip_id = bus.read_byte_data(OCTOQUAD_I2C_ADDR, OCTOQUAD_REG_CHIP_ID)
if chip_id != 0x51:
    print(f"Error: Chip ID {hex(chip_id)} not recognized.")
    sys.exit()

# 2. Initialize Parameters
init_hardware()

print("\nStarting Control Loop. Press Ctrl+C to stop.\n")

while True:
    try:
        # Get all channel data
        all_counts = read_octoquad_data()
        
        # Example: Analyze Absolute Encoder (Channel 0)
        abs_deg = get_degrees(3, all_counts)
        
        # Example: Analyze Relative Encoder (Channel 4)
        rel_deg = get_degrees(4, all_counts)
        
        # Your specific steering pod logic for Channel 4 (Relative)
        # Using degrees instead of raw ticks for better accuracy
        if -5.0 < rel_deg < 5.0:
            status = "FORWARD"
        elif rel_deg > 5.0:
            status = "LEFT"
        else:
            status = "RIGHT"

        print(f"Abs Ch0: {abs_deg:6.1f}° | Rel Ch4: {rel_deg:6.1f}° | Status: {status}", end='\r')
        
        time.sleep(0.05) # 20Hz loop

    except KeyboardInterrupt:
        print("\nStopping...")
        break
