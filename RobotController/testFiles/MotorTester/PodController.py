import time

from RotationalMotor import RotationalMotor

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


class PodController():
    def __init__(self, rot_motors):

        self.podMotors = rot_motors.copy()
        # print("readying wheel motors...")





    def teleTurn(self):
        self.rotateXMotors(45, [2, 0], False)

        self.rotateXMotors(-45, [1, 3], False)
       #===CODE FOR WHEEL MOTORS===
        # for i, motor in enumerate(self.rotational_motor_list[4:8]):
        #     if (i < 2):
        #         if (motor.getPolarity() == 1):
        #             motor.switchPolarity()


    """
    Method: teleRotate(speed)
    Purpose: For the TeleOp controller, allows the pod motors to rotate together while maintaining the same heading
    """

    def teleRotate(self, speed):
        MAX_ROTATE = 60
        for i, motor in enumerate(self.podMotors):
            if ((motor.getCurrentAngle() < MAX_ROTATE and speed < 0) or (
                    motor.getCurrentAngle() > -MAX_ROTATE and speed > 0)):
                if (abs(motor.getCurrentAngle()) < 90):
                    print(f"Angle: {motor.getCurrentAngle()}, Speed: {speed}")
                    motor.setSpeed(speed)
                else:
                    motor.setSpeed(0)
            else:
                motor.setSpeed(0)

    """
    Method: adjustForward(debug)
    Purpose: resets the Pod motors so that they're facing forwards and are ready to rotate in the same direction together
    """

    def adjustForward(self, debug):
        for i, motor in enumerate(self.podMotors[4:8]):
            if (i < 6):
                if (motor.getPolarity() != 1):
                    motor.switchPolarity()
            else:
                if (motor.getPolairty() != -1):
                    motor.switchPolarity()
        self.rotatePods(0, debug)
        return


    def checkRotate(self, motor, angle, speed, debug):
        return motor.rotate(angle, speed, debug)

    def rotatePods(self, angle, debug):
        speed = 0.75
        if angle > 90 or angle < -90:
            print(f"ROTATION ERR: Angle of {angle} degrees will cause wire damage")
            return

        stopCond = False
        MotorList = self.podMotors.copy()

        while (not stopCond):
            for i, motor in enumerate(MotorList):
                isAligned = self.checkRotate(motor, angle, speed, debug)
                if (isAligned):
                    MotorList.pop(i)

            stopCond = len(MotorList) == 0
            time.sleep(0.02)
        self.stopMotors()



    def horizontalMode(self, debug):
        self.rotatePods(-90, debug)

    def rotateXMotors(self, angle, motorList, debug):
        speed = 0.75
        motors = []
        for i in range(len(motorList)):
            motors.append(self.podMotors[motorList[i]])

        if angle > 90 or angle < -90:
            print(f"ROTATION ERR: Angle of {angle} degrees is will cause wire damage")
            return

        stopCond = False

        while (not stopCond):

            for i, motor in enumerate(motors):
                isRotated = self.checkRotate(motor, angle, speed, debug)
                if (isRotated):
                    motors.pop(i)
            stopCond = len(motors) == 0
            time.sleep(0.02)

    def stopMotors(self):
        for motor in self.podMotors:
            motor.kill_motor()





