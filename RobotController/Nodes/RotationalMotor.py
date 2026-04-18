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
  def init_hardware(self):
    """Configures the OctoQuad once based on spec 3.0C"""
    print("Configuring OctoQuad hardware...")
# SetParam (0x01), WrapTrack ID (0x05), Bitfield (0x00 to disable all)
    bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x05, 0xF0])

    # 1. Set Bank Mode: Bank 1 (0-3) = Absolute/PWM, Bank 2 (4-7) = Quad
    # [Cmd, ParamID, Value]
    bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x02, 2]) 
    # 2. Set Min/Max for Absolute Channels (Default 1us to 1024us)
    # Necessary for correct degree math and velocity
    if(self.enc>=4):
        # [Cmd, ParamID, Channel, Min_L, Min_H, Max_L, Max_H]
        bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x04, self.enc, 1, 0, 0, 4])
        bus.write_i2c_block_data(0x30,0x04, [0x01,0x05,0xF0])
        #bus.write_i2c_block_data(0x30, 0x04, [0x01, 0x05, self.enc, 0]) 
    # 3. Save to Flash
    bus.write_byte_data(0x30, 0x04, 0x03)
    time.sleep(0.1)
    print("Hardware ready.")

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
      
      rawPos = self.getCurrentPosition() 
      if self.enc >=4:
          #Convert pwm to degrees
            target = ((self.fVal-1)/1023.0)*360
            #convert current pos to degrees
            currentDeg = ((rawPos-1)/1023.0)*360
        
            error = (target - currentDeg + 180) % 360 - 180
            self.pid.setpoint = currentDeg + error
            feedback = currentDeg
      else:
            # RELATIVE LOGIC (8192 range)
            feedback = (currentPos / 8192.0) * 360.0
            error = self.fVal - feedback
            self.pid.setpoint = self.fVal

      control_signal = self.pid(feedback)
      print(f"Target: {target} | Current: {currentDeg} Encoder: {self.enc} | Error: {error} | Speed: {control_signal}")      
       
      if abs(error) < 1:
            print(f"error: {error}")
            self.motor.move_motor(0)
            return True
      else:
            # Note: Negative sign here should match your motor polarity
            self.motor.move_motor(-control_signal)

            return False

  
  def setMotorSpeed(self,speed):
        self.motor.move_motor(speed)

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
      self.read_octoquad()
      print(RotationalMotor.positions)
      
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
    """Uses atomic I2C transactions to prevent data byte-shifting"""
    # Read 32 bytes (8 channels * 4 bytes each)
    write = i2c_msg.write(0x30, [0x1C])
    read = i2c_msg.read(0x30, 32) 
    bus.i2c_rdwr(write, read)
    
    # Unpack as 8 signed 32-bit integers
    RotationalMotor.positions = struct.unpack('<8i', bytes(list(read)))
        # for i, val in enumerate(positions):

        #     channels[i] = val


        # return position, velocity


    

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
