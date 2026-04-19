import struct
import smbus2
from smbus2 import i2c_msg
from Motor import WheelMotor
import board
from adafruit_pca9685 import PCA9685
import Jetson.GPIO as GPIO
import time
import math
from simple_pid import PID
bus = smbus2.SMBus(1)
class RotationalMotor():

  I2C_ADDR = 0x30

  I2C_BUS = 1

  positions = [0,0,0,0,0,0,0,0]

  velocities = [0,0,0,0,0,0,0,0]  

  WHEELDIAMETER = .144

  WHEELC = WHEELDIAMETER * math.pi
  #=========
  #pip install simple-pid
  #=========
  
  #left is more pos, right is more neg

  def __init__(self, pca, pin, side, enc, fVal,mType):

    self.motor = WheelMotor(pca,pin,side)
    self.mType = mType
    self.enc = enc
    self.init_hardware()
    
    if(side == "r"):

        self.polarity = -1

    else:

        self.polarity = 1

    self.fVal = fVal

    self.currentCount = fVal
    #Kp = 0.006
    #Ki = 0.000008
    #Kd = 0.000001

    
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

  #Returns T/F based on if it's off-centered, put a while loop in MotorController class so it can adjust all motors at once
  
 
  def adjustForward(self):
      
      currentPos = self.getCurrentPosition() 
      
            #convert fVal pwm into degrees
      target = ((self.fVal-1)/1023.0)*360
            #convert current raw position to degrees
      currentDeg = ((currentPos-1)/1023.0)*360
            #calc the difference betweentarget and currentDeg
            # error = (target - currentDeg + 180) % 360 - 180
      error = target - currentDeg
      self.pid.setpoint = currentDeg + error
      feedback = currentDeg

      control_signal = self.pid(feedback)
      print(f"Target: {target} | Current: {currentDeg} Encoder: {self.enc} | Error: {error} | Speed: {control_signal}")      
       
      if abs(error) < 1:
            
            self.motor.move_motor(0)
            return True
      else:
          
            self.motor.move_motor(-control_signal)

            return False

  
  #covers both 90 degree rotations and forward/backward rotations
  def rotate(self, angle, speed):
     speed = abs(speed)
     current = self.getCurrentPosition()
     if(self.enc <=3):
        current_degrees = (current/8192) * 360
         
        angle += ((self.fVal-1)/1023)*360
        target = angle
     else:
        #current_degrees = ((current-1)/1023) * 360
        current_degrees = ((current - 1)/1023) * 360
        target = ((self.fVal-1)/1023)*360 + angle
        speed *= -1
     self.pid.setpoint = target
     control_signal = self.pid(current_degrees)
     # 3. ACT: Update the motor
    
     error = abs(current_degrees - target)
     if abs(error % 180) <0.75  :
         self.motor.move_motor(0)
         print(f"Centered at {current} kP: {self.pid.Kp} kI: {self.pid.Ki} kD: {self.pid.Kd}")
         return True
     else:
         self.motor.move_motor(self.polarity * control_signal * speed)
           # Log status
         direction = "Left" if control_signal > 0 else "Right"
         print(f"Enc: {self.enc} + Error {error} Target: {target}° | Current: {current_degrees:.1f}° | Power: {control_signal:.2f} | Adjusting: {direction}")
         return False

  
  def rotateForward(self,angle,speed):
    

        speed = abs(speed)
        self.pid.Kp = 0.06
        self.pid.Kd = 0.0002
        self.pid.Ki = 0.0002
        return self.rotate(self.polarity * angle,speed)
        
        
  def stopMotor(self):

      self.motor.move_motor(0)

  

  def getCurrentPosition(self):
      self.read_octoquad()
      print(RotationalMotor.positions)
      
      return RotationalMotor.positions[self.enc]



  #input distance in m, speed -1.0 to 1.0

  
  # OctoQuad default settings
  def setValue(self,value,value2,value3):
      self.pid.Kp = value
      self.pid.Ki = value2
      self.pid.Kd = value3
  def read_octoquad(self):
    """Uses atomic I2C transactions to prevent data byte-shifting"""
    # Read 32 bytes (8 channels * 4 bytes each)
    write = i2c_msg.write(0x30, [0x1C])
    read = i2c_msg.read(0x30, 32) 
    bus.i2c_rdwr(write, read)
    
    # Unpack as 8 signed 32-bit integers
    RotationalMotor.positions = struct.unpack('<8i', bytes(list(read)))
       

    

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
