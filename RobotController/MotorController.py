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
        #pin_list_wheel = [[11, 'l'],[10,'l'],[13,'r'],[15,'r']]
        pin_list_rotational = [[2,"l",0,0],[3,"l",1,-200],[4, "l",2,0],[6,"l",3,0],[11,'l',6,0],[10,'l',5,0],[13,'r',4,0],[15,'r',7,0]]
        #print("readying wheel motors...")
        #for i in pin_list_wheel:
        #    motor = WheelMotor(pca,i[0], i[1])
        #    self.wheel_motor_list.append(motor)
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
        stopCond = False
        motor1 = self.rotational_motor_list[0]
        motor2 = self.rotational_motor_list[1]
        motor3 = self.rotational_motor_list[2]
        motor4 = self.rotational_motor_list[3]
        isMotorAligned3 = False
        isMotorAligned4 = False
        while(not stopCond):
            if(not isMotorAligned1):
                cond1 = motor1.adjustForward()
                isMotorAligned1 = cond1
            if(not isMotorAligned2):
                cond2 = motor2.adjustForward()
                isMotorAligned2 = cond2
            if(not isMotorAligned3):
                isMotorAligned3 = motor3.adjustForward()
            if(not isMotorAligned4):
                isMotorAligned4 = motor4.adjustForward()
            stopCond = isMotorAligned2 and isMotorAligned1 and isMotorAligned3 and isMotorAligned4
        self.stopMotors()
    def rotate(self,angle,speed, whichMotor):
        isMotorAligned1 = False
        isMotorAligned2 = False
        isMotorAligned3 = False
        isMotorAligned4 = False
        stopCond = False
        if(whichMotor == "w"):
            motor1 = self.rotational_motor_list[4]
            motor2 = self.rotational_motor_list[5]
            motor3 = self.rotational_motor_list[6]
            motor4 = self.rotational_motor_list[7]
            angle = angle + (motor3.getCurrentPosition()/8192)*360
        else:
            motor1 = self.rotational_motor_list[0]
            motor2 = self.rotational_motor_list[1]
            motor3 = self.rotational_motor_list[2]
            motor4 = self.rotational_motor_list[3]
        while(not stopCond):
            if(not isMotorAligned1):
                cond1 = motor1.rotate(angle,speed)
                isMotorAligned1 = cond1
            if(not isMotorAligned2):
                cond2 = motor2.rotate(angle,speed)
                isMotorAligned2 = cond2
            if(not isMotorAligned3):
                isMotorAligned3 = motor3.rotate(angle,speed)
            if(not isMotorAligned4):
                isMotorAligned4 = motor4.rotate(angle,speed)
            stopCond = isMotorAligned1 and isMotorAligned2 and isMotorAligned3 and isMotorAligned4
            #if(whichMotor == "w"):
             #   stopCond = isMotorAligned1 or isMotorAligned2 or isMotorAligned3 or isMotorAligned4
        self.stopMotors()
    def moveDistance(self, distance,speed):
        rev_dis = distance / .144
        degree_dis = rev_dis *360
        self.rotate(degree_dis,speed,"w")
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
time.sleep(3)
mc.adjustForward()
time.sleep(1)
mc.rotate(-45,.1,"r")
time.sleep(1)
mc.adjustForward()
time.sleep(1)
#mc.moveDistance(0.5,0.1)
#mc.rotate(-45,.3,"w")
#time.sleep(1)
mc.rotate(-90,0.3,"w")
#except KeyboardInterrupt:
 #   mc.stopMotors()
