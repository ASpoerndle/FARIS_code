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
        self.isSideways = False
        self.isTurn = False
        self.isPlan = False
       
        self.controls = {
            # SIDEWAYS MODE
            self.joy.get_button(0) and not isSideways: self.toSideways,  # X
            # NORMAL MODE
            self.joy.get_button(1) and not self.isPlan: self.toForward,  # A
            # TURN MODE
            self.joy.get_button(2) and not self.isTurn: self.toTurn,  # B
            # ALWAYS ON
            self.joy.get_button(7): self.motorController.teleServoIn,  # RBB
            not self.joy.get_button(7): self.motorController.teleServoOut,  # not RBB
            self.joy.get_button(8): print(self.motorController.getHeading()),  # SEL
            self.joy.get_button(4) and self.SLOW_DOWN > 1 and not self.joy.get_button(
                5): self.slowDown,  # LSB
            self.joy.get_button(5) and self.SLOW_DOWN < 10 and not self.joy.get_button(4): self.speedUp,  # RSB
            # PLANNING MODE
            self.isPlan and self.joy.get_button(2): self.motorController.telePathSave,  # B
            self.isPlan and self.joy.get_button(1): self.telePathStart,  # A
            self.isPlan and self.joy.get_button(3): self.motorController.telePathPlay,  # Y
            not self.isPlan and self.joy.get_button(6): self.toPlan,  # LBB
            #self.isPlan and self.joy.get_button(0): self.motorController.telePathClear  # X
        }
        time.sleep(3)

    def toPlan(self):
        print("Planning...")
        self.isSideways = False
        self.isTurn = False

    def telePathStart(self):
        print("Path starting...")
        self.allowLX = False
        self.motorController.telePathStart(False)

    def speedUp(self):
        self.SLOW_DOWN = 3

    def slowDown(self):
        self.SLOW_DOWN = 1.5

    def toSideways(self):
        print("sideways...")
        self.isSideways = True
        self.isTurn = False
        self.isPlan = False
        self.allowLY = False
        self.allowRX = False
        self.allowRY = False
        self.motorController.horizontalMode(False)

    def toForward(self):
        self.isSideways = False
        self.isTurn = False
        self.allowLX = True
        self.allowLY = True
        self.allowRX = True
        self.allowRY = True
        self.motorController.adjustForward(False)

    def toTurn(self):
        print("turning...")
        self.isSideways = False
        self.isTurn = True
        self.allowLX = False
        self.allowLY = False
        self.motorController.teleTurn()

    def use_controller(self):
        mc = self.motorController

        if pygame.joystick.get_count() == 0:
            print("No controller found")
        else:

            self.allowLX = True
            self.allowLY = True
            self.allowRX = True
            self.allowRY = True
            #joy2 = pygame.joystick.Joystick(1)
            self.joy.init()
            #joy2.init()

            print(f"Detected: {self.joy.get_name()} | count {pygame.joystick.get_count()} | button num | {self.joy.get_numbuttons()}")
            default = self.joy.get_axis(0)
            try:
                while True:
                    pygame.event.pump() # Internal pygame update

                    # Button 0 is usually 'A' on the F310 in X-mode
                    if (abs(self.joy.get_axis(0)) >= 0.2 and self.allowLY):
                        # print(f"left and right {joy.get_axis(0)}")
                        mc.teleForward(self.joy.get_axis(0) / self.SLOW_DOWN)
                    elif(abs(self.joy.get_axis(1) >= 0.2) and self.allowLX):
                        mc.teleRotate(self.joy.get_axis(1)/self.SLOW_DOWN)
                    # elif ((abs(self.joy.get_axis(1)) >= 0.2 or abs(
                    #         self.joy.get_axis(0)) >= 0.2) and allowLY and allowLX):
                    #     if (abs(self.joy.get_axis(1)) <= 0.4):
                    #         fSpeed = 0
                    #     else:
                    #         fSpeed = self.joy.get_axis(1)
                    #     if (abs(self.joy.get_axis(0)) <= 0.4):
                    #         turnSpeed = 0
                    #     else:
                    #         turnSpeed = self.joy.get_axis(0)
                    #     if (self.joy.get_axis(1) > 0.4):
                    #         turnSpeed *= -1
                    #     mc.teleForward(-fSpeed / self.SLOW_DOWN)
                    #     mc.teleRotate(turnSpeed / self.SLOW_DOWN)
                    #     # print(f" up and down {joy.get_axis(1)}")
                    elif(self.joy.get_button(3) and self.joy.get_button(9)):
                        mc.rotatePods(-45,False)
                        mc.adjustForward(False)
                        break

                    elif(abs(self.joy.get_axis(2)) >= 0.2 and self.isTurn and not self.isSideways):
                        mc.teleMoveTurn(self.joy.get_axis(2)/self.SLOW_DOWN)
                    elif(abs(self.joy.get_axis(2)) >= 0.2 and not self.isTurn and not self.isSideways):

                        mc.teleRotate(self.joy.get_axis(2)/self.SLOW_DOWN)


                    else:
                        for i in range(len(self.controls)):
                            if(self.controls[i] == True):
                                print(controller.controls[i])
                                self.controls[i]()
                                self.controls[i](False)
                        mc.stopMotors()
                    pygame.time.wait(10) # Prevent 100% CPU usage
            except KeyboardInterrupt:
                pygame.quit()
mc = MotorController()
controller = controller(mc)
controller.use_controller()
