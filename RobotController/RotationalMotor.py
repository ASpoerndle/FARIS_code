 import struct

from smbus2 import SMBus

from Motor import WheelMotor

import board

from adafruit_pca9685 import PCA9685


import Jetson.GPIO as GPIO

import time

import math

class RotationalMotor():

  I2C_ADDR = 0x30

  I2C_BUS = 1

  positions = [0,0,0,0,0,0,0,0]

  velocities = [0,0,0,0,0,0,0,0]  

  WHEELDIAMETER = .144

  WHEELC = WHEELDIAMETER * math.pi

  #left is more pos, right is more neg

  def __init__(self, pca, pin, side, enc, fVal):

    self.motor = WheelMotor(pca,pin,side)

    self.enc = enc

    if(side == "r"):

        self.polarity = -1

    else:

        self.polarity = 1

    self.fVal = fVal

    self.currentCount = fVal

    self.read_octoquad()


  #Returns T/F based on if it's off-centered, put a while loop in MotorController class so it can adjust all motors at once

  def adjustForward(self):

      self.read_octoquad()

      

      currentPos = RotationalMotor.positions[self.enc]

      if(currentPos > self.fVal - 10 and currentPos < self.fVal + 10):

         self.motor.move_motor(0)

         return True

      elif(currentPos < self.fVal):

        self.motor.move_motor(.1)

        print("rotate left for center")

        return False

      else:

          self.motor.move_motor(-.1)

          print("rotate right for center")

          return False

  #right is neg, left is pos

  def setMotorSpeed(self,speed):

      self.motor.move_motor(speed)

  def rotate(self, angle, speed):

    speed = abs(speed)

    self.read_octoquad()

    if(self.polarity > 0):

        if(angle < 0):

            cond = self.rotateLeft(angle, speed)

        if(angle > 0):

        #true = True

            cond = self.rotateRight(angle , speed)

    #else:

      #self.adjustForward()

        if(angle == 0):

            cond = True

    else:

        if(angle > 0):

            cond = self.rotateLeft(angle,speed)

        if(angle < 0):

            

            cond = self.rotateRight(angle,speed)

        if(angle == 0):

            cond = True

    if(cond):

      self.currentCount = self.getCurrentPosition()

      return True

    else:

      return False

  def rotateForward(self,angle,speed):

        speed = abs(speed)

        self.read_octoquad()

        self.currentCount = 0

        if(self.polarity > 0):

            if(angle < 0):

                cond = self.rotateLeft(angle, speed)

            if(angle > 0):

                cond = self.rotateRight(angle , speed)

            if(angle == 0):

                cond = True

        else:

            if(angle < 0):

                cond = self.rotateLeft(angle,speed)

            if(angle > 0):

            

                cond = self.rotateRight(angle,speed)

            if(angle == 0):

                cond = True

        if(cond):

            self.currentCount = self.getCurrentPosition()

            return True

        else:

            return False


  def stopMotor(self):

      self.motor.move_motor(0)

  def rotateLeft(self, angle,  speed):

    new_pos = (angle * 1024)/45  + self.currentCount

    if(self.getCurrentPosition() < new_pos and self.polarity > 0):

        self.motor.move_motor(-speed)

        return False

    elif(self.getCurrentPosition() < new_pos and self.polarity < 0):

        self.motor.move_motor(-speed)

        return False

    else:

      self.motor.move_motor(0)

      return True

    #TODO - if current Pos > forward - 90, rotate left

    

  def rotateRight(self, angle, speed):

    new_pos = (angle * 1024)/45 + self.currentCount

    print("CC: " + str(self.getCurrentPosition()))

    print("NP: " + str(new_pos))

    print("Encoder: " + str(self.enc) + "has speed of: " + str(speed*self.polarity))

    if(self.getCurrentPosition() < new_pos and self.polarity > 0):

     # print("moving motor...")

      self.motor.move_motor(speed)

      return False

    elif(self.getCurrentPosition() > new_pos and self.polarity < 0):

        print("please work")

        self.motor.move_motor(speed)

        return False

    else:

      self.motor.move_motor(0)

      return True

    #TODO - if current Pos < forward + 90, rotate right

  def getCurrentPosition(self):

      return RotationalMotor.positions[self.enc]


  #input distance in m, speed -1.0 to 1.0

  def move(self,distance,speed):

    rev_dis = distance / RotationalMotor.WHEELC

    degree_dis = rev_dis * 360

    

    if(count_dis > self.current_count and distance > 0):

      self.rotate(degree_dis, speed)

      return True

    elif(count_dis < self.current_count and distance < 0):

      self.rotate(degree_dis,speed)

      return True

    else:

        self.current_count = self.getCurrentPosition()

        return False

  # OctoQuad default settings

  def read_octoquad(self):

    with SMBus(RotationalMotor.I2C_BUS) as bus:

        addr = RotationalMotor.I2C_ADDR

        # Read all 8 channels (32 bytes total) starting from register 0x00

        all_positions = bus.read_i2c_block_data(addr, 0x1C, 32)

        all_velocities = bus.read_i2c_block_data(addr, 0x3C,16)

        

        # Unpack into a list of 8 integers

        # '<8i' means 8 little-endian signed integers

        RotationalMotor.velocities = struct.unpack('<8h', bytes(all_velocities))

        RotationalMotor.positions = struct.unpack('<8i', bytes(all_positions))

        print(RotationalMotor.positions) 

        # for i, val in enumerate(positions):

        #     channels[i] = val

    time.sleep(.01)

        # return position, velocity

#Ideal position is -13



"""
TESTING GROUND FOR ROTATIONAL MOTOR

given a pca address, pin value, and a side
"""
"""try:
    i2c = board.I2C()
    pca = PCA9685(i2c)
    pca.frequency = 50
    pin = 11
    side = "l"
    idealfVal = 0
    channel = 6
    rotMotor = RotationalMotor(pca,pin,side,channel,idealfVal)
    val = rotMotor.adjustForward()
    # while(val):
    #     val = rotMotor.adjustForward()
    #     print(rotMotor.getCurrentPosition())
    # print("finshed")
    print("Adjusting forward...")
    while(val):
      val = rotMotor.adjustForward()
    print("Forward adjustment complete!")
    time.sleep(1)
    print("Rotating Motor 90 degrees...")
    val = True
    #rotMotor.setMotorSpeed(-.2)
    while(val):
           
        val = rotMotor.rotate(-90,.1)
    val = True
    while(val):
        val = rotMotor.adjustForward()
    print("Rotation complete!")  
    # startPos = rotMotor.getCurrentPosition()
    # val = rotMotor.move(0.5,.1,startPos)
    # while(val):
    rotMotor.stopMotor()
    #   val = rotMotor.move(0.5,.1)
except KeyboardInterrupt:
    rotMotor.stopMotor()"""
