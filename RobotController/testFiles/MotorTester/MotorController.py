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
        self.angle = 0
        i2c = board.I2C()
        pca = PCA9685(i2c)
        pca.frequency = 50
        self.wheel_motor_list = []
        self.rotational_motor_list = []

        """
        PWM Pin, left or right side, forwardValue, motorType
        """
        pin_list_rotational = 
        [[2, "l", 4, 181,"P"], 
         [3, "l", 5, 144,"P"], 
         [4, "l", 6, 134,"P"], 
         [6, "l", 7, 261,"P"], 
         #WheelMotors
         [11, 'l', 2, 0,"W"],                      
         [10, 'l', 1, 0,"W"], 
         [13, 'r', 0, 0,"W"], 
         [15, 'r', 3, 0,"W"]]

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
    def teleForward(self,speed):
        for motor in self.rotational_motor_list[4:8]:
            motor.setSpeed(speed)
    def adjustForward(self):
        self.rotatePods(0,0.5)
        return
        cond1 = True
        cond2 = False
        self.angle = 0
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

    def rotateForward(self, ticks,distance, speed):
        polar = 0
        if(ticks < 0):
            polar = -1
            speed = -.3
        else:
            polar = 1
            speed = .3
        #Alter logic for determing ramp up and ramp down

        
        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False

        stopCond = False
        

        motor1,motor2,motor3,motor4 = self.rotational_motor_list[4:8]
        motor4.resetEncoder()
        
        while (not stopCond):

            if (not isMotorAligned1):
                isMotorAligned1 = motor1.rotateForward(ticks, speed)

            if (not isMotorAligned2):
                isMotorAligned2 = motor2.rotateForward(ticks, speed)

            if (not isMotorAligned3):
                isMotorAligned3 = motor3.rotateForward(-ticks, speed)

            if (not isMotorAligned4):
                isMotorAligned4 = motor4.rotateForward(-ticks, speed)
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
            # stopCond = (isMotorAligned1 or isMotorAligned2) or (isMotorAligned3 or isMotorAligned4)
            # if(ticks <= halfTicks and speed <= 1 and max_ticks != -1):
            #     print("increase speed")
            #     speed += (1/halfTicks)
            # elif(ticks > halfTicks and speed > 0.6 and max_ticks != -1):
            #     speed -=1/halfTicks
            # ticks+= 1
            # # if(whichMotor == "w"):
            time.sleep(0.02)
            stopCond = isMotorAligned1 or isMotorAligned2 or isMotorAligned3 or isMotorAligned4

        self.stopMotors()

    #       self.adjustForward()
    def rotatePods(self, angle, speed):
        
        if(self.angle + angle > 90 or self.angle + angle < -90):
            return
        self.angle += angle
        



        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False

        stopCond = False

        motor1, motor2, motor3, motor4 = self.rotational_motor_list[0:4]

        while (not stopCond):

            if (not isMotorAligned1):
                isMotorAligned1 = motor1.rotate(angle, speed)

                

            if (not isMotorAligned2):
                isMotorAligned2 = motor2.rotate(angle, speed)

                

            if (not isMotorAligned3):
                isMotorAligned3 = motor3.rotate(angle, speed)

            if (not isMotorAligned4):
                isMotorAligned4 = motor4.rotate(angle, speed)

            stopCond = isMotorAligned2 and isMotorAligned1 and isMotorAligned3 and isMotorAligned4
            time.sleep(0.02)
        self.stopMotors()

    def moveDistance(self, distance, speed):
        #ALL VALUES IN METERS
        cir = math.pi * 0.192
        self.rotatePods(0,.5)

        ticks = (distance / cir) * 1425.1



        self.rotateForward(ticks,distance, speed)

    def horizontalMode(self):
        if(self.angle < 90):
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
mc = MotorController()
#mc.boxDrill(0.2)
# time.sleep(3)
#mc.adjustForward()
mc.moveDistance(-3,1)
#time.sleep(3)
#mc.rotatePods(45,1)
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

