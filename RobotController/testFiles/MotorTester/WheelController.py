import time

from RotationalMotor import RotationalMotor
from PodController import PodController
import board

from adafruit_pca9685 import PCA9685

import Jetson.GPIO as GPIO

import time
import math

# 50.9:1 and 71.2:1

"""
Class: MotorController
@Author: Aidan Spoerndle
Purpose: This class is the brains of the logic for the robot, the following methods allow for the robot to conduct
         complex movement patterns and interactions between the Pod motors and the Wheel motors. 
"""


class WheelController():
    def __init__(self,wheelMotors):
        self.wheelMotors = wheelMotors.copy()

    """
    Method: teleforward(speed)
    Purpose: For the TeleOp controller, allows for the controller to move the robot forward and backward
    """

    def teleForward(self, speed):
        for motor in self.wheelMotors:
            motor.setSpeed(speed)


    """
    Method: teleMoveTurn(Speed)
    Purpose: For the TeleOp controller, allows for the robot to turn in place in "Turn Mode"
    """

    def teleMoveTurn(self, speed):

        for i, motor in enumerate(self.wheelMotors):
            if (i <= 1):
                motor.setSpeed(speed)
            if (i >= 2):
                motor.setSpeed(-speed)


    def adjustForward(self):
        for i,motor in enumerate (self.wheelMotors):
            if(i<6):
                if(motor.getPolarity() != 1):
                    motor.switchPolarity()
            else:
                if(motor.getPolairty() != -1):
                    motor.switchPolarity()


    """
    Method: rampSpeedPos(motor, ticks, speed)
    Purpose: taking in speed input and current tick count, the method ramps the speed up and down. For moving forward
    """

    def rampSpeedPos(self, motor, ticks, speed):
        if (motor.getCurrentPosition() < 100):
            speed = 0.5
        elif (abs(motor.getCurrentPosition()) < abs(3 * ticks // 8) and abs(ticks) > 1000 and speed < .8):
            speed += 0.01
        elif (abs(motor.getCurrentPosition()) > abs(5 * ticks // 8) and abs(ticks) > 1000 and speed > 0.3):
            speed -= 0.01
        return speed

    """
    Method: rampSpeedNeg(motor,ticks,speed)
    Purpose: taking in speed input and current tick count, the method ramps the speed up and down. For moving backward
    """

    def rampSpeedNeg(self, motor, ticks, speed):
        if (motor.getCurrentPosition() > -100):
            speed = -.5
        elif (motor.getCurrentPosition() > 3 * ticks // 8 and ticks < 1000 and speed > -.8):
            speed -= 0.01
        elif (motor.getCurrentPosition() < 5 * ticks // 8 and ticks < 1000 and speed < -.3):
            speed += 0.01
        return speed

    """
    Method: checkRotateForward()
    Purpose: calls the motors rotateForward() method to check if the motor has reached it's intended destination
    """

    def checkRotateForward(self, motor, ticks, speed, isBack, debug):

        if (debug):
            print(f"Ticks: {ticks} | Speed: {speed}")
        return motor.rotateForward(ticks, speed, isBack, debug)

    def rotateForward(self, ticks, debug, inPlace):
        polar = 0
        if (ticks < 0):
            polar = -1
            speed = -.5
            isBack = True
        else:
            polar = 1
            speed = .5
            isBack = False
        # Alter logic for determing ramp up and ramp down
        MotorList = self.wheelMotors.copy()
        stopCond = False
        if (debug):
            print(f"Polar: {polar}")

        MotorList[0].resetEncoder()
        time.sleep(0.05)
        if (debug):
            print(f"Reset encoder {MotorList[0]}")

        while (not stopCond):

            for i, motor in enumerate(MotorList):

                if (i > 1):
                    isThere = self.checkRotateForward(motor, -ticks * inPlace, speed * inPlace, isBack, debug)
                else:
                    isThere = self.checkRotateForward(motor, ticks, speed, isBack, debug)

                if (isThere):
                    MotorList.pop(i)
                    break
                if (debug):
                    print(f"Loop: {i} | Ticks {ticks}")
            stopCond = len(MotorList) <= 3

            if (debug):
                print(f'Ticks: {ticks} + Speed: {speed}')

            if (polar > 0):
                speed = self.rampSpeedPos(MotorList[0], ticks, speed)
            else:
                speed = self.rampSpeedNeg(MotorList[0], ticks, speed)
            time.sleep(0.02)

        self.stopMotors()



    def moveDistance(self, distance, debug, isZero):
        # ALL VALUES IN METERS
        cir = math.pi * 0.192
        # self.rotatePods(0,.5)

        ticks = (distance / cir) * 1425.1
        if (debug):
            print(f"Ticks: {ticks} | distance: {distance} | isZero: {isZero}")
        if (isZero):
            for i in range(2, 4):
                self.wheelMotors[i].switchPolarity()
            self.rotateForward(ticks, debug, -1)
            for i in range(2, 4):
                self.wheelMotors[i].switchPolarity()
        else:
            if (debug):
                print(f"Rotating forward...")
            self.rotateForward(ticks, debug, 1)
    def switchForTurning(self):
        for i in range(2, 4):
            self.wheelMotors[i].switchPolarity()

    def stopMotors(self):
        for motor in self.wheelMotors:
            motor.stopMotor()




