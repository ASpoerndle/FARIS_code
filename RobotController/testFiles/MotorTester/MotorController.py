from RotationalMotor import RotationalMotor
from PodController import PodController
from WheelController import WheelController
from PathController import PathController
from WaypointController import WaypointController
from Servo import Servo
import threading
import board
from PodMotor import PodMotor
from WheelMotor import WheelMotor
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
        #Code for Jetson/adafruit breakout board
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        i2c = board.I2C()
        pca = PCA9685(i2c)
        pca.frequency = 50
        rotational_motor_list = []
        self.servo_list = []
        self.pathController = PathController()
        self.waypointController = WaypointController()
        self.gpsThread = threading.Thread(target=self.waypointController.updateGPS)
        self.gpsThread.start()
        """
        PWM Pin, left or right side, encoder port, forwardValue 
        """
        
        pin_list_rotational = [
         #PodMotors
         [0, "l", 4, 1055] , #BL - Pod-0
         [1, "l", 5, 237], #BR - Pod-1
         [2, "l", 6, -113], #FR - Pod-2
         [3, "l", 7, 1064], #FL - Pod-3
         #WheelMotors
         [4, 'l', 2, 0],   #FL - Wheel-0
         [5, 'l', 1, 0],   #BL - Wheel-1
         [6, 'r', 3, 0],   #FR - Wheel-2
         [7, 'r', 0, 0]]   #BR - Wheel-3
        
        """
        Init Servos
        """
        pin_list_servos = [8]
            


        
        print("readying motors...")
        for i,motor in enumerate(pin_list_rotational):
            if(i > 3):
                motor = WheelMotor(pca, motor[0], motor[1], motor[2], motor[3])
            else:
                motor = PodMotor(pca,motor[0],motor[1], motor[2], motor[3])
            rotational_motor_list.append(motor)
        print("motors ready!")
        print("readying servos...")
        for i in pin_list_servos:
            servo = Servo(pca,i)
            self.servo_list.append(servo)


        self.wheelController = WheelController(rotational_motor_list[4:8])
    

        self.heading = self.getHeading()
        self.podController = PodController(rotational_motor_list[0:4])
        
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
    Method: teleMoveTurn(Speed)
    Purpose: For the TeleOp controller, allows for the robot to turn in place in "Turn Mode"
    """
    def teleMoveTurn(self,speed):
             
           self.wheelController.teleMoveTurn(speed)

    def teleSideways(self,speed):
        self.wheelController.teleSideways(speed)

    """
    Method: teleRotate(speed)
    Purpose: For the TeleOp controller, allows the pod motors to rotate together while maintaining the same heading
    """
    def teleRotate(self,speed):
        self.podController.teleRotate(speed)
    
    """
    Method: teleServoIn()
    Purpose: Closes gripper as long as the specific button is pressed
    """
    def teleServoIn(self):
        self.servo_list[0].setAngle(60)
    """
    Method: teleServoOut()
    Purpose: Opens gripper
    """
    def teleServoOut(self):
        self.servo_list[0].setAngle(120)



    """
    ===PATH PLANNING METHODS===
    """

    """
    Method: getWheelTicks()
    Purpose: When the user pushes LSB, the robot should save how many ticks the wheel motors have run so far. We can take this value as well as some unit 
             conversion to determine how far the robot traveled in both the x and y direction, very useful for saving and loading paths
    """
    def getWheelTicks(self,debug=False):
        tick_list = self.wheelController.getWheelTicks()
        if(debug):
            print(f"Ticks for all wheel motors: {tick_list}")
        return tick_list

    """
    Method: ticksToMeters()
    Purpose: After getting the ticks, convert them into meters for saving them to a text file
    """
    def ticksToMeters(self,debug=False):
        ticks = self.getWheelTicks(debug)    
        cir = math.pi * 0.192
        #self.rotatePods(0,.5)
        distance = (ticks/1425.1) * cir
        if(debug):
            print(f"Tick of WheelMotor 0: {ticks} | distance (m): {distance}")
        return distance
    """
    Method: convertToCoordinates()
    Purpose: converts the ticks measured by the encoders in the wheel motors, as well as the angle the pod motors are facing, first to meters and then 
             into x,y coordiantes that can be saved and read via PathController
    """
    def convertToCoordinates(self,debug=False):
        distance = self.ticksToMeters(debug) #in meters
        podAngle = self.podController.getPodAngle(debug) #We can do right triangle trig to find x and y 
        podAngleRad = math.radians(podAngle)
        x = math.sin(podAngleRad)*distance
        y = math.cos(podAngleRad) * distance
        return x,y

    """
    Method: telePathSave() PathPlan-[b]
    Purpose: When the user presses LSB whilst in Path Planning Mode, the path the robot took (including angle the pod motors are heading in) is saved to a
             text file where it can be played back for automation purposes.
    """
    def telePathSaveCord(self,debug=False):

        x,y = self.convertToCoordinates(debug)
        x = round(x,1)
        
        y = round(y,1)
        if(self.podController.getPodAngle(False) == abs(90)):
            y = 0
        print(x,y)
        #if(abs(x)<0.2):
         #   x = 0
        self.pathController.writePath([x,y,0])
        self.wheelController.resetEncoder()
        self.adjustForward(debug)

    """
    Method: telePathSaveTurn()
    Purpose: whenever the user wants to turn while doing path planning, it saves that turn without accidentally trying
             to save x,y data
    """
    def telePathSaveTurn(self,debug=False):
        print(f"Start Heading: {self.heading % 180} | Current Heading: {self.getHeading() % 180}")
        headingDifference = (self.getHeading() % 360) - (self.heading % 360)
        headingDifference *= -1
        #if(headingDifference < -180):
        #    headingDifference += 180
        if(headingDifference > 180):
            headingDifference -= 180
        headingDifference = int(headingDifference)
        self.heading = self.getHeading()
        self.pathController.writePath([0, 0, headingDifference])
        self.wheelController.resetEncoder()
        self.adjustForward(debug)

    """
    Method: telePathStart() PathPlan-[a]
    Purpose: resets the encoders for accurate forward and backward tick data. Will also disable the ability for a user to rotate the pod wheels and lock
             forward and backward motion
    """
    def telePathStart(self,mode,debug=False):
        self.wheelController.resetEncoder()
        self.heading = self.getHeading()
        if(mode != "turning"):
            self.podController.rotatePods(self.podController.getPodAngle(debug))
    """
    Method: telePathPlay() PathPlan-[y]
    Purpose: plays back the most recently saved path
    """
    def telePathPlay(self):
        print("Playing path...")
        print(f"Pod Angle {self.podController.getPodAngle(False)}")
        self.wheelController.resetEncoder()  
        cords = self.pathController.readPath()
        print(cords)
        for i in cords:
            print(i)
            x = i.split(",")
            cord = float(x[0]),float(x[1])
            angle = float(x[2])
            if(angle != 0 ):
                self.turn(angle)
                continue
            x,y = cord
            if(x ==0 and y ==0):
                continue
            print(x,y)
            self.moveCord((x, y),False)
        print("path played!")
    """
    Method: telePathClear() PathPlan-[LSB + RSB]
    Purpose: clears the current Path.txt document of all recorded paths
    """
    def telePathClear(self):
        print("Path cleared")
        self.pathController.clearPath()

    def readPath(self):
        path_list = self.pathController.readPath()
        for i in range(len(path_list)):
            x, y = path_list[i].split(",")
            self.moveCord([float(x), float(y)], True)

    """
    Method: writePath()
    Purpose: takes in a list of cords and writes them to the PathController
    """

    def writePath(self, cords):
        for i in cords:  # [[x,y],[x,y],...]
            self.pathController.writePath(i)
    """
    WAYPOINT METHODS
    """
    """
    Method: createWaypoint()
    Purpose: creates a waypoint at the GPS' current position. Used mainly in teleop controlled situations.
    """
    def createWaypoint(self):
        self.waypointController.setWaypoint()

    """
    Method: travelToWaypoint(int index, char path_shape)
    Purpose: travels to specified waypoint using desired path shape ("d" == diagonal path, 
             "l" == travel vertical distance then horizontal distance)
    """
    def travelToWaypoint(self, i, shape):
        cords = None
        cords = self.waypointController.travelToWaypoint(i)
        print(cords)
        if(cords != None):
            if(shape == "d"):
                self.travelDiagonal(cords)
            if(shape == "l"):
                self.travelLongWay(cords)
            print(f"Travled Cords: {cords}")
        else:
            print("ERR: Failed to travel to specified Waypoint")
    """
    Method: travelLongWay(list<float> cords)
    Purpose: the robot travels a longer path to the waypoint where it travels the vertical distance first
             and then travels the horizontal distance
    """
    def travelLongWay(self,cords):
        x,y = cords
        self.moveCord([0,y],False)
        self.moveCord([x,0], False)

    """
    Method: travelDiagonal(list<float> cords)
    Purpose: the robot travels a diagonal path to the waypoint
    """
    def travelDiagonal(self, cords):
        self.moveCord(cords,False)
    """
    GENERIC MOVEMENT METHODS
    """
    """
    Method: adjustForward(debug)
    Purpose: resets the Pod motors so that they're facing forwards and are ready to rotate in the same direction together
    """

    def adjustForward(self, debug=False):

        self.podController.rotatePods(0, debug)
        return
    """
    Method: faceForward(debug)
    Purpose: if the current heading isn't 0, turn the robot so that it's facing 0
    """
    def faceForward(self,debug=False):
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
        self.wheelController.driveForward(ticks,inPlace, podHeading, debug)

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
    def moveDistance(self, distance, turnInPlace=False, debug= False):
        #ALL VALUES IN METERS
        cir = math.pi * 0.192
        #self.rotatePods(0,.5)

        ticks = (distance / cir) * 1425.1
        if(debug):
            print(f"Ticks: {ticks} | distance: {distance} | isZero: {turnInPlace}")
        if(turnInPlace):
            print("check line 327 of file MotorController")
            self.wheelController.driveForwardTurning(ticks,debug=debug) #sets in place = -1 which allows turning


        else:
            if(debug):
                print(f"Rotating forward...")
            self.wheelController.driveForward(ticks,1,self.podController.getPodMotor(0).getCurrentAngle(), debug)

    """
    Method: horizontalMode(debug)
    Purpose: sends a command to the podController to rotate the pods so that the robot can crab
             walk 
    """
    def horizontalMode(self,debug=False):
        self.podController.rotateXMotors(90,[0,2])
        self.podController.rotateXMotors(-90, [1, 3])

        # self.podController.rotatePods(-90,debug)
    """
    Method: rotateXMotors(angle, motorList,debug)
    Purpose: sends a command to the podController specifying which motors to rotate to
             a specified degree angle
    """
    def rotateXMotors(self,angle,motorList,debug=False):
        self.podController.rotateXMotors(angle,motorList,debug)


    """
    Method: moveCord(cords, debug)
    Purpose: given a x,y coordinate (in meters), send the proper commands to the wheel and pod
             controllers to allow the robot to travel the shortest path to that destination
    """
    def moveCord(self, cords,debug=False):
        x,y = cords
        hypo = math.sqrt((x**2) + (y**2))
        if(hypo != 0):
            angle = (math.acos(y/hypo) * 180)/math.pi
        print(f"X: {x} Y: {y} hypo: {hypo}") 

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
        if(angle > 90):
            angle -= 90
        if(angle < -90):
            angle += 90
        if(y < 0 and hypo > 0):
            hypo = -hypo
        elif(x<0 and hypo < 0 and y != 0):
            hypo = -hypo
        if(angle != 0 and angle != -90):
            self.podController.rotatePods(angle,debug)
        elif(angle == -90):
            self.horizontalMode()
        print(f"Moving distance...")
        print(x,y,hypo,angle)
        self.moveDistance(hypo,False,debug=True)
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
    def turn(self, angle, debug=False):
    #90 degrees = .38
        angle /= 90
        angle *= .38
        self.podController.rotateXMotors(45,[2,0],debug)

        self.podController.rotateXMotors(-45,[1,3],debug)
        self.moveDistance(angle,True,debug=True)
        self.podController.adjustForward(False)
    """
    Method: getHeading()
    Purpose: to retrieve the current heading of the Octoquad
    """
    def getHeading(self):
       return self.wheelController.getHeading()

    
    def forceNewHeading(self):
        heading = self.getHeading()
        self.heading = heading




    """
       Method: stopMotors()
       Purpose: calls a command to the pod and wheel controllers that stops the motors from running
                but provides the proper amount of current to enable them to not move freely
       """

    def stopMotors(self):
        self.podController.stopMotors()
        self.wheelController.stopMotors()
    def forceJoin(self):
        self.gpsThread.join()
    """
    Method: __del__()
    Purpose: kills the power being supplied to the motors when the MotorController object gets
             deleted
    """

    def __del__(self):


        self.podController.killMotors()
        self.wheelController.killMotors()
        time.sleep(2)
        self.waypointController.stopUpdating()
        print("day")
        self.gpsThread.join(3.0)
        self.gpsThread.is_alive()
        for servo in self.servo_list:
            servo.killServo()
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
