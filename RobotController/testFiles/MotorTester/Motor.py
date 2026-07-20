import board
import time
from adafruit_pca9685 import PCA9685

"""
Class: Motor
@Author: Aidan Spoerndle
Purpose: The Motor class is the most basic version of the code required to move the various GoBilda Yellowjacket
         motors attached to the robot. 
"""
class Motor:
    defaultForward = 5400
    defaultReverse = 5000
    currentDuty = 5200

    def __init__(self, pca, pin, side):
        self.motor = pca.channels[pin]
        self.motor.duty_cycle = 5200
        self.side = side

    """
    Method: forward_motion(speed)
    Purpose: Adjusts the motors duty cycle proportionally to an inputted float speed so that the 
             robot can move forward
    """
    def forwardMotion(self, speed):
        
        newSpeed = Motor.defaultForward + (1300 * speed)
        self.motor.duty_cycle = int(newSpeed)
        Motor.currentDuty = int(newSpeed)
    """
    Method: backward_motion(speed)
    Purpose: Adjusts the motors duty cycle proportionally to an inputted float speed so that
             the robot can move backward
    """
    def backwardMotion(self,speed):
        
        newSpeed = Motor.defaultReverse + (1300 * speed)
        self.motor.duty_cycle = int(newSpeed)
        Motor.currentDuty = int(newSpeed)
    """
    Method: zero_motion()
    Purpose: sets the motor duty cycle to a motionless speed (5200 mHz)
    """
    def zeroMotion(self):
        self.motor.duty_cycle = 5200
        Motor.currentDuty = 5200
    """
    Method: kill_motor()
    Purpose: sets the duty cycle to 0 so that the motor neither moves nor provides resistance to outside forces
             attempting to move it. This was done so that the motors can be adjusted easily and without damaging them.
    """
    def killMotor(self):
        self.motor.duty_cycle = 0
        Motor.currentDuty = 0

    """
    Method: move_motor(speed)
    Purpose: takes a float input {speed} and calls the proper method depending on which side the motor is on
             and whether the inputted speed is positive or negative
    """
    def moveMotor(self, speed):
        if(speed > 0 and speed <= 1):
            if(self.side == 'r'):
                speed *= -1
                self.backwardMotion(speed)
                return
            self.forwardMotion(speed)
            
        elif(speed < 0 and speed >= -1):
            if(self.side == 'r'):
                speed *=-1
                self.forwardMotion(speed)
                return
            self.backwardMotion(speed)

        elif(speed == 0):
            self.zeroMotion()

    #def __del__(self):
        #self.killMotor()
"""
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50
pin = 13
side = "r"
motor = Motor(pca,pin,side)
try:
    while(True):
        speed = input("What speed?")
        motor.moveMotor(float(speed))

except KeyboardInterrupt:
    motor.killMotor()
"""
