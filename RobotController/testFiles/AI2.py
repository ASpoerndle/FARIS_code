import struct
import time
from smbus2 import SMBus, i2c_msg

# Configuration
OCTO_ADDR = 0x30
I2C_BUS = 1

def get_data_hard_sync():
    try:
        with SMBus(I2C_BUS) as bus:
            # 1. Prepare the atomic transaction
            write = i2c_msg.write(OCTO_ADDR, [0x00])
            read = i2c_msg.read(OCTO_ADDR, 32)

            # 2. ACTUALLY execute the transaction
            bus.i2c_rdwr(write, read)

            # 3. Convert the i2c_msg read object to a list of bytes
            raw_bytes = list(read)

            # 4. REPAIR: Rotate the list by 4 bytes (one 32-bit int)
            # This moves the data from the 'Channel 7' position back to 'Channel 0'
            corrected_raw = raw_bytes[-4:] + raw_bytes[:-4]

            # 5. Unpack as 8 Signed 32-bit Integers (Little Endian)
            positions = struct.unpack('<8i', bytes(corrected_raw))
            return positions
            
    except Exception as e:
        print(f"I2C Error: {e}")
        return None

# The 'Ultimate' Loop
print("Starting OctoQuad Read (Shift-Corrected Mode)...")
while True:
    data = get_data_hard_sync()
    
    if data:
        # Using f-string formatting to keep the columns aligned
        output = " | ".join([f"Ch{i}: {val:<8}" for i, val in enumerate(data)])
        print(output, end="\r") # Overwrites the same line for readability
    
    # 20ms delay is essential for the OctoQuad's internal update rate
    time.sleep(0.02)
