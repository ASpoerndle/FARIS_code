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
        pin_list_rotational = [[2, "l", 4, 897], 
         [3, "l", 5, 238], 
         [4, "l", 6, 914], 
         [6, "l", 7, 722], 
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
        self.rotatePods(0,debug)
        return
        

    def rotateForward(self, ticks,debug,zero):
        polar = 0
        if(ticks < 0):
            polar = -1
            speed = -.5
            isBack = True
        else:
            polar = 1
            speed = .5
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
                isMotorAligned3 = motor3.rotateForward(-ticks * zero, speed * zero,isBack,debug)

            if (not isMotorAligned4):
                isMotorAligned4 = motor4.rotateForward(-ticks, speed * zero,isBack * zero,debug)
            if(debug):
                print(f'Ticks: {ticks} + Speed: {speed}')
           
            if(polar > 0):            
                if(motor1.getCurrentPosition() < 100 and polar > 0):
                    speed = 0.5
                elif(abs(motor1.getCurrentPosition()) < abs(3*ticks//8) and abs(ticks) > 1000 and speed < .8):
                    speed += 0.01
                elif(abs(motor1.getCurrentPosition()) > abs(5*ticks//8) and abs(ticks) > 1000 and speed >0.3):
                    speed -= 0.01
            else:
                if(motor1.getCurrentPosition() > -100):
                    speed = -.5
                elif(motor1.getCurrentPosition() > 3 * ticks//8 and ticks < 1000 and speed > -.8):
                    speed -= 0.01
                elif(motor1.getCurrentPosition() < 5 * ticks//8 and ticks < 1000 and speed < -.3):
                    speed += 0.01
           
            time.sleep(0.02)
            stopCond = isMotorAligned1 or isMotorAligned2 or isMotorAligned3 or isMotorAligned4

        self.stopMotors()

  
    def rotatePods(self, angle,debug):
        speed = 0.75
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
        


    def moveDistance(self, distance, debug,isZero):
        #ALL VALUES IN METERS
        cir = math.pi * 0.192
        #self.rotatePods(0,.5)

        ticks = (distance / cir) * 1425.1
        if(isZero):
            for i in range(6,8):
                self.rotational_motor_list[i].switchPolarity()
            self.rotateForward(ticks,debug,-1)
            for i in range(6,8):
                self.rotational_motor_list[i].switchPolarity()
        else:
            self.rotateForward(ticks, debug,1)

    def horizontalMode(self,debug):
        self.rotatePods(-90,debug)
            
    def rotateTwoMotors(self,angle,motor1i,motor2i,debug):
        speed = 0.75
        if angle > 90 or angle < -90:
            print(f"ROTATION ERR: Angle of {angle} degrees is will cause wire damage")
            return
        if(motor1i > 3 or motor2i >3):
            print(f"MOTOR INDEX ERR: motor1 or motor2 index out of range for pod motors | {motor1i} & {motor2i}")
        isMotorAligned1 = isMotorAligned2 = False

        stopCond = False

        motor1 = self.rotational_motor_list[motor1i] 
        motor2 = self.rotational_motor_list[motor2i]

        while (not stopCond):

            if (not isMotorAligned1):
                isMotorAligned1 = motor1.rotate(angle, speed,debug)

            if (not isMotorAligned2):
                isMotorAligned2 = motor2.rotate(angle, speed,debug)

            
            stopCond = isMotorAligned2 and isMotorAligned1 
            time.sleep(0.02)
        self.stopMotors()
    def stopMotors(self):
        for motor in self.rotational_motor_list:
            motor.stopMotor()
    def moveCord(self, cords,debug):
        x,y = cords
        hypo = math.sqrt((x**2) + (y**2))
        angle = (math.acos(abs(x)/hypo) * 180)/math.pi
        if(x > 0):
            angle = -angle
        if(x == 0):
            angle = 0
        if(y == 0):
            angle = -90
            if(x < 0):
                hypo = -hypo
        if(debug):
            print(f"X,Y: {x},{y} | Hypotenuse: {hypo} | Angle (Degrees) {angle}")
            debug = False
        self.rotatePods(angle,debug)
        if(y < 0):
            hypo = -hypo
        self.moveDistance(hypo,debug,False)
        self.adjustForward(debug)
#    def moveCord(self,cords,heading,debug):
 #       x,y = cords
    def turn(self, angle, debug):
    #90 degrees = .38
        angle /= 90
        angle *= -.38
        mc.rotateTwoMotors(45,2,0,False)
        mc.rotateTwoMotors(-45,1,3,False)
        mc.moveDistance(angle,False,True)
        mc.adjustForward(False)
    def boxDrill(self,dis,debug):
        self.adjustForward(debug)
        self.moveDistance(dis,debug,False)
        time.sleep(1)
        self.horizontalMode(debug,False)
        time.sleep(1)
        self.moveDistance(-dis,debug,False)
        time.sleep(1)
        self.adjustForward(debug)
        time.sleep(1)
        self.moveDistance(-dis,debug,False)
        time.sleep(1)
        self.horizontalMode(debug)
        time.sleep(1)
        self.moveDistance(dis,debug,False)
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
#mc = MotorController()
#mc.adjustForward(True)
#mc.boxDrill(1,False)
#mc.adjustForward(False)
#mc.moveCord((-1,1),False)
#mc.moveCord((1,0),False)
##mc.moveCord((0,-1),False)

#mc.adjustForward(False)
#mc.moveCord((0,1),True)
#mc.moveCord((-1,1),False)
#mc.turn(90,False)
#mc.moveCord((1,0),False)
#mc.turn(270,False)



#mc.moveCords((4,5),True)
#print("complete")
