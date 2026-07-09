import time

from RotationalMotor import RotationalMotor

import board

from adafruit_pca9685 import PCA9685

import Jetson.GPIO as GPIO

import time
import math

# 50.9:1 and 71.2:1

"""
Class: PodController
@Author: Aidan Spoerndle
Purpose: This class controls the main functions of rotating the swerve pods on the robot to a desired angle (degrees) 
"""


class PodController():
    def __init__(self, rotMotors):

        self.podMotors = rotMotors.copy()





    """
    Method: teleTurn()
    Purpose: For the TeleOp controller, sets the robot to "Turn Mode", allowing it to turn in place
    """
    def teleTurn(self,debug=False):
        self.rotateXMotors(45, [2, 0], debug)


        self.rotateXMotors(-45, [1, 3], debug)


    """
    Method: teleRotate(speed)
    Purpose: For the TeleOp controller, allows the pod motors to rotate together while maintaining the same heading
    """
    #TO-DO <--fix this not working at all

    def teleRotate(self, speed):
        MAX_ROTATE = 60
        
        
        for i, motor in enumerate(self.podMotors):
            currentAngle = motor.getCurrentAngle()
            currentAngle = currentAngle
            print(f"current angle {currentAngle}")
            if (currentAngle < MAX_ROTATE and speed < 0) or (currentAngle > -MAX_ROTATE and speed > 0):
                    print(f"Motor: {i} Angle: {currentAngle}, Speed: {speed}")
                    motor.setSpeed(speed)
            else:
                print(f"Motor {i} maxxed: {currentAngle}")
                motor.setSpeed(0)
    """
    Method: getPodAngle()
    Purpose: return the current angle the swerve pods are facing
    """
    def getPodAngle(self,debug=False):
        angle = self.podMotors[0].getCurrentAngle()
        if(debug):
            print(f"Angle of Pod Motor 0: {angle}")
        return angle

    """
    Method: adjustForward(debug)
    Purpose: resets the Pod motors so that they're facing forwards and are ready to rotate in the same direction together
    """

    def adjustForward(self, debug=False):

        self.rotatePods(0, debug)
        return

    """
    Method: checkRotate(motor,angle,speed,debug)
    Purpose: calls the specified motors rotate() method which returns back a boolean value whilst also
             rotating the wheel
    """
    def checkRotate(self, motor, angle, speed, debug=False):
        return motor.rotate(angle, speed, debug)

    """
    Method: rotatePods(angle,debug)
    Purpose: rotates all 4 swerve pods to a desired degree angle
    """
    def rotatePods(self, angle, debug= False):
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
            if(debug):
                print(f"{len(MotorList)} motors still rotating...")
            stopCond = len(MotorList) == 0
            time.sleep(0.02)
        self.stopMotors()



    """
    Method: rotateXMotors(angle, motorList,debug)
    Purpose: sends a command to the podController specifying which motors to rotate to
             a specified degree angle
    """
    def rotateXMotors(self, angle, motorList, debug=False):
        speed = 1
        motors = []
        for i in range(len(motorList)):
            motors.append(self.podMotors[motorList[i]]) #copy only the motor indexes specified

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
    """
    Method: stopMotors()
    Purpose: sets the motor speed to 0, stopping the motor whilst not killing it
    """
    def stopMotors(self):
        for motor in self.podMotors:
            motor.motor.stopMotor()
    """
    Method: killMotors()
    Purpose: kills all power to the motors allowing them to move freely, used mostly when MotorController
             obj gets deleted
    """
    def killMotors(self):
        for motor in self.podMotors:
            motor.motor.killMotor()
    def getPodMotor(self,index):
        return self.podMotors[index]




