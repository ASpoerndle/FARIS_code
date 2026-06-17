from RotationalMotor import RotationalMotor
from PodController import PodController
from WheelController import WheelController
from PathController import PathController
import board

from adafruit_pca9685 import PCA9685

import Jetson.GPIO as GPIO

import time
import math

#50.9:1 and 71.2:1

"""
Class: MotorController
@Author: Aidan Spoerndle
Purpose: This class is the brains of the logic for the robot, the following methods allow for the robot to conduct
         complex movement patterns and interactions between the Pod motors and the Wheel motors. 
"""

class MotorController():
    def __init__(self):
        #Code for Jetson/PWM breakout board
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        i2c = board.I2C()
        pca = PCA9685(i2c)
        pca.frequency = 50
        self.rotational_motor_list = []
        self.p_con = PathController()
        """
        PWM Pin, left or right side, encoder port, forwardValue 
        """

        pin_list_rotational = [
         #PodMotors
         [0, "l", 4, 36] , #BL - Pod-0
         [1, "l", 5, 237], #BR - Pod-1
         [2, "l", 6, 914], #FR - Pod-2
         [3, "l", 7, 1065], #FL - Pod-3
         #WheelMotors
         [4, 'l', 2, 0],   #FL - Wheel-0
         [5, 'l', 1, 0],   #BL - Wheel-1
         [6, 'r', 3, 0],   #FR - Wheel-2
         [7, 'r', 0, 0]]   #BR - Wheel-3



        
        print("readying motors...")
        for i in pin_list_rotational:
            motor = RotationalMotor(pca, i[0], i[1], i[2], i[3])
            self.rotational_motor_list.append(motor)
        print("motors ready!")
        self.heading = self.getHeading()
        self.podController = PodController(self.rotational_motor_list[0:4])
        self.wheelController = WheelController(self.rotational_motor_list[4:8])
        #self.podController.adjustForward(True)
 #       self.rotational_motor_list[5].move_motor(0.2)
        #while(True):
        #    self.teleForward(.1)
        #    for i, motor in enumerate(self.rotational_motor_list):
        #        print("Motor index: " +str(i)+  " | Encoder Value: " + str(motor.getCurrentPosition()))
    """
    ===TELE-OPERATION METHODS===
    """

    """
    Method: teleforward(speed)
    Purpose: For the TeleOp controller, allows for the controller to move the robot forward and backward
    """
    def teleForward(self,speed):
        self.wheelController.teleForward(speed)

    """
    Method: teleTurn()
    Purpose: For the TeleOp controller, sets the robot to "Turn Mode", allowing it to turn in place
    """

    def teleTurn(self):
        self.podController.teleTurn()

    """
    Method: teleTurn()
    Purpose: For the TeleOp controller, sets the robot to "Turn Mode", allowing it to turn in place
    """
    def teleTurn(self):
        self.podController.teleTurn()
    
    def moveOne(self):
        self.podController.rotateXMotors(90,0,True)
    """
    Method: teleMoveTurn(Speed)
    Purpose: For the TeleOp controller, allows for the robot to turn in place in "Turn Mode"
    """
    def teleMoveTurn(self,speed):
             
           self.wheelController.teleMoveTurn(speed)
    """
    Method: teleRotate(speed)
    Purpose: For the TeleOp controller, allows the pod motors to rotate together while maintaining the same heading
    """
    def teleRotate(self,speed):
        self.podController.teleRotate(speed)

    """
    Method: adjustForward(debug)
    Purpose: resets the Pod motors so that they're facing forwards and are ready to rotate in the same direction together
    """
    def adjustForward(self,debug):
        self.wheelController.adjustForward()
        self.podController.rotatePods(0,debug)
        return

    """
    ===PATH PLANNING METHODS===
    """

    """
    Method: getWheelTicks()
    Purpose: When the user pushes LSB, the robot should save how many ticks the wheel motors have run so far. We can take this value as well as some unit 
             conversion to determine how far the robot traveled in both the x and y direction, very useful for saving and loading paths
    """
    def getWheelTicks(self,debug):
        tick_list = self.wheelController.getWheelTicks()
        if(debug):
            print(f"Ticks for all wheel motors: {tick_list}")
        return tick_list

    """
    Method: ticksToMeters()
    Purpose: After getting the ticks, convert them into meters for saving them to a text file
    """
    def ticksToMeters(self,debug):
        ticks = self.getWheelTick(debug)    
        cir = math.pi * 0.192
        #self.rotatePods(0,.5)
        distance = (ticks[0]/1425.1) * cir
        if(debug):
            print(f"Tick of WheelMotor 0: {ticks[0]} | distance (m): {distance}")
        return distance
    """
    Method: convertToCoordinates()
    Purpose: converts the ticks measured by the encoders in the wheel motors, as well as the angle the pod motors are facing, first to meters and then 
             into x,y coordiantes that can be saved and read via PathController
    """
    def convertToCoordinates(self,debug):
        distance = ticksToMeters(debug) #in meters
        podAngle = self.podController.getPodAngle() #We can do right triangle trig to find x and y 
        podAngleRad = math.radians(podAngle)
        x = math.sin(podAngleRad)*distance
        y = math.cos(podAngleRad) * distance
        return x,y

    """
    Method: telePathSave()
    Purpose: When the user presses LSB whilst in Path Planning Mode, the path the robot took (including angle the pod motors are heading in) is saved to a
             text file where it can be played back for automation purposes.
    """
    def telePathSave(self,debug):



    """
    Method: faceForward(debug)
    Purpose: if the current heading isn't 0, turn the robot so that it's facing 0
    """
    def faceForward(self,debug):
        diff = abs(self.heading) - abs(self.getHeading())
        if(debug):
            print(f"Original Heading: {self.heading} | Current Heading: {self.getHeading()} | Difference: {diff}")
        if(abs(diff) > 1):
            self.turn(-diff, debug)

    """
    Method: driveForward(ticks, debug, inPlace)
    Purpose: sends a command to the wheelController to drive the robot forward a designated
             number of ticks, as well as specifying if it's turning in place
    """
    def driveForward(self, ticks,debug,inPlace, podHeading):
        self.wheelController.driveForward(ticks,debug,inPlace, podHeading)

    """
    Method: rotatePods(angle, debug)
    Purpose: sends a command to the podController to rotate the pods by a certain degree angle
    """
    def rotatePods(self, angle,debug):
        self.podController.rotatePods(angle,debug)

    """
    Method: moveDistance(distance, debug, inPlace)
    Purpose: takes in a distance (m), converts it into encoder ticks, and then calls the necessary
             then calls the necessary method depending on if it's moving in the forward direction
             or if it's turning inPlace
    """
    def moveDistance(self, distance, debug,turnInPlace):
        #ALL VALUES IN METERS
        cir = math.pi * 0.192
        #self.rotatePods(0,.5)

        ticks = (distance / cir) * 1425.1
        if(debug):
            print(f"Ticks: {ticks} | distance: {distance} | isZero: {turnInPlace}")
        if(turnInPlace):
            #self.wheelController.switchForTurning()
            self.wheelController.driveForward(ticks,debug,-1,0) #sets in place = -1 which allows turning
            #self.wheelController.switchForTurning()

        else:
            if(debug):
                print(f"Rotating forward...")
            self.wheelController.driveForward(ticks,debug,1,self.podController.getPodMotor(0).getCurrentAngle())

    """
    Method: horizontalMode(debug)
    Purpose: sends a command to the podController to rotate the pods so that the robot can crab
             walk 
    """
    def horizontalMode(self,debug):
        self.podController.rotatePods(-90,debug)
    """
    Method: rotateXMotors(angle, motorList,debug)
    Purpose: sends a command to the podController specifying which motors to rotate to
             a specified degree angle
    """
    def rotateXMotors(self,angle,motorList,debug):
        self.podController.rotateXMotors(angle,motorList,debug)

    """
    Method: stopMotors()
    Purpose: calls a command to the pod and wheel controllers that stops the motors from running
             but provides the proper amount of current to enable them to not move freely
    """
    def stopMotors(self):
        self.podController.stopMotors()
        self.wheelController.stopMotors()
    """
    Method: moveCord(cords, debug)
    Purpose: given a x,y coordinate (in meters), send the proper commands to the wheel and pod
             controllers to allow the robot to travel the shortest path to that destination
    """
    def moveCord(self, cords,debug):
        x,y = cords
        hypo = math.sqrt((x**2) + (y**2))
        angle = (math.acos(abs(x)/hypo) * 180)/math.pi
        if((x < 0 and y < 0) or (x > 0 and y > 0)):
            angle = -angle
        if(x == 0):
            angle = 0
            if(y<0):
                hypo = -hypo
        if(y == 0):
            angle = -90
            if(x < 0):
                hypo = -hypo
        if(debug):
            print(f"X,Y: {x},{y} | Hypotenuse: {hypo} | Angle (Degrees) {angle}")
            
        self.podController.rotatePods(angle,debug)
        print(f"Moving distance...")
        self.moveDistance(hypo,debug,False)
        self.podController.adjustForward(debug)

    """
    Method: moveCurve(cords, endHeading,debug)
    Purpose: travel to a designated x,y cord (in meters) whilst changing headings to a new specified heading
    ===IN-DEVELOPMENT===
    """
    def moveCurve(self,cords,heading,debug):
        #Do more research into ackermann steering
        """
        turning radius = Wheelbase / tan (front wheel angle)
        arc length = turning radius * final_heading
        """

        x,y = cords
    """
    Method: turn(angle,debug)
    Purpose: given a degree angle, send the proper commands to the pod controllers to rotate the
             wheels and then execute the logic to allow the robot to turn in place 
    """
    def turn(self, angle, debug):
    #90 degrees = .38
        angle /= 90
        angle *= .38
        self.podController.rotateXMotors(45,[2,0],debug)

        self.podController.rotateXMotors(-45,[1,3],debug)
        self.moveDistance(angle,debug,True)
        self.podController.adjustForward(False)
    """
    Method: getHeading()
    Purpose: to retrieve the current heading of the Octoquad
    """
    def getHeading(self):
        heading = self.rotational_motor_list[0].getCurrentHeading()
        return heading
    
    def forceNewHeading(self):
        heading = self.getHeading()
        self.heading = heading


    def readPath(self):
        path_list = self.p_con.readPath()
        for i in range(len(path_list)):
            x,y = path_list[i].split(",")
            self.moveCord([float(x),float(y)], False)
    """
    Method: writePath()
    Purpose: takes in a list of cords and writes them to the PathController
    """
    def writePath(self,cords):
        for i in cords: #[[x,y],[x,y],...]
           self.p_con.writePath(i) 
    """
    Method: __del__()
    Purpose: kills the power being supplied to the motors when the MotorController object gets
             deleted
    """
    def __del__(self):


        self.podController.killMotors()
        self.wheelController.killMotors()
        time.sleep(2)

        print("finished")


"""
TESTING GROUNDS FOR MOTORCONTROLLER CLASS
"""
#mc = MotorController()

#===CODE FOR ROTATING ROBOT 90 WHILE MOVING===
#mc.rotateXMotors(45,self.rotational_motors_list[2:4],False)
#mc.moveDistacne(1,False,False)
#mc = MotorController()
#mc.adjustForward(False)
#mc.rotateAllMotors(0.1,45,True)
#mc.adjustForward(True)
#mc.boxDrill(1,False)
#mc.adjustForward(False)
#mc.moveCord((-1,1),False)
#mc.moveCord((1,0),False)
#mc.moveCord((0,-1),False)

#mc.adjustForward(False)
#mc.moveCord((0,1),True)
#mc.moveCord((-1,1),False)
#mc.turn(90,False)
#mc.moveCord((1,0),False)
#mc.turn(270,False)



#mc.moveCords((4,5),True)
#print("complete")
