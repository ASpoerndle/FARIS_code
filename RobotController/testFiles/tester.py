import smbus2
import time

bus = smbus2.SMBus(1)
ADDR = 0x30

def force_single_byte_config():
    print("--- Attempting Single-Byte Recovery ---")
    try:
        # Check Signature Byte 0
        sig0 = bus.read_byte_data(ADDR, 0x00)
        if sig0 == ord('Q'):
            print("Found OctoQuad! Forcing Mode 5 on Channel 3...")
            
            # 0x0C is the specific register for Channel 3's Mode
            # We write 0x05 (High-Precision PWM) directly to it
            bus.write_byte_data(ADDR, 0x0C, 0x05)
            time.sleep(0.1)
            
            # Set Polarity (Register 0x13 is Polarity for Chan 3)
            # 0x01 = High Pulse
            bus.write_byte_data(ADDR, 0x13, 0x01)
            time.sleep(0.1)
            
            # Save to Flash (Command 0x03 to Register 0x04)
            bus.write_byte_data(ADDR, 0x04, 0x03)
            print("Save command sent.")
            time.sleep(0.5)
            
            # Verify the Mode stuck
            verify = bus.read_byte_data(ADDR, 0x0C)
            print(f"Verification: Channel 3 Mode is now {verify}")
            # Set the Min Pulse to 0 and Max Pulse to 65535 (FFFF)
# This prevents the -2 (Invalid) error.
# Register 0x11 is Min_L, 0x12 is Min_H, 0x13 is Max_L, 0x14 is Max_H (for Channel 3)
# Note: In Mode 5, registers 0x10-0x17 control these bounds.
            bus.write_byte_data(ADDR, 0x10, 0x00) # Min L
            bus.write_byte_data(ADDR, 0x11, 0x00) # Min H
            bus.write_byte_data(ADDR, 0x12, 1024) # Max L
            bus.write_byte_data(ADDR, 0x13, 1024) # Max H
            bus.write_byte_data(ADDR, 0x04, 0x03) # Save            
        else:
            print(f"Unexpected signature byte: {sig0}")
            
    except Exception as e:
        print(f"Communication error: {e}")

force_single_byte_config()
