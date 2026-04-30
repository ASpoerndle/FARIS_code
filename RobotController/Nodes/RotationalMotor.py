import struct
import smbus2
from smbus2 import i2c_msg
from .Motor import Motor
import board
from adafruit_pca9685 import PCA9685
import Jetson.GPIO as GPIO
import time
import math
from simple_pid import PID
bus = smbus2.SMBus(1)
"""
Class: RotationlMotor
@Author: Aidan Spoerndle
Purpose: A subclass of the Motor class, the RotationalMotor class incorporates the encoder data received from an
         Octoquad MK2 to aid the robot in precise movement of both the pod and the wheel motors.  
"""



class RotationalMotor(Motor):

  I2C_ADDR = 0x30

  I2C_BUS = 1

  positions = [0,0,0,0,0,0,0,0]

  velocities = [0,0,0,0,0,0,0,0]  

 
  
  #left is more pos, right is more neg

  def __init__(self, pca, pin, side, enc, fVal):
    Motor.__init__(self,pca,pin,side)

    
    self.enc = enc
    self.init_hardware()
    
    if(side == "r"):

        self.polarity = -1

    else:

        self.polarity = 1

    self.fVal = fVal

    self.currentCount = fVal
    
    self.pid = PID(0.05,0.000003,0.000002, setpoint=(fVal)) 
    self.pid.output_limits=(-.6,.6)
  
  #Initilizes the Octoquad for a 4 relative, 4 abs set up where the abs values are allowed to wrap 
  def init_hardware(self):
    #===Format for manipulating registers===
    """
    I2C Address:               0x30
    Access a command register: 0x04
    Set parameter:             0x01
    
    Example: set the command register to allow wrapping of abs encoders
    bus.write_i2c_block_data(0x30,0x04,[0x01,0x05,0xF0])
    
    """
        #Allow wrapping (0x05) of all absolute encoders (0xF0)
    bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x05, 0xF0])

    #Set bank mode for encoders to 2 to allow ports 4-7 to be abs and 0-3 to be quadrature
    bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x02, 2]) 

    #set min and max values for abs encoders (from 1-1024 based on REV ThroughBore encoder specs)
    if(self.enc>=4):
        # [Cmd, ParamID, Channel, Min_L, Min_H, Max_L, Max_H]
        bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x04, self.enc, 1, 0, 0, 4])
        bus.write_i2c_block_data(0x30,0x04, [0x01,0x05,0xF0])
        #bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x05, self.enc, 0]) 
    #save settings to octoquad
    bus.write_byte_data(0x30, 0x04, 0x03)
    time.sleep(0.1)
    print("Hardware ready.")

  
  """
  Method: adjustForward()
  Purpose: handles the logic for adjusting the Pod motors to a "forward" position
  """
  def adjustForward(self,debug):
      currentPos = self.getCurrentPosition()
            #convert fVal pwm into degrees
      target = ((self.fVal-1)/1023.0)*360
      target = target %360
            #convert current raw position to degrees
      currentDeg = ((currentPos-1)/1023.0)*360
      currentDeg = currentDeg %360
            #calc the difference betweentarget and currentDeg
            # error = (target - currentDeg + 180) % 360 - 180
      error = (target - currentDeg)
      feedback = currentDeg
      error = (error + 180) % 360 - 180
      self.pid.setpoint = currentDeg + error
      control_signal = self.pid(feedback)
      if(debug):
        print(f"Target: {target%360} | Current: {currentDeg%360} Encoder: {self.enc} | Error: {error} | Speed: {control_signal}")      
       
      if abs(error) < .5 or abs(error) > 177:
            
            self.move_motor(0)
            return True
      else:
          
            self.move_motor(-control_signal * .75)

            return False

  
  """
  Method: rotate(angle {degrees}, speed)
  Purpose: rotates the Pod motors to the designated location based on a degree input
  """
  def rotate(self, angle, speed,debug):
     speed = abs(speed)
     current = self.getCurrentPosition()
     
     forward = ((self.fVal-1)/1023)*360 % 360

     if(self.enc <=3):
        current_degrees = (current/8192) * 360
        angle += ((self.fVal-1)/1023)*360
        target = angle
        speed *= self.polarity
        error = current_degrees - target    
     else:
        #current_degrees = ((current-1)/1023) * 360
        current_degrees = ((current - 1)/1023) * 360 % 360
        
        target = (forward  + angle) % 360
        
        speed *= 0.75
        error = (target -current_degrees + 180) % 360 - 180 
        if (error > 90):
            error -= 180
            speed *= -1
        if(error < -90):
            error += 180
            speed *= -1
        target = current_degrees + error
        speed *= -1
     self.pid.setpoint = target
     control_signal = self.pid(current_degrees)
        
     # Absolute safety check
     if angle > 91 and self.enc >= 4 or angle < -91 and self.enc >= 4:
        self.move_motor(0)
        print("ERR: Cord limit reached!")
        return True
     if abs(error) <2.5:
         self.move_motor(0)
         if(debug):
           print(f"Centered at {current} kP: {self.pid.Kp} kI: {self.pid.Ki} kD: {self.pid.Kd}")
         return True
     if(abs(error) < 10 and self.enc <= 3):
         self.move_motor(0)
         return True
     else:
         self.move_motor(control_signal * speed)
           
         
         if(debug):  
           print(f"Enc: {self.enc} | Error {error} Target: {target} | Current: {current_degrees} | Power: {control_signal}")
         return False

  """
  Method: rotateForward(angle {degrees} ,speed)
  Purpose: handles the logic for moving the wheel motors forward and backward    
  """
  def rotateForward(self,position,speed, isBack,debug):
    
        if((position < 0 or (position > 0 and self.polarity < 0)) and isBack):
            return self.drive_neg(self.polarity * position,speed,debug)
        self.pid.Kp = 0.06
        self.pid.Kd = 0.0002
        self.pid.Ki = 0.0002
        return self.drive(self.polarity * position,speed,debug)

  """
  Method: drive(target {Quadrature}, speed)
  Purpose: the logic that tells the motor to keep running until it reaches its desired location
  """
  def drive(self,target,speed,debug):
      current = self.getCurrentPosition()
      self.pid.setpoint = target
      motor_speed = self.pid(current)
      motor_speed *= speed
      if(self.polarity == 1):
      

        bool = current >= target
        if(bool):
            print(f"===Encoder: {self.enc} Stopped===")
            self.move_motor(0)

        else:
            if(debug):
              print(f"Target: {target} | Current: {current} Encoder: {self.enc} |  Speed: {motor_speed}")
            self.move_motor(motor_speed)
      else:
            bool = current <= -target
            if(bool):
                print(f"Encoder: {self.enc} Stopped===")
                self.move_motor(0)
            else:
                self.move_motor(motor_speed)
      return bool


  """
  Method: drive_neg(target {quadrature}, speed)
  Purpose: allows the motors that need to drive towards negative quadrature values to be able to move with the other motors
  """
  def drive_neg(self,target,speed,debug):
      current = self.getCurrentPosition()
      self.pid.setpoint = target
      motor_speed = self.pid(current)
      motor_speed *= -speed
      
      if(self.polarity == 1):
      

        bool = current <= target
        if(bool):
            print(f"===Encoder: {self.enc} Stopped===")
            self.move_motor(0)

        else:
            if(debug):
              print(f"Target: {target} | Current: {current} Encoder: {self.enc} |  Speed: {motor_speed}")
            self.move_motor(motor_speed)
      else:
            bool = current >= -target
            if(bool):
                print(f"Encoder: {self.enc} Stopped===")
                self.move_motor(0)
            else:
                self.move_motor(motor_speed)
      return bool
  """
  Method: stopMotor()
  Purpose: sets the motor speed equal to 0
  """
        
  def stopMotor(self):

      self.move_motor(0)

  """
  Method: getCurrentPosition()
  Purpose: returns the position of the object's encoder from the OctoQuad
  """

  def getCurrentPosition(self):
      self.read_octoquad()
      # print(RotationalMotor.positions)
      
      return RotationalMotor.positions[self.enc]

  """
  Method: resetEncoder()
  Purpose: resets the relative quadrature encoder values for the wheel motors
  """
  def resetEncoder(self):
      bus.write_i2c_block_data(0x30, 0x04, [0x15, 0x0F])


  #input distance in m, speed -1.0 to 1.0
  def switchPolarity(self):
      self.polarity = -self.polarity 
  def getPolarity(self):
      return self.polarity
  def setPolairty(self, polar):
      self.polarity = polar
  """
  Method: setValue(kP,Ki,Kd)
  Purpose: mostly for debugging PID values.
  """
  def setValue(self,value,value2,value3):
      self.pid.Kp = value
      self.pid.Ki = value2
      self.pid.Kd = value3

  """
  Method: read_octoquad()
  Purpose: returns a list of all of the current positions of the absolute and relative encoders
  """
  def read_octoquad(self):
    """Uses atomic I2C transactions to prevent data byte-shifting"""
    # Read 32 bytes (8 channels * 4 bytes each)
    write = i2c_msg.write(0x30, [0x1C])
    read = i2c_msg.read(0x30, 32) 
    bus.i2c_rdwr(write, read)
    
    # Unpack as 8 signed 32-bit integers
    RotationalMotor.positions = struct.unpack('<8i', bytes(list(read)))
       
  def setSpeed(self,speed):
      self.move_motor(speed)
    

