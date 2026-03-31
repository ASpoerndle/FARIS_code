import struct
from smbus2 import SMBus
from Motor import WheelMotor
class RotationalMotor():
  I2C_ADDR = 0x30
  I2C_BUS = 1
  positions = [0,0,0,0,0,0,0,0]
  velocities = [0,0,0,0,0,0,0,0]  
  forwardVal = -13
  def __init__(self, pca, pin, side, enc):
    self.motor = WheelMotor(pca,pin,side)
    self.enc = enc


  def adjustForward(self):
      read_octoquad()
      currentPos = RotationalMotor.positions[self.enc]
      if(currentPos > RotationalMotor.forwardVal - 5 and currentPos < RotationalMotor.forwardVal + 5):
         return
      elif(currentPos < RotationalMotor.forwardVal):
        print("rotate left for center")
      else:
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
