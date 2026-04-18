import struct
import smbus2
import time

bus = smbus2.SMBus(1)
ADDR = 0x30

# Register Constants from Datasheet
REG_CHIP_ID = 0x00     # Should return 0x51 [cite: 453, 459]
REG_CMD = 0x04         # Command Register [cite: 453]
REG_CH3_DATA = 0x28    # Channel 3 Data 
REG_LOGIC = 0x14       # Logic state 

def configure_octoquad():
    print("--- Configuring OctoQuad for REV Encoder ---")
    
    # 1. Set Bank 0 (Channels 0-3) to Pulse Width Mode (Value 1) 
    # Command: SetParam(0x01), ParamID: BankConfig(0x02), Value: 1 [cite: 516, 531]
    bus.write_i2c_block_data(ADDR, REG_CMD, [0x01, 0x02, 0x01])
    time.sleep(0.1)

    # 2. Set Min/Max Pulse for Channel 3 (Default 1us to 1024us) 
    # Command: SetParam(0x01), ParamID: PulseWidth(0x04), Ch: 3, Min: 1, Max: 1024 [cite: 531]
    # Min 1 (0x0001), Max 1024 (0x0400) - Little Endian 
    bus.write_i2c_block_data(ADDR, REG_CMD, [0x01, 0x04, 0x03, 0x01, 0x00, 0x00, 0x04])
    time.sleep(0.1)

    # 3. Save to Flash 
    bus.write_byte_data(ADDR, REG_CMD, 0x03)
    print("Settings saved to Flash.")

def run_monitor():
    print("\nReading Channel 3...")
    try:
        while True:
            # Read 4-byte signed integer [cite: 492]
            data = bus.read_i2c_block_data(ADDR, REG_CH3_DATA, 4)
            raw_val = struct.unpack('<i', bytes(data))[0]
            
            # Read logic state of pin 3 
            logic = bus.read_byte_data(ADDR, REG_LOGIC)
            pin_3 = (logic >> 3) & 0x01
            
            # Status interpretation
            status = "OK"
            if raw_val == -1: status = "Timeout"
            if raw_val == -2: status = "Invalid/Out of Range"
            
            # Convert to degrees if valid (1-1024 range) [cite: 574]
            deg = ((raw_val - 1) / 1023.0 * 360.0) if raw_val > 0 else 0.0

            print(f"Logic: {pin_3} | Raw: {raw_val:<6} | {deg:6.1f}° | {status}", end='\r')
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
def read_encoders():
    # Base address for Channel 0 is 0x1C 
    # Each channel is 4 bytes apart 
    encoder_values = []
    
    for i in range(5):
        reg = 0x1C + (i * 4)
        data = bus.read_i2c_block_data(ADDR, reg, 4)
        val = struct.unpack('<i', bytes(data))[0]
        encoder_values.append(val)
        
    return encoder_values
if bus.read_byte_data(ADDR, REG_CHIP_ID) == 0x51:
    configure_octoquad()

# Usage in your loop:
while True:
    vals = read_encoders()
    print(f"Ch0: {vals[0]} | Ch1: {vals[1]} | Ch2: {vals[2]} | Ch3: {vals[3]} | Ch4: {vals[4]}", end='\r')
    time.sleep(0.05)
# Verify Chip ID before starting [cite: 459]
else:
    print("OctoQuad not found at 0x30!")
