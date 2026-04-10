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

  def __init__(self, pca, pin, side, enc, fVal):

    self.motor = WheelMotor(pca,pin,side)

    self.enc = enc

    if(side == "r"):

        self.polarity = -1

    else:

        self.polarity = 1

    self.fVal = fVal

    self.currentCount = fVal
    Kp = 0.007
    Ki = 0.00004
    Kd = 0.0001

    self.read_octoquad()
    self.pid = PID(Kp, Ki, Kd, setpoint=(fVal/8192)*360) 
    self.pid.output_limits=(-0.8,0.8)
  
  #Returns T/F based on if it's off-centered, put a while loop in MotorController class so it can adjust all motors at once
  
  def adjustForward(self):
      self.read_octoquad()
      currentPos = RotationalMotor.positions[self.enc] 
      current_degrees = (currentPos / 8192) * 360
    
    
      control_signal = self.pid(current_degrees)
    # 3. ACT: Update the motor
    
      error = (self.fVal/8192)*360 - current_degrees
      if abs(error) < 0.5:
          self.motor.move_motor(0)
          print(f"Centered at {current_degrees}")
          return True
      else:
          self.motor.move_motor(control_signal)
          # Log status
          direction = "Left" if control_signal > 0 else "Right"
          print(f"Target: 0° | Current: {current_degrees:.1f}° | Power: {control_signal:.2f} | Adjusting: {direction}")
          return False

      """
      if(currentPos > self.fVal - 0 and currentPos < self.fVal + 0):
         self.motor.move_motor(0)
         return True
      elif(currentPos < self.fVal):
        self.motor.move_motor(control_signal) #0.1
        print(f"Target: 0° | Current: {current_degrees:.2f}° | Power: {control_signal:.2f}")
        time.sleep(0.02) # Run at 50Hz
        print("rotate left for center")
        return False

      else:
          print(f"Target: 0° | Current: {current_degrees:.2f}° | Power: {control_signal:.2f}")
          time.sleep(0.02) # Run at 50Hz
          self.motor.move_motor(control_signal) #-0.1
          print("rotate right for center")
          return False
"""
  #right is neg, left is pos

  def setMotorSpeed(self,speed):
        self.motor.move_motor(speed)

  def rotate(self, angle, speed):
     speed = abs(speed)
     current = self.getCurrentPosition()
     self.read_octoquad()
     current_degrees = (current / 8192) * 360
     angle += 2*(self.fVal/8192)*360
     self.pid.setpoint = angle
     fDegree = (self.fVal/8192)*360   
     control_signal = self.pid(current_degrees)
     # 3. ACT: Update the motor
    
     error = current_degrees - angle
     if abs(error)-fDegree < 0.5:
         self.motor.move_motor(0)
         print(f"Centered at {current_degrees}")
         return True
     else:
         self.motor.move_motor(control_signal)
           # Log status
         direction = "Left" if control_signal > 0 else "Right"
         print(f"{self.enc} + {error} Target: {angle}° | Current: {current_degrees:.1f}° | Power: {control_signal:.2f} | Adjusting: {direction}")
         return False


  def rotateForward(self,angle,speed):
    

        speed = abs(speed)
        self.rotate(angle,speed)
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


        # return position, velocity




"""
TESTING GROUND FOR ROTATIONAL MOTOR

given a pca address, pin value, and a side
"""

try:
    i2c = board.I2C()
    pca = PCA9685(i2c)
    pca.frequency = 50
    pin = 11
    side = "l"
    idealfVal = 0
    channel = 6
    rotMotor = RotationalMotor(pca,pin,side,channel,idealfVal)
    #val = rotMotor.adjustForward()
    # while(val):
    #     val = rotMotor.adjustForward()
    #     print(rotMotor.getCurrentPosition())
    # print("finshed")
    print("Adjusting forward...")
    
    val = False
    while(not val):
        #val = rotMotor.adjustForward()
      val = rotMotor.rotateForward(90,0.4)  
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
    #while(val):
    #    val = rotMotor.adjustForward()
    #print("Rotation complete!")  
    # startPos = rotMotor.getCurrentPosition()
    # val = rotMotor.move(0.5,.1,startPos)
    # while(val):
    rotMotor.stopMotor()
    #val = rotMotor.move(0.5,.1)
except KeyboardInterrupt:
    rotMotor.stopMotor()
