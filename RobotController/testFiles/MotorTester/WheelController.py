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
        heading = self.wheelMotors[0].getCurrentHeading()
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
    Method: getWheelTicks()
    Purpose: When the user pushes LSB, the robot should save how many ticks the wheel motors have run so far. We can take this value as well as some unit
             conversion to determine how far the robot traveled in both the x and y direction, very useful for saving and loading paths
    """
    def getWheelTicks(self,debug):
        return self.wheelMotors[0].getCurrentPosition()

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
    Method: resetEncoder()
    Purpose: resets the encoder of the wheel motors so that accurate forward and backward data can be recorded
    """
    def resetEncoder(self):
        self.wheelMotors[0].resetEncoder()
    """
    Method: rampSpeedPos(motor, ticks, speed)
    Purpose: taking in speed input and current tick count, the method ramps the speed up and down. For moving forward
    """

    def rampSpeedPos(self, motor, ticks, speed):
        if (motor.getCurrentPosition() < 100):
            speed = 0.6
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
            speed = -.6
        elif (motor.getCurrentPosition() > 3 * ticks // 8 and ticks < 1000 and speed > -.8):
            speed -= 0.01
        elif (motor.getCurrentPosition() < 5 * ticks // 8 and ticks < 1000 and speed < -.3):
            speed += 0.01
        return speed

    """
    Method: checkDriveForward()
    Purpose: calls the motors driveForward() method to check if the motor has reached it's intended destination
    """

    def checkDriveForward(self, motor, ticks, speed, isGoingBackwards, debug):

        if (debug):
            print(f"Ticks: {ticks} | Speed: {speed}")
        return motor.driveForward(ticks, speed, isGoingBackwards, debug)
    """
    Method: driveForward(ticks,debug,inPlace, podHeading)
    Purpose: controls the necessary logic to drive the robot either in the forward direction or to turn in place
    """
    def driveForward(self, ticks, debug, inPlace, currentMotorAngle):

        motor_speed = .5
        if (ticks < 0 and inPlace > 0):
            polar = -1
            speed = -.5
            isGoingBackwards = True
            isTurning = False
        elif(ticks > 0 and inPlace < 0):
            isTurning = True
            speed = 0.5
            polar = 1
            isGoingBackwards = False
            if(debug):
                print("===isRight===")
        elif(ticks<0 and inPlace < 0):
            polar = -1
            speed = .5
            isGoingBackwards = True
            isTurning = True
        else:
            isTurning = False
            polar = 1
            speed = .5
            isGoingBackwards = False
        target_heading = self.getHeading()
        if(debug):
            print(f"Init Speed: {speed} | isTurning: {isTurning} | Polar: {polar} | isGoingBackawrds: {isGoingBackwards} | InPlace: {inPlace} | Current Motor Angle (degrees): {currentMotorAngle}")

        #pid = PID(Kp=.1, Ki=0.0, Kd=0, setpoint=target_heading)
        #pid.output_limits = (-.6, .6)

        # Alter logic for determing ramp up and ramp down
        MotorList = self.wheelMotors.copy()
        stopCond  = False
        isThere = False
        if (debug):
            print(f"Polar: {polar}")

        self.resetEncoder()
        time.sleep(0.05)
        if(debug):
            print(f"Reset encoder {MotorList[0]}")

        while (not stopCond):
            stopCond = len(MotorList) <= 3
            current_heading = self.getHeading()
            if(debug):
                print(f"Current heading: {current_heading} | Target Heading: {target_heading}")
            error = target_heading - current_heading
            if error > 180:
                current_heading += 360
            elif error < -180:
                current_heading -= 360

            #correction = pid(current_heading)
            kP = .1
            correction = kP * error
            if(debug):
                print(f"PID Correction: {correction}")
            for i, motor in enumerate(MotorList):

                if(not isTurning):
                    if(currentMotorAngle > -80 and currentMotorAngle < 100):
                        if (i > 1 and abs(speed) <= 1):  # Adjust rightside
                                 motor_speedR = speed + correction
                        elif (i <= 1 and abs(speed) <= 1):  # Adjust leftside
                                 motor_speedL = speed - correction
                            # else:
                            #     motor_speedL = speed
                            #     motor_speedR = speed
                        if(debug):
                                print(f"IMU Error: {error} ")
                        if (i > 1):
                            isThere = self.checkDriveForward(motor, -ticks*inPlace, motor_speedR, isGoingBackwards, debug)  # CHANGE: -ticks * inPlace
                        elif (i <= 1):
                            isThere = self.checkDriveForward(motor, ticks, motor_speedL, isGoingBackwards, debug)

                    if(currentMotorAngle < -45 and currentMotorAngle > -135): #when the wheels are facing sideways -90 degrees
                        if(i%2 == 0 and abs(speed) <=1): #adjust forward motors
                            motor_speedF = speed + correction
                        if(i%2 == 1 and abs(speed) <=1): #adjust backward motors
                            motor_speedB = speed - correction
                        if (i  % 2 == 0):
                            isThere = self.checkDriveForward(motor, -ticks*inPlace, motor_speedF, isGoingBackwards, debug)  # CHANGE: -ticks * inPlace
                        elif (i % 2 == 1):
                            isThere = self.checkDriveForward(motor, ticks, motor_speedB, isGoingBackwards, debug)
                elif(isTurning):
                        if(i > 1): #motor_speed * in place
                            isThere= self.checkDriveForward(motor, -polar*ticks, polar*.3 * inPlace,not isGoingBackwards, debug)
                        elif(i <= 1):
                            isThere = self.checkDriveForward(motor, ticks*polar, polar*-.3*inPlace,isGoingBackwards, debug)
                if (isThere):
                    MotorList.pop(i)
                    break
                if (debug):
                    print(f"Loop: {i} | Ticks {ticks} | Current Motor Tick: {motor.getCurrentPosition()}")
                stopCond = len(MotorList) <= 3

                if (debug):
                    print(f'Ticks: {ticks} + Speed: {speed}')

                if (polar > 0 and inPlace > 0):
                    if(debug):
                        print("Ramping forward")
                    speed = self.rampSpeedPos(MotorList[0], ticks, speed)
                elif(polar < 0 and inPlace > 0):
                    if(debug):
                        print("Ramping backward")
                    speed = self.rampSpeedNeg(MotorList[0], ticks, speed)
                time.sleep(0.02)

        self.stopMotors()

    """
    Method: driveForwardTurning()
    Purpose: A sister method to driveForward but only for the robot turning in place. This is necessary due to motor
             polarities needing to be changed in order to get the turning in place effect.
    """

    def driveForwardTurning(self, ticks, debug):
        speed = 0.5
        if (ticks > 0):
            polar = 1
            isGoingBackwards = False

        elif (ticks < 0):
            polar = -1
            isGoingBackwards = True


        if (debug):
            print(
                f"Init Speed: {speed}  | Polar: {polar} | isGoingBackawrds: {isGoingBackwards} ")

        MotorList = self.wheelMotors.copy()
        stopCond = False
        isThere = False
        if (debug):
                print(f"Polar: {polar}")
        self.resetEncoder()
        if (debug):
                print(f"Reset encoder {MotorList[0]}")
        stopCond = len(MotorList) <= 3
        while (not stopCond):
            for i, motor in enumerate(MotorList):
                if (i > 1):  # motor_speed * in place
                    isThere = self.checkDriveForward(motor, -polar * ticks, polar * .3 * -1, not isGoingBackwards,
                                                     debug)
                elif (i <= 1):
                    isThere = self.checkDriveForward(motor, ticks * polar, polar * -.3 * -1, isGoingBackwards,
                                                     debug)
                if (isThere):
                    MotorList.pop(i)
                    break
                if (debug):
                    print(f"Loop: {i} | Ticks {ticks} | Current Motor Tick: {motor.getCurrentPosition()}")


                if (debug):
                    print(f'Ticks: {ticks} + Speed: {speed}')


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


