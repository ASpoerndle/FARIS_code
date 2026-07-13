import struct
import smbus2
from smbus2 import i2c_msg
from Motor import Motor
import board
from adafruit_pca9685 import PCA9685
import Jetson.GPIO as GPIO
import time
import math
from Encoder import Encoder
from simple_pid import PID
"""
Class: RotationlMotor
@Author: Aidan Spoerndle
Purpose: A subclass of the Motor class, the RotationalMotor class incorporates the encoder data received from an
         Octoquad MK2 to aid the robot in precise movement of both the pod and the wheel motors.  
"""

bus = smbus2.SMBus(1)
class MotorWithEncoder(Motor):

  I2C_ADDR = 0x30

  I2C_BUS = 1

  def __init__(self, pca, pin, side, enc, fVal):
    Motor.__init__(self,pca,pin,side)


    self.encoder = Encoder(enc,fVal)

    
    if(side == "r"):

        self.polarity = -1

    else:

        self.polarity = 1

    self.forwardValue = fVal #the value that results in the swerve pods to face "forward"



    self.pid = PID(0.05,0.000003,0.000002, setpoint=(fVal)) 
    self.pid.output_limits=(-.6,.6)



  """
  Method: stopMotor()
  Purpose: sets the motor speed equal to 0
  """
        
  def stopMotor(self):

      self.moveMotor(0)

  def setSpeed(self,speed):
      self.moveMotor(speed)

  def getCurrentHeading(self):
      self.encoder.getCurrentHeading()

"""
TESTING GROUND FOR ROTATIONAL MOTOR

given a pca address, pin value, and a side
"""

"""
try:
    i2c = board.I2C()
    pca = PCA9685(i2c)
    pca.frequency = 50
    pin = 3
    side = "r"
    idealfVal =538
    channel = 3
    rotMotor = RotationalMotor(pca,pin,side,channel,idealfVal)
    
    #val = rotMotor.adjustForward()
    # while(val):
    #     val = rotMotor.adjustForward()
    #     print(rotMotor.getCurrentPosition())
    # print("finshed")
    #print("Adjusting forward...")
    

    val = False
    while(not val):
      
            rotMotor.setSpeed(0.1)

    
    print("Forward adjustment complete!")
    time.sleep(1)
    print("Rotating Motor 90 degrees...")
    
    
    val = False
    #rotMotor.setMotorSpeed(-.2)
    #target = (rotMotor.getCurrentPosition()/8192)*360
    #print("current degrees", target)
     
    #target += 10 
    #print("new degrees",target)
    #while(not val): 
    #    val = rotMotor.driveForward(target,.1)
    #val = True
    #print("Rotation complete!")
    # startPos = rotMotor.getCurrentPosition()
    # val = rotMotor.move(0.5,.1,startPos)
    # while(val):
    rotMotor.stopMotor()
    #val = rotMotor.move(0.5,.1)
except KeyboardInterrupt:
        rotMotor.kill_motor()
"""

