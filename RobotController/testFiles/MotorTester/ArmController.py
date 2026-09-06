#from RotationFocusedMotor import RotationFocusedMotor
import math
from Servo import Servo
import torch
import numpy as np
#import modern_robotics as mr
import pytorch_mr as mr
import board
import Jetson.GPIO as GPIO
from adafruit_pca9685 import PCA9685
from ArmMotor import ArmMotor
from IK import IK
#import pandas as pd
#import serial
import time
from RotationFocusedMotor import RotationFocusedMotor
class ArmController():
    def __init__(self, armMotors, armServos):
        self.armMotors = armMotors
        """
        Motor 0 = Shoulder
        Motor 1 = Arm
        Motor 2 = Forearm
        """
        self.armServos = armServos
        """
        Servo 0 = Tilt (pitch)
        Servo 1 = Twist (roll)
        Servo 2 = Grab
        """
        self.wristPitchValues = [0,45,90,135,160]
        self.wristRollValues = [0,45,90,120,200]
        self.graspValues = [155,200]
        self.wristPitchIndex = 0
        self.wristRollIndex = 0
        self.graspIndex = 0
        self.IK = IK()
    def teleWristPitch(self):
        if(self.wristPitchIndex + 1 > len(self.wristPitchValues)):
            self.wristPitchIndex = 0
        print(self.wristPitchValues[self.wristPitchIndex])
        self.armServos[0].setAngle(self.wristPitchValues[self.wristPitchIndex])
        self.wristPitchIndex +=1
    def teleWristRoll(self):
        if(self.wristRollIndex + 1 > len(self.wristRollValues)):
            self.wristRollIndex = 0
        self.armServos[1].setAngle(self.wristRollValues[self.wristRollIndex])
        print((self.wristRollValues[self.wristRollIndex]))
        self.wristRollIndex += 1
    def teleGrasp(self):
        if(self.graspIndex + 1 > len(self.graspValues)):
            self.graspIndex = 0
        self.armServos[2].setAngle(self.graspValues[self.graspIndex])
        #print(self.graspValues[self.graspIndex])
        self.graspIndex += 1
        
    def obtainJointAngles(self, x,y,z):
        angleList = IK.performIK(x,y,z)
        return angleList
    def travelArm(self,x,y,z,debug=False):
        jointAngles = self.obtainJointAngles(x,y,z)
        #TODO Uncomment to allow for arm to auto rotate
        #self.setRotationArm(jointAngles,debug)
        if(debug):
            print(f"Arm traveled: \n Real World Position: \n \t {x} \n \t {y} \n \t {z}")
            print(f"Joint Angles:")
            for angle in jointAngles:
                print(f"\t {angle}")

    """
    Method: setRotationArm(List<List<float>> rotationMatrix)
    Purpose: the matrix tells the motors how far they should rotate. This should rotate all of the motors
             to the correct position
    """
    def setRotationArm(self, angle,debug=False):
        motorList = [self.armMotors[1],self.armMotors[2]]

        #rotation matrix = 3 x 4
        stopCond = len(motorList) == 0
        speed = 0.3
        #angle = ((angle + 180) % 360) - 180
        #print(angle)
        for i in range(len(motorList)):
            while(True):
         
                isAligned = self.checkRotate(motorList[i], angle[i], 0.3, debug)
                #isAligned = motor.motor.encoder.getCurrentAngle() < angle
                if (isAligned):
                    break
                    #else:
                #    motor.motor.motor.moveMotor(speed)
        for motor in motorList:
            motor.motor.motor.stopMotor()


    def checkRotate(self, motor, angle, speed, debug=False):
            return motor.rotate(angle, speed, debug)


    """
    Method: teleServoOut()
    Purpose: Opens gripper
    """


    def setServoAngles(self,Joint):
        for servo in range(len(self.armServos)):
            self.armServos[servo].setAngle(Joint[servo])
        time.sleep(i)
        for servo in self.armServos:
            servo.killServo()
    def setMotorSpeed(self,motor,speed):
        try:
            if(motor > 2):
                return
            self.armMotors[motor].moveMotor(speed)
        except:
            print("ERR finding motor")


    def killMotors(self):
        for motor in self.armMotors:
            motor.killMotor()
    def stopMotors(self):
        for motor in self.armMotors:
            motor.moveMotor(0)

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50
motorList = [
    [12,"l",4,1,0,0,0],
    [13,"l",5,1,-410,-280,90],
    [14,"l",6,1,-243,80,0]
        ]
motorObj = []
servoList = [8,9,10]
servoObj = []
for i in servoList:
    servo = Servo(pca,i)
    servoObj.append(servo)
for i in motorList:
    motor = ArmMotor(i[4],i[5],i[6],pca,i[0],i[1],i[2],i[3],7)
    motorObj.append(motor)
arm = ArmController(motorObj,servoObj)


try:

    input("Pause")
    arm.armMotors[1].motor.motor.moveMotor(0) 

    #Set J2 to 45 degrees and J3 to -30 degrees
    #arm.setRotationArm([45,-30],True)

    # Set J2 to -45 degrees and J3 to -30 degrees
    #arm.setRotationArm([-45,-30],True)

    #input("Pause")
    # Set J2 to 45 degrees and J3 to -65 degrees (this can be used as a "default" position)
    #arm.setRotationArm([45,-65],True)

    #arm.travelArm(0,0,0)
    

except KeyboardInterrupt:
    arm.killMotors()

arm.killMotors()

