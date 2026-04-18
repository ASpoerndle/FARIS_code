import smbus2
import time

bus = smbus2.SMBus(1)
ADDR = 0x30
CMD_REG = 0x04

def force_mode_manual():
    print("Sending manual raw byte sequence...")
    # [OpCode, ParamID, Channel, Value]
    # We send this directly to the CMD_REG (0x04)
    # This sets Channel 3 (0x03) to PWM Mode (0x02)
    msg = [0x01, 0x02, 0x03, 0x02]
    bus.write_i2c_block_data(ADDR, CMD_REG, msg)
    time.sleep(0.2)
    
    print("Sending Save-to-Flash...")
    # Command 0x03 = Save all settings
    bus.write_byte_data(ADDR, CMD_REG, 0x03)
    time.sleep(0.5)
    
    # Check if it stuck immediately BEFORE power cycle
    check = bus.read_byte_data(ADDR, 0x09 + 3)
    print(f"Immediate verification: Mode is {check}")
    if check == 2:
        print("IT WORKED! Now power cycle to finalize.")
    else:
        print("Still failing. Trying alternate length...")
        # Some firmware versions expect a length byte first
        msg_alt = [4, 0x01, 0x02, 0x03, 0x02]
        bus.write_i2c_block_data(ADDR, CMD_REG, msg_alt)
        time.sleep(0.2)
        bus.write_byte_data(ADDR, CMD_REG, 0x03)
        print(f"Alt verification: Mode is {bus.read_byte_data(ADDR, 0x0C)}")

force_mode_manual()
