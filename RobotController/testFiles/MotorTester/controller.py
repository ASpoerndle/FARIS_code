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
        self.joy = pygame.joystick.Joystick(0)
        self.mode = "normal"
        self.allowLX = True
        self.allowLY = True
        self.allowRX = True
        self.allowRY = True
        self.servoState = False
        self.end = False
        self.controls = {
            "normal":{
                0:self.toSideways,
                1:self.toForward,
                2:self.toTurn,
                7:self.servoControl,
                8:print(self.motorController.getHeading()),
                4:self.slowDown,
                5:self.speedUp,
                6: self.toPlan,
                9:self.endProgram 

            },
            "planning":{
                0:self.motorController.telePathClear,
                1:self.telePathStart,
                2:self.telePathSave,
                3:self.motorController.telePathPlay,
                6:self.toForward,
            },
            "sideways": {
                1:self.toForward,
                2:self.toTurn
            },
            "turning": {
                0: self.toSideways,
                1:self.toForward

            }

        }
    def endProgram(self):
        self.end = True
    def telePathSave(self):
        self.motorController.telePathSave(True)
        print("Path Saved")
        self.allowLX = True
    def servoControl(self):
        self.servoState = not self.servoState #true = in False = out
        if(self.servoState == True):
            self.motorController.teleServoIn()
        else:
            self.motorController.teleServoOut()
    def toPlan(self):
        print("Planning...")
        self.mode = "planning"

    def telePathStart(self):
        print("Path starting...")
        self.allowLX = False
        self.motorController.telePathStart(True)

    def speedUp(self):
        self.SLOW_DOWN = 3

    def slowDown(self):
        self.SLOW_DOWN = 1.5

    def toSideways(self):
        print("sideways...")
        self.mode = "sideways"
        self.allowLY = False
        self.allowRX = False
        self.allowRY = False
        self.motorController.horizontalMode(False)

    def toForward(self):
        self.mode = "normal"
        self.allowLX = True
        self.allowLY = True
        self.allowRX = True
        self.allowRY = True
        self.motorController.adjustForward(False)

    def toTurn(self):
        print("turning...")
        self.mode = "turning"
        self.allowLX = False
        self.allowLY = False
        self.motorController.teleTurn()

    def handleButtonInput(self, button):
        #try:
            mode_buttons = self.controls[self.mode]
            mode_buttons[button]()
        #except Exception as e:
            print("ERR: Button not mapped")
         #   print(e)
    def use_controller(self):
        mc = self.motorController

        if pygame.joystick.get_count() == 0:
            print("No controller found")
        else:
            self.joy.init()

            print(f"Detected: {self.joy.get_name()} | count {pygame.joystick.get_count()} | button num | {self.joy.get_numbuttons()}")

            try:
                while self.end == False:
                    pygame.event.pump() # Internal pygame update
                    joyLY = self.joy.get_axis(1)
                    joyLX = self.joy.get_axis(0)
                    joyRY = self.joy.get_axis(3)
                    joyRX = self.joy.get_axis(2)

                    for event in pygame.event.get():
                        if (event.type == pygame.JOYBUTTONDOWN):
                            self.handleButtonInput(event.button)


                    if self.mode == "normal" or self.mode == "planning":
                        if(abs(joyLY) >=0.2 and self.allowLY and abs(joyLX) >= 0.2 and self.allowLX):
                            self.motorController.teleForward(-joyLY/self.SLOW_DOWN)
                            self.motorController.teleRotate(joyLX/self.SLOW_DOWN)
                        elif abs(joyLY) >= 0.2 and self.allowLY:
                            self.motorController.teleForward(-joyLY / self.SLOW_DOWN)
                        elif abs(joyLX) >= 0.2 and self.allowLX:
                            self.motorController.teleRotate(joyLX / self.SLOW_DOWN)
                        else:
                            mc.stopMotors()

                    elif self.mode == "sideways":
                        if abs(joyLX) >= 0.2 and self.allowLX:
                            self.motorController.teleForward(joyLX / self.SLOW_DOWN)
                        else:
                            mc.stopMotors()

                    elif self.mode == "turning":
                        if abs(joyRX) >= 0.2 and self.allowRX:
                            self.motorController.teleMoveTurn(joyRX / self.SLOW_DOWN)
                        else:
                            mc.stopMotors()
                    else:
                        mc.stopMotors()

                    pygame.time.wait(10) # Prevent 100% CPU usage
            except KeyboardInterrupt:
                pygame.quit()
mc = MotorController()
controller = controller(mc)
controller.use_controller()
