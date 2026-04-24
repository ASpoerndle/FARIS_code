import time

from Motor import WheelMotor

from RotationalMotor import RotationalMotor

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
        
        """
        PWM Pin, left or right side, forwardValue, motorType
        """
        pin_list_rotational = [[2, "l", 4, -18539], 
         [3, "l", 5, -11016], 
         [4, "l", 6, -81946], 
         [6, "l", 7, -13779], 
         #WheelMotors
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
    
    
    
    
    def teleForward(self,speed):
        for motor in self.rotational_motor_list[4:8]:
            motor.setSpeed(speed)
    def adjustForward(self,debug):
        self.rotatePods(0,0.5,debug)
        return
        

    def rotateForward(self, ticks,debug):
        polar = 0
        if(ticks < 0):
            polar = -1
            speed = -.3
            isBack = True
        else:
            polar = 1
            speed = .3
            isBack = False
        #Alter logic for determing ramp up and ramp down

        
        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False

        stopCond = False
        if(debug):
            print(f"Polar: {polar}") 

        motor1,motor2,motor3,motor4 = self.rotational_motor_list[4:8]
        motor4.resetEncoder()
        
        while (not stopCond):

            if (not isMotorAligned1):
                isMotorAligned1 = motor1.rotateForward(ticks, speed,isBack,debug)

            if (not isMotorAligned2):
                isMotorAligned2 = motor2.rotateForward(ticks, speed,isBack,debug)

            if (not isMotorAligned3):
                isMotorAligned3 = motor3.rotateForward(-ticks, speed,isBack,debug)

            if (not isMotorAligned4):
                isMotorAligned4 = motor4.rotateForward(-ticks, speed,isBack,debug)
            if(debug):
                print(f'Ticks: {ticks} + Speed: {speed}')
           
            if(polar > 0):            
                if(motor1.getCurrentPosition() < 100 and polar > 0):
                    speed = 0.3
                elif(abs(motor1.getCurrentPosition()) < abs(3*ticks//8) and abs(ticks) > 1000 and speed < .8):
                    speed += 0.01
                elif(abs(motor1.getCurrentPosition()) > abs(5*ticks//8) and abs(ticks) > 1000 and speed >0.3):
                    speed -= 0.01
            else:
                if(motor1.getCurrentPosition() > -100):
                    speed = -.3
                elif(motor1.getCurrentPosition() > 3 * ticks//8 and ticks < 1000 and speed > -.8):
                    speed -= 0.01
                elif(motor1.getCurrentPosition() < 5 * ticks//8 and ticks < 1000 and speed < -.3):
                    speed += 0.01
           
            time.sleep(0.02)
            stopCond = isMotorAligned1 or isMotorAligned2 or isMotorAligned3 or isMotorAligned4

        self.stopMotors()

  
    def rotatePods(self, angle, speed): 
        if angle > 90 or angle < -90:
            print(f"ROTATION ERR: Angle of {angle} degrees is will cause wire damage")
            return

        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False

        stopCond = False

        motor1, motor2, motor3, motor4 = self.rotational_motor_list[0:4]

        while (not stopCond):

            if (not isMotorAligned1):
                isMotorAligned1 = motor1.rotate(angle, speed,debug)

            if (not isMotorAligned2):
                isMotorAligned2 = motor2.rotate(angle, speed,debug)

            if (not isMotorAligned3):
                isMotorAligned3 = motor3.rotate(angle, speed,debug)

            if (not isMotorAligned4):
                isMotorAligned4 = motor4.rotate(angle, speed,debug)

            stopCond = isMotorAligned2 and isMotorAligned1 and isMotorAligned3 and isMotorAligned4
            time.sleep(0.02)
        self.stopMotors()

    def moveDistance(self, distance, debug):
        #ALL VALUES IN METERS
        cir = math.pi * 0.192
        self.rotatePods(0,.5)

        ticks = (distance / cir) * 1425.1

        self.rotateForward(ticks, debug)

    def horizontalMode(self,debug):
        if(self.angle < 90):
            self.rotatePods(-90, 0.75,debug)
            
        
    def stopMotors(self):
        for motor in self.rotational_motor_list:
            motor.stopMotor()
            
    def boxDrill(self,dis,debug):
        self.adjustForward(debug)
        self.moveDistance(dis,debug)
        time.sleep(1)
        self.horizontalMode(debug)
        time.sleep(1)
        self.moveDistance(-dis,debug)
        time.sleep(1)
        self.adjustForward(debug)
        time.sleep(1)
        self.moveDistance(-dis,debug)
        time.sleep(1)
        self.horizontalMode(debug)
        time.sleep(1)
        self.moveDistance(dis,debug)
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
mc = MotorController()
mc.boxDrill(1,False)

print("complete")
