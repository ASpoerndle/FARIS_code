import struct
import smbus2
from smbus2 import i2c_msg
import time

# --- CONSTANTS ---
OCTOQUAD_ADDR = 0x30
REG_CMD = 0x04
REG_ENC0 = 0x1C

# --- GLOBAL BUS SETUP ---
# Open the bus once and keep it open
bus = smbus2.SMBus(1)

def init_octoquad(channel):
    print("--- Starting Slow-Motion Init ---")
    
    # 1. Clear the bus
    time.sleep(0.5)

    # 2. Set Bank Mode 2 (PWM)
    # Adding a longer sleep after this specific command
    print("Setting Bank Mode 2...")
    bus.write_i2c_block_data(OCTOQUAD_ADDR, REG_CMD, [0x01, 0x02, 2])
    time.sleep(0.5) # Increased from 0.1

    # 3. Configure Min/Max Pulse
    print(f"Configuring Channel {channel}...")
    bus.write_i2c_block_data(OCTOQUAD_ADDR, REG_CMD, [0x01, 0x04, channel, 1, 0, 0, 4])
    time.sleep(0.5)

    # 4. Save to Flash
    print("Saving...")
    bus.write_byte_data(OCTOQUAD_ADDR, REG_CMD, 0x03)
    time.sleep(1.0) # Long wait for Flash write
    
    print("--- Init Finished. LED should be steady. ---")
def read_all_channels():
    """Atomic read of all 8 channels (32 bytes)"""
    write = i2c_msg.write(OCTOQUAD_ADDR, [REG_ENC0])
    read = i2c_msg.read(OCTOQUAD_ADDR, 32)
    bus.i2c_rdwr(write, read)
    return struct.unpack('<8i', bytes(list(read)))

# --- TEST EXECUTION ---
target_channel = 3 # Change this to the channel your WHITE wire is on
# --- IMPROVED READING LOGIC ---
def read_single_channel(channel_index):
    # Calculate register: Channel 0 is 0x1C, each channel is 4 bytes
    reg = 0x1C + (channel_index * 4)
    
    # Read 4 bytes (32-bit integer)
    write = i2c_msg.write(OCTOQUAD_ADDR, [reg])
    read = i2c_msg.read(OCTOQUAD_ADDR, 4)
    bus.i2c_rdwr(write, read)
    
    # Unpack as a little-endian signed integer ('<i')
    raw_pulse = struct.unpack('<i', bytes(list(read)))[0]
    return raw_pulse

# Inside your loop:

    
try:
    init_octoquad(target_channel)
    
    print(f"Reading Channel {target_channel}. Rotate the wheel now.")
    print("RAW_VAL | DEGREES")
    print("-" * 20)
   while True:
        raw_val = read_single_channel(target_channel) # Use the target_channel variable!
        
        # The REV Encoder PWM range is roughly 1 to 1024 microseconds
        # We normalize it to 0.0 - 1.0
        normalized = (raw_val - 1) / 1023.0
        degrees = normalized * 360.0
        
        print(f"Raw Pulse: {raw_val}µs | Degrees: {degrees:.2f}°          ", end='\r')
        time.sleep(0.05)
except:
    print("bit")
"""
    while True:
        # 1. Get fresh data
        all_counts = read_all_channels()
        raw_val = all_counts[target_channel]

        # 2. Software Modulo Fix (Prevents negative numbers and wraps)
        # This keeps the number between 1 and 1024
        clean_raw = ((raw_val - 1) % 1024) + 1

        # 3. Convert to Degrees
        # Use 1023.0 to ensure floating point math
        degrees = ((clean_raw - 1) / 1023.0) * 360.0

        # 4. Print with formatting to catch oscillations
        # If RAW_VAL only toggles 0 and 1, the Bank Mode didn't stick.
        print(f"Raw: {raw_val:<6} | Clean: {clean_raw:<6} | Deg: {degrees:>6.2f}°", end='\r')
        
        time.sleep(0.05)
"""
"""except KeyboardInterrupt:
    print("\nTest Stopped.")
except Exception as e:
    print(f"\nError: {e}")"""
