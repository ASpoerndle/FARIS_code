from MotorController import MotorController
import struct
import smbus2
from smbus2 import i2c_msg
from Motor import Motor
import board
from adafruit_pca9685 import PCA9685
import Jetson.GPIO as GPIO
import time
import math
mc = MotorController()
bus = smbus2.SMBus(1)

def reset_IMU():

    bus.write_byte_data(0x30, 0x04, 0x28)
    while True:
        status = bus.read_byte_data(0x30, 0x0D)
        if status == 4:
            print("Localizer Ready!")
            break
        elif status == 5:
            raise Exception("IMU Fault: Device not detected")

    print("Hardware ready.")
def read_heading():
    data = bus.read_i2c_block_data(0x30, 0x18, 2)
    raw_heading = struct.unpack('<h', bytes(data))[0]
    #print(raw_heading)
    headingRad = raw_heading / 5000.0
    headingDeg = headingRad * 180 / math.pi
    return headingDeg

def set_the_scalar(scalar):
    packed_scalar = struct.pack('<f', float(scalar))
    payload = [0x01, 0x36] + list(packed_scalar)

    # 3. Write the payload starting at the Command Register (0x04)
    # All operand registers must be written in the same transaction [cite: 202]
    bus.write_i2c_block_data(0x30, 0x04, payload)
#Reset IMU
reset_IMU()
#Rotate the robot 3600 degrees - do an input pause in case it's not perfect straight
mc.turn(3600,False)
#find the scalar value
heading = read_heading()
scalar = (3600-heading)/3600

#set the scalar value
set_the_scalar(scalar)
#rotate 90 degree, check heading, confirm input
for i in range(4):
    mc.turn(90,False)
    input(f"Current reading: {read_heading()}")
#save everything
bus.write_byte_data(0x30, 0x04, 0x03)