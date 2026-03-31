import time
from .Motor import WheelMotor
from .RotationalMotor import RotationalMotor
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
        pin_list_rotational = [["pin","side"]]
        print("readying wheel motors...")
        for i in pin_list_wheel:
            motor = WheelMotor(pca,i[0], i[1])
            self.wheel_motor_list.append(motor)
        print("readying rotational motors...")
        for i in pin_list_rotational:
            motor = RotationalMotor(pca, i[0],i[1])
            self.rotational_motor_list.append(motor)
        
    def moveWheels(self, i):
        print("moving forward")
        if(i < -1 or i > 1):
            print("ERR: invalid input")
            return
        for motor in self.motor_list:
            motor.move_motor(i)

    def __del__(self):
        for motor in self.motor_list:
            motor.move_motor(0)
        time.sleep(3)
        print("finished")
   
        


