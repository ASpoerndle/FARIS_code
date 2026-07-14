import pygame
import os
import time
from MotorController import MotorController


"""
NUM | BUTTON
0 - X
1 - A
2 - B
3 - Y
4 - LB
5 - RB 
6 - LT
7 - RT
8 - SEL
9 - START
10 - LSTICK 
11 - RSTICK
"""



class controller():
   
   

    def __init__(self, MC):
        self.motorController = MC
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        self.SLOW_DOWN = 1.5
        pygame.init()
        pygame.joystick.init()
        self.joy = None
        self.mode = "normal"
        self.subMode = "normal"
        self.allowLX = True
        self.allowLY = True
        self.allowRX = True
        self.allowRY = True
        self.servoState = False
        self.end = False
        buttonsXbox = {
            "X":0,
            "A":1,
            "B":2,
            "Y":3,
            "LB":4,
            "RB":5,
            "LT":6,
            "RT":7,
            "SELECT":8,
            "START":9,
            "L3":10,
            "R3":11



        }


        self.controls = {
            "normal":{
                buttonsXbox["X"]:self.toSideways,
                buttonsXbox["A"]:self.toForward,
                buttonsXbox["B"]:self.toTurn,
                buttonsXbox["RT"]:self.servoControl,
                buttonsXbox["SELECT"]:print(self.motorController.getHeading()),
                buttonsXbox["LB"]:self.slowDown,
                buttonsXbox["RB"]:self.speedUp,
                buttonsXbox["LT"]: self.toPlan,
                buttonsXbox["START"]:self.endProgram,
                buttonsXbox["L3"]:self.motorController.createWaypoint,
                buttonsXbox["R3"]:self.travelToWay


            },
            "planning":{
                buttonsXbox["X"]:self.motorController.telePathClear,
                buttonsXbox["A"]:self.telePathStart,
                buttonsXbox["B"]:self.telePathSave,
                buttonsXbox["Y"]:self.telePathPlay,
                buttonsXbox["LB"]:self.toSideways,
                buttonsXbox["RB"]:self.toTurn,
                buttonsXbox["LT"]:self.toForward,
                buttonsXbox["RT"]:self.adjustForward
            },
            "sideways": {
                buttonsXbox["A"]:self.toForward,
                buttonsXbox["B"]:self.toTurn
            },
            "turning": {
                buttonsXbox["X"]: self.toSideways,
                buttonsXbox["A"]:self.toForward

            }

        }
    def travelToWay(self):
        
        self.motorController.travelToWaypoint(0,"l")
    def adjustForward(self):
        self.motorController.teleOperationController.adjustForward(False)
        self.subMode = "normal"
        self.allowLY = True
        self.allowLX = True
        
    def telePathPlay(self):
        self.allowLY = False
        self.motorController.telePathPlay()
        self.allowLY = True
        
    def endProgram(self):
        self.end = True
        print("Goodbye...")
    def telePathSave(self):
        if(self.subMode == "turning"):
            self.motorController.telePathSaveTurn(True)
        else:
            self.motorController.telePathSaveCord(True)
        print("Path Saved")
        self.allowLX = True
        self.allowLY = True
    def servoControl(self):
        self.servoState = not self.servoState #true = in False = out
        if(self.servoState == True):
            self.motorController.teleOperationController.teleServoIn()
        else:
            self.motorController.teleOperationController.teleServoOut()
    def toPlan(self):
        self.mode = "planning"
        print(f"Mode: {self.mode}")
    def telePathStart(self):
        if(self.subMode != "sideways"): 
            self.allowLX = False

        self.motorController.telePathStart(self.subMode,False)

    def speedUp(self):
        self.SLOW_DOWN = 3

    def slowDown(self):
        self.SLOW_DOWN = 1.5

    def toSideways(self):
        if(self.mode != "planning"):
            print(f"Mode: {self.mode}")
            self.mode = "sideways"
            self.subMode = "normal"
        else:
            self.subMode = "sideways"

        self.allowLY = False
        self.allowRX = False
        self.allowRY = False
        self.allowLX = True
        self.motorController.teleOperationController.horizontalMode(False)

    def toForward(self):
        self.mode = "normal"
        self.subMode = "normal"
        print(f"Mode: {self.mode}")
        self.allowLX = True
        self.allowLY = True
        self.allowRX = True
        self.allowRY = True
        self.motorController.teleOperationController.adjustForward(False)
        print("Forward")

    def toTurn(self):
        if(self.mode != "planning"):
            print("turning...")
            self.mode = "turning"
            self.subMode = "normal"
        else:
            self.subMode = "turning"
        self.allowLX = False
        self.allowLY = False
        self.allowRX = True
        
        self.motorController.teleOperationController.teleTurn()

    def handleButtonInput(self, button):
        try:
            mode_buttons = self.controls[self.mode]
            mode_buttons[button]()
        except Exception as e:
            print("ERR: Button not mapped")
            print(e)
    def use_controller(self):
        mc = self.motorController
        controller = True

        while pygame.joystick.get_count() == 0:
            print("No controller found")
            time.sleep(3)
            if(pygame.joystick.get_count() > 0):
                self.joy = pygame.joystick.Joystick(0)
                self.joy.init()
        else:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()

            print(f"Detected: {self.joy.get_name()} | count {pygame.joystick.get_count()} | button num | {self.joy.get_numbuttons()}")

            try:
                while self.end == False:
                    #print(mc.getHeading())
                    pygame.event.pump() # Internal pygame update
                    for event in pygame.event.get():
                        if event.type == pygame.JOYDEVICEREMOVED:
                            controller = False
                            break
                        if (event.type == pygame.JOYBUTTONDOWN):
                            self.handleButtonInput(event.button)
                    joyLY = self.joy.get_axis(1)
                    joyLX = self.joy.get_axis(0)
                    joyRY = self.joy.get_axis(3)
                    joyRX = self.joy.get_axis(2)

   
                    if(controller == False):
                        print("Please connect controller")
                        mc.stopMotors()
                        if(pygame.joystick.get_count() > 0):
                            self.joy = pygame.joystick.Joystick(0)
                            self.joy.init()
                            controller = True
                        else:
                            time.sleep(1)
                            pass
                    if self.mode == "normal" or self.mode == "planning":
                        if(abs(joyLY) >=0.2 and self.allowLY and abs(joyLX) >= 0.2 and self.allowLX and self.subMode != "sideways"):
                            if(joyLY > 0):
                                joyLX = -joyLX
                            self.motorController.teleOperationController.teleForward(-joyLY/self.SLOW_DOWN)
                            self.motorController.teleOperationController.teleRotate(joyLX/self.SLOW_DOWN)
                        elif abs(joyLY) >= 0.2 and self.allowLY:
                            self.motorController.teleOperationController.teleForward(-joyLY / self.SLOW_DOWN)
                            self.motorController.teleOperationController.teleRotate(0)
                        elif abs(joyLX) >= 0.2 and self.allowLX and self.subMode != "sideways":
                            self.motorController.teleOperationController.teleRotate(joyLX / self.SLOW_DOWN)
                        elif abs(joyRX) >= 0.2 and self.allowRX:
                            self.motorController.teleOperationController.teleMoveTurn(joyRX / self.SLOW_DOWN)
                        elif abs(joyLX) >= 0.2 and self.allowLX and self.subMode == "sideways":
                            self.motorController.teleOperationController.teleSideways(joyLX/self.SLOW_DOWN)
                        else:
                            mc.stopMotors()

                    elif self.mode == "sideways":
                        if abs(joyLX) >= 0.2 and self.allowLX:
                            self.motorController.teleOperationController.teleSideways(joyLX / self.SLOW_DOWN)
                        else:
                            mc.stopMotors()

                    elif self.mode == "turning":
                        if abs(joyRX) >= 0.2 and self.allowRX:
                            self.motorController.teleOperationController.teleMoveTurn(joyRX / self.SLOW_DOWN)
                        else:
                            mc.stopMotors()
                    else:
                        mc.stopMotors()

                    pygame.time.wait(10) # Prevent 100% CPU usage
            except KeyboardInterrupt:
                pygame.quit()
                #self.motorController.forceJoin()
                del self.motorController

mc = MotorController()
controller = controller(mc)
controller.use_controller()
