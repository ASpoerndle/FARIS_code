import board
import time
import busio
from adafruit_pca9685 import PCA9685
import Jetson.GPIO as GPIO
"""
Class: Motor
@Author: Aidan Spoerndle
Purpose: The Motor class is the most basic version of the code required to move the various GoBilda Yellowjacket
         motors attached to the robot. 
"""
class Servo:
    
    def __init__(self,pca, pin, maxi=270):
        self.servo = pca.channels[pin]
        #max = 10500
        #min = 1750
        self.max = maxi 
    
    """
    Method: setAngle(angle)
    Purpose: sets the duty cycle to between values of 1750 and 10500 depending on the ratio between the user given angle and the max angle the servo can 
    handle
    """
    def setAngle(self,angle):
        angle = angle % 360
        if(angle > self.max):
            print("ERR: Angle too large")
        angle /= self.max
        duty = angle * 8750 +1750
        self.servo.duty_cycle = int(duty)
    """
    Method: kill_motor()
    Purpose: sets the duty cycle to 0 so that the motor neither moves nor provides resistance to outside forces
             attempting to move it. This was done so that the motors can be adjusted easily and without damaging them.
    """ 
    def killServo(self):
        self.servo.duty_cycle = 0
    def __init__(self,pca, pin, maxi=270):
        self.servo = pca.channels[pin]
        #max = 10500
        #min = 1750
        self.max = maxi 
""" 
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 60
         
        
servo = Servo(pca,8)
servo.setAngle(180)
time.sleep(1)
servo.setAngle(90)
time.sleep(1)
servo.setAngle(75)
time.sleep(1)
input("...")
servo.killServo()

GPIO.cleanup()
"""