"""
TESTING GROUND FOR ROTATIONAL MOTOR

given a pca address, pin value, and a side
"""
"""
try:
    i2c = board.I2C()
    pca = PCA9685(i2c)
    pca.frequency = 50
    pin = 6
    side = "r"
    idealfVal =538
    channel = 3
    rotMotor = RotationalMotor(pca,pin,side,channel,idealfVal,"P")
    #val = rotMotor.adjustForward()
    # while(val):
    #     val = rotMotor.adjustForward()
    #     print(rotMotor.getCurrentPosition())
    # print("finshed")
    print("Adjusting forward...")
    
    
    while True:
        value = float(input("gimme a Kp"))
        value2 = float(input("gimme a Kp"))
        value3 = float(input("gimme a Kp"))
         
        rotMotor.setValue(value,value2,value3)





        val = False
        d+= 90
        while(not val):
      
            val = rotMotor.adjustForward()  
            time.sleep(0.02)
            val = False
        while(not val):
            val = rotMotor.rotate(90,.1)
            time.sleep(0.02)
    

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
    #    val = rotMotor.rotateForward(target,.1)
    #val = True
    while(not val):
        val = rotMotor.adjustForward()
        time.sleep(0.02)
    #print("Rotation complete!")  
    # startPos = rotMotor.getCurrentPosition()
    # val = rotMotor.move(0.5,.1,startPos)
    # while(val):
    rotMotor.stopMotor()
    #val = rotMotor.move(0.5,.1)
except KeyboardInterrupt:
    rotMotor.stopMotor()"""

