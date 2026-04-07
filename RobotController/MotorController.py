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

        pin_list_rotational = [[2,"l",0,0],[3,"l",1,0],[4, "l",2,0],[6,"l",3,0],[11,'l',6,0],[10,'l',5,0],[13,'r',4,0],[15,'r',7,0]]

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

    def adjustForward(self, resetWheels):

        cond1 = True

        cond2 = False

        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False

        stopCond = False

        if(resetWheels):

            motor1,motor2,motor3,motor4 = self.rotational_motor_list[4:8]

        else:

            motor1,motor2,motor3,motor4 = self.rotational_motor_list[0:4]

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

        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False


        stopCond = False

        if(whichMotor == "w"):

            motor1,motor2,motor3,motor4 = self.rotational_motor_list[4:8]

            angle1 = angle + (motor1.getCurrentPosition()/8192)*360

            angle2 = angle + (motor2.getCurrentPosition()/8192)*360

            angle3 = angle + (motor3.getCurrentPosition()/8192)*360

            angle4 = angle + (motor4.getCurrentPosition()/8192)*360
            print(angle1,angle2,angle3,angle4)
            print(str(motor4.getCurrentPosition()) + "CP")

        else:

            angle1=angle2=angle3=angle4=angle

            motor1,motor2,motor3,motor4 = self.rotational_motor_list[0:4]

        while(not stopCond):

            if(not isMotorAligned1):

                isMotorAligned1 = motor1.rotateForward(angle1,-speed)

            if(not isMotorAligned2):

                isMotorAligned2 = motor2.rotateForward(angle2,speed)

            if(not isMotorAligned3):

                isMotorAligned3 = motor3.rotateForward(angle3,speed)

            if(not isMotorAligned4):

                print(angle4)

                isMotorAligned4 = motor4.rotateForward(angle4,speed)

            stopCond = isMotorAligned1 and isMotorAligned2 and isMotorAligned3 and isMotorAligned4

            #if(whichMotor == "w"):

             #   stopCond = isMotorAligned1 or isMotorAligned2 or isMotorAligned3 or isMotorAligned4

        self.stopMotors()

    def moveDistance(self, distance,speed):

        rev_dis = distance / .144

        degree_dis = rev_dis *360

        print(degree_dis)

        self.rotate(degree_dis,speed,"w")

    def stopMotors(self):

        for motor in self.rotational_motor_list:

            motor.stopMotor()

    def __del__(self):

        for motor in self.wheel_motor_list:

            motor.move_motor(0)

        for motor in self.rotational_motor_list:

            motor.stopMotor()

        time.sleep(2)

        print("finished")

   

#try:       

mc = MotorController()

time.sleep(3)

#mc.adjustForward(False)

#mc.adjustForward(True)

#time.sleep(1)

#mc.rotate(-45,.1,"r")

#time.sleep(1)

#mc.adjustForward(False)

#time.sleep(1)

#mc.moveDistance(0.5,0.1)

#mc.rotate(-45,.3,"w")

#time.sleep(1)

while True:

    rot = input("To which degree")

    mc.rotate(int(rot),0.3,"w")

#except KeyboardInterrupt:

 #   mc.stopMotors() 
