import time

from RotationalMotor import RotationalMotor
from PodController import PodController
import board

from adafruit_pca9685 import PCA9685

import Jetson.GPIO as GPIO

import time
from simple_pid import PID
import math

# 50.9:1 and 71.2:1

"""
Class: WheelController
@Author: Aidan Spoerndle
Purpose: This class contains the necessary functions to move the Wheel Motors attached to the swerve pods to any
         desired distance 
"""


class WheelController():
    def __init__(self,wheelMotors):
        self.wheelMotors = wheelMotors.copy()

    """
        Method: getHeading()
        Purpose: to retrieve the current heading of the Octoquad
        """

    def getHeading(self):
        heading = self.wheelMotors.getCurrentHeading()
        return heading

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

    """
    Method:adjustForward()
    Purpose: resets the polarity of each wheel in case it gets changed for any reason
    """
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
    Method: checkDriveForward()
    Purpose: calls the motors driveForward() method to check if the motor has reached it's intended destination
    """

    def checkDriveForward(self, motor, ticks, speed, isBack, debug):

        if (debug):
            print(f"Ticks: {ticks} | Speed: {speed}")
        return motor.driveForward(ticks, speed, isBack, debug)
    """
    Method: driveForward(ticks,debug,inPlace)
    Purpose: controls the necessary logic to drive the robot either in the forward direction or to turn in place
    """
    def driveForward(self, ticks, debug, inPlace):
        polar = 0
        motor_speed = 0
        if (ticks < 0 and inPlace > 0):
            polar = -1
            speed = -.5
            isBack = True
            isRight = False
        elif(ticks > 0 and inPlace < 0):
            isRight = True
            speed = 0.3
            polar = 1
            isBack = True
            if(debug):
                print("===isRight===")
        elif(ticks<0 and inPlace < 0):
            polar = -1
            speed = -.3
            isBack = True
            isRight = False
        else:
            isRight = False
            polar = 1
            speed = .5
            isBack = False
        target_heading = self.getHeading()

        # Tune these values! Start with Kp, keep Ki and Kd at 0.
        # output_limits restricts how radically the PID can alter the base speed
        pid = PID(Kp=0.05, Ki=0.0, Kd=0.01, setpoint=target_heading)


        # Alter logic for determing ramp up and ramp down
        MotorList = self.wheelMotors.copy()
        stopCond  = False
        isThere = False
        if (debug):
            print(f"Polar: {polar}")

        MotorList[0].resetEncoder()
        time.sleep(0.05)
        if (debug):
            print(f"Reset encoder {MotorList[0]}")

        while (not stopCond):
            current_heading = self.getHeading()
            error = target_heading - current_heading
            if error > 180:
                current_heading += 360
            elif error < -180:
                current_heading -= 360

            correction = pid(current_heading)
            for i, motor in enumerate(MotorList):
                if(i>1 and abs(speed <= 1)): #Adjust rightside
                    motor_speed = speed - correction
                elif(i<=1 and abs(speed <=1)): #Adjust left
                    motor_speed =speed +  correction


                if (i > 1 and not isRight):
                    isThere = self.checkDriveForward(motor, -ticks * inPlace, motor_speed, isBack, debug)
                elif(i <= 1 and not isRight):
                    isThere = self.checkDriveForward(motor, ticks, motor_speed, isBack, debug)
                elif(i > 1 and isRight): #motor_speed * in place
                    isThere= self.checkDriveForward(motor,ticks * inPlace,motor_speed, isBack,debug)

                elif(i <= 1 and isRight):
                    isThere = self.checkDriveForward(motor,ticks, motor_speed, isBack,debug)
                if (isThere):
                    MotorList.pop(i)
                    break
                if (debug):
                    print(f"Loop: {i} | Ticks {ticks}")
            stopCond = len(MotorList) <= 3

            if (debug):
                print(f'Ticks: {ticks} + Speed: {speed}')

            if (polar > 0 and inPlace > 0):
                speed = self.rampSpeedPos(MotorList[0], ticks, speed)
            elif(polar < 0 and inPlace > 0):
                speed = self.rampSpeedNeg(MotorList[0], ticks, speed)
            time.sleep(0.02)

        self.stopMotors()


    """
    Method: switchForTurning()
    Purpose: switches the polarity of the motors on the right side of the robot, used primarily for turning in place
    """
    def switchForTurning(self):
        for i in range(2, 4):
            self.wheelMotors[i].switchPolarity()

    """
    Method: stopMotors()
    Purpose: sets the motor speed to 0, stopping the motor whilst not killing it
    """
    def stopMotors(self):
        for motor in self.wheelMotors:
            motor.stopMotor()

    """
    Method: killMotors()
    Purpose: kills all power to the motors allowing them to move freely, used mostly when MotorController
             obj gets deleted
    """
    def killMotors(self):
        for motor in self.wheelMotors:
            motor.kill_motor()


