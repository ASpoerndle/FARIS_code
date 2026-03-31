import struct
from smbus2 import SMBus
from Motor import WheelMotor
import board
from adafruit_pca9685 import PCA9685

import Jetson.GPIO as GPIO
import time
class RotationalMotor():
  I2C_ADDR = 0x30
  I2C_BUS = 1
  positions = [0,0,0,0,0,0,0,0]
  velocities = [0,0,0,0,0,0,0,0]  
  forwardVal = -13
  def __init__(self, pca, pin, side, enc):
    self.motor = WheelMotor(pca,pin,side)
    self.enc = enc

  #Returns T/F based on if it's off-centered, put a while loop in MotorController class so it can adjust all motors at once
  def adjustForward(self):
      read_octoquad()
      currentPos = RotationalMotor.positions[self.enc]
      if(currentPos > RotationalMotor.forwardVal - 5 and currentPos < RotationalMotor.forwardVal + 5):
         return False
      elif(currentPos < RotationalMotor.forwardVal):
        print("rotate left for center")
        return True
      else:
        return True
        print("rotate right for center")
  def rotateLeft(self):
    #TODO - if current Pos > forward - 90, rotate left
  def rotateRight(self):
    #TODO - if current Pos < forward + 90, rotate right
  # OctoQuad default settings
  def read_octoquad():
    with SMBus(I2C_BUS) as bus:
        # Read all 8 channels (32 bytes total) starting from register 0x00
        all_positions = bus.read_i2c_block_data(I2C_ADDR, 0x00, 32)
        all_velocities = bus.read_i2c_block_data(I2C_ADDR, 0x20,16)
        
        # Unpack into a list of 8 integers
        # '<8i' means 8 little-endian signed integers
        RotationalMotor.velocities = struct.unpack('<8h', bytes(all_velocities))
        RotationaMotor.positions = struct.unpack('<8i', bytes(all_positions))
        
        # for i, val in enumerate(positions):
        #     channels[i] = val

        # return position, velocity
#Ideal position is -13

"""
TESTING GROUND FOR ROTATIONAL MOTOR

given a pca address, pin value, and a side
"""
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50
pin = 2
side = "l"
rotMotor = RotationalMotor(pca,pin,side,0)
val = rotMotor.adjustForward()
while(val):
  val = rotMotor.adjustForward()


