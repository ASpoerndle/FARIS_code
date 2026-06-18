import pygame
import os
import time
from MotorController import MotorController
# Hide the "XDG_RUNTIME_DIR" error if you are on SSH
os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
pygame.joystick.init()
time.sleep(3)
def get_default(obj,num):
    return obj.get_axis(num)
mc = MotorController()

mc.adjustForward(False)
SLOW_DOWN = 1.5
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






isSideways = False
if pygame.joystick.get_count() == 0:
    print("No controller found! Check the X/D switch on the back.")
else:

    joy = pygame.joystick.Joystick(0)
    #joy2 = pygame.joystick.Joystick(1)
    joy.init()
    #joy2.init()
    isTurn = False
    print(f"Detected: {joy.get_name()} | count {pygame.joystick.get_count()} | button num | {joy.get_numbuttons()}")
    default = joy.get_axis(0)
    try:
        while True:
            pygame.event.pump() # Internal pygame update

            # Button 0 is usually 'A' on the F310 in X-mode
            if(abs(joy.get_axis(0)) >= 0.2 and isSideways and not isTurn):
                #print(f"left and right {joy.get_axis(0)}")
                mc.teleForward(joy.get_axis(0)/2)
            elif((abs(joy.get_axis(1)) >= 0.2 or abs(joy.get_axis(0)) >= 0.2)  and not isSideways and not isTurn):
                if(abs(joy.get_axis(1)) <= 0.4):
                    fSpeed = 0
                else:
                    fSpeed = joy.get_axis(1)
                if(abs(joy.get_axis(0)) <= 0.4):
                    turnSpeed = 0
                else:
                    turnSpeed = joy.get_axis(0)
                if(joy.get_axis(1) > 0.4):
                    turnSpeed *= -1
                mc.teleForward(-fSpeed/SLOW_DOWN)
                mc.teleRotate(turnSpeed/2)
                #print(f" up and down {joy.get_axis(1)}")
            elif(joy.get_button(0) and not isSideways):
                mc.horizontalMode(False)
                isSideways = True
                isTurn = False
            elif(joy.get_button(1)):
                mc.adjustForward(False)
                isSideways = False
                isTurn = False
            elif(joy.get_button(3) and joy.get_button(9)):
                mc.rotatePods(-45,False)
                mc.adjustForward(False)
                break
            elif(joy.get_button(2) and not isTurn):
                isTurn = True
                isSideways = False
                mc.teleTurn()
                continue
            elif(abs(joy.get_axis(2)) >= 0.2 and isTurn and not isSideways):
                mc.teleMoveTurn(joy.get_axis(2)/2)
            elif(abs(joy.get_axis(0)) >= 0.2 and not isTurn and not isSideways):
                print("hi")
                #mc.teleRotate(joy.get_axis(0)/2)
            elif(joy.get_button(4) and SLOW_DOWN >1 and not joy.get_button(5)):
                SLOW_DOWN =1.5
            elif(joy.get_button(5) and SLOW_DOWN < 10 and not joy.get_button(4)):
                SLOW_DOWN = 3
            elif(joy.get_button(8)):
                print(mc.getHeading())
            elif(joy.get_button(4) and joy.get_button(5)):
                break
            elif(joy.get_button(7)):
                mc.teleServoIn()
            else:
                mc.teleServoOut()
                mc.stopMotors()
            pygame.time.wait(10) # Prevent 100% CPU usage
    except KeyboardInterrupt:
        pygame.quit()
