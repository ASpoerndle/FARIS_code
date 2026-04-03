import time
from Motor import WheelMotor
from RotationalMotor import RotationalMotor
import board
from adafruit_pca9685 import PCA9685

import Jetson.GPIO as GPIO
import time


class MotorController():

    def __init__(self):
        
        pin1 = 31
        pin2 = 29
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
        GPIO.setup(pin1, GPIO.IN)  # pin 31
        GPIO.setup(pin2, GPIO.IN) # pin 29


        input1 = GPIO.input(pin1)  # Read input
        input2 = GPIO.input(pin2)





        i2c = board.I2C()
        pca = PCA9685(i2c)
        pca.frequency = 50

        self.wheel_motor_list = []
        self.rotational_motor_list = []
        pin_list_wheel = [[11, 'l'],[10,'l'],[13,'r'],[15,'r']]
        pin_list_rotational = [[2,"l",0,0],[3,"r",1,0]]
        print("readying wheel motors...")
        for i in pin_list_wheel:
            motor = WheelMotor(pca,i[0], i[1])
            self.wheel_motor_list.append(motor)
        print("readying rotational motors...")
        for i in pin_list_rotational:
            motor = RotationalMotor(pca, i[0],i[1],i[2],i[3])
            self.rotational_motor_list.append(motor)
        
    def moveWheels(self, i):
        print("moving forward")
        if(i < -1 or i > 1):
            print("ERR: invalid input")
            return
        for motor in self.wheel_motor_list:
            motor.move_motor(i)
    def adjustForward(self):
        cond1 = True
        cond2 = False
        isMotorAligned1 = False
        isMotorAligned2 = False
        motor1 = self.rotational_motor_list[0]
        motor2 = self.rotational_motor_list[1]
        while((cond1 and cond2) or ( not isMotorAligned1 and not isMotorAligned2)):
            if(not isMotorAligned1):
                cond1 = motor1.adjustForward()
                isMotorAligned1 = cond1
            if(not isMotorAligned2):
                cond2 = motor2.adjustForward()
                isMotorAligned2 = cond2
        self.stopMotors()
    def stopMotors(self):
        for motor in self.rotational_motor_list:
            motor.stopMotor()
    def __del__(self):
        for motor in self.wheel_motor_list:
            motor.move_motor(0)
        for motor in self.rotational_motor_list:
            motor.stopMotor()
        time.sleep(3)
        print("finished")
   
#try:       
mc = MotorController()
mc.adjustForward()
#except KeyboardInterrupt:
 #   mc.stopMotors()
