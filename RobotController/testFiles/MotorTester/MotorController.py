import time

from Motor import WheelMotor

from RotationalMotor import RotationalMotor

import board

from adafruit_pca9685 import PCA9685

import Jetson.GPIO as GPIO

import time
import math


# 50.9:1 and 71.2:1
class MotorController():
    def __init__(self):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
        i2c = board.I2C()
        pca = PCA9685(i2c)
        pca.frequency = 50
        self.wheel_motor_list = []
        self.rotational_motor_list = []

        """
        PWM Pin, left or right side, forwardValue, motorType
        """
        pin_list_rotational = [[2, "l", 4, 897],
                               [3, "l", 5, 238],
                               [4, "l", 6, 914],
                               [6, "l", 7, 722],
                               # WheelMotors
                               [11, 'l', 2, 0],
                               [10, 'l', 1, 0],
                               [13, 'r', 0, 0],
                               [15, 'r', 3, 0]]

        # print("readying wheel motors...")

        print("readying motors...")
        for i in pin_list_rotational:
            motor = RotationalMotor(pca, i[0], i[1], i[2], i[3])
            self.rotational_motor_list.append(motor)
        print("motors ready!")

    def teleForward(self, speed):
        for motor in self.rotational_motor_list[4:8]:
            motor.setSpeed(speed)

    def teleTurn(self):
        self.rotateXMotors(45, [self.rotational_motor_list[2], self.rotational_motor_list[0]], False)

        self.rotateXMotors(-45, [self.rotational_motor_list[1], self.rotational_motor_list[3]], False)
        for i, motor in enumerate(self.rotational_motor_list[4:8]):
            if (i < 2):
                if (motor.getPolarity() == 1):
                    motor.switchPolarity()

    def teleMoveTurn(self, speed):

        for i, motor in enumerate(self.rotational_motor_list[4:8]):
            if (i == 0):
                motor.setSpeed(speed)
            if (i == 1):
                motor.setSpeed(speed)
            if (i == 2):
                motor.setSpeed(-speed)
            if (i == 3):
                motor.setSpeed(-speed)
        """ 
         for i,motor in enumerate(self.rotational_motor_list[4:8]):
g               if(i == 0 or i == 1):
                 motor.setSpeed(speed)
             else:
                 motor.setSpeed(speed)
         for i in range(6,8):
             self.rotational_motor_list[i].switchPolarity()
         """

    def adjustForward(self, debug):
        for i, motor in enumerate(self.rotational_motor_list[4:8]):
            if (i < 6):
                if (motor.getPolarity() != 1):
                    motor.switchPolarity()
            else:
                if (motor.getPolairty() != -1):
                    motor.switchPolarity()
        self.rotatePods(0, debug)
        return

    def rampSpeedPos(self, motor, ticks, speed):
        if (motor.getCurrentPosition() < 100):
            speed = 0.5
        elif (abs(motor.getCurrentPosition()) < abs(3 * ticks // 8) and abs(ticks) > 1000 and speed < .8):
            speed += 0.01
        elif (abs(motor.getCurrentPosition()) > abs(5 * ticks // 8) and abs(ticks) > 1000 and speed > 0.3):
            speed -= 0.01
        return speed

    def rampSpeedNeg(self, motor, ticks, speed):
        if (motor.getCurrentPosition() > -100):
            speed = -.5
        elif (motor.getCurrentPosition() > 3 * ticks // 8 and ticks < 1000 and speed > -.8):
            speed -= 0.01
        elif (motor.getCurrentPosition() < 5 * ticks // 8 and ticks < 1000 and speed < -.3):
            speed += 0.01
        return speed

    def checkRotateForward(self, motor, ticks, speed, isBack, debug):
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

        MotorList = self.rotational_motor_list[4:8]

        stopCond = False
        if (debug):
            print(f"Polar: {polar}")

        MotorList[0].resetEncoder()

        while (not stopCond):

            for i, motor in enumerate(motorList):
                if (i > 5):
                    ticks *= -1
                else:
                    ticks = abs(ticks)
                isThere = self.checkRotateForward(motor, ticks, speed, isBack, debug)
                if (isThere):
                    motorList.pop(i)
            stopCond = len(motorList) == 0

            if (debug):
                print(f'Ticks: {ticks} + Speed: {speed}')

            if (polar > 0):
                speed = self.rampSpeedPos(motor1, ticks, speed)
            else:
                speed = self.rampSpeedNeg(motor1, ticks, speed)
            time.sleep(0.02)

        self.stopMotors()

    def checkRotate(self, motor, angle, speed, debug):
        return motor.rotate(angle, speed, debug)

    def rotatePods(self, angle, debug):
        speed = 0.75
        if angle > 90 or angle < -90:
            print(f"ROTATION ERR: Angle of {angle} degrees will cause wire damage")
            return

        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False

        stopCond = False

        motor1, motor2, motor3, motor4 = self.rotational_motor_list[0:4]

        while (not stopCond):

            if (not isMotorAligned1):
                isMotorAligned1 = self.checkRotate(motor1, angle, speed, debug)

            if (not isMotorAligned2):
                isMotorAligned2 = self.checkRotate(motor2, angle, speed, debug)

            if (not isMotorAligned3):
                isMotorAligned3 = self.checkRotate(motor3, angle, speed, debug)

            if (not isMotorAligned4):
                isMotorAligned4 = self.checkRotate(motor4, angle, speed, debug)

            stopCond = isMotorAligned2 and isMotorAligned1 and isMotorAligned3 and isMotorAligned4
            time.sleep(0.02)
        self.stopMotors()

    def moveDistance(self, distance, debug, isZero):
        # ALL VALUES IN METERS
        cir = math.pi * 0.192
        # self.rotatePods(0,.5)

        ticks = (distance / cir) * 1425.1
        if (isZero):
            for i in range(6, 8):
                self.rotational_motor_list[i].switchPolarity()
            self.rotateForward(ticks, debug, -1)
            for i in range(6, 8):
                self.rotational_motor_list[i].switchPolarity()
        else:
            self.rotateForward(ticks, debug, 1)

    def horizontalMode(self, debug):
        self.rotatePods(-90, debug)

    def rotateXMotors(self, angle, motorList, debug):
        speed = 0.75
        if angle > 90 or angle < -90:
            print(f"ROTATION ERR: Angle of {angle} degrees is will cause wire damage")
            return

        isMotorAligned1 = isMotorAligned2 = False

        stopCond = False

        while (not stopCond):

            for i, motor in enumerate(motorList):
                isRotated = self.checkRotate(motor, angle, speed, debug)
                if (isRotated):
                    motorList.pop(i)
            stopCond = len(motorList) == 0
            time.sleep(0.02)
        self.stopMotors()

    def stopMotors(self):
        for motor in self.rotational_motor_list:
            motor.stopMotor()

    def moveCord(self, cords, debug):
        x, y = cords
        hypo = math.sqrt((x ** 2) + (y ** 2))
        angle = (math.acos(abs(x) / hypo) * 180) / math.pi
        if (x > 0):
            angle = -angle
        if (x == 0):
            angle = 0
        if (y == 0):
            angle = -90
            if (x < 0):
                hypo = -hypo
        if (debug):
            print(f"X,Y: {x},{y} | Hypotenuse: {hypo} | Angle (Degrees) {angle}")
            debug = False
        self.rotatePods(angle, debug)
        if (y < 0):
            hypo = -hypo
        self.moveDistance(hypo, debug, False)
        self.adjustForward(debug)

    def moveCurve(self, cords, heading, debug):
        # Do more research into ackermann steering
        """
        turning radius = Wheelbase / tan (front wheel angle)
        arc length = turning radius * final_heading
        """

        x, y = cords

    def turn(self, angle, debug):
        # 90 degrees = .38
        angle /= 90
        angle *= -.38
        self.rotateXMotors(45, [self.rotational_motor_list[2], self.rotational_motor_list[0]], debug)

        self.rotateXMotors(-45, [self.rotational_motor_list[1], self.rotational_motor_list[3]], debug)
        self.moveDistance(angle, False, True)
        self.adjustForward(False)

    def boxDrill(self, dis, debug):
        self.adjustForward(debug)
        self.moveDistance(dis, debug, False)
        time.sleep(1)
        self.horizontalMode(debug, False)
        time.sleep(1)
        self.moveDistance(-dis, debug, False)
        time.sleep(1)
        self.adjustForward(debug)
        time.sleep(1)
        self.moveDistance(-dis, debug, False)
        time.sleep(1)
        self.horizontalMode(debug)
        time.sleep(1)
        self.moveDistance(dis, debug, False)
        self.adjustForward(debug)

        print("complete")

    def __del__(self):

        for motor in self.wheel_motor_list:
            motor.move_motor(0)

        for motor in self.rotational_motor_list:
            motor.stopMotor()

        time.sleep(2)

        print("finished")


"""
TESTING GROUNDS FOR MOTORCONTROLLER CLASS
"""
# mc = MotorController()

# ===CODE FOR ROTATING ROBOT 90 WHILE MOVING===
# mc.rotateTwoMotors(45,2,3,False)
# mc.moveDistacne(1,False,False)


# mc.adjustForward(True)
# mc.boxDrill(1,False)
# mc.adjustForward(False)
# mc.moveCord((-1,1),False)
# mc.moveCord((1,0),False)
# mc.moveCord((0,-1),False)

# mc.adjustForward(False)
# mc.moveCord((0,1),True)
# mc.moveCord((-1,1),False)
# mc.turn(90,False)
# mc.moveCord((1,0),False)
# mc.turn(270,False)


# mc.moveCords((4,5),True)
# print("complete")
