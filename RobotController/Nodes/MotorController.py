import time



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
        

    def rotateForward(self, ticks,distance, speed):


        #Alter logic for determing ramp up and ramp down

        
        isMotorAligned1 = isMotorAligned2 = isMotorAligned3 = isMotorAligned4 = False

        stopCond = False
        whichMotor = "w"
        if (whichMotor == "w"):
            for i in range(0,4):
                self.rotational_motor_list[i+4].resetEncoder()
            # motor1, motor2, motor3, motor4 = self.rotational_motor_list[4:8]
            #
            # angle1 = angle + (motor1.getCurrentPosition() / 8192) * 360
            #
            # angle2 = angle + (motor2.getCurrentPosition() / 8192) * 360
            #
            # angle3 = (motor3.getCurrentPosition() / 8192) * 360 - angle
            #
            # angle4 = (motor4.getCurrentPosition() / 8192) * 360 - angle
            # print(angle1, angle2, angle3, angle4)
            # print(str(motor4.getCurrentPosition()) + "CP")

        else:

            # angle1 = angle2 = angle3 = angle4 = angle

            motor1, motor2, motor3, motor4 = self.rotational_motor_list[0:4]

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

    def moveDistance(self, distance, speed):
        #ALL VALUES IN METERS
        cir = math.pi * 0.192


        ticks = (distance / cir) * 1425.1



        self.rotateForward(ticks,distance, speed)

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
# mc = MotorController()
# mc.boxDrill(1,False)

print("complete")
