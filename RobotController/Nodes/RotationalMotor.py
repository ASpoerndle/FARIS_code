import struct
from smbus2 import SMBus
from Motor import WheelMotor
import board
from adafruit_pca9685 import PCA9685
import Jetson.GPIO as GPIO
import time
import math
from simple_pid import PID
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
    with SMBus(RotationalMotor.I2C_BUS) as bus:
            # Set Bank 0 to PWM (Absolute), Bank 1 to Quad
            bus.write_i2c_block_data(RotationalMotor.I2C_ADDR, 0x04, [0x01, 0x02, 2])
            # Set Min/Max for absolute channels (1-1024)
            bus.write_i2c_block_data(RotationalMotor.I2C_ADDR, 0x04, [0x01, 0x04, self.enc, 1, 0, 0, 4])
            # Enable Wrap Tracking for absolute channels
            # bus.write_i2c_block_data(RotationalMotor.I2C_ADDR, 0x04, [0x01, 0x05, 0x0F])
            # Save to Flash ONCE
            bus.write_byte_data(self.I2C_ADDR, 0x04, 0x03)
            time.sleep(0.1) # Give it time to save
    if(side == "r"):

        self.polarity = -1

    else:

        self.polarity = 1

    self.fVal = fVal

    self.currentCount = fVal
    #Kp = 0.006
    #Ki = 0.000008
    #Kd = 0.000001

    self.read_octoquad()
    self.pid = PID(0.05,0.000019,0.001, setpoint=(fVal)) 
    self.pid.output_limits=(-.6,.6)
  
  #Returns T/F based on if it's off-centered, put a while loop in MotorController class so it can adjust all motors at once
  
  # def adjustForward(self):
  #   self.read_octoquad()
  #   # currentPos is in raw microseconds (1 to 1024)
  #   currentPos = self.getCurrentPosition() 
    
  #   # Ensure your target (fVal) is ALSO in microseconds
  #   target_us = self.fVal 
  #   total_range = 1023 # (Max - Min)
  #   half_range = total_range / 2

  #   # Normalize error to be within [-half_range, +half_range]
  #   # This prevents the motor from spinning 359 degrees to move 1 degree
  #   error = (target_us - currentPos + half_range) % total_range - half_range
  #   #error = self.fVal - currentPos
  #   # Pass the raw error-based setpoint to the PID
  #   self.pid.setpoint = currentPos + error
  #   control_signal = self.pid(0)

  #   if abs(error) < 1.5: # Equivalent to roughly 0.7 degrees
  #       self.motor.move_motor(0)
  #       return True
  #   else:
  #       self.motor.move_motor(0.1*control_signal)
  #       return False
  def adjustForward(self):
      self.read_octoquad()
      currentPos = self.getCurrentPosition() 
      
      if self.enc <= 3:
            #Convert pwm to degrees
            self.fVal = ((self.fVal-1)/1023)*360
            #convert current pos to degrees
            currentPos = ((currentPos-1)/1023)*360
        
            error = (self.fVal - currentPos + 180) % 360 - 180
            self.pid.setpoint = currentPos + error
            feedback = currentPos
      else:
            # RELATIVE LOGIC (8192 range)
            feedback = (currentPos / 8192.0) * 360.0
            error = self.fVal - feedback
            self.pid.setpoint = self.fVal

      control_signal = self.pid(feedback)

      if abs(error) < 0.5:
            self.motor.move_motor(0)
            return True
      else:
            # Note: Negative sign here should match your motor polarity
            self.motor.move_motor(control_signal * 0.1)
            return False

  
  def setMotorSpeed(self,speed):
        self.motor.move_motor(speed)

  def rotate(self, angle, speed):
     speed = abs(speed)
     current = self.getCurrentPosition()
     self.read_octoquad()
     current_degrees = (current / 8192) * 360
     angle += (self.fVal/8192)*360
     self.pid.setpoint = angle
     fDegree = (self.fVal/8192)*360   
     control_signal = self.pid(current_degrees)
     # 3. ACT: Update the motor
     control_signal *= speed
    
     error = abs(current_degrees - angle)
     if abs(error) < 0.5:
         self.motor.move_motor(0)
         print(f"Centered at {current} kP: {self.pid.Kp} kI: {self.pid.Ki} kD: {self.pid.Kd}")
         return True
     else:
         self.motor.move_motor(self.polarity * control_signal)
           # Log status
         direction = "Left" if control_signal > 0 else "Right"
         print(f"{self.enc} + {error} Target: {angle}° | Current: {current:.1f}° | Power: {control_signal:.2f} | Adjusting: {direction}")
         return False


  def rotateForward(self,angle,speed):
    

        speed = abs(speed)
        self.pid.Kp = 0.05
        self.pid.Kd = 0.0002
        self.pid.Ki = 0.000175
        return self.rotate(self.polarity * angle,speed)
        
        """
        self.read_octoquad()
        angle_offset = 228
        self.currentCount = 0
        current = self.getCurrentPosition()
        if(self.polarity > 0):

            if(current - (angle/360) * 8192 - 228 < 0):
                print("left")
                cond = self.rotateLeft(angle, speed)

            if(current - (angle/360) * 8192 + 228 > 0):
                print("right")
                cond = self.rotateRight(angle , speed)

            if(angle == 0):

                cond = True

        else:
            

            if(-current+(angle/360) *8192 + 100 < 0):
                print("left")
                cond = self.rotateLeft(angle,speed)
                return cond
            if(-current+(angle/360)*8192 + 100> 0):
                print("right")
            

                cond = self.rotateRight(angle,speed)
                return cond
            if(angle == 0):

                cond = True

        if(cond):

            self.currentCount = self.getCurrentPosition()

            return True

        else:

            return False

  """
  def stopMotor(self):

      self.motor.move_motor(0)

  def rotateLeft(self, angle,  speed):
    
    current = self.getCurrentPosition()
    new_pos = (angle * 1024)/45  + self.currentCount
    if(current >0):
        new_pos *= -1
    print(f'Current position {current} | target {new_pos} speed {speed} | encoder: {self.enc}')
    if(current < new_pos and self.polarity > 0):

        self.motor.move_motor(speed)

        return False
    if(current > new_pos and angle > 0 and self.polarity >0):
        self.motor.move_motor(speed)
    if(self.polarity < 0):

        
            if(current > new_pos):
                

                self.motor.move_motor(speed)

                return False

    

    self.motor.move_motor(0)

    return True

    #TODO - if current Pos > forward - 90, rotate left

    

  def rotateRight(self, angle, speed):
      
    
    new_pos = (angle * 1024)/45 + self.currentCount

    print("CC: " + str(self.getCurrentPosition()))

    print("NP: " + str(new_pos))

    print("Encoder: " + str(self.enc) + "has speed of: " + str(speed*self.polarity))

    if(self.getCurrentPosition() > new_pos and self.polarity > 0):

     # print("moving motor...")

      self.motor.move_motor(-speed)

      return False

    elif(self.getCurrentPosition() < new_pos and self.polarity < 0):

        print("please work")

        self.motor.move_motor(-speed)

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
  def setValue(self,value,value2,value3):
      self.pid.Kp = value
      self.pid.Ki = value2
      self.pid.Kd = value3
  def read_octoquad(self):

      addr = 0x30
      with SMBus(RotationalMotor.I2C_BUS) as bus:
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


        # return position, velocity


    

"""
TESTING GROUND FOR ROTATIONAL MOTOR

given a pca address, pin value, and a side
"""

try:
    i2c = board.I2C()
    pca = PCA9685(i2c)
    pca.frequency = 50
    pin = 4
    side = "r"
    idealfVal = 203
    channel = 2
    rotMotor = RotationalMotor(pca,pin,side,channel,idealfVal,"P")
    #val = rotMotor.adjustForward()
    # while(val):
    #     val = rotMotor.adjustForward()
    #     print(rotMotor.getCurrentPosition())
    # print("finshed")
    print("Adjusting forward...")
    d = 0
    val = False
    """
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
    """

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
    #print("Rotation complete!")  
    # startPos = rotMotor.getCurrentPosition()
    # val = rotMotor.move(0.5,.1,startPos)
    # while(val):
    rotMotor.stopMotor()
    #val = rotMotor.move(0.5,.1)
except KeyboardInterrupt:
    rotMotor.stopMotor()
