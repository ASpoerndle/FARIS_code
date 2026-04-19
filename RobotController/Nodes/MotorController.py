import time

from .Motor import WheelMotor

from .RotationalMotor import RotationalMotor

import board

from adafruit_pca9685 import PCA9685

import Jetson.GPIO as GPIO

import time
import math

#50.9:1 and 71.2:1
class MotorController():
    def __init__(self):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
        
        i2c = board.I2C()
        pca = PCA9685(i2c)
        pca.frequency = 50
        self.wheel_motor_list = []
        self.rotational_motor_list = []

        # pin_list_wheel = [[11, 'l'],[10,'l'],[13,'r'],[15,'r']]
        # 265 207
        pin_list_rotational = [[2, "l", 4, -18553,"P"], [3, "l", 5, -11016,"P"], [4, "l", 6, -81946,"P"], [6, "l", 7, -13787,"P"], [11, 'l', 2, 0,"W"],
                               [10, 'l', 1, 0,"W"], [13, 'r', 0, 0,"W"], [15, 'r', 3, 0,"W"]]

        # print("readying wheel motors...")

        
        print("readying motors...")
        for i in pin_list_rotational:
            motor = RotationalMotor(pca, i[0], i[1], i[2], i[3],i[4])
            self.rotational_motor_list.append(motor)
        print("motors ready!")
    def moveWheels(self, i):
        print("moving forward")
        if (i < -1 or i > 1):
            print("ERR: invalid input")
            return
        for motor in self.wheel_motor_list:
            motor.move_motor(i)

    def adjustForward(self):
        cond1 = True
        cond2 = False
        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False
        stopCond = False
        motor1, motor2, motor3, motor4 = self.rotational_motor_list[0:4]
        while (not stopCond):
            if (not isMotorAligned1):
                cond1 = motor1.adjustForward()
                isMotorAligned1 = cond1
            if (not isMotorAligned2):
                cond2 = motor2.adjustForward()
                isMotorAligned2 = cond2
            if (not isMotorAligned3):
                isMotorAligned3 = motor3.adjustForward()
            if (not isMotorAligned4):
                isMotorAligned4 = motor4.adjustForward()
            stopCond = isMotorAligned2 and isMotorAligned1 and isMotorAligned3 and isMotorAligned4
            time.sleep(0.02)
        self.stopMotors()

    def rotateForward(self, angle,distance, speed):
        #117 rpm
        #y ticks = distance (m) * 355 ticks/m
        speed = .3
        #max_ticks = distance * 144
        max_ticks = (91 * abs(distance))/.2
        ticks = 0
        halfTicks = max_ticks // 2
        if(distance < .2 and distance > -0.2):
            ticks = halfTicks = max_ticks = -1
            speed = 0.5

        
        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False

        stopCond = False
        whichMotor = "w"
        if (whichMotor == "w"):

            motor1, motor2, motor3, motor4 = self.rotational_motor_list[4:8]

            angle1 = angle + (motor1.getCurrentPosition() / 8192) * 360

            angle2 = angle + (motor2.getCurrentPosition() / 8192) * 360

            angle3 = (motor3.getCurrentPosition() / 8192) * 360 - angle

            angle4 = (motor4.getCurrentPosition() / 8192) * 360 - angle
            print(angle1, angle2, angle3, angle4)
            print(str(motor4.getCurrentPosition()) + "CP")

        else:

            angle1 = angle2 = angle3 = angle4 = angle

            motor1, motor2, motor3, motor4 = self.rotational_motor_list[0:4]

        while (not stopCond):

            if (not isMotorAligned1):
                isMotorAligned1 = motor1.rotateForward(angle1, speed)

            if (not isMotorAligned2):
                isMotorAligned2 = motor2.rotateForward(angle2, speed)

            if (not isMotorAligned3):
                isMotorAligned3 = motor3.rotateForward(-angle3, speed)

            if (not isMotorAligned4):
                isMotorAligned4 = motor4.rotateForward(-angle4, speed)
            print(f'Ticks: {ticks} + Speed: {speed}')
            stopCond = (isMotorAligned1 or isMotorAligned2) or (isMotorAligned3 or isMotorAligned4)
            if(ticks <= halfTicks and speed <= 1 and max_ticks != -1):
                print("increase speed")
                speed += (1/halfTicks)
            elif(ticks > halfTicks and speed > 0.5 and max_ticks != -1):
                speed -=1/halfTicks
            ticks+= 1
            # if(whichMotor == "w"):
            time.sleep(0.02)
            #   stopCond = isMotorAligned1 or isMotorAligned2 or isMotorAligned3 or isMotorAligned4

        self.stopMotors()

    #       self.adjustForward()
    def rotatePods(self, angle, speed):

        cond1 = True

        cond2 = False

        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False

        stopCond = False

        motor1, motor2, motor3, motor4 = self.rotational_motor_list[0:4]

        while (not stopCond):

            if (not isMotorAligned1):
                cond1 = motor1.rotate(angle, speed)

                isMotorAligned1 = cond1

            if (not isMotorAligned2):
                cond2 = motor2.rotate(angle, speed)

                isMotorAligned2 = cond2

            if (not isMotorAligned3):
                isMotorAligned3 = motor3.rotate(angle, speed)

            if (not isMotorAligned4):
                isMotorAligned4 = motor4.rotate(angle, speed)

            stopCond = isMotorAligned2 and isMotorAligned1 and isMotorAligned3 and isMotorAligned4
            time.sleep(0.02)
        self.stopMotors()

    def moveDistance(self, distance, speed):

        rev_dis = distance / (.144 * math.pi)

        degree_dis = rev_dis * 360

        self.rotateForward(degree_dis,distance, speed)

    def horizontalMode(self):
        self.rotatePods(-90, 0.75)

    def stopMotors(self):

        for motor in self.rotational_motor_list:
            motor.stopMotor()
    def boxDrill(self,dis):
        self.adjustForward()
        self.moveDistance(dis, .1)
        time.sleep(1)
        self.horizontalMode()
        time.sleep(1)
        self.moveDistance(-dis, .1)
        time.sleep(1)
        self.adjustForward()
        time.sleep(1)
        self.moveDistance(-dis, .1)
        time.sleep(1)
        self.horizontalMode()
        time.sleep(1)
        self.moveDistance(dis, .1)
        self.adjustForward()

        print("complete")

    def __del__(self):

        for motor in self.wheel_motor_list:
            motor.move_motor(0)

        for motor in self.rotational_motor_list:
            motor.stopMotor()

        time.sleep(2)

        print("finished")


# try:
#distance = .01
#time.sleep(2)
#mc = MotorController()
#mc.boxDrill(0.2)
# time.sleep(3)

#mc.adjustForward()
#time.sleep(3)

#mc.moveDistance(.2, 0.25)
#time.sleep(1)
#time.sleep(1)
#mc.horizontalMode()
#time.sleep(1)
#mc.moveDistance(-.1, 0.25)
#time.sleep(1)
#mc.adjustForward()
#time.sleep(1)
#mc.moveDistance(-.1, 0.25)
#time.sleep(1)
#mc.horizontalMode()
#time.sleep(1)
#mc.moveDistance(.1, 0.25)
#mc.adjustForward()

print("complete")
# mc.adjustForward(True)

#time.sleep(1)
# mc.horizontalMode()
# mc.rotate(-45,.1,"r")

# time.sleep(1)


# time.sleep(1)

# while True:

#    rot = input("To which degree")
#    if(rot == "x"):
#        break
#    mc.rotateForward(int(rot),.25,"w")


# mc.adjustForward(False)
# time.sleep(1)
# except KeyboardInterrupt:

#   mc.stopMotors()
